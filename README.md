# kk-Reddit

`kk-Reddit` is a Codex skill for Reddit workflows powered by `opencli-rs`
or OpenCLI (`opencli`).
It wraps the existing Reddit CLI commands with safer action handling,
repeatable research workflows, local monitoring, and clear installation docs.

The skill is designed for:

- Reddit research across subreddits, search queries, frontpage, and popular.
- Thread reading with comment limits, depth, sort order, and Markdown output.
- Watch workflows that show what is new since the last run.
- First-class write actions: comment, upvote, downvote, unvote, save, unsave,
  subscribe, and unsubscribe.
- Explicit safety gates before any Reddit write action is executed.

## Quick install

```bash
curl -fsSL https://raw.githubusercontent.com/vicekang/kk-Reddit/main/install.sh | bash
```

The installer will:

1. Install/check OpenCLI (`opencli`) for the browser bridge.
2. Check whether `opencli-rs` is available.
3. Copy the `reddit-opencli` Codex skill into `${CODEX_HOME:-$HOME/.codex}/skills`.
4. Run diagnostics so you can verify the browser bridge.

After installation, restart or refresh Codex so the skill list is reloaded.

## Requirements

- macOS or Linux shell.
- `opencli-rs` as the preferred CLI backend when present.
- OpenCLI (`opencli`) as the browser bridge provider and fallback backend.
- Chrome or Chromium.
- The OpenCLI Chrome extension connected to the local daemon for browser-mode
  Reddit commands.
- A Reddit login in Chrome for account-specific reads and all write actions.

Check the backend:

```bash
opencli --version
opencli doctor
opencli-rs --version
```

If the doctor output says the Chrome extension is not connected, follow
[Chrome extension setup](docs/CHROME_EXTENSION.md). Install/update OpenCLI with:

```bash
npm install -g @jackwener/opencli
```

Do not use the old `nashsu/opencli-rs` installer link for this project; that
path now installs `autocli`, not the `opencli-rs` binary used by this wrapper.

## Use from Codex

Ask Codex for Reddit work naturally, for example:

- "Use reddit-opencli to find the top discussions about local LLMs in r/LocalLLaMA and r/selfhosted."
- "Read this Reddit thread and summarize the strongest objections."
- "Watch r/openai and r/MachineLearning for new high-engagement posts about agents."
- "Prepare a Reddit comment for this post, show me the exact command, and wait before posting."
- "Subscribe me to r/rust after showing the action preview."

The skill instructs Codex to use the bundled wrapper. By default the wrapper
prefers `opencli-rs` when it exists, then falls back to `opencli`. Force a
backend with `KK_REDDIT_BACKEND=opencli` or `KK_REDDIT_BACKEND=opencli-rs`.

```bash
KK_REDDIT_BACKEND=opencli python3 reddit-opencli/scripts/redditctl.py research --subreddit LocalLLaMA --query "agentic coding" --limit 20 --format md
python3 reddit-opencli/scripts/redditctl.py thread "https://www.reddit.com/r/rust/comments/..." --limit 20 --depth 2 --format md
python3 reddit-opencli/scripts/redditctl.py act upvote "https://www.reddit.com/r/rust/comments/..." --yes
```

For full command examples, see [Usage guide](docs/USAGE.md).

## Safety model

Read-only commands can run directly. Write actions require a two-step flow:

1. Preview the target, text, and exact `opencli-rs` command.
2. Execute only after the user explicitly confirms.

The wrapper will not execute a write action unless `--yes` is supplied.
Codex should only add `--yes` after the user confirms the exact action.

## Do I need a Chrome extension?

Yes for browser-mode Reddit commands. The extension is named **OpenCLI** and is
part of the OpenCLI browser bridge used by `opencli`. `opencli-rs` can use this
browser bridge, but the Chrome extension itself is not called `opencli-rs` or
AutoCLI. Chrome extension installation still needs normal browser extension
setup because Chrome intentionally protects that flow.

Can this project ship a Reddit-specific extension? Yes, but it should be a
separate milestone. A custom extension only helps `opencli-rs` if it implements
the same bridge protocol or if `opencli-rs` is updated to call it. A generic
content script alone will not automatically make `opencli-rs reddit ...` use
it. See [extension design notes](extension/README.md).

## Repository layout

```text
kk-Reddit/
├── install.sh
├── reddit-opencli/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/reddit-opencli-reference.md
│   └── scripts/
│       ├── ensure_opencli.sh
│       └── redditctl.py
├── docs/
│   ├── CHROME_EXTENSION.md
│   └── USAGE.md
└── extension/
    └── README.md
```

## License

MIT
