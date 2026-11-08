# System Architecture: Git Dojo & Nexus Inventory Platform

## 1. Executive Overview
**Git Dojo** is an advanced, offline-first engineering simulation laboratory designed to train developers, Tech Leads, Release Managers, and Site Reliability Engineers on complex Git workflows, GitHub administration, CI/CD pipelines, and high-severity repository incidents.

---

## 2. Component Architecture

```
+----------------------------------------------------------------------------+
|                          GIT DOJO RUNTIME ARCHITECTURE                     |
+----------------------------------------------------------------------------+
|                                                                            |
|   Interactive CLI Controller (./dojo)                                      |
|      ├── ANSI Dashboard & Menu Engine                                      |
|      ├── Challenge Dispatcher (Levels 01 - 30)                             |
|      ├── Forensic Health Inspector                                         |
|      ├── Broken Repository Museum                                          |
|      └── State & Progress Persistence (.git_dojo/state.json)               |
|                                                                            |
|   Disposable Playground Sandbox (.git_dojo/playground/nexus-platform)       |
|      ├── Safe Subprocess Git Client (RepoManager)                          |
|      ├── Isolated from host files, zero risk of external data destruction |
|      └── Automated Verification & Teardown Runners                         |
|                                                                            |
|   Nexus Inventory Platform (Reference Enterprise SUT)                      |
|      ├── 8 Interdependent Domain Services                                 |
|      ├── Alembic Migration Runner                                          |
|      ├── REST API Dispatcher                                               |
|      └── Integration Test Suite (unittest / pytest)                        |
|                                                                            |
|   Nexus Engineering Organization Model                                     |
|      ├── 15 Specialized Engineering Teams                                 |
|      ├── 100 Deterministic Fictional Developer Identities                  |
|      └── Commit Behavioral Distribution Models                             |
|                                                                            |
+----------------------------------------------------------------------------+
```

---

## 3. The Nexus Inventory Platform (System Under Test)

The application simulates a realistic distributed inventory and supply-chain platform. It avoids trivial mockups by enforcing cross-module functional dependencies:

1. **Authentication (`auth.py`)**: HMAC token creation and constant-time verification.
2. **User Management (`users.py`)**: Role-based customer and staff identities.
3. **Product Catalogue (`products.py`)**: SKU management, active status flags, pricing.
4. **Warehouse Management (`warehouse.py`)**: Storage facilities, capacities, zones.
5. **Inventory Allocation (`inventory.py`)**: Stock tracking, atomic reservations, threshold audits.
6. **Order Processing (`orders.py`)**: Transactional checkout coordinating Users, Products, Warehouses, and Inventory reservations.
7. **Reporting (`reporting.py`)**: Aggregated inventory valuation and gross revenue calculations.
8. **Event Processing (`events.py`)**: Audit logging for all domain state transitions.

---

## 4. Safety & Sandbox Invariants

To adhere to enterprise safety standards:
1. **Repository Isolation**: All scenario operations are strictly confined within `.git_dojo/playground/`. Any operation attempting to modify paths outside this directory triggers a security assertion error.
2. **Zero External Network Requirements**: All 30 levels and tests execute completely offline without relying on remote GitHub repositories, third-party API keys, or active network connections.
3. **No Real Secrets**: All security incidents use synthetic dummy keys (e.g., `AKIA_NEXUS_LEAKED_KEY_9921_SECRET`).
4. **Deterministic Reproducibility**: Random seed (`DETERMINISTIC_SEED = 1337`) ensures identical developer names, commit logs, and failure states across all runs.

