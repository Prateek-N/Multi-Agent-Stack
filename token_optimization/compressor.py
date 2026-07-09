"""
token_optimization/compressor.py

Skeleton for the programmatic token optimization layer.
Applies token policies from config/token_policies.yaml before sending
a prompt to any LLM provider.

Usage (dry run, no API calls):
    python token_optimization/compressor.py --dry-run \\
        --policy feature_implementation \\
        --context-file /path/to/context.txt \\
        --query "Add soft-delete to UserService"

This module has NO live HTTP calls. Implement a ProviderAdapter subclass
and call adapter.send(compressed_context) to integrate with a real API.
"""

from __future__ import annotations

import argparse
import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class FileEntry:
    path: str
    content: str
    relevance_score: float = 0.0
    truncated: bool = False
    lines_omitted: int = 0


@dataclass
class TokenPolicy:
    workflow: str
    max_input_files: int = 8
    max_input_tokens: int = 24000
    history_summarize_after_turns: int = 6
    output_style: str = "standard"
    relevance_drop_threshold: float = 0.35
    snippet_max_lines: int = 200
    snippet_head_lines: int = 40
    snippet_tail_lines: int = 40


@dataclass
class ContextBlock:
    project_state: str = ""
    files: list[FileEntry] = field(default_factory=list)
    conversation_state: str = ""
    active_query: str = ""


@dataclass
class CompressionReport:
    turns_summarized: int = 0
    files_dropped: list[tuple[str, float]] = field(default_factory=list)
    files_truncated: list[tuple[str, int]] = field(default_factory=list)
    files_retained: int = 0
    estimated_token_reduction_pct: float = 0.0
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Policy loader
# ---------------------------------------------------------------------------

class PolicyLoader:
    """Loads token policies from config/token_policies.yaml."""

    def __init__(self, config_path: str | Path = "config/token_policies.yaml") -> None:
        self._config_path = Path(config_path)
        self._raw: dict[str, Any] = {}

    def load(self) -> None:
        """Parse the YAML config file. Requires PyYAML if used; falls back to empty defaults."""
        try:
            import yaml  # optional dep
            with self._config_path.open() as f:
                self._raw = yaml.safe_load(f) or {}
        except ImportError:
            print(
                "[compressor] PyYAML not installed — using built-in defaults. "
                "Install pyyaml to load token_policies.yaml.",
                file=sys.stderr,
            )
        except FileNotFoundError:
            print(
                f"[compressor] config file not found at {self._config_path} — using defaults.",
                file=sys.stderr,
            )

    def get_workflow_policy(self, workflow: str) -> TokenPolicy:
        """Return a TokenPolicy for the given workflow name."""
        defaults = self._raw.get("defaults", {})
        workflow_overrides = self._raw.get("workflows", {}).get(workflow, {})
        merged = {**defaults, **workflow_overrides}
        return TokenPolicy(
            workflow=workflow,
            max_input_files=merged.get("max_input_files", 8),
            max_input_tokens=merged.get("max_input_tokens", 24000),
            history_summarize_after_turns=merged.get("history_summarize_after_turns", 6),
            output_style=merged.get("output_style", "standard"),
            relevance_drop_threshold=merged.get("relevance_drop_threshold", 0.35),
            snippet_max_lines=merged.get("snippet_max_lines", 200),
            snippet_head_lines=merged.get("snippet_head_lines", 40),
            snippet_tail_lines=merged.get("snippet_tail_lines", 40),
        )


# ---------------------------------------------------------------------------
# Relevance filter
# ---------------------------------------------------------------------------

class RelevanceFilter:
    """
    Scores and selects files for inclusion in the context block.
    See token_optimization/relevance_filter.md for the full scoring model.
    """

    # Weights sum to 1.0. (A prior "recency" weight was removed: it had no data
    # source and was hardwired to 0.0, so it silently contributed nothing; its
    # budget is folded into lexical_overlap, the primary textual signal.)
    weights = {
        "lexical_overlap": 0.45,
        "direct_reference": 0.30,
        "symbol_mention": 0.20,
        "structural_importance": 0.05,
    }

    _structural_patterns = ("pyproject.toml", "package.json", "setup.py", "Makefile", "schema")

    def __init__(self, policy: TokenPolicy) -> None:
        self.policy = policy

    def score_files(self, files: list[FileEntry], query: str) -> list[FileEntry]:
        """Compute relevance scores for each file in-place and return the list."""
        query_tokens = set(query.lower().split())
        for f in files:
            f.relevance_score = self._score(f, query_tokens, query)
        return files

    def select(self, scored_files: list[FileEntry]) -> tuple[list[FileEntry], list[FileEntry]]:
        """
        Partition scored files into (retained, dropped).
        Retained files are sorted by score descending and capped at max_input_files.
        """
        above_threshold = [
            f for f in scored_files
            if f.relevance_score >= self.policy.relevance_drop_threshold
        ]
        dropped = [
            f for f in scored_files
            if f.relevance_score < self.policy.relevance_drop_threshold
        ]
        above_threshold.sort(key=lambda f: f.relevance_score, reverse=True)
        retained = above_threshold[: self.policy.max_input_files]
        dropped += above_threshold[self.policy.max_input_files :]
        return retained, dropped

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _score(self, f: FileEntry, query_tokens: set[str], raw_query: str) -> float:
        content_lower = f.content.lower()
        path_lower = f.path.lower()

        lexical = self._lexical_overlap(content_lower, query_tokens)
        direct = 1.0 if f.path in raw_query or Path(f.path).stem.lower() in raw_query.lower() else 0.0
        symbol = self._symbol_mention(content_lower, raw_query)
        structural = 1.0 if any(p in path_lower for p in self._structural_patterns) else 0.0

        return (
            self.weights["lexical_overlap"] * lexical
            + self.weights["direct_reference"] * direct
            + self.weights["symbol_mention"] * symbol
            + self.weights["structural_importance"] * structural
        )

    @staticmethod
    def _lexical_overlap(content: str, query_tokens: set[str]) -> float:
        if not query_tokens:
            return 0.0
        matches = sum(1 for t in query_tokens if t in content)
        return matches / len(query_tokens)

    @staticmethod
    def _symbol_mention(content: str, query: str) -> float:
        """Detect if any identifier from content appears in the query."""
        import re
        identifiers = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]{3,}\b", content))
        query_lower = query.lower()
        for ident in identifiers:
            if ident.lower() in query_lower:
                return 1.0
        return 0.0


