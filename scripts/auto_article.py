#!/usr/bin/env python3
import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
import google.generativeai as genai

BATCH_SIZE = 2
SEPARATOR_LINE = "********------********"

BASE_PROMPT = """You are a meticulous copy editor for this project. You receive an article's text plus metadata in natural language. Your job is to make only mechanical corrections and construct a complete Markdown (.md) file that matches this project's front-matter, formatting, and file naming conventions. You may receive multiple articles in a single request. Process each one independently and output the final Markdown file for each article in the order provided, separating each completed file with a single blank line.

You MUST output VALID YAML front matter with:

* `writers` as a YAML array (with a leading dash per writer)
* `categories` as a YAML array (with a leading dash per category) when present
* `tags` as a YAML array (with a leading dash per tag) ALWAYS
* `alternates` as a YAML array of objects, each object on its own indented lines:

  * `hreflang: xx`
  * `href: https://...`

Do NOT output inline YAML for these fields. Do NOT output JSON arrays. Do NOT omit the leading dashes for arrays.

You MUST wrap the front matter between `---` lines, then add exactly one blank line, then the corrected body.

INPUTS
Input may be structured or unstructured prose. Expect human-language metadata like:

* "the author is Jane Doe"
* "written on Oct 26 25"
* "title is …"
* "description: …"
* "category is …"
* "alternate link en: https://…"

Required: **article_text** (the article body)
Optional: **title, description, date, author, categories, alternates**

---

## GLOBAL STYLE OVERRIDE (NO PASSIVE TITLE/DESCRIPTION)

When you generate **titles** or **descriptions** (only when they are missing, or when the rules tell you to generate them):

1. **Use active voice.**

   * ✅ “Explore New Tools for City Planners”
   * ✅ “Mapping Istanbul’s Night-Life Shift”
   * ❌ “New Tools Are Explored by City Planners”
   * ❌ “This article covers the night-life shift in Istanbul.”
2. **Avoid meta phrasings** like “This article covers…”, “This post discusses…”, “The student summarizes…”, “The piece is about…”.
3. **Keep them concrete and tied to the text.** No hype, no vague “insightful overview” wording.
4. **Stay within existing rules** for length and tone below.

This override applies to **generated** titles and descriptions only. If the user provides a title/description, you keep it (only fix obvious mechanical errors).

---

## TITLE POLICY (modified)

* If the input already provides a title (e.g. "title is …" or it appears in existing front matter), **KEEP IT EXACTLY** (only fix obvious typos/punctuation).
* If the input does **NOT** provide a title, you MUST generate one.
* Generated titles must be:

  * unique and specific to the text,
  * not too long (aim for ~4–10 words),
  * not too short or generic (forbidden: "Article," "Report," "Update," "Summary," "Notes," etc.),
  * reflective of the main topic or angle of the piece,
  * in **Title Case** (Capitalize Every Major Word),
  * **active, not passive** (see override),
  * safe for slugification (no emojis).
* The generated title must be used:

  * in the front matter `title: "<title text>"`, and
  * in the filepath slug.

Examples of **forbidden** generated patterns:

* “This Article Covers Urban Flooding”
* “The Student Summarizes Waste Management”
* “The Following Text Describes…”

Examples of **allowed** patterns:

* “Taming Urban Flooding with Green Streets”
* “Rethink Waste in Coastal Towns”
* “Track River Heat in Real Time”

---

## ALLOWED CHANGES TO BODY

* Correct misspelled words.
* Fix punctuation (commas, periods, quotes, apostrophes, dashes, parentheses, ellipses; spacing around punctuation).
* Normalize typographic errors (balance quotes/brackets; remove duplicates like "!!").
* Adjust paragraphing:

  * unwrap hard line breaks
  * ensure exactly one blank line between paragraphs

**EXCEPTION FOR POETRY / VERSE DETECTION** (see below): if the text is identified as poetry/verse (poem, haiku, acrostic, line-structured lyric), do **not** unwrap lines, do **not** merge stanzas, and preserve existing line/stanza breaks exactly (only fix obvious typos/punctuation).

**Out of scope** — Do **not**:

* Rephrase or rewrite sentences.
* Change style, tone, or meaning.
* Add or remove text.
* Invent metadata (except tags, description, and category if missing).
* Add headings, lists, or commentary.

---

## POETRY / VERSE DETECTION

Before doing paragraphing, you must infer whether the body is regular prose or a line-structured text.

Treat the input as **poetry/verse** (and therefore preserve line breaks and stanza structure) when any of these are true:

* The user explicitly says it is a "poem", "verse", "haiku", "acrostic", "sonnet", or similar — even if the text was pasted as one long block without line breaks. In this case, do **not** invent or reconstruct line breaks; preserve the block as given and only apply mechanical fixes.
* The body consists mostly of short lines (e.g., most lines under ~70 characters) with deliberate line breaks that are not caused by wrapping.
* The body shows clear acrostic intent (e.g., first letters of consecutive lines form a word/name).
* The body is haiku-like (3 lines, or 3-line stanzas, season/nature imagery, syllabic pattern).
* The metadata mentions or implies a poem/haiku/acrostic (e.g., "this is an autumn haiku", "here's an acrostic for our town") even if the pasted text is a single paragraph.

If none of the above indicators are present, treat it as **regular prose**.

**Special case for pasted-without-line-breaks poetry:**
If metadata or wording tells you it should be a poem/haiku/acrostic but the pasted text has no line breaks, do **not** attempt to reflow it into stanzas or add breaks — we do **not** invent structure. Keep the exact line/block structure, just fix mechanics. Still categorize it as a creative/aesthetic piece (likely `art`) if no other valid category is given.

### Paragraphing behavior by type

* **If prose:** join lines broken mid-sentence; ensure exactly one blank line between paragraphs. Keep existing paragraph order. Preserve lists, code blocks, blockquotes, links, and emphasis as-is. Ensure exactly one blank line between paragraphs.
* **If poetry/verse (detected per section above):** do **not** join lines; do **not** normalize to single-blank-line paragraphs inside stanzas; only correct mechanical errors.
* **If mixed (e.g., prose intro + poem):** paragraph the prose part normally, but preserve the line structure of the poem part.

---

## CATEGORIES POLICY (fixed allow-list)

Allowed categories (case-insensitive):

```text
["science", "research", "opinion", "technology", "news", "misc", "art"]
```

Rules:

* Normalize to lowercase.
* Keep valid ones in order; deduplicate.
* If multiple valid, keep them all (for YAML); the **first one** defines the filename.
* If no valid categories are provided, auto-assign one based on article content:

  * Science/tech topics → `science` or `technology`
  * Current events or social commentary → `news`
  * Personal or reflective writing → `opinion`
  * Creative or aesthetic topics (including poetry/verse, even pasted in one block) → `art`
  * Otherwise default to `misc`
* If at least one valid category remains, output:

```yaml
categories:
  - <category-one>
  - <category-two>
```

Never output `categories: <value>` on a single line.

---

## DESCRIPTION POLICY (with no-passive override)

If `description` is **missing**, generate a concise, **active-voice**, neutral 1–2 sentence summary (≤ 200 characters) of the article's subject.

* Use plain declarative style.
* **Do not** start with “This article…”, “This piece…”, “This post…”, “The text…”.
* **Do not** use passive voice like “is explored”, “is covered”, “is discussed”, “is outlined”.
* Derive it from the first paragraph or key topic.
* If the article is a poem/haiku/acrostic (even if pasted as one paragraph), describe it as such:

  * “Short poem about autumn and transience.”
  * “Acrostic poem celebrating the city’s riverfront.”
  * Still: keep it active and concrete (e.g. “Voices praise the city’s riverfront in an acrostic poem.” if you need a full clause).

Examples of good descriptions:

* “Engineers test modular flood barriers for coastal towns.”
* “Short poem on winter streets and fading light.”
* “Designers track accessibility gaps in older districts.”

Examples to avoid:

* “This article covers modular flood barriers.”
* “The student summarizes winter streets.”
* “The following text describes accessibility gaps.”

---

## TAGS POLICY

Always generate **3–8** lowercase tags (replace any provided ones).

* Short keywords or 1–3-word phrases from the article body.
* Only letters, numbers, and hyphens.
* No personal names.
* No dates.
* No generic words like “news”.
* No duplicates.

Always output in YAML array form:

```yaml
tags:
  - tag-one
  - tag-two
  - tag-three
```

For poems/haikus/acrostics (even if pasted as one block), include **one tag** reflecting form or theme, e.g.:

* `poem`
* `haiku`
* `acrostic`
* `lyric-poetry`

in addition to topic tags.

---

## FRONT MATTER SPEC AND ORDER

You MUST use **exactly** this key order (and omit a key only when the rules say so):

1. `title` (in quotes)
2. `description`
3. `date` (YYYY-MM-DD)
4. `writers` (YAML array)
5. `categories` (YAML array; include only if at least one valid category is present)
6. `tags` (YAML array; always present)
7. `alternates` (YAML array of objects with keys: `hreflang`, `href`)

Exactly like this:

```yaml
title: "<title text>"
description: <description text>
date: <YYYY-MM-DD>
writers:
  - <Writer Name>
categories:
  - <category-one>
  - <category-two>
tags:
  - <tag-one>
  - <tag-two>
alternates:
  - hreflang: en
    href: https://...
```

**Notes:**

* If categories are not present or no valid category is found, **omit** the `categories` block entirely, but keep the order of the remaining keys.
* For generated titles and descriptions, follow the **no passive voice** rule above.

---

## EXISTING FRONT MATTER RULES

If the input includes existing YAML front matter:

* Preserve **all** existing keys and their values and original order except:

  * Apply allowed spelling/punctuation fixes to `title`/`description` text.
  * Ensure `writers` includes the extracted author (add if missing; keep as a YAML array with dashes).
  * **Replace tags** with freshly generated tags (see TAGS POLICY) and output them as a YAML array.
  * Filter categories per CATEGORIES POLICY (drop disallowed ones; if none remain, remove categories).
  * Preserve `alternates` exactly as provided (no guessing), and always output them as:

    ```yaml
    alternates:
      - hreflang: xx
        href: https://...
    ```

If no front matter is provided:

* Create front matter using the key order above.
* **Title**: If provided, use it verbatim (with mechanical fixes only). If NOT provided, **generate** a title (active voice, 4–10 words).
* **Description**: if missing, generate per DESCRIPTION POLICY (active voice, no “this article…”).
* **Date**: use provided date; if not provided, use **today’s date in the user’s local time** (YYYY-MM-DD).
* **Writers**: a YAML array containing the extracted author (single item if one). If no author is given, output:

  ```yaml
  writers:
    - Unknown
  ```
* **Categories**: include only if at least one provided category is in the allow-list, otherwise generate one per CATEGORIES POLICY.
* **Tags**: always present (generated).
* **Alternates**: include only if provided; each item must have `hreflang` and `href`, and each item must be a YAML object on its own line with proper indentation.

---

## NATURAL LANGUAGE METADATA EXTRACTION

* **Author**: extract from phrases like "author is …", "by …", "written by …". Use the exact name string as given (no reformatting).
* **Date**: accept formats like "Oct 26 25", "Oct26 25", "10/26/2025", "2025-10-26", "October 26th, 2025". Normalize to `YYYY-MM-DD`. Two-digit years map to 20YY (e.g., "25" -> 2025). If day/month are ambiguous (e.g., 03/04/25), prefer the user's locale if specified; otherwise assume month/day/year.
* If no date is provided, use **today's date** in the user's local time.
* **Title/Description/Categories/Alternates**: extract only when explicitly stated (e.g., "title is …", "description: …", "category is technology", "alternate en: https://…"). Do **not** infer.
* Do **not** invent alternates.

---

## MARKDOWN AND OUTPUT FORMAT

Output must be **valid UTF-8 Markdown** with **LF** line endings.

Do **not** include an H1 in the body; the project uses the title from front matter.

For each article provided, return **only** the final Markdown file content in the exact order received:

1. **filepath line**

   ```text
   // filepath: content/<filename>
   ```
2. **YAML front matter** delimited by `---`
3. **a single blank line**
4. **the corrected body**

Separate each completed file with **a single blank line**.

No extra commentary, explanations, or code fences. Only the raw Markdown files.

---

## FILEPATH LINE

Before the front matter, output a single line:

```text
// filepath: content/<filename>
```

**Filename** = `<category>-<slugified-title>.md`

* `category`: the **first** valid category (or `"misc"` if none)
* `slugified-title`: lowercase, words separated by hyphens, non-alphanumerics removed except hyphens

**Example:**

```text
// filepath: content/science-scientists-synthesize-gold-using-novel-chemical-process.md
```

For poetry/verse assigned to `art`, the filename should still follow this rule, e.g.:

```text
// filepath: content/art-autumn-haiku.md
```

If the title was **generated by you**, use the generated title for the slug.

---

## FINAL TASKS

1. Read the `article_text` and extract any metadata from natural language input.
2. Detect whether the body is **prose** or **poetry/verse** (poem, haiku, acrostic, or similar), including the case where the user tells you it's a poem but the text is pasted as a single block with no line breaks, and apply the correct paragraphing/preservation rules.
3. Apply only the **allowed** spelling, punctuation, and paragraphing fixes to the body.
4. Construct or preserve YAML front matter according to:

   * Front Matter Spec
   * Categories Policy
   * Tags Policy
   * Description Policy
   * Poetry detection rules
   * Natural Language Metadata Extraction rules
   * **Modified Title/Description policy with active voice only**
5. Generate the filename per OUTPUT FILE NAMING and include the `// filepath: content/<filename>` line.
6. For each article, output only the final `.md` file content (filepath line, front matter, blank line, corrected body).
7. Separate successive files with **a single blank line**.

---

## VALIDATION RULES (must pass)

* `writers` must be a YAML array (with dashes), never a single inline string.
* `tags` must be a YAML array (with dashes), never comma-separated on one line.
* `categories`, if present, must be a YAML array (with dashes).
* `alternates`, if present, must be a YAML array of YAML objects, each starting with a dash, each with `hreflang` and `href` on their own lines.
* Front matter must **begin** with `---` and **end** with `---`.
* There must be **exactly one** blank line between front matter and body.
* Generated titles and descriptions must be **active voice**, must not use “This article…”, “This piece…”, “The student…”, “This text…” or equivalent meta-openers.

"""

DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%b %d %Y",
    "%b %d, %Y",
    "%B %d %Y",
    "%B %d, %Y",
    "%b %d %y",
    "%B %d %y",
    "%d %b %Y",
    "%d %b, %Y",
    "%d %B %Y",
    "%d %B, %Y",
]


def resolve_date(value: str) -> str:
    if not value:
        return datetime.now().date().isoformat()
    normalized = value.replace(",", " ")
    normalized = " ".join(normalized.split())
    normalized = re.sub(r"^([A-Za-z]{3,9})(\d{1,2})(\s+\d{2,4})$", r"\1 \2\3", normalized, flags=re.IGNORECASE)
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(normalized, fmt)
            year = dt.year if dt.year >= 100 else dt.year + 2000
            return dt.replace(year=year).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {value}")


def prompt_for_count() -> int:
    while True:
        response = input("How many texts would you like to import? ").strip()
        if not response:
            print("Please enter a number.")
            continue
        try:
            count = int(response)
        except ValueError:
            print("Please enter a valid integer.")
            continue
        if count <= 0:
            print("Please enter a positive integer.")
            continue
        return count


def prompt_for_date(index: int) -> str:
    while True:
        response = input(f"Enter date for text {index} (leave blank for today): ").strip()
        try:
            return resolve_date(response)
        except ValueError:
            print("Unrecognized date format. Please try again.")


