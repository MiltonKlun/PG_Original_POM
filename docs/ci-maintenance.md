# CI and maintenance handoff

Hosted workflows are verified for `MiltonKlun/PG_Original_POM`; run links and
downloaded-artifact inspections are recorded in
[release evidence](evidence/release-verification.json). PR #1 is the implementation;
PR #2 was an isolated, restored acceptance experiment. Main-branch merge and
protection remain pending owner approval.

## Jobs and scope

| Workflow | Trigger | Checks | Merge requirement |
|---|---|---|---|
| `ci.yml` / Mock CI | PR/push to main; manual | Windows and Ubuntu static/offline checks; Ubuntu Chromium UI against Docker/nginx | Require all three jobs below |
| `live-smoke.yml` | Manual; Monday 09:00 UTC (06:00 Buenos Aires) | Serial Chromium `smoke and live_safe`; no submissions | Non-required; failures stay failures |
| `compatibility.yml` | Manual; Monday 09:30 UTC | Full mock UI on Firefox/WebKit; Chromium Pixel 7 smoke | Non-required initially |

Primary jobs have a 10/15-minute timeout, read-only repository permissions and
cancel obsolete runs. Artifacts have unique matrix/attempt names and 14-day
retention. Reports include JUnit, standalone HTML and JSON; local mock failures
also retain browser evidence and server logs. Live artifacts exclude raw browser
traces, video and the separate runtime log. Review even live HTML/JUnit before
redistribution: failure text can include client page content. No trace is public
portfolio evidence until reviewed.

`scripts/ci_summary.py` requires the JSON summary and referenced JUnit file.
Missing or invalid evidence exits nonzero. Summarizing a failed run does not
override the failed pytest step. No workflow uses `continue-on-error`.

## Publication acceptance procedure

Steps 1-4 have hosted evidence. Steps 5-6 are the remaining owner-controlled
publication work. Recheck the latest PR #1 checks before merging; run records
identify both the source head SHA and the generated PR merge revision tested.

1. Publish the reviewed implementation branch and open a PR to `main` when
   requested. Observe `Mock CI` on the exact pushed SHA; record its run URL in
   `IMPROVEMENTS.md` and `docs/evidence/release-verification.json`.
2. Download a passing run's artifacts. Open the HTML offline and compare JSON
   counts with JUnit. Confirm target, seed, revision and artifact paths.
3. On a temporary PR branch, deliberately change one expected mock cart subtotal
   in the test data. Verify the UI job fails and still uploads its HTML/JUnit,
   trace and server log. Inspect the failure, restore the change and confirm
   green CI. Do not merge the deliberate defect. Record both run URLs.
4. Dispatch live smoke and compatibility on the implementation ref. Inspect
   selections and actual outcomes. A live timeout is unresolved evidence until
   investigated, not proof of an application defect. Schedules run from the
   default branch after merge and may be delayed by GitHub.
   Before the new workflows existed on main, acceptance used temporary
   `pull_request` triggers on PR #2 with identical runtime steps. Both workflows
   passed, and the temporary triggers were reverted. First default-branch
   dispatch/scheduled execution remains a post-merge check.
5. In the repository's main-branch ruleset/protection settings, require PRs and
   the exact check names `Quality (ubuntu-24.04)`, `Quality (windows-latest)`, and
   `Mock UI (Chromium)`. Select names from a real run, require an up-to-date
   branch, and enforce the rule for normal contributors. Do not require the
   live job. Confirm a failing mock PR cannot merge under the configured rule.
6. After approval, mark PR #1 ready, merge the reviewed SHA with passing required
   checks, and verify main's Mock CI. Dispatch live/compatibility from main and
   check their actual outcomes. Close the core milestone only after the branch
   rule is verified. No tag or release is implied by this step.

### Prepared branch protection

[`branch-protection.json`](branch-protection.json) is the concrete proposed API
payload. It requires the three verified GitHub Actions checks (observed app ID
15368), an up-to-date PR branch, resolved conversations and no force pushes or
deletions, including for administrators. It sets zero mandatory human approvals
for this single-owner portfolio, while still requiring a PR and green checks.
It does not require the external live workflow. Main was observed unprotected;
re-read existing settings before applying so later owner changes are preserved.

Once authorized, from the repository root:

```text
gh api --method PUT repos/MiltonKlun/PG_Original_POM/branches/main/protection --input docs/branch-protection.json
gh api repos/MiltonKlun/PG_Original_POM/branches/main/protection
```

Inspect the response and PR merge requirements; do not deliberately merge a
failing change to test the rule. The payload is prepared, not already applied.
See [GitHub branch protection API](https://docs.github.com/en/rest/branches/branch-protection#update-branch-protection)
and [manual dispatch requirements](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

## Dependency updates

Actions are SHA-pinned; `.github/dependabot.yml` proposes monthly Actions updates
(maximum three open PRs). Review release notes and CI before merging them.

Python pins are maintained as one change to `requirements.in` and the universal
hashed `requirements.txt`. Dependabot is not configured to rewrite this uv-generated
pip lock. Once a month, or when a relevant fix is released:

```text
uv pip compile requirements.in --universal --python-version 3.12 --generate-hashes -o requirements.txt
python -m pip install --require-hashes -r requirements.txt
python -m pip check
python -m playwright install --with-deps chromium firefox webkit
python -m black --check conftest.py config pages components tests scripts
python -m flake8 conftest.py config pages components tests scripts
python -m pytest
```

The lock was generated with uv 0.11.29. Update intended direct pins first; review
all resolved changes. Reinstall matching browsers after a Playwright update,
run compatibility and clean Windows/Linux installs, and include results in the
PR. Keep nginx's image digest updated in a separate reviewed Docker change.

References: [GitHub artifacts](https://docs.github.com/en/actions/tutorials/store-and-share-data),
[Playwright CI](https://playwright.dev/python/docs/ci),
[uv pip compile](https://docs.astral.sh/uv/pip/compile/).
