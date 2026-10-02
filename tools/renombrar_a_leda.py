"""Renames the product from Prisma to Leda (ADR 0015, odd/tasks/renombre-a-leda.md).

Usage, from the root of the checkout to rename:
  python tools/renombrar_a_leda.py aplicar
      `git mv` every tracked path whose name contains the old name (deepest first),
      then rewrites the content of every tracked text file, bytes in and out (keeps
      CRLF/LF and BOM-less files intact).
  python tools/renombrar_a_leda.py verificar <pre-rev> <post-rev>
      Applies the same substitution to the pre-rename tree and compares it byte for
      byte with the post-rename tree. Prints the files that are not pure substitution.
  python tools/renombrar_a_leda.py env <file>...
      Applies the substitution to untracked config files (the `.env` files) without
      printing any content; reports only whether each file changed. Before the first
      rewrite it keeps a copy as `<file>.antes-leda` (never overwritten).
  python tools/renombrar_a_leda.py restos
      Lists every remaining tracked occurrence of the old name, by file and count.
  python tools/renombrar_a_leda.py probar
      Self-test of the substitution (case map and protected tokens).

The substitution preserves case (PRISMA -> LEDA, Prisma -> Leda, prisma -> leda) and
never touches the protected tokens: names of things outside the rename's scope that
keep their old name (the repository folder, the GitHub repository, a real backup file).
"""
import pathlib
import subprocess
import sys

RULES = [("PRISMA", "LEDA"), ("Prisma", "Leda"), ("prisma", "leda")]

# Outside the rename's scope (decided by the user): they keep their real names.
PROTECTED = [
    "Prisma-PM",            # D:\Proyectos\Prisma-PM and Prisma-PM-worktrees
    "arields85/prisma",     # GitHub repository
    "prisma-antes-flujo",   # db/respaldos/prisma-antes-flujo-20260930.dump (real file)
]

# Files that describe the rename itself, plus this script: they must keep naming the old.
EXCLUDE_FILES = {
    "odd/tasks/renombre-a-leda.md",
    "docs/decisions/0015-renombre-del-producto-a-leda.md",
    "tools/renombrar_a_leda.py",
}
LOCKFILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "uv.lock"}
BINARY_EXT = {".ico", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".woff", ".woff2",
              ".ttf", ".pdf", ".zip", ".dump", ".gz"}


def sub(text: str) -> str:
    holders = {}
    for i, token in enumerate(PROTECTED):
        holder = f"\x00PROTECTED{i}\x00"
        holders[holder] = token
        text = text.replace(token, holder)
    for old, new in RULES:
        text = text.replace(old, new)
    for holder, token in holders.items():
        text = text.replace(holder, token)
    return text


def git(*args: str, cwd: str = ".") -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8", check=True, cwd=cwd).stdout


def is_binary_path(path: str) -> bool:
    return pathlib.PurePosixPath(path).suffix.lower() in BINARY_EXT


def is_untouched(path: str) -> bool:
    """Content the substitution never rewrites: excluded, binary or lockfile."""
    return (path in EXCLUDE_FILES or is_binary_path(path)
            or pathlib.PurePosixPath(path).name in LOCKFILES)


def sub_bytes(raw: bytes) -> bytes | None:
    """The substituted bytes, or None if the content is not UTF-8 text."""
    try:
        return sub(raw.decode("utf-8")).encode("utf-8")
    except UnicodeDecodeError:
        return None


def aplicar() -> None:
    # A dirty tree would mix the rename with unrelated edits and break `verificar`.
    if git("status", "--porcelain").strip():
        sys.exit("the working tree is not clean: commit or stash first")
    tracked = git("ls-files", "-z").split("\0")
    tracked = [p for p in tracked if p]
    moves = sorted({p for p in tracked if p not in EXCLUDE_FILES and sub(p) != p},
                   key=lambda p: -p.count("/"))
    for path in moves:
        target = sub(path)
        pathlib.Path(target).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "mv", path, target], check=True)
    changed = 0
    for path in [p for p in git("ls-files", "-z").split("\0") if p]:
        if is_untouched(path):
            continue
        file = pathlib.Path(path)
        raw = file.read_bytes()
        new = sub_bytes(raw)
        if new is not None and new != raw:
            file.write_bytes(new)
            changed += 1
    print(f"paths moved: {len(moves)} | files rewritten: {changed}")


