# ADO_Mermaid

**GitHub Copilot skill + instructions for writing Mermaid diagrams that actually render in an Azure DevOps project wiki.**

Includes a zero-dependency validator that catches the failure modes a normal Mermaid linter misses — because they aren't Mermaid errors, they're Azure DevOps constraints.

---

## Credits first

This project is **not** written from scratch. It is a retarget of existing community work, and that work deserves the credit.

### Primary source: `design-doc-mermaid`

- **Repository:** [SpillwaveSolutions/design-doc-mermaid](https://github.com/SpillwaveSolutions/design-doc-mermaid)
- **Author:** Rick Hightower ([@RichardHightower](https://github.com/RichardHightower)) / [Spillwave Solutions](https://github.com/SpillwaveSolutions)
- **License:** MIT — as stated in the upstream `README.md` ("Part of Claude Code Skills - MIT License") and in `.claude-plugin/plugin.json` (`"license": "MIT"`).
  ⚠️ **Note:** at the time of writing the upstream repository contains **no `LICENSE` file**, and the GitHub API reports `"license": null`. The MIT designation is taken from the author's own README and plugin manifest. If you intend to redistribute commercially, confirm licensing with the author directly.
- **Referenced at:** upstream `main` as of commit `c36d835` (2026-08-24)
- **Popularity:** ~44,000 installs via [skills.sh](https://skills.sh), 167 GitHub stars — it is the most-used Mermaid agent skill available.

**Why this one?** Of every Mermaid skill I surveyed, it was the only one that already reasoned about *publishing targets* (GitHub wiki vs. Confluence) rather than just Mermaid syntax. It carries hard-won practical rules — node budgets, reserved-word escaping, contrast requirements on `classDef` — that take months of broken diagrams to learn. That operational wisdom is the valuable part, and it is entirely Rick Hightower's.

### Secondary sources (consulted, no code taken)

- **[github/awesome-copilot](https://github.com/github/awesome-copilot)** (MIT) — surveyed all 449 skills and 226 instruction files. It contains **no** Mermaid skill; `draw-io-diagram-generator` and `excalidraw-diagram-generator` are unsuitable for Azure DevOps. Its `markdown-gfm.instructions.md` and `documentation-writer` (Diátaxis) skills informed the structure of the instructions file, but no text was copied.
- **[softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit)** — `mermaid-diagrams` skill (~4,800 installs). Evaluated and not used: broad syntax reference with no publishing-target awareness and no validation tooling.
- **Microsoft Learn** — the authoritative constraints. See [Sources](#sources).

---

## Why a retarget was necessary

`design-doc-mermaid` targets **GitHub wiki and Confluence**. Azure DevOps is a materially different renderer, and using the upstream skill unmodified produces diagrams that fail silently.

Three findings from verifying against Microsoft's documentation:

### 1. Azure DevOps does not use a backtick fence

ADO wiki requires a **container fence**:

```text
::: mermaid
flowchart TD
    A[Client] --> B[API]
:::
```

A ```` ```mermaid ```` block renders as a plain grey code block. **Every example in the upstream skill uses backtick fences** — Copilot copies the pattern it sees.

### 2. Azure DevOps runs Mermaid 8.13.9, and excludes two types outright

From the [Sprint 200 release note](https://learn.microsoft.com/en-us/azure/devops/release-notes/2022/wiki/sprint-200-update), verbatim:

> "We have upgraded the version of mermaid charts used in wiki pages to **8.13.9** … Flowchart, Sequence diagrams, Gantt charts, Pie charts, Requirement diagrams, State diagrams, User Journey. **Diagrams that are in experimental mode such as Entity Relationship and Git Graph are not included.**"

The upstream skill recommends `erDiagram` as a default for database documentation, and lists C4 diagrams as GitHub-safe. Neither renders in Azure DevOps.

### 3. No JavaScript, no iframes

Per [Microsoft Learn](https://learn.microsoft.com/en-us/azure/devops/project/wiki/markdown-guidance): *"Markdown in Azure DevOps doesn't support JavaScript or iframes."* This rules out `click` handlers, and rules out embedding interactive HTML diagram tools in the wiki at all.

---

## What was changed, file by file

| File | Origin | Change |
|---|---|---|
| `.github/skills/ado-wiki-mermaid/SKILL.md` | **Original** | Written for this project. Retains upstream's *authoring philosophy* (node budget, reserved words, `classDef` contrast, derive-from-reality) with attribution; all fence, version-gate, and diagram-type rules are ADO-specific and new. |
| `.github/skills/ado-wiki-mermaid/references/ado-wiki-reference.md` | **Original** | Written for this project. ADO constraints, escaping table, theming, ER/C4 substitute patterns, troubleshooting, `.order`/`.attachments` mechanics. |
| `.github/skills/ado-wiki-mermaid/scripts/validate_ado_mermaid.py` | **Original** | Written for this project. Python 3 stdlib only. Upstream ships `resilient_diagram.py`, which validates via `mmdc` (Mermaid CLI) against *modern* Mermaid — that validates the wrong thing for ADO, so it was **not** carried over. |
| `.github/instructions/ado-wiki-mermaid.instructions.md` | **Original** | Written for this project. Scoped via `applyTo` so it does not collide with an existing repo-wide `copilot-instructions.md`. |
| `references/upstream-guides/**` (8 files) | **Upstream, modified** | Copied verbatim from `design-doc-mermaid/references/guides/`, then each file received a prepended warning header marking it as GitHub-targeted and directing the reader to the ADO files on any conflict. Content otherwise unaltered. |
| `references/templates/**` (5 files) | **Upstream, modified** | Copied verbatim from `design-doc-mermaid/assets/`, with a one-line conversion notice prepended. Content otherwise unaltered. |
| `references/guides/wiki-ticket-and-github.md` | **Upstream, removed** | Deleted. It is the GitHub/Confluence/PlantUML publishing guide — precisely the file whose advice is wrong for Azure DevOps. |
| upstream `scripts/` (3 Python files) | **Upstream, removed** | `resilient_diagram.py`, `mermaid_to_image.py`, `extract_mermaid.py` all depend on `mmdc` (npm) and validate against modern Mermaid. Replaced by the ADO validator. |

**Summary:** 4 original files, 13 upstream files retained with headers, 4 upstream files removed.

---

## Layout

```
.github/
├── instructions/
│   └── ado-wiki-mermaid.instructions.md   # auto-applied to wiki .md files only
└── skills/ado-wiki-mermaid/
    ├── SKILL.md                       # loaded on demand by Copilot
    ├── references/
    │   ├── ado-wiki-reference.md      # full ADO constraints + substitutes
    │   ├── upstream-guides/           # design-doc-mermaid guides (headered)
    │   └── templates/                 # design-doc skeletons (headered)
    └── scripts/
        └── validate_ado_mermaid.py    # linter, stdlib only
```

---

## Install

Copy the `.github/` folder into your repository. No npm, no pip, no build step. Python 3 is needed only to run the validator.

**It will not clash with an existing `.github/copilot-instructions.md`.** These rules ship as a *scoped* instructions file — `.github/instructions/ado-wiki-mermaid.instructions.md` — which is a separate mechanism from the repo-wide instructions file. Both load; neither overwrites the other.

| File | Scope | Loads |
|---|---|---|
| `.github/copilot-instructions.md` | whole repo | always, every request |
| `.github/instructions/*.instructions.md` | `applyTo` glob | only for matching files |

### Set the scope

The shipped glob assumes wiki content lives under `wiki/` or `docs/`:

```yaml
---
description: 'Azure DevOps wiki Markdown and Mermaid conventions'
applyTo: '**/wiki/**/*.md, **/docs/**/*.md'
---
```

Edit `applyTo` to match your layout — `'**/*.md'` if the whole repository is wiki content. Without a matching `applyTo`, the file never auto-applies.

Then in VS Code:

1. Reload window (`Ctrl+Shift+P` → *Developer: Reload Window*)
2. Copilot Chat → **Configure Skills** → confirm `ado-wiki-mermaid` is enabled
3. Open a wiki `.md`, ask anything, and check the response's **References** section — the instructions file should be listed

> If it does not appear: confirm `chat.instructionsFilesLocations` includes `.github/instructions` (the default) and that `chat.includeApplyingInstructions` is enabled.

### Composing with a project-investigation skill

This skill only answers *how a diagram should be drawn* — the fence, the supported diagram
types, and the 8.13.9 rendering constraints. It deliberately has no opinion on *what* the
diagram should show or how the model should go find that out.

If a diagram is being generated as part of a larger documentation flow (e.g. a
`create-project-documentation-wiki.prompt.md`-style skill that reads a README, source tree,
and pipeline files to build up an architecture picture), keep that investigation logic in its
own instructions file — do not duplicate diagram syntax rules there. Instead have it defer to
this skill for the "how", something like:

```markdown
## Diagram Rules
- When a documentation task requires a diagram, follow the `ado-wiki-mermaid` skill/instructions
  for syntax, fence, supported diagram types, and the Azure DevOps 8.13.9 constraint set.
- Arrange flow diagrams to show source -> transformation -> destination; prefer `flowchart LR`/`TD`.
- Before finalizing, run `validate_ado_mermaid.py` on the generated file if the skill is
  installed in this workspace.
```

Two things to check when composing the two:

1. **`applyTo` must actually match where the generated file lands.** If the investigation
   skill writes e.g. `DOCUMENTATION_WIKI.md` to a project root rather than under `wiki/` or
   `docs/`, the shipped glob above will never match it and these rules silently won't load.
   Widen it: `applyTo: '**/wiki/**/*.md, **/docs/**/*.md, **/DOCUMENTATION_WIKI.md'`.
2. **Don't hardcode fence/syntax details in the investigation skill's own instructions.**
   A duplicated copy of the `::: mermaid` rule (or worse, a partial one) drifts from this
   skill's rules over time and reintroduces exactly the silently-broken-diagram problem this
   skill exists to prevent. Point at this skill instead of restating its rules.

Optional, in `.vscode/settings.json`, so Copilot can self-check without prompting:

```json
{
  "chat.tools.terminal.autoApprove": {
    "/^python3? .*validate_ado_mermaid\\.py/": true
  }
}
```

> The `name:` in `SKILL.md` must match its folder name (`ado-wiki-mermaid`), or VS Code silently skips the skill.

---

## Use

The instructions file applies automatically to any Markdown matching its `applyTo` glob — you
get the ADO rules even when you never mention the skill. Invoke the skill explicitly with `/ado-wiki-mermaid`
when you want the full workflow: diagram-type check, guide lookup, and validation.

All examples below are in **Agent mode**, which the skill requires.

### Creating a diagram

```
/ado-wiki-mermaid draw the runtime architecture for this service
/ado-wiki-mermaid sequence diagram for the OAuth login flow, from browser to IdP to API
/ado-wiki-mermaid state diagram for the order lifecycle in OrderStatus.cs
/ado-wiki-mermaid flowchart of the nightly reconciliation job, from the scheduler entry point
/ado-wiki-mermaid gantt chart for the Q3 migration phases in this planning page
```

Ask for the diagram *from a source* — a file, a folder, a class — rather than from memory.
The skill is instructed to derive nodes from real code and not invent components.

### Fixing a diagram that does not render

The most common reason to reach for the skill. Paste the broken block, or point at the page:

```
/ado-wiki-mermaid this diagram shows as a grey code block in our wiki, fix it
/ado-wiki-mermaid this renders on GitHub but is blank in Azure DevOps — why?
/ado-wiki-mermaid the arrows render but all the labels are invisible in dark mode
/ado-wiki-mermaid fix every Mermaid block in docs/Architecture.md for Azure DevOps
```

### Migrating existing content

```
/ado-wiki-mermaid convert every ```mermaid fence in this folder to the ::: mermaid fence
/ado-wiki-mermaid this page uses erDiagram — rewrite it as something ADO can render
/ado-wiki-mermaid this C4Context diagram is empty in the wiki, give me a flowchart equivalent
/ado-wiki-mermaid split this 40-node diagram into a parent page and subpages
```

`erDiagram`, `gitGraph`, and the C4 family are the three that bite hardest — they are valid
Mermaid, they render on GitHub, and Azure DevOps shows nothing. The skill carries
copy-ready flowchart substitutes for each.

### Reviewing before publishing

```
/ado-wiki-mermaid review this page for Azure DevOps wiki compatibility
/ado-wiki-mermaid run the validator on docs/ and fix everything it reports
/ado-wiki-mermaid is stateDiagram-v2 supported in our wiki?
```

### Page structure, not just diagrams

The skill also carries the ADO wiki conventions — `.order` files, `.attachments` paths,
root-relative page links, `[[_TOC_]]`:

```
/ado-wiki-mermaid why is my subpage not showing in the wiki tree?
/ado-wiki-mermaid my screenshot link is broken after moving the page — fix the path
/ado-wiki-mermaid restructure this long page into a parent with subpages
```

### Without invoking the skill

Because the instructions file auto-applies to matching files, ordinary requests already follow the rules:

```
add a diagram of the payment flow to this page
document this module for the wiki
```

Use `/ado-wiki-mermaid` when you want the diagram-type check and the validation step
performed explicitly — on anything you are about to publish, it is worth the extra keystrokes.

---

## Validate

```bash
# single page
python3 .github/skills/ado-wiki-mermaid/scripts/validate_ado_mermaid.py page.md

# whole wiki, warnings also fail
python3 .github/skills/ado-wiki-mermaid/scripts/validate_ado_mermaid.py --recurse wiki/ --strict

# machine-readable
python3 .github/skills/ado-wiki-mermaid/scripts/validate_ado_mermaid.py --json page.md
```

Exit codes: `0` clean · `1` errors (or warnings under `--strict`) · `2` bad invocation.

### Checks

| Code | Level | Catches |
|---|---|---|
| ADO001 | error | Backtick fence instead of `::: mermaid` |
| ADO002 | error | Unclosed `::: mermaid` block |
| ADO010 | error | Diagram type ADO cannot render |
| ADO011 | warn | `classDiagram` — renders, but absent from the official list |
| ADO012 | warn | Unrecognized diagram type |
| ADO020 | warn | Blank line inside the fence |
| ADO030–035 | error | Post-8.13.9 syntax (`%%{init}`, `@{shape}`, md-strings, `click`, `~~~`) |
| ADO040 | error | Reserved word as a bare node id (`end`, `default`, …) |
| ADO050 | error | `classDef` with `fill:` but no `color:` |
| ADO060 | warn | More than ~16 nodes |
| ADO061 | warn | `subgraph` nested deeper than 2 |
| ADO070 | warn | Attachment path not root-relative |

### Pipeline gate

```yaml
- script: python3 .github/skills/ado-wiki-mermaid/scripts/validate_ado_mermaid.py --recurse wiki/
  displayName: Validate wiki Mermaid
```

---

## Verification

The validator was exercised against a fixture containing every failure mode: **10 errors and 3 warnings caught**. A clean, correct page returns **PASS with zero false positives** — including correctly *not* flagging the legitimate `end` keyword that closes a `subgraph`.

**The failure mode this exists to prevent:** the VS Code Markdown preview and the Mermaid Live Editor both run Mermaid 10/11. A diagram can look perfect locally and fail in Azure DevOps. The validator closes exactly that gap.

---

## Maintenance

If Microsoft upgrades the wiki past Mermaid 8.13.9, most constraints here relax. Revisit the version gates in `SKILL.md` and `references/ado-wiki-reference.md`, and check the [Azure DevOps release notes](https://learn.microsoft.com/en-us/azure/devops/release-notes/).

Where the upstream guides in `references/upstream-guides/` conflict with `SKILL.md` or `ado-wiki-reference.md`, **the ADO files win.**

---

## Sources

**Upstream skill**
- [SpillwaveSolutions/design-doc-mermaid](https://github.com/SpillwaveSolutions/design-doc-mermaid) — Rick Hightower, MIT (per README/plugin.json)

**Azure DevOps documentation**
- [Markdown syntax for files, widgets, and wikis](https://learn.microsoft.com/en-us/azure/devops/project/wiki/markdown-guidance)
- [Wiki — Sprint 200 Update](https://learn.microsoft.com/en-us/azure/devops/release-notes/2022/wiki/sprint-200-update) — the 8.13.9 pin and supported-type list
- [Which version of Mermaid is supported in Azure DevOps Wikis](https://stackoverflow.com/questions/64822151/which-version-of-mermaid-is-supported-in-azure-devops-wikis)
- [Support standard fenced code block syntax for Mermaid](https://developercommunity.visualstudio.com/t/Support-standard-fenced-code-block-synta/11041901) — open request; backtick fences are not yet supported

**Copilot / skills**
- [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [About agent skills — GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [github/awesome-copilot](https://github.com/github/awesome-copilot) — MIT
- [Mermaid 8.13.9 release](https://github.com/mermaid-js/mermaid/releases/tag/8.13.9)

---

## License

MIT — see [`LICENSE`](LICENSE).

Files under `references/upstream-guides/` and `references/templates/` derive from
[design-doc-mermaid](https://github.com/SpillwaveSolutions/design-doc-mermaid) by Rick Hightower,
used under the MIT terms stated by its author. See [`NOTICE`](NOTICE) for full attribution.
