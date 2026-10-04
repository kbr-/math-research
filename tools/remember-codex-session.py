#!/usr/bin/env python3
"""Validate an existing external binding; an agent must never replace one."""
import os
from pathlib import Path
import uuid


def main():
    raw = os.environ.get('CODEX_THREAD_ID')
    if not raw:
        raise SystemExit('CODEX_THREAD_ID is unavailable.')
    session = str(uuid.UUID(raw))
    path = Path(__file__).resolve().parents[1] / '.codex-session-id'
    if not path.exists() or path.read_text().strip() != session:
        raise SystemExit('Session binding is owned by the external launcher; this agent cannot replace it.')
    print('The external session binding matches this thread.')


if __name__ == '__main__':
    main()