def verificar(pre: str, post: str) -> int:
    def ls(rev):
        return [p for p in git("ls-tree", "-r", "-z", "--name-only", rev).split("\0") if p]

    def show(rev, path):
        return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True,
                              check=True).stdout

    post_files = set(ls(post))
    same, differ, missing = 0, [], []
    for old_path in ls(pre):
        excluded = old_path in EXCLUDE_FILES
        new_path = old_path if excluded else sub(old_path)
        if new_path not in post_files:
            missing.append(f"{old_path} -> {new_path}")
            continue
        before, after = show(pre, old_path), show(post, new_path)
        if not is_untouched(old_path):
            before = sub_bytes(before) or before
        if before == after:
            same += 1
        else:
            differ.append(new_path)
    added = post_files - {p if p in EXCLUDE_FILES else sub(p) for p in ls(pre)}
    print(f"pure substitution: {same} | differ: {len(differ)} | missing: {len(missing)}"
          f" | added: {len(added)}")
    for label, items in (("DIFFER", differ), ("MISSING", missing), ("ADDED", sorted(added))):
        for item in items:
            print(f"  {label} {item}")
    return 0 if not differ and not missing and not added else 1


def env(files: list[str]) -> None:
    for name in files:
        file = pathlib.Path(name)
        if not file.exists():
            print(f"{name}: does not exist")
            continue
        raw = file.read_bytes()
        new = sub_bytes(raw)
        if new is None:
            print(f"{name}: not UTF-8, left untouched")
        elif new == raw:
            print(f"{name}: unchanged")
        else:
            backup = file.with_name(file.name + ".antes-leda")
            if not backup.exists():
                backup.write_bytes(raw)
            file.write_bytes(new)
            print(f"{name}: renamed (copy kept as {backup.name})")


def restos() -> None:
    # `git grep` exits 1 when nothing matches; anything else is a real failure.
    p = subprocess.run(["git", "grep", "-c", "-I", "-i", "prisma"], capture_output=True,
                       text=True, encoding="utf-8")
    if p.returncode not in (0, 1):
        sys.exit(f"git grep failed ({p.returncode}): {p.stderr.strip()}")
    print(p.stdout or "no occurrences")


SELF_TEST = {
    "PRISMA_DB_URL": "LEDA_DB_URL",
    "Sos Prisma.": "Sos Leda.",
    "from prisma.db import x": "from leda.db import x",
    "set role prisma_app": "set role leda_app",
    "current_setting('prisma.workspace_id')": "current_setting('leda.workspace_id')",
    "src/prisma/cli.py": "src/leda/cli.py",
    "prisma_flujo": "leda_flujo",
    "D:/Proyectos/Prisma-PM/.venv": "D:/Proyectos/Prisma-PM/.venv",
    "D:\\Proyectos\\Prisma-PM-worktrees\\x": "D:\\Proyectos\\Prisma-PM-worktrees\\x",
    "arields85/prisma": "arields85/prisma",
    "db/respaldos/prisma-antes-flujo-20260930.dump":
        "db/respaldos/prisma-antes-flujo-20260930.dump",
}


def probar() -> int:
    bad = [(k, sub(k), v) for k, v in SELF_TEST.items() if sub(k) != v]
    for given, got, want in bad:
        print(f"FAIL {given!r}: got {got!r}, want {want!r}")
    print(f"{len(SELF_TEST) - len(bad)}/{len(SELF_TEST)} ok")
    return 1 if bad else 0


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "aplicar":
        aplicar()
    elif command == "verificar" and len(sys.argv) == 4:
        sys.exit(verificar(sys.argv[2], sys.argv[3]))
    elif command == "env" and len(sys.argv) > 2:
        env(sys.argv[2:])
    elif command == "restos":
        restos()
    elif command == "probar":
        sys.exit(probar())
    else:
        print(__doc__)
        sys.exit(2)
