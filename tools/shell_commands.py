"""Conservative invocation parsing for checks that need evidence of an executed command.

Quoted operators remain arguments. Ambiguous control flow and redirects are not execution evidence;
callers can ask for a separate simple invocation instead of guessing which branch ran.
"""
import shlex

# Bash help documents these as replacing/stopping the shell, executing shell code, installing handlers,
# or changing parsing/lookup. An aggregate exit status cannot prove a later segment ran after one of them.
SHELL_CONTROL = {'exit', 'exec', 'logout', 'return', 'break', 'continue', 'eval', 'source', '.', 'trap',
                 'set', 'shopt', 'enable', 'alias', 'unalias', 'hash'}


def unambiguous_commands(command: str, *, chain: bool = False) -> list[list[str]]:
    if '\n' in command:
        return []
    lexer = shlex.shlex(command, posix=False, punctuation_chars=';&|()<>')
    lexer.whitespace_split = True
    lexer.commenters = '#'
    try:
        tokens = list(lexer)
        allowed = {'&&', '|'} if chain else set()
        if any(token and set(token) <= set(';&|()<>') and token not in allowed for token in tokens):
            return []
        commands, words = [], []
        for token in tokens:
            if token in allowed:
                if not words:
                    return []
                commands.append(words)
                words = []
            else:
                value = shlex.split(token)
                if len(value) != 1:
                    return []
                words.append(value[0])
        found = commands + [words] if words else []
        for invocation in found:
            effective = list(invocation)
            while effective and (effective[0] in ('command', 'builtin', 'env') or '=' in effective[0]):
                effective.pop(0)
                while effective and effective[0].startswith('-'):
                    effective.pop(0)
            if effective and effective[0] in SHELL_CONTROL:
                return []
        return found
    except ValueError:
        return []
