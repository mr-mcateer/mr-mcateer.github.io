# .githooks/

Versioned git hooks for this repo. Active on this clone via:

```sh
git config core.hooksPath .githooks
```

Run that one line after cloning. (Already set on Andrew's machine 2026-04-23.)

## pre-commit

Catches phantom git submodules (gitlinks committed without a corresponding `.gitmodules` entry).

**Why this exists:** on 2026-04-22 a Claude Code worktree at `.claude/worktrees/keen-pike` got committed as a gitlink (mode 160000) with no `.gitmodules` file. Three consecutive GitHub Pages builds errored on `git submodule update --init --recursive`. The live site at promptaisolutions.com/stock-analysis/ was frozen at the prior commit for three days before anyone noticed. This hook prevents that class of failure.

**Behavior:** scans the staged diff for any new gitlinks (mode 160000). For each, requires either an existing `.gitmodules` entry with that path, or the commit aborts with an explanatory message.

**Bypass** (only when you really mean it): `git commit --no-verify`.
