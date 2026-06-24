# Chrome Extension Setup

Reddit browser-mode commands need the OpenCLI Chrome extension connected to the
local OpenCLI daemon. The extension is named **OpenCLI**.

## Check Status

```bash
opencli doctor
```

Healthy output should include a running daemon and a connected extension. If
the extension is missing or unstable, Reddit commands can fail.

## Install Or Update OpenCLI

```bash
npm install -g @jackwener/opencli
```

Upstream project: [jackwener/opencli](https://github.com/jackwener/opencli).

After installation, check whether extension assets exist:

```bash
find ~/.opencli/extensions -maxdepth 1 -type d -name 'opencli-extension-v*' -print
```

They are commonly located under:

```text
~/.opencli/extensions/opencli-extension-v*/
```

## Load The Extension In Chrome

1. Open `chrome://extensions`.
2. Enable "Developer mode".
3. Click "Load unpacked".
4. Select the unpacked extension folder, for example
   `~/.opencli/extensions/opencli-extension-v1.0.20`.
5. Open a normal Chrome window and log in to Reddit.
6. Run `opencli doctor` again.

Chrome intentionally requires user interaction for unpacked extension loading.
The shell installer can detect the missing connection but should not silently
override Chrome's extension safety model.

## Troubleshooting

Run:

```bash
opencli doctor
python3 reddit-opencli/scripts/redditctl.py check --smoke-subreddit rust --limit 3
```

Common states:

| Symptom | Meaning | Fix |
| --- | --- | --- |
| Extension missing or unstable | The OpenCLI daemon cannot keep a stable Chrome bridge connection. | Enable/update the OpenCLI extension and open Chrome. |
| Reddit write returns auth/login error | Chrome is not logged in to Reddit or the selected browser profile is wrong. | Log in to Reddit in Chrome, then retry. |
| Empty results | Query/subreddit may be wrong, or Reddit page/API changed. | Try a smaller smoke test and check direct `opencli reddit ... -f json`. |
| Repeated write failure | Reddit may be rate limiting or blocking automation. | Stop retrying and inspect the returned error. |

