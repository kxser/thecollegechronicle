sudo chown -R $(whoami) .
read -p "Enter commit message: " commit_msg

if [ -z "$commit_msg" ]; then
  echo "Error: Commit message cannot be empty."
  exit 1
fi

git add .
git commit -m "Deploy Production: $commit_msg"
git push
npm run build && npx wrangler deploy