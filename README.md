# PG Original - Page Object Model

<br>

<div align="center">
  <img src="assets/pg_logo.png" alt="PG Original Logo" width="300"/>
  <br>
  <br>
  <h2>Automated Testing Framework for <a href="https://www.pgoriginal.com/">pgoriginal.com</a>.</h2>
</div>


<div align="center">
  <a href="https://www.pgoriginal.com/">
    <img src="https://img.shields.io/badge/Client-PG%20Original-000?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Website"/>
  </a>
  <a href="https://www.instagram.com/pgoriginalind/">
    <img src="https://img.shields.io/badge/Instagram-@pgoriginalind-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram"/>
  </a>
</div>

---

<div align="center">
  <a href="https://github.com/MiltonKlun/PG_Original_POM/actions/workflows/ci.yml"><img src="https://github.com/MiltonKlun/PG_Original_POM/actions/workflows/ci.yml/badge.svg" alt="Mock CI"/></a>
  <a href="https://github.com/MiltonKlun/PG_Original_POM/actions/workflows/live-smoke.yml"><img src="https://github.com/MiltonKlun/PG_Original_POM/actions/workflows/live-smoke.yml/badge.svg" alt="Live read-only smoke"/></a>
  <img src="https://img.shields.io/badge/Python-3.12-blue" alt="Python"/>
  <img src="https://img.shields.io/badge/Framework-Playwright-orange" alt="Framework"/>
</div>


## Architecture & Design Principles

### 🧩 Key Patterns Implemented