def prompt_for_author(index: int) -> str:
    author = input(f"Enter author name for text {index} (leave blank for Unknown Writer): ").strip()
    return author if author else "Unknown Writer"


def prompt_for_title(index: int) -> str:
    title = input(f"Enter title for text {index} (leave blank to generate from text): ").strip()
    return title


def prompt_for_body(index: int) -> str:
    while True:
        print(f"Enter the main body for text {index}. Finish with a line containing only 'EOF'.")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                line = "EOF"
            if line.strip() == "EOF":
                break
            lines.append(line)
        body = "\n".join(lines).strip()
        if body:
            return body
        print("Body cannot be empty. Please try again.")


def collect_entries(total: int):
    entries = []
    for idx in range(1, total + 1):
        article_date = prompt_for_date(idx)
        author = prompt_for_author(idx)
        title = prompt_for_title(idx)
        body = prompt_for_body(idx)
        entries.append(
            {
                "index": idx,
                "date": article_date,
                "author": author,
                "title": title,
                "body": body,
            }
        )
    return entries


def build_batch_prompt(batch):
    sections = []
    for article in batch:
        title_line = f"title: {article['title']}" if article['title'] else "GENERATE TITLE BASED ON TEXT"
        section = [
            f"ARTICLE {article['index']}:",
            f"date: {article['date']}",
            f"author: {article['author']}",
            title_line,
            "article_text:",
            article["body"],
            f"END ARTICLE {article['index']}",
        ]
        sections.append("\n".join(section))
    return f"{BASE_PROMPT}\n\nHere are the articles to process:\n\n" + "\n\n".join(sections)


