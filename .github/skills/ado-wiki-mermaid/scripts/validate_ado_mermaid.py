#!/usr/bin/env python3
"""
Validate Mermaid diagrams for Azure DevOps wiki (Mermaid 8.13.9, ::: mermaid fence).

Catches the failure modes that render as raw text or an error box in ADO,
none of which a normal Mermaid linter flags.

Usage:
    python3 validate_ado_mermaid.py page.md [more.md ...]
    python3 validate_ado_mermaid.py --recurse path/to/wiki
    python3 validate_ado_mermaid.py --json page.md

Exit code 0 = clean, 1 = errors found, 2 = bad invocation.
Stdlib only. Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# --- Azure DevOps Mermaid 8.13.9 capability tables -------------------------

SUPPORTED = {
    "flowchart", "graph", "sequenceDiagram", "stateDiagram-v2",
    "gantt", "pie", "journey", "requirementDiagram",
}

# Explicitly excluded by the Sprint 200 release note, or postdating 8.13.9.
UNSUPPORTED = {
    "erDiagram": "Excluded from ADO (experimental in 8.13.9). Use a flowchart with '1..*' edge labels, or a Markdown table.",
    "gitGraph": "Excluded from ADO (experimental in 8.13.9). Use 'flowchart LR'.",
    "C4Context": "C4 does not exist in Mermaid 8.13.9. Use a flowchart with subgraph boundaries.",
    "C4Container": "C4 does not exist in Mermaid 8.13.9. Use a flowchart with subgraph boundaries.",
    "C4Component": "C4 does not exist in Mermaid 8.13.9. Use a flowchart with subgraph boundaries.",
    "C4Dynamic": "C4 does not exist in Mermaid 8.13.9. Use a flowchart with subgraph boundaries.",
    "C4Deployment": "C4 does not exist in Mermaid 8.13.9. Use a flowchart with subgraph boundaries.",
    "mindmap": "Mermaid 9.3+. Not available in ADO. Use a flowchart.",
    "timeline": "Mermaid 9.4+. Not available in ADO. Use a gantt chart.",
    "quadrantChart": "Mermaid 10+. Not available in ADO.",
    "sankey-beta": "Mermaid 10+. Not available in ADO.",
    "xychart-beta": "Mermaid 10.7+. Not available in ADO.",
    "block-beta": "Mermaid 11+. Not available in ADO.",
    "packet-beta": "Mermaid 11+. Not available in ADO.",
    "architecture-beta": "Mermaid 11+. Not available in ADO.",
    "kanban": "Mermaid 11+. Not available in ADO.",
    "radar-beta": "Mermaid 11+. Not available in ADO.",
    "treemap-beta": "Mermaid 11+. Not available in ADO.",
    "zenuml": "Not available in ADO.",
}

# Renders in practice but absent from the Sprint 200 list.
UNVERIFIED = {
    "classDiagram": "Not listed in the ADO Sprint 200 supported set. Verify on one page before relying on it wiki-wide.",
    "stateDiagram": "Use 'stateDiagram-v2'; the v1 keyword is legacy and lays out differently.",
}

# Mermaid keywords that break the parser when used as a bare node id.
RESERVED_IDS = {
    "end", "default", "graph", "subgraph", "class", "classDef",
    "click", "style", "linkStyle", "direction", "state", "note",
}

MERMAID_FENCE_OPEN = re.compile(r"^:::\s*mermaid\s*$", re.IGNORECASE)
MERMAID_FENCE_CLOSE = re.compile(r"^:::\s*$")
BACKTICK_MERMAID = re.compile(r"^\s*(?:```+|~~~+)\s*mermaid\b", re.IGNORECASE)


class Finding:
    __slots__ = ("path", "line", "level", "code", "message")

    def __init__(self, path, line, level, code, message):
        self.path = path
        self.line = line
        self.level = level
        self.code = code
        self.message = message

    def as_dict(self):
        return {
            "file": str(self.path), "line": self.line, "level": self.level,
            "code": self.code, "message": self.message,
        }

    def __str__(self):
        tag = {"error": "ERROR", "warning": "WARN "}[self.level]
        return f"{tag} {self.path}:{self.line} [{self.code}] {self.message}"


def find_blocks(lines):
    """Yield (start_line_1based, end_line_1based, body_lines) for ::: mermaid blocks."""
    blocks = []
    i = 0
    while i < len(lines):
        if MERMAID_FENCE_OPEN.match(lines[i].rstrip()):
            start = i
            j = i + 1
            while j < len(lines) and not MERMAID_FENCE_CLOSE.match(lines[j].rstrip()):
                j += 1
            body = lines[start + 1:j]
            closed = j < len(lines)
            blocks.append((start + 1, j + 1 if closed else None, body))
            i = j + 1
        else:
            i += 1
    return blocks


def check_backtick_fences(path, lines, out):
    for n, line in enumerate(lines, 1):
        if BACKTICK_MERMAID.match(line):
            out.append(Finding(
                path, n, "error", "ADO001",
                "Backtick-fenced ```mermaid does not render in Azure DevOps wiki. "
                "Replace the opening fence with '::: mermaid' and the closing fence with ':::'.",
            ))


def check_block(path, start, end, body, out):
    if end is None:
        out.append(Finding(
            path, start, "error", "ADO002",
            "Unclosed '::: mermaid' block — no closing ':::' found.",
        ))

    # Diagram type: first non-empty, non-comment line.
    decl = None
    decl_line = start
    for offset, raw in enumerate(body, 1):
        s = raw.strip()
        if not s or s.startswith("%%"):
            continue
        decl = s
        decl_line = start + offset
        break

    if decl is None:
        out.append(Finding(path, start, "error", "ADO003", "Empty mermaid block."))
        return

    token = decl.split()[0].rstrip(";")
    base = token.split("-")[0] if token.startswith("stateDiagram") else token

    if token in UNSUPPORTED:
        out.append(Finding(path, decl_line, "error", "ADO010",
                           f"'{token}' does not render in Azure DevOps. {UNSUPPORTED[token]}"))
    elif token in UNVERIFIED:
        out.append(Finding(path, decl_line, "warning", "ADO011",
                           f"'{token}': {UNVERIFIED[token]}"))
    elif token not in SUPPORTED and base not in SUPPORTED:
        out.append(Finding(path, decl_line, "warning", "ADO012",
                           f"Unrecognized diagram type '{token}'. Supported in ADO: "
                           f"{', '.join(sorted(SUPPORTED))}."))

    joined_lines = list(enumerate(body, start + 1))

    for n, raw in joined_lines:
        s = raw.strip()

        # Blank line inside a container fence can terminate it early in some renderers.
        if not s:
            out.append(Finding(path, n, "warning", "ADO020",
                               "Blank line inside a '::: mermaid' block — can terminate the "
                               "container early. Use a '%%' comment line instead."))
            continue

        if s.startswith("%%{") or "%%{init" in s:
            out.append(Finding(path, n, "error", "ADO030",
                               "'%%{init: ...}%%' directives are unreliable in ADO wiki. Remove it."))

        if re.match(r"^\s*config\s*:", raw) or s == "---":
            out.append(Finding(path, n, "warning", "ADO031",
                               "YAML frontmatter config inside a diagram is Mermaid 10+. Not supported in 8.13.9."))

        if re.search(r"@\{\s*shape\s*:", s):
            out.append(Finding(path, n, "error", "ADO032",
                               "'A@{ shape: ... }' node syntax is Mermaid 11. Use A[text], A(text), "
                               "A[(text)], A{text} or A((text))."))

        if s.startswith("click ") or re.match(r"^\s*click\b", s):
            out.append(Finding(path, n, "error", "ADO033",
                               "'click' handlers require JavaScript, which Azure DevOps wiki blocks."))

        if re.search(r'\[\s*"\s*`', s) or re.search(r'`\s*"\s*\]', s):
            out.append(Finding(path, n, "error", "ADO034",
                               'Markdown strings in labels (["`**bold**`"]) are Mermaid 9.4+. Use plain text.'))

        if "~~~" in s and not s.startswith("%%"):
            out.append(Finding(path, n, "warning", "ADO035",
                               "'~~~' invisible links postdate 8.13.9."))

        # Reserved word as a bare node id at the start of an edge statement.
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*(-->|---|-\.->|==>|--[ox])", s)
        if m and m.group(1) in RESERVED_IDS:
            out.append(Finding(path, n, "error", "ADO040",
                               f"Reserved word '{m.group(1)}' used as a bare node id. "
                               f'Write {m.group(1).capitalize()}["{m.group(1)}"] instead.'))
        for m2 in re.finditer(
            r"(?:-->|---|-\.->|==>|--[ox])(?:\|[^|]*\|)?\s*([A-Za-z_][A-Za-z0-9_-]*)\s*(?:$|[;&])", s
        ):
            if m2.group(1) in RESERVED_IDS:
                out.append(Finding(path, n, "error", "ADO040",
                                   f"Reserved word '{m2.group(1)}' used as a bare node id. "
                                   f'Write {m2.group(1).capitalize()}["{m2.group(1)}"] instead.'))

        # classDef must set an explicit text colour (ADO has a dark theme).
        if s.startswith("classDef"):
            if "fill:" in s and "color:" not in s:
                out.append(Finding(path, n, "error", "ADO050",
                                   "classDef sets 'fill:' without 'color:'. Text becomes unreadable "
                                   "in the ADO dark theme. Add an explicit 'color:'."))

    # Node budget.
    ids = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*[\[\(\{]", "\n".join(body)))
    ids -= RESERVED_IDS
    if len(ids) > 16:
        out.append(Finding(path, start, "warning", "ADO060",
                           f"~{len(ids)} nodes in one diagram (soft cap 16). Split across wiki "
                           f"subpages, or summarize with '+N more'."))

    # subgraph nesting depth.
    depth = 0
    for n, raw in joined_lines:
        s = raw.strip()
        if s.startswith("subgraph"):
            depth += 1
            if depth > 2:
                out.append(Finding(path, n, "warning", "ADO061",
                                   "subgraph nested deeper than 2 levels — unpredictable layout in 8.13.9."))
        elif s == "end":
            depth = max(0, depth - 1)


def check_attachments(path, lines, out):
    for n, line in enumerate(lines, 1):
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", line):
            url = m.group(1).strip()
            if ".attachments" in url and not url.startswith("/"):
                out.append(Finding(path, n, "warning", "ADO070",
                                   f"Attachment path '{url}' should be root-relative: "
                                   f"'/.attachments/...'."))


def validate_file(path):
    out = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [Finding(path, 0, "error", "ADO000", f"Cannot read file: {exc}")]

    lines = text.splitlines()
    check_backtick_fences(path, lines, out)
    check_attachments(path, lines, out)
    for start, end, body in find_blocks(lines):
        check_block(path, start, end, body, out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate Mermaid for Azure DevOps wiki.")
    ap.add_argument("paths", nargs="+", help="Markdown files, or directories with --recurse")
    ap.add_argument("--recurse", action="store_true", help="Walk directories for *.md")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = ap.parse_args(argv)

    targets = []
    for p in args.paths:
        path = pathlib.Path(p)
        if path.is_dir():
            if not args.recurse:
                print(f"{p} is a directory; pass --recurse", file=sys.stderr)
                return 2
            targets.extend(sorted(path.rglob("*.md")))
        else:
            targets.append(path)

    if not targets:
        print("No markdown files found.", file=sys.stderr)
        return 2

    findings = []
    for t in targets:
        findings.extend(validate_file(t))

    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    if args.json:
        print(json.dumps({
            "filesChecked": len(targets),
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": [f.as_dict() for f in findings],
        }, indent=2))
    else:
        for f in findings:
            print(f)
        status = "FAIL" if errors else ("WARN" if warnings else "PASS")
        print(f"\n{status}: {len(targets)} file(s), {len(errors)} error(s), {len(warnings)} warning(s).")

    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
