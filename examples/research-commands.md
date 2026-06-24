# Example Commands

Research AI agent discussion across subreddits:

```bash
python3 reddit-opencli/scripts/redditctl.py research \
  --subreddit openai \
  --subreddit LocalLLaMA \
  --query "agents" \
  --time month \
  --limit 20 \
  --format md
```

Read and summarize a thread:

```bash
python3 reddit-opencli/scripts/redditctl.py thread "<reddit-thread-url>" --format md
```

Preview a write action:

```bash
python3 reddit-opencli/scripts/redditctl.py act comment "<reddit-thread-url>" --text "Draft comment"
```

