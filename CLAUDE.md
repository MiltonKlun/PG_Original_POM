# PG_Original_POM

Playwright + Pytest Page Object Model automation with a default local simulation
and separate read-only pgoriginal.com checks.

## Start here

Read [IMPROVEMENTS.md](IMPROVEMENTS.md) for the authoritative task status and
accepted scope. The old `01-PG-ORIGINAL-POM.md` is historical, not an execution
checklist. Follow [README.md](README.md) for setup and architecture,
[test strategy](docs/test-strategy.md) for scenario coverage,
[site contract](docs/site-contract.md) for observed versus simulated behavior,
and [troubleshooting](docs/troubleshooting.md) for evidence handling.

The next incomplete gate is remote CI acceptance (Tasks 7.1/7.2). See
[CI maintenance](docs/ci-maintenance.md) for the concrete publication sequence
and required check names. Do not mark remote runs/settings verified from local
passes. Keep live actions within the plan's agreed read-only scope.

## Agent skills

### Issue tracker

Issues live as GitHub issues in `MiltonKlun/PG_Original_POM`, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, each using its default label string. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