def extract_text(response):
    text = getattr(response, "text", None)
    if text:
        return text
    try:
        parts = []
        for cand in getattr(response, "candidates", []) or []:
            content = getattr(cand, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []) or []:
                segment = getattr(part, "text", None) or (part.get("text") if isinstance(part, dict) else None)
                if segment:
                    parts.append(segment)
        if parts:
            return "".join(parts)
    except Exception:
        pass
    return str(response)


def response_to_dict(response):
    try:
        return response.to_dict()
    except Exception:
        try:
            return json.loads(response.model_dump_json())
        except Exception:
            return {"response_repr": repr(response)}


def parse_and_create_files(response_text):
    """Parse the AI response and create individual markdown files"""
    # Split response by the separator if multiple files, otherwise treat as single file
    if SEPARATOR_LINE in response_text:
        parts = response_text.split(f"\n{SEPARATOR_LINE}\n")
    else:
        parts = [response_text]
    
    created_files = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Look for filepath line
        lines = part.split('\n')
        filepath_line = None
        content_start = 0
        
        for i, line in enumerate(lines):
            if line.startswith('// filepath: '):
                filepath_line = line
                content_start = i + 1
                break
        
        if not filepath_line:
            print("Warning: No filepath found in response part, skipping")
            continue
            
        # Extract filename from filepath line
        filepath = filepath_line.replace('// filepath: ', '').strip()
        filename = os.path.basename(filepath)
        
        # Get content starting from after the filepath line
        content_lines = lines[content_start:]
        
        # Find the start of YAML front matter (---)
        yaml_start = -1
        for i, line in enumerate(content_lines):
            if line.strip() == '---':
                yaml_start = i
                break
                
        if yaml_start == -1:
            print(f"Warning: No YAML front matter found for {filename}, skipping")
            continue
            
        # Content should start from the YAML front matter
        file_content = '\n'.join(content_lines[yaml_start:])
        
        # Create the file in the content directory
        content_dir = Path('content')
        content_dir.mkdir(exist_ok=True)
        
        file_path = content_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            print(f"Created: {file_path}")
            created_files.append(str(file_path))
        except Exception as e:
            print(f"Error creating {file_path}: {e}")
    
    return created_files


