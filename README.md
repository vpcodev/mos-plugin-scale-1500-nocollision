# MOS Plugin Repository Scale and GraphQL Fixtures

This public repository is a reproducible test corpus for repository scanners that discover
plugins, parse manifests, and fetch skill files from GitHub. This no-collision variant contains
**1,561 plugin candidates**: 1,450 clean control plugins and 111 deliberately varied edge cases.
It omits the two case-only paths because the scanner rejects those paths before reading plugins.
Every candidate has at least one skill with substantive Markdown content; malformed manifests and
unusual Git objects are intentional test inputs, not examples to copy into production.

The layout follows the repository scanner's plugin convention:

```text
plugins/<plugin-name>/plugin.json
plugins/<plugin-name>/skills/<skill-name>/SKILL.md
```

Some edge fixtures use the compatibility manifest at
`plugins/<plugin-name>/.github/plugin/plugin.json`. The generator also adds a small number of
Git-index-only paths that Windows cannot safely stage from the working tree; those entries are
present in the committed Git tree and are covered by the repository totals.

## Fixture inventory

| Group | Count | What it tests |
|---|---:|---|
| Clean controls | 1,450 | Valid manifests and one substantive skill each, spread across 20 technology and operations domains |
| Large manifests and skills | 18 | Valid JSON padded to 240 KiB, 520 KiB, or 1.1 MiB; skill files use the same size bands |
| Exactly 20 skills | 10 | The accepted skill-count boundary |
| 21 skills | 12 | Behavior above the declared-skill limit |
| Path stress | 20 | Deep paths, one 240-character segment, Unicode, spaces, `#`, and `@` |
| Content stress | 16 | Duplicate and invalid JSON, UTF-8 BOM, invalid UTF-8, binary content, CRLF, and empty files |
| Git object stress | 12 | Symlinks, a submodule entry, and a Git LFS pointer |
| Duplicate plugin names | 10 | Distinct paths that declare the same plugin name |
| Manifest layout conflicts | 12 | Root and compatibility manifests with different declared skills |
| GraphQL expression path | 1 | A committed path containing a quote, backslash, colon, `#`, and `@` |

The 1,450 clean controls are the unambiguous valid baseline. Edge fixtures are counted separately
because validity and fallback behavior are the point of those tests.

## Reproduce the corpus

Run from a clone of this repository with Python 3.10+ and Git:

```powershell
python tools\generate_plugins.py
```

The generator writes the ordinary fixtures and adds Git-object-only test entries to the index.
Stage the working-tree files first, then restore the Git-only fixtures in the index before
committing:

```powershell
git -c core.longpaths=true add -- README.md .gitattributes .gitmodules tools plugins
python tools\generate_plugins.py --mode index-edges
git commit -m "test: add generated plugin fixtures"
```

The `index-edges` pass also preserves the CRLF test blob byte-for-byte, even when the local Git
configuration would otherwise normalize line endings.

The source fixture commit is intentionally kept small so generated content can be published in a
small number of commits.

To create an over-limit corpus, create a separate branch from the default branch and run:

```powershell
git switch -c over-limits
python tools\generate_plugins.py --mode over-limits
git -c core.longpaths=true add -- .gitmodules plugins
python tools\generate_plugins.py --mode index-edges
```

That branch adds 1,500 more plugins and hundreds of extra files. It is intended to cross scanner
file-count and tree-metadata limits: it includes 3,000 Git-index-only entries with long paths,
bringing its recursive Git tree response above 10 MiB while remaining within the 48 MiB full
snapshot response limit. Do not merge it into the default branch.

## GraphQL probe plan

Probe pinned commit paths through `repository.object(expression: ...)`, using one GraphQL alias per
file. Record batch sizes 50, 100, 250, and 500; response duration; `rateLimit` cost, remaining
budget, and reset time; GraphQL errors; and each fixture's returned `text`, `isTruncated`, and
`isBinary` values. Keep REST fallback results separate from GraphQL results so the probe shows
which cases the batch reader can safely serve.

The repository is synthetic. It contains no credentials, customer data, or real user records.
