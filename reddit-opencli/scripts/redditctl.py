#!/usr/bin/env python3
"""Small Reddit workflow wrapper around OpenCLI.

The script intentionally uses only Python standard library modules so it can be
bundled inside a Codex skill without extra package installation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


class CommandError(RuntimeError):
    def __init__(self, command: list[str], returncode: int, stdout: str, stderr: str):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"command failed with exit {returncode}: {shlex.join(command)}")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def find_opencli() -> str:
    binary = os.environ.get("OPENCLI") or shutil.which("opencli")
    if not binary:
        raise SystemExit("opencli is not installed or not on PATH")
    return binary


def run_command(command: list[str], *, expect_json: bool = False) -> Any:
    proc = subprocess.run(command, text=True, capture_output=True)
    if proc.returncode != 0:
        raise CommandError(command, proc.returncode, proc.stdout, proc.stderr)
    if expect_json:
        return parse_json_output(proc.stdout)
    return proc.stdout


def parse_json_output(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    starts = [pos for pos in (stripped.find("{"), stripped.find("[")) if pos >= 0]
    if not starts:
        raise ValueError("No JSON object or array found in command output")
    start = min(starts)
    candidate = stripped[start:]
    for end in range(len(candidate), 0, -1):
        chunk = candidate[:end].strip()
        if not chunk:
            continue
        try:
            return json.loads(chunk)
        except json.JSONDecodeError:
            continue
    raise ValueError("Could not parse JSON output")


def as_list(data: Any) -> list[Any]:
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("posts", "items", "results", "data", "children", "comments"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return [data]
    return []


def first_value(row: dict[str, Any], keys: tuple[str, ...], default: Any = "") -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return default


def clean_subreddit(value: str) -> str:
    text = value.strip()
    if text.lower().startswith("r/"):
        return text[2:]
    return text


def to_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().lower().replace(",", "")
    if not text:
        return 0
    multiplier = 1
    if text.endswith("k"):
        multiplier = 1000
        text = text[:-1]
    elif text.endswith("m"):
        multiplier = 1000000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0


def post_id_from_target(target: str) -> str:
    target = target.strip()
    if target.startswith("t3_"):
        return target
    match = re.search(r"/comments/([A-Za-z0-9_]+)/", target)
    if match:
        return match.group(1)
    return target


def canonical_url(row: dict[str, Any]) -> str:
    url = str(first_value(row, ("url", "link", "post_url", "comments_url"), ""))
    permalink = str(first_value(row, ("permalink", "path"), ""))
    if permalink.startswith("/"):
        permalink = "https://www.reddit.com" + permalink
    return url or permalink


def normalize_post(raw: Any, source: dict[str, Any]) -> dict[str, Any]:
    row = raw if isinstance(raw, dict) else {"value": raw}
    url = canonical_url(row)
    post_id = str(first_value(row, ("id", "post_id", "thing_id"), ""))
    fullname = str(first_value(row, ("fullname", "name"), ""))
    if not post_id and url:
        extracted = post_id_from_target(url)
        if extracted != url:
            post_id = extracted
    if not fullname and post_id and not post_id.startswith("t3_"):
        fullname = f"t3_{post_id}"

    score = to_int(first_value(row, ("score", "ups", "upvotes", "points"), 0))
    comments = to_int(first_value(row, ("comments", "num_comments", "comment_count", "replies"), 0))
    title = str(first_value(row, ("title", "name", "headline"), "")).strip()
    subreddit = clean_subreddit(str(first_value(row, ("subreddit", "community", "sub"), "")))

    normalized = {
        "id": post_id,
        "fullname": fullname,
        "title": title,
        "author": first_value(row, ("author", "username", "user"), ""),
        "subreddit": subreddit,
        "url": url,
        "permalink": first_value(row, ("permalink", "path"), ""),
        "score": score,
        "comments": comments,
        "engagement": score + comments * 3,
        "created": first_value(row, ("created", "created_utc", "time", "date"), ""),
        "source": source,
        "raw": row,
    }
    return normalized


def post_key(post: dict[str, Any]) -> str:
    for key in ("fullname", "id", "url", "permalink"):
        value = str(post.get(key) or "").strip()
        if value:
            return value.lower()
    title = str(post.get("title") or "").strip().lower()
    subreddit = str(post.get("subreddit") or "").strip().lower()
    return f"{subreddit}:{title}"


def command_base() -> list[str]:
    return [find_opencli(), "reddit"]


def reddit_json(args: list[str]) -> Any:
    return run_command(command_base() + args + ["-f", "json"], expect_json=True)


def collect_research(args: argparse.Namespace) -> dict[str, Any]:
    posts: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []

    def fetch(label: str, cli_args: list[str], source: dict[str, Any]) -> None:
        sources.append({"label": label, "args": cli_args, **source})
        try:
            data = reddit_json(cli_args)
            for item in as_list(data):
                post = normalize_post(item, {"label": label, **source})
                if post["score"] < args.min_score:
                    continue
                key = post_key(post)
                existing = posts.get(key)
                if existing is None or post["engagement"] > existing["engagement"]:
                    posts[key] = post
        except CommandError as exc:
            errors.append(
                {
                    "label": label,
                    "command": exc.command,
                    "returncode": exc.returncode,
                    "stdout": exc.stdout.strip(),
                    "stderr": exc.stderr.strip(),
                }
            )
        except Exception as exc:  # Keep collecting other sources.
            errors.append({"label": label, "args": cli_args, "error": str(exc)})

    limit = str(args.limit)
    sorts = parse_csv(args.sorts)

    if args.include_frontpage:
        fetch("frontpage", ["frontpage", "--limit", limit], {"type": "frontpage"})
    if args.include_popular:
        fetch("popular", ["popular", "--limit", limit], {"type": "popular"})

    for subreddit in args.subreddit:
        clean = clean_subreddit(subreddit)
        if not clean:
            continue
        for sort in sorts:
            cli_args = ["subreddit", clean, "--sort", sort, "--limit", limit]
            if sort in ("top", "controversial"):
                cli_args += ["--time", args.time]
            fetch(f"r/{clean}:{sort}", cli_args, {"type": "subreddit", "subreddit": clean, "sort": sort})

    for query in args.query:
        query = query.strip()
        if not query:
            continue
        cli_args = ["search", query, "--limit", limit, "--sort", args.search_sort, "--time", args.time]
        if args.search_subreddit:
            for subreddit in args.search_subreddit:
                clean = clean_subreddit(subreddit)
                scoped = cli_args + ["--subreddit", clean]
                fetch(
                    f"search:{query}:r/{clean}",
                    scoped,
                    {"type": "search", "query": query, "subreddit": clean, "sort": args.search_sort},
                )
        else:
            fetch(f"search:{query}", cli_args, {"type": "search", "query": query, "sort": args.search_sort})

    ordered = sorted(posts.values(), key=lambda item: item.get("engagement", 0), reverse=True)
    return {
        "generated_at": utc_now(),
        "source_count": len(sources),
        "sources": sources,
        "post_count": len(ordered),
        "posts": ordered,
        "errors": errors,
    }


def parse_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def write_payload(payload: Any, args: argparse.Namespace, *, default_name: str) -> None:
    text = render_payload(payload, args.format)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"Wrote {path}")
    else:
        print(text)


def render_payload(payload: Any, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False)
    if fmt == "md":
        if isinstance(payload, dict) and "posts" in payload:
            return render_posts_markdown(payload)
        return render_thread_markdown(payload)
    raise ValueError(f"Unsupported format: {fmt}")


def escape_cell(value: Any) -> str:
    text = str(value or "").replace("\n", " ").strip()
    return text.replace("|", "\\|")


def render_posts_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Reddit Research",
        "",
        f"- Generated: {payload.get('generated_at')}",
        f"- Sources: {payload.get('source_count')}",
        f"- Posts: {payload.get('post_count')}",
    ]
    if payload.get("errors"):
        lines += ["", "## Source Errors", ""]
        for error in payload["errors"]:
            lines.append(f"- `{escape_cell(error.get('label'))}`: {escape_cell(error.get('error') or error.get('stderr') or error.get('stdout'))}")
    lines += [
        "",
        "## Posts",
        "",
        "| Rank | Subreddit | Score | Comments | Title | Link | Source |",
        "| ---: | --- | ---: | ---: | --- | --- | --- |",
    ]
    for index, post in enumerate(payload.get("posts", []), start=1):
        title = escape_cell(post.get("title") or "(untitled)")
        url = post.get("url") or post.get("permalink") or ""
        link = f"[link]({url})" if url else ""
        source = post.get("source") or {}
        lines.append(
            f"| {index} | r/{escape_cell(post.get('subreddit'))} | {post.get('score', 0)} | "
            f"{post.get('comments', 0)} | {title} | {link} | {escape_cell(source.get('label'))} |"
        )
    return "\n".join(lines)


def render_thread_markdown(payload: Any) -> str:
    lines = ["# Reddit Thread", ""]
    if isinstance(payload, dict):
        post = payload.get("post") if isinstance(payload.get("post"), dict) else payload
        title = first_value(post, ("title", "name"), "") if isinstance(post, dict) else ""
        url = canonical_url(post) if isinstance(post, dict) else ""
        if title:
            lines.append(f"## {title}")
            lines.append("")
        if url:
            lines.append(f"- Link: {url}")
        comments = payload.get("comments") if isinstance(payload.get("comments"), list) else as_list(payload)
    else:
        comments = as_list(payload)
    if comments:
        lines += ["", "## Comments", ""]
        for index, comment in enumerate(comments, start=1):
            if not isinstance(comment, dict):
                lines.append(f"{index}. {escape_cell(comment)}")
                continue
            author = first_value(comment, ("author", "username", "user"), "unknown")
            score = first_value(comment, ("score", "ups", "upvotes"), "")
            body = first_value(comment, ("body", "text", "comment"), "")
            lines.append(f"{index}. **{escape_cell(author)}** ({escape_cell(score)}): {escape_cell(body)}")
    else:
        lines.append(json.dumps(payload, indent=2, ensure_ascii=False))
    return "\n".join(lines)


def cmd_check(args: argparse.Namespace) -> int:
    binary = find_opencli()
    print(f"opencli: {binary}")
    print(run_command([binary, "--version"]).strip())
    print()
    print(run_command([binary, "doctor"]).strip())
    if args.smoke_subreddit:
        print()
        print(f"Smoke test: r/{args.smoke_subreddit}")
        data = reddit_json(["subreddit", args.smoke_subreddit, "--sort", "hot", "--limit", str(args.limit)])
        posts = [normalize_post(item, {"label": "smoke"}) for item in as_list(data)]
        print(json.dumps({"post_count": len(posts), "posts": posts[: args.limit]}, indent=2, ensure_ascii=False))
    return 0


def cmd_research(args: argparse.Namespace) -> int:
    payload = collect_research(args)
    write_payload(payload, args, default_name="reddit-research")
    return 1 if payload["errors"] and payload["post_count"] == 0 else 0


def cmd_thread(args: argparse.Namespace) -> int:
    cli_args = [
        "read",
        args.post,
        "--limit",
        str(args.limit),
        "--depth",
        str(args.depth),
        "--replies",
        str(args.replies),
        "--sort",
        args.sort,
        "--max-length",
        str(args.max_length),
    ]
    payload = reddit_json(cli_args)
    write_payload(payload, args, default_name="reddit-thread")
    return 0


def action_command(args: argparse.Namespace) -> tuple[str, list[str], dict[str, Any]]:
    action = args.action
    target = args.target.strip()
    meta: dict[str, Any] = {"action": action, "target": target}

    if action == "comment":
        if not args.text:
            raise SystemExit("--text is required for comment")
        post_id = post_id_from_target(target)
        meta["post_id"] = post_id
        meta["text"] = args.text
        return action, command_base() + ["comment", post_id, args.text, "-f", "json"], meta

    if action in ("upvote", "downvote", "unvote"):
        direction = {"upvote": "up", "downvote": "down", "unvote": "none"}[action]
        post_id = post_id_from_target(target)
        meta["post_id"] = post_id
        meta["direction"] = direction
        return action, command_base() + ["upvote", post_id, "--direction", direction, "-f", "json"], meta

    if action in ("save", "unsave"):
        post_id = post_id_from_target(target)
        command = command_base() + ["save", post_id]
        if action == "unsave":
            command += ["--undo", "true"]
        meta["post_id"] = post_id
        return action, command + ["-f", "json"], meta

    if action in ("subscribe", "unsubscribe"):
        subreddit = clean_subreddit(target)
        command = command_base() + ["subscribe", subreddit]
        if action == "unsubscribe":
            command += ["--undo", "true"]
        meta["subreddit"] = subreddit
        return action, command + ["-f", "json"], meta

    raise SystemExit(f"Unsupported action: {action}")


def cmd_act(args: argparse.Namespace) -> int:
    action, command, meta = action_command(args)
    preview = {
        "will_execute": bool(args.yes),
        "action": action,
        "target": args.target,
        "metadata": meta,
        "command": command,
        "risk": "Reddit write actions are public/account-affecting and may trigger platform automation controls.",
    }
    if not args.yes:
        print(json.dumps(preview, indent=2, ensure_ascii=False))
        print()
        print("Not executed. Re-run with --yes only after explicit user confirmation.")
        return 0

    print(json.dumps(preview, indent=2, ensure_ascii=False))
    print()
    result = run_command(command, expect_json=True)
    print(json.dumps({"executed_at": utc_now(), "result": result}, indent=2, ensure_ascii=False))
    return 0


def watch_state_path(args: argparse.Namespace) -> Path:
    if args.state_file:
        return Path(args.state_file).expanduser()
    material = json.dumps(
        {
            "subreddit": args.subreddit,
            "query": args.query,
            "search_subreddit": args.search_subreddit,
            "sorts": args.sorts,
            "time": args.time,
            "include_frontpage": args.include_frontpage,
            "include_popular": args.include_popular,
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    root = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return root / "kk-reddit" / "watch" / f"{digest}.json"


def cmd_watch(args: argparse.Namespace) -> int:
    payload = collect_research(args)
    path = watch_state_path(args)
    previous: set[str] = set()
    if path.exists():
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
            previous = {str(item) for item in old.get("seen", [])}
        except Exception:
            previous = set()

    current = [post_key(post) for post in payload.get("posts", [])]
    new_posts = [post for post in payload.get("posts", []) if post_key(post) not in previous]
    watch_payload = {
        **payload,
        "watch_state": str(path),
        "new_count": len(new_posts),
        "posts": new_posts,
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"updated_at": utc_now(), "seen": sorted(set(previous).union(current))}, indent=2), encoding="utf-8")
    write_payload(watch_payload, args, default_name="reddit-watch")
    return 1 if payload["errors"] and not new_posts else 0


def add_research_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--subreddit", action="append", default=[], help="Subreddit to scan; can be repeated")
    parser.add_argument("--query", action="append", default=[], help="Search query; can be repeated")
    parser.add_argument("--search-subreddit", action="append", default=[], help="Limit searches to subreddit; can be repeated")
    parser.add_argument("--sorts", default="hot,new,rising,top", help="Comma list for subreddit sorts")
    parser.add_argument("--search-sort", default="relevance", choices=["relevance", "hot", "top", "new", "comments"])
    parser.add_argument("--time", default="month", choices=["hour", "day", "week", "month", "year", "all"])
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--min-score", type=int, default=0)
    parser.add_argument("--include-frontpage", action="store_true")
    parser.add_argument("--include-popular", action="store_true")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument("--output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reddit workflow wrapper for OpenCLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Verify opencli and optionally smoke-test Reddit")
    check.add_argument("--smoke-subreddit")
    check.add_argument("--limit", type=int, default=3)
    check.set_defaults(func=cmd_check)

    research = subparsers.add_parser("research", help="Collect and de-duplicate Reddit posts")
    add_research_args(research)
    research.set_defaults(func=cmd_research)

    thread = subparsers.add_parser("thread", help="Read a Reddit post and comments")
    thread.add_argument("post", help="Post id or Reddit URL")
    thread.add_argument("--limit", type=int, default=25)
    thread.add_argument("--depth", type=int, default=2)
    thread.add_argument("--replies", type=int, default=5)
    thread.add_argument("--sort", default="best", choices=["best", "top", "new", "controversial", "old", "qa"])
    thread.add_argument("--max-length", type=int, default=2000)
    thread.add_argument("--format", choices=["json", "md"], default="json")
    thread.add_argument("--output")
    thread.set_defaults(func=cmd_thread)

    act = subparsers.add_parser("act", help="Preview or execute Reddit write actions")
    act.add_argument("action", choices=["comment", "upvote", "downvote", "unvote", "save", "unsave", "subscribe", "unsubscribe"])
    act.add_argument("target", help="Post URL/id for post actions, or subreddit for subscribe actions")
    act.add_argument("--text", help="Comment text")
    act.add_argument("--yes", action="store_true", help="Execute after explicit user confirmation")
    act.set_defaults(func=cmd_act)

    watch = subparsers.add_parser("watch", help="Show posts that are new since last run")
    add_research_args(watch)
    watch.add_argument("--state-file")
    watch.set_defaults(func=cmd_watch)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except CommandError as exc:
        print(json.dumps(
            {
                "error": str(exc),
                "command": exc.command,
                "returncode": exc.returncode,
                "stdout": exc.stdout.strip(),
                "stderr": exc.stderr.strip(),
            },
            indent=2,
            ensure_ascii=False,
        ), file=sys.stderr)
        return exc.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
