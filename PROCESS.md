# Engineering Process & QA Methodology

This document outlines the strategic decisions, methodology, and problem-solving approaches applied during the development of this Test Automation Framework. It is intended to provide insight into the "Senior QA" mindset behind the code.

## 1. Architectural Strategy: Scalability & Maintenance
**Goal**: Build a framework that scales with the application, not just a collection of scripts.

*   **Page Object Model (POM)**: We strictly separated Page Logic (selectors, interactions) from Test Logic (assertions, flows). This ensures that if a localized UI change occurs (e.g., a button ID changes), we only update one file in `pages/`, and all tests accessing that page are automatically fixed.
*   **SOLID Principles**:
    *   *Single Responsibility*: Each Page Object handles only its page. `BasePage` handles only driver interactions.
    *   *DRY (Don't Repeat Yourself)*: Common actions like `navigate` and `wait_for_element` were abstracted to `BasePage` to prevent code duplication.

## 2. Iterative & Risk-Based Delivery
**Goal**: Deliver value immediately by prioritizing high-risk/high-value flows.

*   **Shift Left / MVP**: We did not wait for "100% coverage" to start running tests.
*   **Prioritization**:
    1.  **Core Business Value**: We started with the "Shopping Cart" flow (`test_shop.py`). If users can't buy, nothing else matters.
    2.  **Smoke Tests**: Created fast feedback loops (`test_smoke.py`) for critical UI elements.
    3.  **Edge Cases**: Addressed complex scenarios like Authentication only after core value was secured.

## 3. Real-World Constraint Handling (Context-Driven Testing)
**Goal**: Demonstrate adaptability when facing external blockers (Anti-Bot Protection).

*   **The Challenge**: The Application Under Test (AUT) implements proactive Anti-Bot protection, which blocked standard automated login attempts (returning 403 or throttling timeouts).
*   **The Pivot**: Instead of writing brittle workarounds or skipping the test, we treated this as a **Constraint**.
*   **The Solution**: We implemented **Self-Documenting Failures**.
    *   We wrapped the login interaction in a robust error handler.
    *   Upon timeout/block, the framework dynamically injects a visible **"AUTOMATION DETECTED"** banner into the browser DOM.
    *   This ensures the resulting proof (screenshot/video) explicitly communicates *why* the test failed, distinguishing a "Test Defect" from an "Environment Constraint."

## 4. Observability & Reporting
**Goal**: Reduce "Time to Resolution" (MTTR) for developers.

*   **Visual Evidence**: Configured `pytest` hooks to capture Screenshots and Video *only* on failure.
*   **Artifact Organization**: Proofs are automatically sorted into a structured `proofs/` directory.
*   **Result**: A developer doesn't need to re-run the test to understand a bug; the artifact provides the full context immediately.

---
*This project represents not just technical proficiency with Playwright/Python, but a mature approach to Software Quality Assurance.*