*   **Page Object Model (POM)**: Selectors and domain actions live in `pages/` and `components/`; business assertions live in `tests/`.
*   **Composition & Inheritance**: Page objects inherit a small `BasePage`, which composes shared modules such as `Navbar`, `SearchModal`, and `CartDrawer`.
*   **DRY (Don't Repeat Yourself)**: Centralized target configuration, reusable components, and fixtures managed by pytest-playwright.
*   **Explicit Waits**: Playwright auto-waiting and retrying `expect` assertions wait for observable UI state.

## Testing Features

### 1. 📊 Data Driven Testing (DDT)

- **Implementation**: Named datasets in `data/test_data.json` parameterize negative login and contact-input cases.
- **Benefit**: Cover multiple inputs while keeping expected data separate from the synthetic storefront's catalog.

### 2. 🛡️ Business Assertions (Playwright)

- **Implementation**: Product tests verify selected identity and current price. Cart tests verify exact product, variant, quantity, line amount, and subtotal.
- **Benefit**: Detect incorrect shopping outcomes, including quantity updates and removal, with retained evidence when a test fails.

### 3. 🎭 Dynamic Data Generation (`Faker`)

- **Implementation**: Contact tests generate reproducible Spanish-language inputs from the case ID and seed (`1729` by default), using `example.com` email addresses.
- **Benefit**: Replay generated inputs alongside explicit accented-name, whitespace, and malformed-email cases.

The suite includes **62 cases: 37 offline checks and 25 UI cases**. It covers navigation, search, product details, filtering, cart behavior, and non-submitting form checks. Each UI case receives an isolated browser context.

## Project Structure

```text
├── pages/                  # 📍 Page Objects
│   ├── base_page.py        #    - Shared navigation and component composition
│   ├── home_page.py        #    - Home navigation
│   ├── shop_page.py        #    - Product discovery and filtering
│   ├── product_page.py     #    - Product details and variant selection
│   ├── login_page.py       #    - Login and reset-page controls
│   └── contact_page.py     #    - Contact fields and native validation
├── components/             # 🧩 Navbar, search modal, cart drawer, cookies
├── config/                 # ⚙️ Target settings, seeded data, money, reporting
├── tests/                  # 🧪 UI scenarios and offline framework checks
├── data/                   # 💾 Named test inputs and expected values
├── mock_site/              # 🛍️ Local synthetic storefront and Dockerfile
├── scripts/                # 🛠️ Mock server and CI summaries
├── .github/workflows/      # 🔄 Mock CI, live smoke, browser compatibility
├── requirements.in         # 📦 Direct dependency pins
└── requirements.txt        # 📦 Hashed dependency resolution
```

## Setup & Execution

> **DISCLAIMER:**
> This project is a tailored QA framework designed for **PG Original** as a client deliverable.
> *   **Authorized Use**: Verified for portfolio demonstration by the client.
> *   **Test Scope**: Default runs use a local simulation. Live checks are read-only; they do not submit credentials, contact messages, purchases, or reset emails. Challenges are not bypassed. Mock results do not certify production transactions.

### Prerequisites

*   Python 3.12 and `pip`
*   Docker (optional, for container-based mock serving)

### Installation

```bash
git clone https://github.com/MiltonKlun/PG_Original_POM.git
cd PG_Original_POM
python -m venv venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS shell
source venv/bin/activate
```

Install the pinned dependencies and browser:

```bash
python -m pip install --require-hashes -r requirements.txt
python -m pip check
python -m playwright install chromium
```

On Linux, use `python -m playwright install --with-deps chromium` for the last command to include required system libraries.

On Windows, commands can also use `venv\Scripts\python.exe` directly without activating the environment. Windows and Ubuntu execution are verified; macOS has not been verified.

### Running Tests

**Run All Tests:**

```bash
python -m pytest tests/
```

The default headless run starts and stops its own local mock server at `http://127.0.0.1:8090` and rejects external HTTP(S) requests.

**Run Specific Features:**

```bash
python -m pytest -m smoke        # Navigation, search, product smoke
python -m pytest -m shop         # Shopping and cart flows
python -m pytest -m auth         # Local negative login and reset navigation
python -m pytest -m contact      # Non-submitting form checks
python -m pytest tests/framework # Offline framework checks
python -m pytest --seed 1729     # Reproduce generated inputs
```

**Read-Only Live Smoke:**

```powershell
# Windows PowerShell
$env:TARGET = "live"
try {
    python -m pytest tests -m "smoke and live_safe" --browser chromium
} finally {
    Remove-Item Env:TARGET
}
```

```bash
# Linux / macOS shell
TARGET=live python -m pytest tests -m "smoke and live_safe" --browser chromium
```

This selects three read-only checks for home/shop access, search controls, and product details. Cart mutations and invalid-login submissions stay local.

**Optional Docker Mock:**

```bash
docker build -t pgoriginal-mock mock_site
docker run --rm -p 127.0.0.1:8090:80 pgoriginal-mock
```

In another terminal with the Python environment active, run `python -m pytest --base-url http://127.0.0.1:8090`. Pytest verifies and reuses the server; stop the foreground Docker command with Ctrl+C when finished.

**Browser Compatibility:**

```bash
python -m playwright install firefox webkit
python -m pytest tests -m "not framework" --browser firefox
python -m pytest tests -m "not framework" --browser webkit
python -m pytest tests -m smoke --browser chromium --device "Pixel 7"
```

On Linux, add `--with-deps` when installing browsers. Pixel 7 coverage is mobile emulation. CI runs mock checks on pull requests; live smoke and compatibility also have manual and weekly workflows.

### 📑 Reporting

Each run creates a standalone HTML report, JUnit XML, and JSON summary under `reports/<run-id>/`. Open `report.html` directly in a browser. Reports identify the target, browser, seed, revision, and actual outcomes.

Failed cases retain traces, screenshots, and video under `test-results/<run-id>/`; runtime logs are in `logs/`. Review live evidence before sharing because it may contain session or client data.

```bash
python -m playwright show-trace test-results/<run-id>/<failed-case>/trace.zip
```

Use `--headed` to watch a local test or `--run-id <unique-name>` to name its reports. Custom run IDs are one-use; choose a new name for each run.

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

## Author

**Milton Klun**  
*QA Automation Engineer | AI Quality Testing*

<div align="left">
  <a href="https://www.linkedin.com/in/milton-klun/"><img src="https://img.shields.io/badge/LINKEDIN-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a><a href="mailto:miltonericklun@gmail.com"><img src="https://img.shields.io/badge/EMAIL-D14836?style=for-the-badge" alt="Email"/></a><a href="https://www.miltonklun.com"><img src="https://img.shields.io/badge/PORTFOLIO-000000?style=for-the-badge" alt="Live Site"/></a>
</div>
