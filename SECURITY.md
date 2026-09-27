# Security policy

## Scope

This policy covers the code in this repository: the test framework, the
local storefront simulation and the CI workflows. It does not cover
[pgoriginal.com](https://www.pgoriginal.com/) itself; problems with the store
should be reported to PG Original directly.

## Reporting a vulnerability

Please report suspected vulnerabilities privately through GitHub's
**Report a vulnerability** button on the repository's Security tab, or by
email to the address in the README. Don't open a public issue. I aim to
acknowledge reports within a week.

## How this repository handles sensitive data

- No credentials, tokens or accounts are used or stored. Test data is
  synthetic; generated emails use the reserved `example.com` domain.
- Live checks are read-only and never submit logins, orders, messages or
  password resets.
- Application logs omit input values. Browser traces can contain cookies,
  typed values and request URLs, so live traces are never uploaded as CI
  artifacts and stay out of git (`test-results/`, `reports/`, `logs/`).
- Dependencies are pinned to exact versions. GitHub Actions are pinned to
  full commit SHAs, workflows run with a read-only token and don't persist
  checkout credentials.
- The Security workflow audits the pinned dependencies, including the
  packages they pull in, for known
  vulnerabilities (pip-audit) and the workflows for insecure patterns
  (zizmor) on every pull request and weekly.
