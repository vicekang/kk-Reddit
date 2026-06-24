# Chrome Extension Setup

Reddit browser-mode commands need the OpenCLI Chrome extension connected to the
local OpenCLI daemon. The extension is named **OpenCLI**. It is not AutoCLI.

This repository's wrapper can call either `opencli-rs` or `opencli`, but the
browser extension itself comes from the OpenCLI browser bridge.

## Check status

```bash
opencli doctor
```

Healthy output should include:

```text
Chrome/Chromium
Daemon running
Chrome extension connected
```

If the extension is not connected, Reddit commands can fail with:

```text
Chrome extension not connected
```

## Install or enable the OpenCLI extension

Recommended source:

```bash
npm install -g @jackwener/opencli
```

That package is the supported way to install/update `opencli` and prepare the
OpenCLI browser extension assets. Upstream project:
[jackwener/opencli](https://github.com/jackwener/opencli).

Do not use the old `nashsu/opencli-rs` installer link for extension setup here.
That path now installs `autocli`, which is a different binary name and is not
what this wrapper calls by default.

After installation, check whether the extension folder exists:

```bash
find ~/.opencli/extensions -maxdepth 1 -type d -name 'opencli-extension-v*' -print
```

If `opencli-rs` has already downloaded the extension, it is commonly located at:

```text
~/.opencli/extensions/opencli-extension-v*/
```

Manual Chrome setup:

1. Open `chrome://extensions`.
2. Enable "Developer mode".
3. Click "Load unpacked".
4. Select the unpacked extension folder, for example
   `~/.opencli/extensions/opencli-extension-v1.0.17`.
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
| `Chrome extension not connected` | The daemon is running but Chrome extension is not attached. | Enable/load the OpenCLI extension and open Chrome. |
| Reddit write returns auth/login error | Chrome is not logged in to Reddit or the selected browser profile is wrong. | Log in to Reddit in Chrome, then retry. |
| Empty results | Query/subreddit may be wrong, or Reddit page/API changed. | Try a smaller smoke test and check direct `opencli reddit ... -f json` or `opencli-rs reddit ... -f json`. |
| Repeated write failure | Reddit may be rate limiting or blocking automation. | Stop retrying and inspect the returned error. |

## Can kk-Reddit ship its own Reddit Chrome extension?

Yes, but it should be treated as a separate integration project.

The current browser-mode commands talk to the OpenCLI extension/daemon bridge.
A Reddit-specific extension would need one of these paths:

1. Implement the same bridge protocol expected by OpenCLI.
2. Add upstream CLI support for a companion Reddit extension.
3. Work independently of `opencli-rs`, which would make it a different backend.

For v1, `kk-Reddit` uses the official OpenCLI browser bridge and focuses on the
skill, wrapper, safety gates, and documentation.