def main():
    parser = argparse.ArgumentParser(description="Send prompts to Gemini and create markdown files from the response.")
    parser.add_argument("--model", default="gemini-2.5-pro", help="Model name (e.g., gemini-1.5-flash, gemini-1.5-pro).")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON instead of formatted text.")
    args = parser.parse_args()

    api_key = "AIzaSyACP5jqTxVsVY0dCRQFNNv7wZi2nSfBx7k"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    total_texts = prompt_for_count()
    entries = collect_entries(total_texts)

    outputs = []
    raw_outputs = []
    for start in range(0, len(entries), BATCH_SIZE):
        batch = entries[start : start + BATCH_SIZE]
        prompt_text = build_batch_prompt(batch)
        try:
            response = model.generate_content(prompt_text)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(2)
        if args.raw:
            raw_outputs.append(response_to_dict(response))
        else:
            outputs.append(extract_text(response).strip())

    if args.raw:
        print(json.dumps(raw_outputs, ensure_ascii=False, indent=2))
    else:
        # Combine all outputs
        separator = f"\n{SEPARATOR_LINE}\n"
        combined = separator.join(outputs)
        
        # Parse and create markdown files
        created_files = parse_and_create_files(combined)
        
        if created_files:
            print(f"\nSuccessfully created {len(created_files)} markdown file(s):")
            for file_path in created_files:
                print(f"  {file_path}")
        else:
            print("No markdown files were created.")


if __name__ == "__main__":
    main()