# ---------------------------------------------------------------------------
# Snippet truncator
# ---------------------------------------------------------------------------

class SnippetTruncator:
    """Truncates large file snippets according to the active token policy."""

    def __init__(self, policy: TokenPolicy) -> None:
        self.policy = policy

    def truncate(self, f: FileEntry) -> FileEntry:
        lines = f.content.splitlines()
        if len(lines) <= self.policy.snippet_max_lines:
            return f

        head = lines[: self.policy.snippet_head_lines]
        tail = lines[-self.policy.snippet_tail_lines :]
        omitted = len(lines) - self.policy.snippet_head_lines - self.policy.snippet_tail_lines
        gap = f"# ... [{omitted} lines omitted — request full file if needed] ..."
        f.content = "\n".join(head + [gap] + tail)
        f.truncated = True
        f.lines_omitted = omitted
        return f


# ---------------------------------------------------------------------------
# Context assembler
# ---------------------------------------------------------------------------

class ContextAssembler:
    """Builds the final context block string from its components."""

    def build(
        self,
        project_state: str,
        retained_files: list[FileEntry],
        conversation_state: str,
        total_files: int,
        policy: TokenPolicy,
    ) -> str:
        parts: list[str] = []

        parts.append("## Project State")
        parts.append(project_state.strip() or "(not provided)")

        header = f"## Relevant Files ({len(retained_files)} of {total_files} retained; threshold: {policy.relevance_drop_threshold})"
        parts.append(header)
        for f in retained_files:
            ext = Path(f.path).suffix.lstrip(".") or "text"
            score_tag = f"(score: {f.relevance_score:.2f})"
            parts.append(f"\n### {f.path} {score_tag}")
            parts.append(f"```{ext}")
            parts.append(f.content)
            parts.append("```")

        parts.append("## Conversation State")
        parts.append(conversation_state.strip() or "Session start.")

        return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Provider adapters (stubs — no live HTTP calls)
# ---------------------------------------------------------------------------

class ProviderAdapter(ABC):
    """
    Base class for LLM provider adapters.
    Subclass this to integrate with a specific provider's API.
    """

    @abstractmethod
    def format_messages(self, system_prompt: str, context: str, user_query: str) -> Any:
        """Convert context + query into the provider's message format."""

    @abstractmethod
    def send(self, messages: Any, output_style: str) -> str:
        """
        Send messages to the provider and return the completion text.
        Implement with httpx or the provider's SDK.
        Raises NotImplementedError in this skeleton.
        """
        raise NotImplementedError("Implement send() in your ProviderAdapter subclass.")


class ClaudeAdapter(ProviderAdapter):
    """
    Adapter for Anthropic Claude (claude-sonnet-4-6, claude-opus-4-7, etc.).
    See platforms/claude.md for full integration guide.
    """

    def __init__(self, model: str = "claude-sonnet-4-6", api_key: str = "") -> None:
        self.model = model
        self.api_key = api_key

    def format_messages(self, system_prompt: str, context: str, user_query: str) -> dict:
        return {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": f"{context}\n\n---\n\n{user_query}"},
            ],
            "max_tokens": 4096,
        }

    def send(self, messages: dict, output_style: str) -> str:
        raise NotImplementedError(
            "ClaudeAdapter.send() is a stub. "
            "Install anthropic SDK and implement: "
            "client = anthropic.Anthropic(api_key=self.api_key); "
            "return client.messages.create(**messages).content[0].text"
        )


