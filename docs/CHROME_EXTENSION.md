# Chrome Extension Setup

`opencli-rs reddit ...` uses browser mode on this machine. Browser mode needs
the OpenCLI Chrome extension connected to the local daemon.

## Check status

```bash
opencli-rs doctor
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
6. Run `opencli-rs doctor` again.

Chrome intentionally requires user interaction for unpacked extension loading.
The shell installer can detect the missing connection but should not silently
override Chrome's extension safety model.

## Troubleshooting

Run:

```bash
opencli-rs doctor
python3 reddit-opencli/scripts/redditctl.py check --smoke-subreddit rust --limit 3
```

Common states:

| Symptom | Meaning | Fix |
| --- | --- | --- |
| `Chrome extension not connected` | The daemon is running but Chrome extension is not attached. | Enable/load the OpenCLI extension and open Chrome. |
| Reddit write returns auth/login error | Chrome is not logged in to Reddit or the selected browser profile is wrong. | Log in to Reddit in Chrome, then retry. |
| Empty results | Query/subreddit may be wrong, or Reddit page/API changed. | Try a smaller smoke test and check direct `opencli-rs reddit ... -f json`. |
| Repeated write failure | Reddit may be rate limiting or blocking automation. | Stop retrying and inspect the returned error. |

## Can kk-Reddit ship its own Reddit Chrome extension?

Yes, but it should be treated as a separate integration project.

The current `opencli-rs` commands talk to the OpenCLI extension/daemon bridge.
A Reddit-specific extension would need one of these paths:

1. Implement the same bridge protocol expected by `opencli-rs`.
2. Add upstream `opencli-rs` support for a companion Reddit extension.
3. Work independently of `opencli-rs`, which would make it a different backend.

For v1, `kk-Reddit` uses the official OpenCLI browser bridge and focuses on the
skill, wrapper, safety gates, and documentation.

