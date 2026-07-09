"""
context_loaders/project_summary.py

Produce a compact, structured project summary for agent context.
Detects the tech stack, primary services/modules, main entrypoints,
test structure, and key config files by inspecting the repository.

Usage:
    python context_loaders/project_summary.py --path /your/repo
    python context_loaders/project_summary.py --path /your/repo --output summary.txt

Output: paste directly as the "## Project State" section in your agent session.

The summary is intentionally compact (300–600 tokens) — it is the basis
for all agent context and should not be summarized further.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

__version__ = "1.0.0"


# ---------------------------------------------------------------------------
# Stack detection rules
# Each entry: (indicator_file_or_dir, language, framework_or_runtime)
# ---------------------------------------------------------------------------

STACK_INDICATORS: list[tuple[str, str, str]] = [
    # Python
    ("pyproject.toml", "Python", ""),
    ("setup.py", "Python", ""),
    ("requirements.txt", "Python", ""),
    ("Pipfile", "Python", "Pipenv"),
    ("manage.py", "Python", "Django"),
    ("wsgi.py", "Python", "WSGI/Django"),
    ("asgi.py", "Python", "ASGI"),
    # Node / JS / TS
    ("package.json", "Node.js", ""),
    ("tsconfig.json", "TypeScript", ""),
    ("next.config.js", "TypeScript", "Next.js"),
    ("next.config.ts", "TypeScript", "Next.js"),
    ("nuxt.config.ts", "TypeScript", "Nuxt.js"),
    ("vite.config.ts", "TypeScript", "Vite"),
    ("angular.json", "TypeScript", "Angular"),
    # Go
    ("go.mod", "Go", ""),
    # Java / Kotlin
    ("pom.xml", "Java", "Maven"),
    ("build.gradle", "Java/Kotlin", "Gradle"),
    ("build.gradle.kts", "Kotlin", "Gradle"),
    # Rust
    ("Cargo.toml", "Rust", "Cargo"),
    # Ruby
    ("Gemfile", "Ruby", "Bundler"),
    ("config/routes.rb", "Ruby", "Rails"),
    # Infra
    ("docker-compose.yml", "", "Docker Compose"),
    ("docker-compose.yaml", "", "Docker Compose"),
    ("Dockerfile", "", "Docker"),
    ("k8s/", "", "Kubernetes"),
    ("helm/", "", "Helm"),
    ("terraform/", "", "Terraform"),
    (".tf", "", "Terraform"),
]

FRAMEWORK_INDICATORS: list[tuple[str, str]] = [
    ("fastapi", "FastAPI"),
    ("flask", "Flask"),
    ("django", "Django"),
    ("starlette", "Starlette"),
    ("tornado", "Tornado"),
    ("express", "Express"),
    ("koa", "Koa"),
    ("nestjs", "NestJS"),
    ("spring", "Spring"),
    ("gin", "Gin"),
    ("fiber", "Fiber"),
    ("actix", "Actix"),
    ("axum", "Axum"),
]

TEST_FRAMEWORK_INDICATORS: list[tuple[str, str]] = [
    ("pytest", "pytest"),
    ("unittest", "unittest"),
    ("jest", "Jest"),
    ("vitest", "Vitest"),
    ("mocha", "Mocha"),
    ("jasmine", "Jasmine"),
    ("rspec", "RSpec"),
    ("minitest", "Minitest"),
    ("junit", "JUnit"),
    ("testng", "TestNG"),
    ("go test", "go test"),
]

ENTRYPOINT_NAMES = frozenset({
    "main.py", "app.py", "server.py", "wsgi.py", "asgi.py", "run.py",
    "index.js", "index.ts", "server.js", "server.ts", "app.js", "app.ts",
    "main.go", "main.java", "main.rs", "main.rb",
})

SERVICE_DIR_PATTERNS = ("service", "services", "api", "routes", "handlers", "controllers", "workers")
MODEL_DIR_PATTERNS = ("model", "models", "schema", "schemas", "entities", "domain")
TEST_DIR_PATTERNS = ("test", "tests", "spec", "specs", "__tests__")


def _read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return ""


def detect_stack(root: Path) -> tuple[list[str], list[str], str | None]:
    """Returns (languages, frameworks, build_tool)."""
    languages: list[str] = []
    frameworks: list[str] = []
    build_tool: str | None = None

    for indicator, lang, framework in STACK_INDICATORS:
        target = root / indicator
        if target.exists():
            if lang and lang not in languages:
                languages.append(lang)
            if framework and framework not in frameworks:
                frameworks.append(framework)
            if indicator in ("pyproject.toml", "setup.py", "requirements.txt"):
                build_tool = build_tool or "pip"
            elif indicator == "package.json":
                pkg = _read_text_safe(target).lower()
                build_tool = build_tool or ("pnpm" if "pnpm" in pkg else "npm/yarn")
            elif indicator in ("pom.xml",):
                build_tool = "Maven"
            elif indicator.startswith("build.gradle"):
                build_tool = "Gradle"
            elif indicator == "Cargo.toml":
                build_tool = "Cargo"
            elif indicator == "Gemfile":
                build_tool = "Bundler"
            elif indicator == "go.mod":
                build_tool = "go"

    # Detect framework from dependency files
    dep_files = ["requirements.txt", "pyproject.toml", "package.json", "Pipfile", "Gemfile"]
    for dep_file in dep_files:
        content = _read_text_safe(root / dep_file).lower()
        for key, name in FRAMEWORK_INDICATORS:
            if key in content and name not in frameworks:
                frameworks.append(name)

    return languages, frameworks, build_tool


def detect_test_framework(root: Path) -> str | None:
    dep_files = ["requirements.txt", "pyproject.toml", "package.json", "setup.cfg"]
    for dep_file in dep_files:
        content = _read_text_safe(root / dep_file).lower()
        for key, name in TEST_FRAMEWORK_INDICATORS:
            if key in content:
                return name
    # Go: detect by go.mod existence
    if (root / "go.mod").exists():
        return "go test"
    return None


def detect_containerization(root: Path) -> str:
    if (root / "k8s").is_dir() or (root / "kubernetes").is_dir():
        return "Kubernetes"
    if (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists():
        return "Docker Compose"
    if (root / "Dockerfile").exists():
        return "Docker"
    return "none"


def find_services(root: Path, max_depth: int = 3) -> list[tuple[str, str]]:
    """Return list of (path, description) for service/module directories."""
    results = []

    def _scan(directory: Path, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = list(directory.iterdir())
        except PermissionError:
            return
        for entry in entries:
            if not entry.is_dir():
                continue
            name_lower = entry.name.lower()
            if any(p in name_lower for p in ("__pycache__", ".git", "node_modules", ".venv")):
                continue
            rel = str(entry.relative_to(root)).replace("\\", "/")
            for pattern in SERVICE_DIR_PATTERNS:
                if pattern in name_lower:
                    results.append((rel + "/", "service/handler layer"))
                    break
            for pattern in MODEL_DIR_PATTERNS:
                if pattern in name_lower:
                    results.append((rel + "/", "data models / schemas"))
                    break
            _scan(entry, depth + 1)

    _scan(root, 0)
    return results[:10]


def find_entrypoints(root: Path) -> list[tuple[str, str]]:
    results = []
    for name in ENTRYPOINT_NAMES:
        p = root / name
        if p.exists():
            results.append((name, "application entrypoint"))
    # Also search one level deep
    for child in root.iterdir():
        if child.is_dir() and child.name not in ("__pycache__", "node_modules", ".git", ".venv"):
            for name in ENTRYPOINT_NAMES:
                p = child / name
                if p.exists():
                    rel = str(p.relative_to(root)).replace("\\", "/")
                    results.append((rel, "application entrypoint"))
    return results[:8]


def find_test_dirs(root: Path) -> list[tuple[str, str]]:
    results = []

    # Skip dependency/VCS/build dirs so large repos aren't traversed (matches find_services).
    skip = ("__pycache__", ".git", "node_modules", ".venv", "venv", "env")

    def _scan(directory: Path, depth: int = 0) -> None:
        if depth > 3:
            return
        try:
            for entry in directory.iterdir():
                if not entry.is_dir():
                    continue
                name_lower = entry.name.lower()
                if any(p in name_lower for p in skip):
                    continue
                if any(p in name_lower for p in TEST_DIR_PATTERNS):
                    rel = str(entry.relative_to(root)).replace("\\", "/")
                    results.append((rel + "/", "test suite"))
                _scan(entry, depth + 1)
        except PermissionError:
            pass

    _scan(root)
    return results[:6]


def find_key_configs(root: Path) -> list[tuple[str, str]]:
    config_map = {
        "pyproject.toml": "Python project config + dependencies",
        "setup.py": "Python package setup",
        "requirements.txt": "Python dependencies",
        "requirements-dev.txt": "Python dev dependencies",
        "package.json": "Node.js dependencies + scripts",
        "tsconfig.json": "TypeScript compiler config",
        "go.mod": "Go module definition",
        "Cargo.toml": "Rust crate config",
        "Gemfile": "Ruby dependencies",
        "pom.xml": "Java Maven config",
        "build.gradle": "Java/Kotlin Gradle config",
        "Dockerfile": "Container build definition",
        "docker-compose.yml": "Multi-service container config",
        "docker-compose.yaml": "Multi-service container config",
        "Makefile": "Build / task runner",
        ".env.example": "Required environment variables",
        "alembic.ini": "Database migration config (Alembic)",
        "migrate.go": "Database migration entrypoint",
        "schema.prisma": "Prisma ORM schema",
        "schema.graphql": "GraphQL schema",
    }
    results = []
    for filename, description in config_map.items():
        if (root / filename).exists():
            results.append((filename, description))
    return results


def build_summary(root: Path) -> str:
    languages, frameworks, build_tool = detect_stack(root)
    test_framework = detect_test_framework(root)
    containerization = detect_containerization(root)
    services = find_services(root)
    entrypoints = find_entrypoints(root)
    test_dirs = find_test_dirs(root)
    configs = find_key_configs(root)

    stack_str = ", ".join(languages) if languages else "Unknown"
    frameworks_str = ", ".join(frameworks) if frameworks else "none detected"

    lines: list[str] = [
        "## Project Summary",
        "",
        f"**Stack**: {stack_str}",
        f"**Frameworks**: {frameworks_str}",
        f"**Build tool**: {build_tool or 'unknown'}",
        f"**Test framework**: {test_framework or 'unknown'}",
        f"**Containerization**: {containerization}",
        "",
    ]

    if services:
        lines.append("## Services / Modules")
        lines.append("")
        lines.append("| Path | Responsibility |")
        lines.append("|---|---|")
        for path, desc in services:
            lines.append(f"| `{path}` | {desc} |")
        lines.append("")

    if entrypoints:
        lines.append("## Main Entrypoints")
        lines.append("")
        lines.append("| File | Purpose |")
        lines.append("|---|---|")
        for path, desc in entrypoints:
            lines.append(f"| `{path}` | {desc} |")
        lines.append("")

    if configs:
        lines.append("## Key Config Files")
        lines.append("")
        lines.append("| File | Purpose |")
        lines.append("|---|---|")
        for path, desc in configs:
            lines.append(f"| `{path}` | {desc} |")
        lines.append("")

    if test_dirs:
        lines.append("## Test Structure")
        lines.append("")
        lines.append("| Path | Type |")
        lines.append("|---|---|")
        for path, desc in test_dirs:
            lines.append(f"| `{path}` | {desc} |")
        lines.append("")

    lines.append(f"_Summary generated from: `{root}`_")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a compact project summary for agent context."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--path", required=True, help="Repository root directory.")
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory.", file=sys.stderr)
        sys.exit(1)

    summary = build_summary(root)

    if args.output:
        Path(args.output).write_text(summary, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        sys.stdout.buffer.write(summary.encode("utf-8"))


if __name__ == "__main__":
    main()
