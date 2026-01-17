# PG Original - QA Automation Portfolio

<br>

<div align="center">
  <img src="assets/pg_logo.png" alt="PG Original Logo" width="300"/>
  <br>
  <br>
  <h2>Automated Testing Framework tailored for <a href="https://www.pgoriginal.com/">pgoriginal.com</a>.</h2>
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
  <img src="https://img.shields.io/badge/Status-Complete-success" alt="Status"/>
  <img src="https://img.shields.io/badge/Tests-Passing-green" alt="Tests"/>
  <img src="https://img.shields.io/badge/Python-3.12-blue" alt="Python"/>
  <img src="https://img.shields.io/badge/Framework-Playwright-orange" alt="Framework"/>
</div>


## Architecture & Design Principles

### 🧩 Key Patterns Implemented
*   **Page Object Model (POM)**: Strict separation of selectors (in `pages/`) and assertions (in `tests/`).
*   **Composition & Inheritance**: `Navbar` logic is inherited by `BasePage`, making navigation methods (`home.navbar.open_search()`) available universally.
*   **DRY (Don't Repeat Yourself)**: Centralized configuration (e.g., `BASE_URL` in `BasePage`) and reusable components.
*   **Explicit Waits**: Smart waits (`wait_for_load_state`, `wait_for_selector`) for flaky-free execution.


## Testing Features


### 1. 📊 Data Driven Testing (DDT)

- **Implementation**: `data/test_data.json`
- **Benefit**: Testing multiple datasets (e.g., different users, checkout flows) without implementing hardcoded values.


### 2. 🛡️ Soft Assertions (`pytest-check`)

- **Implementation**: Instead of stopping at the first failure, Product Detail Page tests verify **Price**, **Name**, and **Buttons** in a single pass.
- **Benefit**: Maximizes defect discovery per test execution cycle.


### 3. 🎭 Dynamic Data Generation (`Faker`)

- **Implementation**: Contact Form tests use `Faker` to generate unique names and emails for every run.
- **Benefit**: Uncovers edge cases (long strings, special characters) that static data misses.


## Project Structure

```bash
├── pages/                  # 📍 Page Objects
│   ├── base_page.py        #    - Parent class (Logger, Wrappers, Base URL)
│   ├── home_page.py        #    - Home & Search logic
│   ├── shop_page.py        #    - PLP (Product List Page) logic
│   ├── product_page.py     #    - PDP (Detailed) logic
│   ├── login_page.py       #    - Authentication logic
│   └── contact_page.py     #    - Forms & Validation logic
├── components/             # 🧩 Shared UI Components
│   └── navbar.py           #    - Header/Nav interactions
├── tests/                  # 🧪 Test Suite
│   ├── conftest.py         #    - Fixtures (Setup, Teardown, Data Loading)
│   ├── test_smoke.py       #    - Critical Health Checks
│   ├── test_shop.py        #    - E2E Shopping Flows (Soft Assertions)
│   ├── test_auth.py        #    - DDT Login Tests
│   └── test_contact.py     #    - Faker Dynamic Tests
├── data/                   # 💾 External Data
│   └── test_data.json      #    - JSON Test Data
└── requirements.txt        # 📦 Dependencies
```

## Setup & Execution

> **DISCLAIMER:**
> This project is a tailored QA framework designed for **PG Original** as a client deliverable.
> *   **Authorized Use**: Verified for portfolio demonstration by the client.
> *   **Anti-Bot Policy**: The target site `pgoriginal.com` implements strict anti-bot mechanisms. This framework handles them professionally by documenting blocks rather than bypassing them unethically. Use strictly for learning; any bad practice on the website will incur into possible IP bans.

### Prerequisites
*   Python 3.8+
*   `pip`

### Installation
```bash
git clone https://github.com/MiltonKlun/PG_Original_POM.git
cd PG_Original_POM
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
playwright install
```

### Running Tests
**Run All Tests:**
```bash
pytest tests/
```

**Run Specific Features:**
```bash
pytest -m smoke        # Health checks
pytest -m integration  # Shopping flows
pytest -m auth         # Login/Register
pytest -m contact      # Forms
```

### 📑 Reporting
Generate professional Allure reports:
```bash
pytest --alluredir=reports
allure serve reports
```

---

## Author
**Milton Klun**  
*QA Automation Engineer*

<div align="left">
  <a href="https://www.linkedin.com/in/milton-klun/">
    <img src="https://img.shields.io/badge/LinkedIn-Milton%20Klun-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn"/>
  </a>
  <a href="mailto:miltonericklun@gmail.com">
    <img src="https://img.shields.io/badge/Email-Contact%20Me-red?style=for-the-badge&logo=gmail" alt="Email"/>
  </a>
</div>
