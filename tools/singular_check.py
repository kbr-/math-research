#!/usr/bin/env python3
"""Run a Singular assertion script, preserving its output and rejecting false success.

Use through compute.sh. Received lines are forwarded and flushed unchanged;
output the child has not emitted before an interruption cannot be preserved.
Singular may return zero after parser errors, so a check
must have no diagnostic/FAILED lines and end with a PASS token. The script owns
its expected assertion count and must check that count before printing PASS.
"""
import argparse
import re
import subprocess
import sys

DIAGNOSTIC = re.compile(br'^\s*(?:\?|FAILED(?:\s|:|$))')


def acceptable(returncode, diagnostic, last_line):
    return returncode == 0 and not diagnostic and last_line.split()[:1] == [b'PASS']


def run_script(script, output):
    diagnostic = False
    last_line = b''
    with subprocess.Popen(['Singular', '-q', str(script)], stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT) as process:
        for line in process.stdout:
            output.write(line)
            output.flush()
            if line.strip():
                last_line = line.strip()
            diagnostic = diagnostic or bool(DIAGNOSTIC.match(line))
        returncode = process.wait()
    return 0 if acceptable(returncode, diagnostic, last_line) else 1


def main(argv=None, output=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', help='Assertion script ending with a PASS token')
    args = parser.parse_args(argv)
    return run_script(args.script, output if output is not None else sys.stdout.buffer)


if __name__ == '__main__':
    sys.exit(main())
