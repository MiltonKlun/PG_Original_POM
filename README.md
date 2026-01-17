# 🧪 PG Original - QA Automation Portfolio

> **Automated Testing Framework** tailored for [pgoriginal.com](https://www.pgoriginal.com/).  


![Status](https://img.shields.io/badge/Status-Complete-success)
![Tests](https://img.shields.io/badge/Tests-Passing-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Framework](https://img.shields.io/badge/Framework-Playwright-orange)

---

## 🏗️ Architecture & Design Principles


### 🧩 Key Patterns Implemented
*   **Page Object Model (POM)**: Strict separation of selectors (in `pages/`) and assertions (in `tests/`).
*   **Composition & Inheritance**: `Navbar` logic is inherited by `BasePage`, making navigation methods (`home.navbar.open_search()`) available universally.
*   **DRY (Don't Repeat Yourself)**: Centralized configuration (e.g., `BASE_URL` in `BasePage`) and reusable components.
*   **Explicit Waits**: Zero use of `time.sleep()`. We use smart waits (`wait_for_load_state`, `wait_for_selector`) for flaky-free execution.

---

## 🚀 Testing Features


### 1. 📊 Data Driven Testing (DDT)

- **Implementation**: `data/test_data.json`
- **Benefit**: We can test multiple datasets (e.g., different users, checkout flows) without touching a single line of code.

### 2. 🛡️ Soft Assertions (`pytest-check`)

- **Implementation**: Instead of stopping at the first failure, our Product Detail Page tests verify **Price**, **Name**, AND **Buttons** in a single pass.
- **Benefit**: Maximizes defect discovery per test execution cycle.

### 3. 🎭 Dynamic Data Generation (`Faker`)

- **Implementation**: The Contact Form tests use `Faker` to generate unique names and emails for every run.
- **Benefit**: Uncovers edge cases (long strings, special characters) that static data misses.


---

## 📂 Project Structure

```bash
├── pages/                  # 📍 Page Objects (The "Model")
│   ├── base_page.py        #    - Parent class (Logger, Wrappers, Base URL)
│   ├── home_page.py        #    - Home & Search logic
│   ├── shop_page.py        #    - PLP (Product List Page) logic
│   ├── product_page.py     #    - PDP (Detailed) logic
│   ├── login_page.py       #    - Authentication logic
│   └── contact_page.py     #    - Forms & Validation logic
├── components/             # 🧩 Shared UI Components
│   └── navbar.py           #    - Header/Nav interactions
├── tests/                  # 🧪 The Test Suite
│   ├── conftest.py         #    - Fixtures (Setup, Teardown, Data Loading)
│   ├── test_smoke.py       #    - Critical Health Checks
│   ├── test_shop.py        #    - E2E Shopping Flows (Soft Assertions)
│   ├── test_auth.py        #    - DDT Login Tests
│   └── test_contact.py     #    - Faker Dynamic Tests
├── data/                   # 💾 External Data
│   └── test_data.json      #    - JSON Test Data
└── requirements.txt        # 📦 Dependencies
```

---

## ⚡ Setup & Execution

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
pytest -m smoke      # Health checks
pytest -m integration # Shopping flows
pytest -m auth       # Login/Register
pytest -m contact    # Forms
```

### 📑 Reporting
Generate professional Allure reports:
```bash
pytest --alluredir=reports
allure serve reports
```

---

## 👨‍💻 Author
**Your Name/Agency**  
*Senior QA Automation Engineer*  
*Specializing in Python, Playwright, and Enterprise Frameworks.*
