"""A PDF extension must never bypass the explicit binary release gate."""
from __future__ import annotations

import hashlib

from tools.release_audit import reviewed_binary


def test_binary_approval_requires_exact_hash_and_every_path() -> None:
    content = b'\x00synthetic reviewed bytes'
    approved = {'outputs/demo.pdf': [hashlib.sha256(content).hexdigest()]}
    assert reviewed_binary({'outputs/demo.pdf'}, content, approved)
    assert not reviewed_binary({'outputs/demo.pdf'}, content + b'changed', approved)
    assert not reviewed_binary({'outputs/other.pdf'}, content, approved)
    assert not reviewed_binary({'outputs/demo.pdf', 'outputs/other.pdf'}, content, approved)
    assert not reviewed_binary(set(), content, approved)
