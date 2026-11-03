# chinese-report-voice

[简体中文](README.md) | **English**

**For Chinese formal documents read by judges, executives or investors: decide the register before writing. Report voice, technical doc and spoken script are three different languages — mixing them wastes the whole draft.**

![Python](https://img.shields.io/badge/python-3.9%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-yellow)
![spec](https://img.shields.io/badge/agentskills.io-spec%20valid-2E7D32)

## Install

```bash
npx skills add zhanguoliang715/chinese-report-voice
```

Or as a Claude Code plugin:

```bash
claude plugin marketplace add zhanguoliang715/chinese-report-voice
claude plugin install chinese-report-voice@chinese-report-voice
```

## Three registers, decided first

| Register | Reader | What they decide with it | Test |
|---|---|---|---|
| **Report voice** | judges, authorities, investors | whether it deserves a score, a budget, a yes | no first-person narrative; each section opens with a judgement; data has provenance |
| **Technical doc** | engineers | whether they can reproduce it | diagrams, parameters, commands, exit codes |
| **Spoken script** | an audience, listening | whether to keep watching | short sentences, breathing room, first person, only numbers that survive being heard |

The most common failure is handing a technical document to judges (they cannot see whether it is worth doing), or writing report voice as a spoken script (all "we" and story).

## What it enforces

- **Six voice rules** for report register: subject is "this category of user / this approach", not "we"; first sentence of each section is a judgement; enumerated items as 1．2．3．; chapter opening and closing conventions; formal vocabulary; zero dashes and zero colloquialisms.
- **Self-undermining sentences are deleted** — "for reference only", "sample too small", "no conclusion drawn" cost points in a review setting.
- **Inherited data is forbidden** — "the previous version said so" is not a source. Without a record file, restating a number is fabrication.

## Two runnable gates

```bash
python scripts/check_voice.py 正文.txt          # also .md / .docx / .pdf / .py
python scripts/check_pdf_layout.py 报告.pdf      # also --margin 2.6 --min-chars 330
```

| Script | Checks | Exit codes |
|---|---|---|
| `check_voice.py` | colloquialisms, dashes, self-undermining phrases, filler; **reports, never rewrites** | 0 pass / 1 hard violation / 2 advisory only |
| `check_pdf_layout.py` | paper size (A4), thin and blank pages, table overflow, table-of-contents page numbers | 0 pass / non-zero found issues |

## Boundaries

- **Style and layout only, not truth.** Facts still need checking.
- **Cannot make wrong content right.** It can make correct prose read like a report; it cannot turn fabrication into fact.
- **Event or institution templates win.** If the official chapter list conflicts with these rules, the template is authoritative.

## Docs

- [Beginner handbook](docs/新手手册.md)
- [Technical doc](docs/技术文档.md)
- [examples/bad_vs_good.md](examples/bad_vs_good.md) — paragraph-by-paragraph contrast

## License

MIT.
