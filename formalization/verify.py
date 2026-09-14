#!/usr/bin/env python3
"""Worker for verify.sh; run through the protected launcher."""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
NAME = r"[A-Za-z_][A-Za-z_0-9']*(?:\.[A-Za-z_][A-Za-z_0-9']*)*"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="save complete output to a new file (relative to repo root)")
    args = parser.parse_args()
    report = None
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        report = args.out.open("x")

    def emit(message):
        print(message, flush=True)
        if report:
            report.write(message + "\n")
            report.flush()

    def run(command):
        emit("$ " + " ".join(command))
        lines = []
        with subprocess.Popen(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as process:
            for line in process.stdout:
                emit(line.rstrip("\n"))
                lines.append(line)
            if process.wait():
                raise ValueError("Command failed")
        return "".join(lines)

    try:
        pins = [ROOT / name for name in ("lean-toolchain", "lakefile.lean", "lake-manifest.json")]
        before = {path: path.read_bytes() for path in pins}
        emit("Lean toolchain: " + pins[0].read_text().strip())
        for package in json.loads(pins[2].read_text())["packages"]:
            emit(f"Dependency: {package['name']} {package['rev']}")
        files = sorted(path for directory in ("claims", "third-party-claims")
                       for path in (ROOT / directory).rglob("*.lean"))
        declarations = []
        statement_names = set()
        statement_files = 0
        for path in files:
            source = path.read_text()
            header = re.match(r"\s*/-\s*\n(.*?)\n-/", source, re.S)
            if not header:
                raise ValueError(f"{path.relative_to(ROOT)}: missing claim header")
            fields = dict(re.findall(r"^(Claim|Source|Scope|Declarations): (.+)$", header[1], re.M))
            if set(fields) != {"Claim", "Source", "Scope", "Declarations"}:
                raise ValueError(f"{path.relative_to(ROOT)}: incomplete claim header")
            if not fields["Source"].startswith("https://") or "#" not in fields["Source"]:
                raise ValueError("Source must be an HTTPS notebook link with an anchor")
            names = fields["Declarations"].split()
            if not names or any(not re.fullmatch(NAME, name) for name in names):
                raise ValueError("Declarations must list fully qualified Lean names separated by spaces")
            declarations.extend(names)
            status = re.search(r"^Status: (.+)$", header[1], re.M)
            if status:
                if status[1] != "statement-only":
                    raise ValueError("Optional Status field must be statement-only")
                statement_files += 1
                statement_names.update(names)
            emit(f"Claim file: {path.relative_to(ROOT)}\n{header[1]}")
        run(["lake", "--wfail", "build"])
        for path in files:
            # Re-elaborate even if cached, so unfinished proofs cannot hide in build output.
            run(["lake", "env", "lean", "-DwarningAsError=true", str(path.relative_to(ROOT))])
        if files:
            def module_component(part):
                if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9']*", part):
                    return part
                if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9'-]*", part):
                    raise ValueError(f"Unsupported module path component: {part}")
                return "«" + part + "»"
            imports = ["import " + ".".join(module_component(part) for part in
                       path.relative_to(ROOT).with_suffix("").parts) for path in files]
            commands = []
            for name in declarations:
                commands.extend(["#check @" + name,
                                 "#print axioms " + name])
                if name in statement_names:
                    commands.append("#print " + name)
            audit = "\n".join(imports + commands) + "\n"
            with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", dir=ROOT / ".lake") as temp:
                temp.write(audit)
                temp.flush()
                output = run(["lake", "env", "lean", "-DwarningAsError=true", temp.name])
            for name in declarations:
                match = re.search(r"'" + re.escape(name) + r"' depends on axioms: \[([^\]]*)\]", output)
                if match:
                    axioms = {item.strip() for item in match[1].split(",") if item.strip()}
                    if axioms - STANDARD_AXIOMS:
                        raise ValueError(f"{name}: unapproved axioms {sorted(axioms - STANDARD_AXIOMS)}")
                elif f"'{name}' does not depend on any axioms" not in output:
                    raise ValueError(f"Missing axiom report for {name}")
        if any(path.read_bytes() != content for path, content in before.items()):
            raise ValueError("Dependency configuration changed during verification")
        emit(f"PASS: {len(files) - statement_files} proof files; {statement_files} statement-only files "
             f"(no proof claimed); {len(declarations)} audited declarations."
             if files else "SETUP ONLY: build passed; no claim files exist and no research claim is verified.")
    except (ValueError, OSError) as error:
        emit("FAIL: " + str(error))
        return 1
    finally:
        if report:
            report.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
