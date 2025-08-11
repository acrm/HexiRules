#!/usr/bin/env python3
"""Lightweight commit message linter enforcing repository guidelines.

Rules enforced:
- Subject line <= 72 chars.
- Subject imperative mood heuristic: avoid trailing 's', 'ed' endings for first word.
- Subject starts with Uppercase letter (PascalCase or capitalized word).
- No leading/trailing whitespace in subject.
- No emojis (basic unicode ranges + ':' shortcodes) in subject.
- Body lines (after blank separator) <= 72 chars.
- Wrap body: warns (not fails) on single-paragraph long bodies without blank lines.

Exit codes:
0 = pass, 1 = fail (hard violation), 2 = warnings only.

Usage:
  python tools/commit_msg_lint.py <path-to-commit-msg-file>

Integrates with .githooks/commit-msg.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

EMOJI_PATTERN = re.compile(r"[\U0001F300-\U0001F6FF\U0001F900-\U0001FAFF]|:[a-z_]+:")
TRAILING_VERB_ENDINGS = ("ed", "s")  # heuristic
MAX_WIDTH = 72


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")


def warn(msg: str) -> None:
    print(f"WARN: {msg}")


def check_subject(subject: str) -> bool:
    ok = True
    if len(subject) > MAX_WIDTH:
        fail(f"subject length {len(subject)} > {MAX_WIDTH}")
        ok = False
    if subject != subject.strip():
        fail("subject has leading/trailing whitespace")
        ok = False
    if not subject or not subject[0].isupper():
        fail("subject must start with uppercase letter")
        ok = False
    first_word = subject.split()[0]
    lw = first_word.lower()
    # crude imperative mood heuristic
    if lw.endswith(TRAILING_VERB_ENDINGS):
        warn("subject may not be imperative (heuristic) -> consider base verb form")
    if EMOJI_PATTERN.search(subject):
        fail("emoji detected in subject")
        ok = False
    return ok


def check_body(lines: List[str]) -> bool:
    if not lines:
        return True
    ok = True
    blank_seen = False
    for i, line in enumerate(lines):
        if line.strip() == "":
            blank_seen = True
            continue
        if len(line) > MAX_WIDTH:
            fail(f"body line {i+2} length {len(line)} > {MAX_WIDTH}")
            ok = False
    if not blank_seen and len(lines) > 1:
        warn("body is multiple lines without blank separator")
    return ok


def lint_commit_msg(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    # Remove comment lines (git uses #)
    content_lines = [l for l in text.splitlines() if not l.startswith("#")]
    if not content_lines:
        fail("empty commit message")
        return 1
    subject = content_lines[0]
    body = content_lines[1:]
    subject_ok = check_subject(subject)
    body_ok = check_body(body)
    if subject_ok and body_ok:
        print("Commit message passed lint checks")
        return 0
    # If only warnings (no fail messages), exit 0 already handled. Fail otherwise.
    return 1 if not (subject_ok and body_ok) else 0


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: commit_msg_lint.py <commit-msg-file>")
        return 1
    path = Path(argv[1])
    if not path.exists():
        fail(f"file not found: {path}")
        return 1
    return lint_commit_msg(path)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
