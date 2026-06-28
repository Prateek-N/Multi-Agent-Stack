"""
tools/domain_utils.py

Shared domain scoring and detection logic — used by generate_prompt.py,
init_project.py, and validate_kit.py to avoid triplicated scoring code.

Usage (as a module):
    from tools.domain_utils import detect_domain, score_domain

Usage (standalone — prints detected domain for a given message):
    python tools/domain_utils.py "build a REST API for user auth"
"""

from __future__ import annotations

__version__ = "1.0.0"

import sys
from pathlib import Path

# Allow running as a script from any working directory
_HERE = Path(__file__).resolve().parent
_KIT_DIR = _HERE.parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

try:
    import yaml
except ImportError:
    print("[ERROR] pyyaml is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def _load_yaml(path: Path) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"[ERROR] YAML parse error in {path}: {e}", file=sys.stderr)
        return {}
    except FileNotFoundError:
        return {}
    except PermissionError:
        print(f"[ERROR] Permission denied reading {path}", file=sys.stderr)
        return {}


def score_domain(
    message: str,
    domains: dict,
    settings: dict,
    *,
    include_score: bool = False,
) -> tuple[str, str] | tuple[str, str, float]:
    """
    Score `message` against domain detection signals and return the best match.

    Returns (domain, confidence) by default.
    Returns (domain, confidence, score) when include_score=True.

    confidence values: "high" | "medium" | "low"
    """
    msg_lower = message.lower()
    scores: dict[str, float] = {}

    for d, cfg in domains.items():
        if d == "general":
            continue
        strong = cfg.get("detection_signals", {}).get("strong", [])
        weak = cfg.get("detection_signals", {}).get("weak", [])
        s = sum(1.0 for sig in strong if sig in msg_lower)
        w = sum(0.4 for sig in weak if sig in msg_lower)
        scores[d] = (s + w) / 3

    if not scores:
        return ("general", "low", 0.0) if include_score else ("general", "low")

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    top_d, top_s = ranked[0]
    _, sec_s = ranked[1] if len(ranked) > 1 else ("general", 0.0)

    conf_t = settings.get("confidence_threshold", 0.40)
    amb_t = settings.get("ambiguity_threshold", 0.10)

    if top_s < conf_t:
        confidence = "low"
        top_d = "general"
    elif (top_s - sec_s) < amb_t:
        confidence = "medium"
    else:
        confidence = "high"

    if include_score:
        return top_d, confidence, top_s
    return top_d, confidence


def detect_domain(
    message: str,
    *,
    kit_dir: Path | None = None,
    include_score: bool = False,
) -> tuple[str, str] | tuple[str, str, float]:
    """
    Load domain_profiles.yaml from the kit directory and score `message`.

    kit_dir defaults to the parent of this file's directory (agents-maker root).
    Returns (domain, confidence) or (domain, confidence, score) when include_score=True.
    """
    base = kit_dir or _KIT_DIR
    domain_cfg_path = base / "config" / "domain_profiles.yaml"

    if not domain_cfg_path.exists():
        print(f"[WARN] domain_profiles.yaml not found at {domain_cfg_path} — defaulting to 'general'", file=sys.stderr)
        return ("general", "low", 0.0) if include_score else ("general", "low")

    raw = _load_yaml(domain_cfg_path)
    if not raw:
        return ("general", "low", 0.0) if include_score else ("general", "low")

    domains = raw.get("domains", {})
    settings = raw.get("settings", {})
    return score_domain(message, domains, settings, include_score=include_score)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Detect the domain of a message.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("message", nargs="?", help="Message to classify (reads stdin if omitted)")
    args = parser.parse_args()

    text = args.message or sys.stdin.read().strip()
    if not text:
        print("[ERROR] Provide a message as argument or via stdin.", file=sys.stderr)
        sys.exit(1)

    result = detect_domain(text, include_score=True)
    domain, confidence, score = result  # type: ignore[misc]
    print(f"Domain: {domain}  Confidence: {confidence}  Score: {score:.3f}")