class OpenAIAdapter(ProviderAdapter):
    """
    Adapter for OpenAI (gpt-4o, gpt-4-turbo, etc.).
    See platforms/openai.md for full integration guide.
    """

    def __init__(self, model: str = "gpt-4o", api_key: str = "") -> None:
        self.model = model
        self.api_key = api_key

    def format_messages(self, system_prompt: str, context: str, user_query: str) -> list[dict]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context}\n\n---\n\n{user_query}"},
        ]

    def send(self, messages: list[dict], output_style: str) -> str:
        raise NotImplementedError(
            "OpenAIAdapter.send() is a stub. "
            "Install openai SDK and implement: "
            "client = openai.OpenAI(api_key=self.api_key); "
            "return client.chat.completions.create(model=self.model, messages=messages).choices[0].message.content"
        )


class GenericAdapter(ProviderAdapter):
    """
    Adapter for any OpenAI-compatible API endpoint.
    Set base_url to the provider's chat completions URL.
    """

    def __init__(self, base_url: str, model: str, api_key: str = "") -> None:
        self.base_url = base_url
        self.model = model
        self.api_key = api_key

    def format_messages(self, system_prompt: str, context: str, user_query: str) -> list[dict]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context}\n\n---\n\n{user_query}"},
        ]

    def send(self, messages: list[dict], output_style: str) -> str:
        raise NotImplementedError(
            "GenericAdapter.send() is a stub. "
            "Implement using httpx: "
            "httpx.post(self.base_url, json={'model': self.model, 'messages': messages}, "
            "headers={'Authorization': f'Bearer {self.api_key}'})"
        )


# ---------------------------------------------------------------------------
# Main compressor
# ---------------------------------------------------------------------------

class Compressor:
    """
    Orchestrates the full compression pipeline:
      1. Relevance filtering
      2. Snippet truncation
      3. Context assembly
      4. Report generation
    """

    def __init__(self, policy: TokenPolicy) -> None:
        self.policy = policy
        self._filter = RelevanceFilter(policy)
        self._truncator = SnippetTruncator(policy)
        self._assembler = ContextAssembler()

    def compress(
        self,
        context: ContextBlock,
    ) -> tuple[str, CompressionReport]:
        """
        Apply the full compression pipeline to a ContextBlock.
        Returns (compressed_context_string, report).
        """
        report = CompressionReport()

        # Score and filter files
        scored = self._filter.score_files(context.files, context.active_query)
        retained, dropped = self._filter.select(scored)
        report.files_dropped = [(f.path, f.relevance_score) for f in dropped]
        report.files_retained = len(retained)

        # Truncate large files
        truncated_files = [self._truncator.truncate(f) for f in retained]
        report.files_truncated = [
            (f.path, f.lines_omitted) for f in truncated_files if f.truncated
        ]

        # Estimate token reduction from truncation only (not from file drops).
        # Comparing retained files before vs after truncation gives an accurate
        # measure of how much the snippet truncator saved.
        pre_trunc_chars = sum(len(f.content) for f in retained)
        post_trunc_chars = sum(len(f.content) for f in truncated_files)
        if pre_trunc_chars > 0:
            report.estimated_token_reduction_pct = round(
                (1 - post_trunc_chars / pre_trunc_chars) * 100, 1
            )

        compressed = self._assembler.build(
            project_state=context.project_state,
            retained_files=truncated_files,
            conversation_state=context.conversation_state,
            total_files=len(context.files),
            policy=self.policy,
        )

        return compressed, report


# ---------------------------------------------------------------------------
# CLI dry-run entry point
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Dry-run the compressor: shows what would be sent to an LLM without making any API calls."
    )
    p.add_argument("--dry-run", action="store_true", help="Required to run without API calls.")
    p.add_argument("--policy", default="defaults", help="Workflow name from token_policies.yaml.")
    p.add_argument("--context-file", help="Path to a text file containing a raw context block.")
    p.add_argument("--query", default="", help="The active user query.")
    p.add_argument("--config", default="config/token_policies.yaml", help="Path to token_policies.yaml.")
    return p


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    if not args.dry_run:
        print("Pass --dry-run to use this script without API calls.", file=sys.stderr)
        sys.exit(1)

    loader = PolicyLoader(args.config)
    loader.load()
    policy = loader.get_workflow_policy(args.policy)

    raw_context = ""
    if args.context_file:
        raw_context = Path(args.context_file).read_text(encoding="utf-8")

    # Build a minimal ContextBlock from the raw text (single pseudo-file)
    demo_file = FileEntry(path="<context>", content=raw_context)
    block = ContextBlock(
        project_state="(loaded from --context-file)",
        files=[demo_file],
        conversation_state="Session start.",
        active_query=args.query,
    )

    compressor = Compressor(policy)
    compressed, report = compressor.compress(block)

    print("=== COMPRESSED CONTEXT START ===")
    print(compressed)
    print("=== COMPRESSED CONTEXT END ===\n")

    print("=== COMPRESSION REPORT ===")
    print(json.dumps(
        {
            "workflow": policy.workflow,
            "output_style": policy.output_style,
            "files_retained": report.files_retained,
            "files_dropped": report.files_dropped,
            "files_truncated": report.files_truncated,
            "estimated_token_reduction_pct": report.estimated_token_reduction_pct,
            "warnings": report.warnings,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
