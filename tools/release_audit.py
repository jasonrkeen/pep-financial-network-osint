"""Bounded, read-only release checks. Not a general secret detector or legal audit.

Scans every blob reachable from the fetched refs, including historical versions.
Never prints matching secret values. Does not change repository visibility.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], stderr=subprocess.PIPE)


def audit() -> dict:
    failures: list[dict[str, str]] = []
    patterns = {
        "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
        "github_token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
        "github_fine_grained_token": re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{60,}\b"),
        "aws_access_key_id": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
        "slack_token": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
        "openai_style_key": re.compile(rb"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b"),
        "credential_in_url": re.compile(rb"https?://[^\s/:@]{2,}:[^\s/@]{6,}@"),
    }
    if git("rev-parse", "--is-shallow-repository").strip() != b"false":
        raise RuntimeError("Full fetched history is required; shallow checkout refused")
    commits = git("rev-list", "--all").decode().splitlines()
    if not commits:
        raise RuntimeError("No reachable commits found")
    blobs: dict[str, set[str]] = {}
    for commit in commits:
        message = git("show", "-s", "--format=%B", commit)
        for kind, pattern in patterns.items():
            if pattern.search(message):
                failures.append({"kind": kind, "object": commit, "path": "commit_message"})
        for entry in git("ls-tree", "-rz", commit).split(b"\0"):
            if not entry:
                continue
            meta, raw_path = entry.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            path = raw_path.decode("utf-8", errors="strict")
            if kind != "blob" or mode not in {"100644", "100755"}:
                failures.append({"kind": "unreviewed_object_type", "object": oid, "path": path})
                continue
            blobs.setdefault(oid, set()).add(path)
    known_graph = "7addfd05c6036dbf3bf4ae6f5788e8c4b669de9d9e74827d89d3292dd57b279b"
    binary_blobs = 0
    text_blobs = 0
    source_versions = 0
    suspicious_path = re.compile(r"(^|/)(\.env(?:\..*)?|id_rsa|id_ed25519|credentials(?:\.[^/]*)?)$|\.(?:p12|pfx|key)$", re.I)
    for oid, paths in sorted(blobs.items()):
        content = git("cat-file", "blob", oid)
        for path in sorted(paths):
            if suspicious_path.search(path) and not path.endswith((".env.example", ".env.sample")):
                failures.append({"kind": "sensitive_filename", "object": oid, "path": path})
            if re.search(r"aliyev|bayholding|hillside|pilatus|registry_document_request", path, re.I):
                failures.append({"kind": "case_specific_filename", "object": oid, "path": path})
        for kind, pattern in patterns.items():
            if pattern.search(content):
                failures.append({"kind": kind, "object": oid, "path": sorted(paths)[0]})
        try:
            text = content.decode("utf-8")
            if "\0" in text:
                raise UnicodeError("NUL byte")
            text_blobs += 1
        except UnicodeError:
            binary_blobs += 1
            if paths != {"outputs/demo_network.png"} or hashlib.sha256(content).hexdigest() != known_graph:
                failures.append({"kind": "unreviewed_binary", "object": oid, "path": sorted(paths)[0]})
            continue
        if "data/synthetic_sources.csv" in paths:
            source_versions += 1
            rows = list(csv.DictReader(io.StringIO(text)))
            if not rows:
                failures.append({"kind": "empty_source_register", "object": oid, "path": "data/synthetic_sources.csv"})
            for row in rows:
                if not row.get("title", "").startswith("SYNTHETIC:") or not row.get("reference", "").startswith("demo://"):
                    failures.append({"kind": "non_synthetic_source_metadata", "object": oid, "path": "data/synthetic_sources.csv"})
    if source_versions == 0:
        raise RuntimeError("Production source register was not found in history")
    license_text = Path("LICENSE").read_text(encoding="utf-8")
    if not license_text.startswith("MIT License\n") or "Copyright (c) 2026 Jason Keen" not in license_text:
        failures.append({"kind": "license_not_approved_mit", "object": "HEAD", "path": "LICENSE"})
    for path in [Path("README.md"), *Path("docs").glob("*.md")]:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).exists():
                failures.append({"kind": "broken_local_document_link", "object": "HEAD", "path": str(path)})
    return {
        "head": git("rev-parse", "HEAD").decode().strip(),
        "scope": "All commits and unique blobs reachable from refs fetched by checkout; not inaccessible or deleted remote objects",
        "commits_scanned": len(commits),
        "unique_blobs_scanned": len(blobs),
        "text_blobs_scanned": text_blobs,
        "binary_blobs_checked_against_reviewed_hash": binary_blobs,
        "production_source_register_versions_checked": source_versions,
        "secret_pattern_categories": sorted(patterns),
        "failures": failures,
        "limitations": [
            "Pattern checks are not proof that no secret or private narrative exists.",
            "Commit author identity/email metadata is not removed or anonymized.",
            "The graph hash links to the prior documented visual self-review; not a new independent image audit.",
            "Does not scan prior Actions logs, external artifacts, issues or PR comments.",
            "No source authenticity, operational effectiveness or legal-title validation is claimed.",
            "No repository visibility, permissions, tag or release mutation is performed.",
        ],
    }


def main() -> int:
    try:
        report = audit()
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(json.dumps({"status": "ERROR", "error_type": type(exc).__name__}))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
