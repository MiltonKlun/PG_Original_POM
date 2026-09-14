# Running and diagnosing a case

Activate the isolated Python 3.12 environment from the README. `TARGET` defaults
to `mock`; the fixture owns the Python server for a normal local run. Explicit
live runs enforce `live_safe` eligibility even if `-m` is omitted.

```text
python -m pytest tests/test_cart.py::test_cart_quantity --seed 1729 --headed
python -m pytest --collect-only -q
python -m pytest tests/framework -q
```

The header reports the resolved target, origin and seed. Data is derived from
seed plus node ID, so rerunning that node does not depend on test order.

## Evidence

Each run gets a unique ID. `reports/<id>/` contains a self-contained
`report.html`, `results.xml` and `summary.json`. Browser evidence goes to
`test-results/<id>/`, logs to `logs/<id>.log`. Passing cases do not retain
screenshots/videos/traces. The HTML includes target, browser, seed, revision
and effective paths; browser artifacts remain separate companion files.

Open `report.html` directly in a browser. Inspect the trace from a failed case:

```text
python -m playwright show-trace test-results/<id>/<case>/trace.zip
```

For a deliberate stable label, use `--run-id my-investigation-01`; IDs may
contain letters, digits, hyphens and underscores. Reusing an existing report
directory is rejected to preserve evidence. Choose a new ID rather than
deleting another run. Explicit `--output`, `--junitxml` and `--html` paths are
supported and recorded; use unique paths when overriding the defaults.

## Diagnose the actual failure

| Evidence | Interpretation / next step |
|---|---|
| Configuration/collection error | Fix invalid target, URL, marker or malformed dataset before browser debugging. |
| Fixture/setup error | A precondition failed; pytest/JUnit call this an error, not a passed or skipped case. Inspect its assertion and trace. |
| Assertion failure | Compare expected business state with DOM, action sequence and network evidence. Do not relax the assertion to get green. |
| Strict locator error | Check responsive duplicates or changed markup; correct scope in the owning POM. Do not add arbitrary `.first`. |
| Timeout | Inspect the trace first. It may be a locator, data, product, network or environment problem. It alone does not establish bot detection. |
| Observed first-party 403/429 or challenge UI | Record endpoint path/status and screenshot. Stop repeated attempts; keep the live workflow's failed result visible. |
| Browser installation error | Run `python -m playwright install chromium` using the same interpreter as pytest; Linux needs `--with-deps`. |
| `Mock attempted external requests` | A local asset/redirect escaped the mock origin. Fix the mock/serving contract, rather than permitting production traffic. |

First-party HTTP failures log method-independent status/path without response
bodies or query tokens. JavaScript errors log the error type; use the local
trace for full details. No handler paints an artificial failure overlay or
automatically turns a failure into a skip.

## Server ownership and ports

```text
python scripts/serve_mock.py --host 127.0.0.1 --port 8090
python -m pytest --base-url http://127.0.0.1:8090
```

Run these in separate terminals to reuse an explicit foreground server. It
must serve the exact `/__health` identity. Stop that server with Ctrl+C.
Normal pytest uses an owned daemon thread with context-managed shutdown; no
helper process remains after pytest exits. Windows sockets request exclusive
ownership so another listener cannot silently share the same port.

If the port is occupied, identify its owner (`Get-NetTCPConnection -LocalPort
8090` in PowerShell, `ss -ltnp` on Linux). Stop only your own server/container
or use a different explicit port. After forcibly terminating a Docker session,
list containers and stop only the named PG Original container you started.
The fixture never stops a server supplied through `--base-url`.

## Sharing evidence

Use synthetic mock inputs for portfolio artifacts. Application logs omit input
values, but traces/videos may include DOM, typed values, cookies or request
URLs. Keep unmodified local diagnostic originals; share only reviewed
synthetic evidence or clearly labeled sanitized excerpts. Public workflows
must not upload authenticated live traces or client credentials. This suite
does not use real accounts.

The reviewed [cart error screenshot](evidence/mock-cart-error.png) is from a
deliberate defect in a disposable local copy: the UI said “Agregado al carrito”
but the cart remained empty. The setup assertion detected the missing item.
It is not a client production defect. Full original reports remain in ignored
local artifact directories; future Actions runs upload their own evidence.
