#!/usr/bin/env python3
"""Bind this checkout to the current main Codex session; never commit the ID."""
import os
from pathlib import Path
import tempfile
import uuid


def main():
    raw = os.environ.get('CODEX_THREAD_ID')
    if not raw:
        raise SystemExit('CODEX_THREAD_ID is unavailable; run this from the main Codex session.')
    session = str(uuid.UUID(raw))
    root = Path(__file__).resolve().parents[1]
    with tempfile.NamedTemporaryFile(mode='w', dir=root, prefix='.codex-session-id.', delete=False) as output:
        output.write(session + '\n')
        temporary = Path(output.name)
    temporary.replace(root / '.codex-session-id')
    print('Saved the current main session ID in .codex-session-id (machine-local, ignored by Git).')


if __name__ == '__main__':
    main()
