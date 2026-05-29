# Script that inserts file header comments into known Python, JavaScript, and Markdown files.
# File: add_file_headers.py
#
# Simple overview:
# - This helper is used to add plain-language file headers to code and docs.
# - It maps repository paths to descriptive summaries for consistent annotations.
# - Run this script from the repo root when new files need headers.

# Script that inserts file header comments into supported repository files.
# File: add_file_headers.py
#
# Simple overview:
# - Automatically annotates Python, JavaScript, JSX, MJS, Markdown, YAML, and TXT files.
# - Skips generated artifacts and package lock files, since those files are not source docs.
# - Leaves JSON files untouched because JSON does not support comments.

from pathlib import Path

COMMENT_STYLES = {
    ".py": "#",
    ".js": "/*",
    ".jsx": "/*",
    ".mjs": "/*",
    ".md": "<!--",
    ".yaml": "<!--",
    ".yml": "<!--",
    ".txt": "#",
}

IGNORED_PREFIXES = {
    "frontend/node_modules",
    "frontend/.next",
    ".venv",
    ".pytest_cache",
    "__pycache__",
}

SUPPORTED_EXTENSIONS = set(COMMENT_STYLES.keys())

root = Path(__file__).parent


def is_ignored(path: Path) -> bool:
    relative = str(path.relative_to(root)).replace("\\", "/")
    return any(relative.startswith(prefix) for prefix in IGNORED_PREFIXES)


def build_header(path: Path, rel_path: str) -> str:
    suffix = path.suffix
    comment_text = f"Project file: {rel_path}"
    if suffix == ".py" or suffix == ".txt":
        return f"# {comment_text}\n# File: {rel_path}\n\n"
    if suffix in {".js", ".jsx", ".mjs"}:
        return f"/* {comment_text} */\n/* File: {rel_path} */\n\n"
    if suffix in {".md", ".yaml", ".yml"}:
        return f"<!-- {comment_text} -->\n<!-- File: {rel_path} -->\n\n"
    return ""


def already_has_header(text: str) -> bool:
    lines = text.splitlines()
    if not lines:
        return False
    first = lines[0].strip()
    return first.startswith(("#", "//", "/*", "<!--"))


def main():
    file_paths = []
    for suffix in SUPPORTED_EXTENSIONS:
        file_paths.extend(sorted(root.rglob(f"*{suffix}")))

    for path in sorted(set(file_paths)):
        if not path.is_file() or is_ignored(path):
            continue

        rel_path = str(path.relative_to(root)).replace("\\", "/")
        text = path.read_text(encoding="utf-8", errors="ignore")
        if already_has_header(text):
            print(f"Skipping already-commented file: {rel_path}")
            continue

        header = build_header(path, rel_path)
        if not header:
            print(f"Skipping unsupported file type: {rel_path}")
            continue

        path.write_text(header + text, encoding="utf-8")
        print(f"Added header to {rel_path}")

    print("Done")


if __name__ == "__main__":
    main()
