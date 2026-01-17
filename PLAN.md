# PG Original QA Portfolio Plan

## Goal
Build a professional-grade automated testing framework for [pgoriginal.com](https://www.pgoriginal.com/) that demonstrates senior-level QA capabilities to recruiters. The project will emphasize strict adherence to **Page Object Model (POM)**, **SOLID** principles, **Clean Code**, and **DRY** (Don't Repeat Yourself).

## Core Principles
- **Page Object Model (POM)**: strict separation of selectors/actions from assertions.
- **Explicit Waits**: No `time.sleep()`. Use smart waits for stability.
- **Data Driven**: Test data typically extracted to JSON/YAML files.
- **Atomic Tests**: Each test aims to verify one specific behavior.
- **Reporting**: Clear, visual reporting (e.g., Allure).

### ISTQB Fundamentals & Best Practices
- **Testing shows presence of defects**: Our tests aim to find bugs, not just prove correctness.
- **Early Testing**: We implement tests alongside development (Shift Left).
- **Defect Clustering**: We focus heavily on complex areas like "Shopping Cart" and "Checkout" where bugs often congregate.
- **Pesticide Paradox**: We will regularly review and update test cases (e.g., adding Negative Tests) so they remain effective.
- **Context Dependent**: Tests are tailored specifically for an E-commerce context (e.g., emphasis on pricing accuracy).


## Phase 1: Foundation & Architecture
*Goal: Establish a solid, scalable codebase.*
1.  **Refine Project Structure**:
    - Ensure logical separation: `pages/`, `tests/`, `components/`, `utils/`, `data/`.
    - Setup `conftest.py` for robust fixtures (browser setup, teardown, base URL).
2.  **Base Page Implementation**:
    - Create `BasePage` class with common wrappers for Playwright/Selenium methods (click, type, wait_for_element).
    - Implement error handling logging within base actions.
3.  **Linting & Formatting Setup**:
    - Configure `black`, `flake8`, or `pylint` to enforce code style.

## Phase 2: Smoke & Navigation (Read-Only Tests)
*Goal: Verify the generic stability of the site.*
1.  **Home Page Tests**:
    - Verify Hero banner, Feature sections load.
    - Check Header/Footer link integrity.
2.  **Product Navigation**:
    - Verify navigation to "Shop" (Productos).
    - Verify Category filtering.
    - Verify Search functionality (Modal).

## Phase 3: Core Business Logic (The "Money" Flow)
*Goal: Ensure users can buy products.*
1.  **Product Detail Page (PDP)**:
    - Verify Price display.
    - Test Variant Selection (Size/Color).
    - Test "Add to Cart".
2.  **Cart & Checkout Interaction**:
    - Verify Cart Modal/Page updates correctly.
    - Test "Proceed to Checkout" (up to the point of external redirect or payment form).
3.  **End-to-End Cart Flow**:
    - Search -> Select -> Add to Cart -> Change Qty -> Verify Total.

## Phase 4: User Management & Forms
*Goal: Verify user retention features.*
1.  **Authentication**:
    - Registration (Success & Failure).
    - Login (Success & Failure).
    - Forgot Password flow.
2.  **Contact Forms**:
    - Submit "Contact Us" form.
    - Validation checks on empty fields.

## Phase 5: Professional Polish (Interview Ready)
*Goal: Add the "Wow" factor.*
1.  **CI/CD Pipeline**:
    - Create `.github/workflows/test_run.yml` to run tests on push.
2.  **Reporting**:
    - Configure Allure or HTML reports to generate artifacts on failure.
    - Capture screenshots/video on failure.
3.  **Documentation**:
    - Comprehensive `README.md` explaining *architectural decisions*.
    - "How to Run" instructions.

## Recommended Tech Stack (Python)
- **Framework**: Playwright (Recommended for speed/reliability) or Sellerium (if legacy support needed). *Assuming Playwright based on current trends, but can adapt to Selenium.*
- **Runner**: Pytest.
- **Reporting**: Allure-pytest.

## Next Steps
1. Review this plan.
2. Confirm the preferred tool (Playwright vs Selenium).
3. Begin Phase 1.
