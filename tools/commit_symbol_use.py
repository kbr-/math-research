#!/usr/bin/env python3
"""Flag symbols a commit adds without a user in that same commit.

For each commit in BASE..TIP (run inside the repository), parses the Python and TypeScript files the
commit changes with tree-sitter and lists the symbols its added lines define:

- Python: functions, methods and classes, module-level UPPER_CASE constants, and annotated class
  fields in files whose path names settings or config;
- TypeScript: `export`ed functions, constants, classes, interfaces, types and enums, and top-level
  functions.

A use is an identifier in code naming the symbol, in the commit's own tree, outside the symbol's own
definition: strings, comments, import statements and non-code files don't count. A symbol has no
user when it has no use, or when every use sits inside another symbol of the same commit that has
no user; that is applied until nothing changes, so a helper whose only caller is unused is found in
the same pass as its caller, and so is code left behind when its only user moves to another commit.
Such a symbol is flagged NO USER, naming the unused symbols it's only used by, and fails the check.
One whose only users are tests is listed as TESTS ONLY, for review. That is desired for a building
block added for a later commit, when the block has a commit of its own whose message motivates it
by what will build on it. It is wrong when the layer rides along in a commit that does other work,
or lands a commit before its real user. Telling these apart needs the commit's purpose, which a
parse can't see, so a reader decides. For both, the first later commit in the range with a non-test
use is named: that is where the symbol probably belongs. Handlers wired by a decorator or a
framework (routes, fixtures, validators, CLI commands, migrations, ORM models, which a
`__tablename__` registers on the ORM's metadata, Next.js route-segment files' exports, default
exports, dunders, tests) are skipped. The output ends with a recap of every NO USER finding.

Limit: uses are matched by name, so a symbol whose name also names something else (a settings field
called `sync_enabled` when other settings classes have one) looks used. Review such names by hand. A
symbol reached only through a string (a dotted path in configuration) looks unused.

Needs the tree-sitter, tree-sitter-python and tree-sitter-typescript packages.

Usage: ./tools/commit_symbol_use.py BASE [TIP]   (TIP defaults to HEAD; exit 1 on any NO USER)
"""
import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field

import tree_sitter_python
import tree_sitter_typescript
from tree_sitter import Language, Parser

PARSERS = {
    "python": Parser(Language(tree_sitter_python.language())),
    "typescript": Parser(Language(tree_sitter_typescript.language_typescript())),
    "tsx": Parser(Language(tree_sitter_typescript.language_tsx())),
}
GRAMMAR_BY_SUFFIX = {".py": "python", ".ts": "typescript", ".tsx": "tsx", ".js": "tsx", ".jsx": "tsx",
                     ".mjs": "tsx", ".cjs": "tsx"}
SKIP_DECORATOR = re.compile(r"@\w*(router|app|api)\.|@pytest|@(field_|model_)?validator|@\w+\.(command|task|group)|@(computed_field|override)")
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]*$|\.(test|spec)\.[jt]sx?$|conftest\.py$")
SKIP_PATH = re.compile(r"(^|/)(alembic/versions|migrations)/")
# Next.js reads a route segment's exports (the component, generateMetadata, route handlers) itself.
NEXT_ROUTE_FILE = re.compile(r"(^|/)app/(.*/)?(page|layout|template|loading|error|not-found|default|route)\.[jt]sx?$")
IMPORTS = {"import_statement", "import_from_statement", "future_import_statement"}
TS_DECLARATIONS = {"function_declaration", "generator_function_declaration", "class_declaration",
                   "abstract_class_declaration", "interface_declaration", "type_alias_declaration",
                   "enum_declaration"}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def grammar(path):
    suffix = path[path.rfind("."):] if "." in path else ""
    return GRAMMAR_BY_SUFFIX.get(suffix)


@dataclass
class Definition:
    name: str
    path: str
    start: int  # byte span of the whole definition, decorators included
    end: int
    name_start: int  # byte offset of the defining name


@dataclass
class ParsedFile:
    definitions: list = field(default_factory=list)  # every candidate definition in the file
    references: dict = field(default_factory=dict)  # name -> byte offsets of identifiers naming it
    line_starts: list = field(default_factory=list)


