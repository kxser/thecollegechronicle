from pathlib import Path

CONTENT_ROOT = Path(__file__).resolve().parent.parent / "content"
BASE_URL = "https://thecollegechronicle.org"

def compute_slug(path: Path) -> str:
    rel = path.relative_to(CONTENT_ROOT)
    if rel.name == "index.md":
        parts = rel.parts[:-1]
        if parts:
            return "/" + "/".join(parts)
        return "/"
    return "/" + rel.with_suffix("").as_posix()

def ensure_alternates(path: Path) -> bool:
    text = path.read_text()
    if not text.startswith("---"):
        return False
    lines = text.splitlines()
    try:
        closing_idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return False
    front_matter = lines[1:closing_idx]
    if any(line.strip().startswith("alternates:" ) for line in front_matter):
        return False
    slug_path = compute_slug(path)
    href = BASE_URL if slug_path == "/" else f"{BASE_URL}{slug_path}"
    insertion = []
    if front_matter and lines[closing_idx - 1].strip():
        insertion.append("")
    insertion.extend([
        "alternates:",
        "  - hreflang: en",
        f"    href: {href}",
    ])
    for offset, value in enumerate(insertion):
        lines.insert(closing_idx + offset, value)
    path.write_text("\n".join(lines) + "\n")
    return True

def main():
    updated = 0
    for md_file in sorted(CONTENT_ROOT.rglob("*.md")):
        if ensure_alternates(md_file):
            updated += 1
    print(f"Updated {updated} files with alternates")

if __name__ == "__main__":
    main()
