# Future Improvements Plan

This document outlines the roadmap for elevating the framework to a "Senior QA Engineer" standard, focusing on scalability, robustness, and maintainability.

## 1. 📊 Data Driven Testing (DDT)
*   **Goal**: Separate Test Logic from Test Data.
*   **Action**: Extract hardcoded strings (emails, passwords, product names) into external JSON/YAML files.
*   **Benefit**: Allows running the same test verification against multiple datasets (e.g., Guest vs User, US vs EU) without code changes.

## 2. 🛡️ Soft Assertions (`pytest-check`)
*   **Goal**: Comprehensive Defect Reporting.
*   **Action**: Implement `pytest-check` to verifying multiple attributes (Price + Name + SKU) before failing the test.
*   **Benefit**: Prevents the "Ping-Pong" effect where fixing one assertion immediately reveals the next one in the same test. Maximizes information per run.

## 3. 🎭 Dynamic Data (Faker)
*   **Goal**: Eliminate "Pesticide Paradox".
*   **Action**: Use `Faker` library to generate random, realistic user data for forms.
*   **Benefit**: Uncovers edge cases (long names, special characters) that static data misses.