class Blobs:
    """File contents by `rev:path`, read through one `git cat-file --batch`, parsed once per blob."""

    def __init__(self, names):
        self.proc = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE)
        self.parsed = {}
        self.names = sorted(names)  # every symbol name the range defines
        self.index = {}  # commit -> {name: [(path, ParsedFile)]}

    def files_referencing(self, commit, name):
        """[(path, ParsedFile)] of the commit's code files with an identifier naming name. The index
        is built once per commit, from one grep for every name and one parse per file."""
        if commit not in self.index:
            patterns = [arg for n in self.names for arg in ("-e", n)]
            try:
                out = git("grep", "-l", "-w", "-F", *patterns, commit, "--",
                          *("*"+suffix for suffix in GRAMMAR_BY_SUFFIX)) if patterns else ""
            except subprocess.CalledProcessError:
                out = ""
            wanted, index = set(self.names), {}
            for hit in out.splitlines():
                path = hit.split(":", 1)[1]
                parsed = self.parse(commit, path)
                if parsed is not None:
                    for n in wanted.intersection(parsed.references):
                        index.setdefault(n, []).append((path, parsed))
            self.index[commit] = index
        return self.index[commit].get(name, [])

    def read(self, rev, path):
        self.proc.stdin.write(f"{rev}:{path}\n".encode())
        self.proc.stdin.flush()
        header = self.proc.stdout.readline().split()
        if len(header) < 3 or header[1] != b"blob":
            return None, None
        data = self.proc.stdout.read(int(header[2]))
        self.proc.stdout.read(1)
        return header[0].decode(), data

    def parse(self, rev, path):
        kind = grammar(path)
        if kind is None:
            return None
        sha, data = self.read(rev, path)
        if sha is None:
            return None
        if sha not in self.parsed:
            self.parsed[sha] = parse(PARSERS[kind].parse(data).root_node, data, path, kind)
        return self.parsed[sha]


def parse(root, data, path, kind):
    result = ParsedFile(line_starts=[0] + [m.end() for m in re.finditer(rb"\n", data)])
    config_file = re.search(r"settings|config", path) is not None

    def add(name_node, span_node):
        result.definitions.append(Definition(name_node.text.decode(), path, span_node.start_byte,
                                             span_node.end_byte, name_node.start_byte))

    def decorators_of(node):
        parent = node.parent
        if parent is not None and parent.type == "decorated_definition":
            return parent, [d.text.decode() for d in parent.children if d.type == "decorator"]
        return node, []

    def orm_model(node):
        body = node.child_by_field_name("body")
        return node.type == "class_definition" and body is not None and any(
            s.type == "expression_statement" and s.named_children and s.named_children[0].type == "assignment"
            and s.named_children[0].child_by_field_name("left").text == b"__tablename__" for s in body.named_children)

    def python(node):
        if node.type in ("function_definition", "class_definition"):
            span, decorators = decorators_of(node)
            name = node.child_by_field_name("name")
            if not any(SKIP_DECORATOR.search(d) for d in decorators) and not orm_model(node):
                add(name, span)
        elif node.type == "assignment" and node.parent.type == "expression_statement":
            target = node.child_by_field_name("left")
            scope = node.parent.parent
            if target is not None and target.type == "identifier":
                name = target.text.decode()
                if scope.type == "module" and re.fullmatch(r"[A-Z][A-Z0-9_]+", name):
                    add(target, node.parent)
                elif (config_file and scope.type == "block" and scope.parent.type == "class_definition"
                      and node.child_by_field_name("type") is not None and re.fullmatch(r"[a-z_][a-z0-9_]*", name)):
                    add(target, node.parent)

    def typescript(node):
        if node.parent is None or node.parent.type != "program":
            return
        if node.type == "export_statement":
            if any(c.type == "default" for c in node.children):
                return
            declaration = node.child_by_field_name("declaration")
            if declaration is None:
                return
            if declaration.type in TS_DECLARATIONS:
                add(declaration.child_by_field_name("name"), node)
            elif declaration.type in ("lexical_declaration", "variable_declaration"):
                for declarator in declaration.children:
                    target = declarator.child_by_field_name("name") if declarator.type == "variable_declarator" else None
                    if target is not None and target.type == "identifier":
                        add(target, declarator)
        elif node.type in ("function_declaration", "generator_function_declaration"):
            add(node.child_by_field_name("name"), node)

    visit_definition = python if kind == "python" else typescript
    aliases = []    # (the name a file imports a symbol under, the symbol's own name)
    stack = [(root, False)]
    while stack:
        node, in_import = stack.pop()
        in_import = in_import or node.type in IMPORTS or (
            node.type == "export_statement" and node.child_by_field_name("source") is not None)
        if node.type.endswith("identifier") and node.child_count == 0 and not in_import:
            result.references.setdefault(node.text.decode(), []).append(node.start_byte)
        if node.type == "import_specifier" or (node.type == "aliased_import" and node.parent.type == "import_from_statement"):
            name, alias = node.child_by_field_name("name"), node.child_by_field_name("alias")
            if name is not None and alias is not None:
                aliases.append((alias.text.decode(), name.text.decode()))
        visit_definition(node)
        stack.extend((child, in_import) for child in node.children)
    # A use of the alias is a use of the symbol: `from m import publish as send` then `send()` uses publish.
    for alias, name in aliases:
        if alias in result.references:
            result.references.setdefault(name, []).extend(result.references[alias])
    return result


def skipped(name):
    return name.startswith(("test_", "__")) or name in ("upgrade", "downgrade")


def added_definitions(commit, blobs):
    """{name: [Definition]} for the candidate symbols whose defining name is on a line the commit adds."""
    added_lines, path = {}, None
    for line in git("show", "-U0", "--format=", "--no-color", commit).splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif path and line.startswith("@@"):
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            start, count = int(m.group(1)), int(m.group(2) or 1)
            added_lines.setdefault(path, set()).update(range(start, start + count))
    found = {}
    for path, lines in added_lines.items():
        if SKIP_PATH.search(path) or TEST_PATH.search(path) or NEXT_ROUTE_FILE.search(path):
            continue
        parsed = blobs.parse(commit, path)
        if parsed is None:
            continue
        for d in parsed.definitions:
            if line_of(parsed, d.name_start) in lines and not skipped(d.name):
                found.setdefault(d.name, []).append(d)
    return found


def line_of(parsed, offset):
    lo, hi = 0, len(parsed.line_starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if parsed.line_starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


def uses(commit, name, blobs):
    """Uses of name in commit's tree: [(path, name of the innermost definition enclosing the use or
    None, is_test)], leaving out uses inside a definition of name itself."""
    found = []
    for path, parsed in blobs.files_referencing(commit, name):
        for offset in parsed.references[name]:
            around = [d for d in parsed.definitions if d.start <= offset < d.end]
            if any(d.name == name for d in around):
                continue
            user = min(around, key=lambda d: d.end - d.start).name if around else None
            found.append((path, user, TEST_PATH.search(path) is not None))
    return found


def classify(commit, defs, blobs):
    """{name: (kind, [names it's only used by])} for the commit's symbols without a live non-test use.

    A use counts against a symbol the commit adds only through that symbol: once it has no user,
    neither do the uses inside it."""
    users = {name: [(user if user in defs else None, is_test) for _, user, is_test in uses(commit, name, blobs)]
             for name in defs}
    dead = set()
    changed = True
    while changed:
        changed = False
        for name, found in users.items():
            if name not in dead and all(user in dead for user, _ in found):
                dead.add(name)
                changed = True
    result = {}
    for name, found in users.items():
        if name in dead:
            result[name] = ("NO USER", sorted({user for user, _ in found}))
        elif not any(not is_test for user, is_test in found if user not in dead):
            result[name] = ("TESTS ONLY", [])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("base", metavar="BASE", help="the revision the branch starts from; its commits are BASE..TIP")
    parser.add_argument("tip", metavar="TIP", nargs="?", default="HEAD", help="the branch's last commit (default: HEAD)")
    args = parser.parse_args()
    base, tip = args.base, args.tip
    commits = git("rev-list", "--reverse", f"{base}..{tip}").split()
    subjects = {c: git("log", "-1", "--format=%h %s", c).strip() for c in commits}
    blobs = Blobs(())
    added = {commit: added_definitions(commit, blobs) for commit in commits}
    blobs.names = sorted({name for defs in added.values() for name in defs})
    recap, tests_only = [], 0
    for i, commit in enumerate(commits):
        defs = added[commit]
        findings = []
        flagged = classify(commit, defs, blobs)
        unused = {n for n, (kind, _) in flagged.items() if kind == "NO USER"}
        first_use = {}

        def first_used(name):
            """Index of the first later commit using name outside the commit's unused symbols, or
            using one of the unused symbols name is only used by."""
            if name not in first_use:
                first_use[name] = None  # guards a cycle of unused symbols
                direct = next((j for j in range(i + 1, len(commits)) if any(
                    not is_test and user not in unused for _, user, is_test in uses(commits[j], name, blobs))), None)
                through = [first_used(user) for user in flagged.get(name, ("", []))[1]]
                found = [j for j in [direct, *through] if j is not None]
                first_use[name] = min(found) if found else None
            return first_use[name]

        for name, (kind, via) in sorted(flagged.items()):
            later = commits[first_used(name)] if first_used(name) is not None else None
            detail = f"; only used by {', '.join(via)}" if via else ""
            detail += f"; first used in {subjects[later]}" if later else ""
            line = f"{kind}: {name} ({defs[name][0].path}){detail}"
            findings.append("  " + line)
            if kind == "NO USER":
                recap.append(f"  {subjects[commit]}: {line[len('NO USER: '):]}")
            else:
                tests_only += 1
        if findings:
            print(subjects[commit])
            print("\n".join(findings))
    print(f"{len(commits)} commits, {len(recap)} symbols with no user, {tests_only} used only by tests")
    if recap:
        print("No user (fails the check):")
        print("\n".join(recap))
    sys.exit(1 if recap else 0)


if __name__ == "__main__":
    main()
