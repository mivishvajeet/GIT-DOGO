# GIT DOJO — ELITE ENGINEERING SIMULATOR
### Advanced Git, GitHub, DevOps, CI/CD, Release Engineering & Production Incident Laboratory

Welcome to **Git Dojo**, a simulation environment designed to develop Staff Software Engineers, Principal DevOps Engineers, Release Managers, and Site Reliability Engineers capable of mastering Git internals and leading incident response across high-throughput engineering organizations.

---

## Quickstart

Start the interactive terminal CLI:
```bash
./dojo
```

---

## 1. What is Git Dojo?

Most developers know basic Git commands (`git add`, `git commit`, `git push`), but freeze when confronted with:
- Multiple simultaneous merge conflicts across stacked PRs.
- Stale branches diverged by dozens of commits after massive directory reorganizations.
- A corrupted release tag triggering failed production deployments.
- Accidental `git push --force` destroying days of team commits.
- Conflicting database migration DAGs in Alembic/Django.
- Committed API tokens and secrets needing full history purge.
- The **Catastrophic Merge** where broken code is buried under legitimate production commits.

**Git Dojo creates a fully functioning, realistic engineering organization on your local Mac with zero external risk.**

---

## 2. The Nexus Engineering Organization

Simulates a high-velocity tech enterprise:
- **15 Engineering Teams**: Platform, Backend, Frontend, Data, DevOps, SRE, Security, QA, Infrastructure, Database, API, Observability, Release Engineering, Developer Experience, Architecture.
- **100 Fictional Developer Identities**: Deterministically generated with specific roles, emails (`@nexus.internal`), code ownership areas, and realistic human behavioral quirks (clean commits, monolithic commits, forgot to pull before push, force-push prone, bug introducers, blind mergers, breaking API modifiers).

---

## 3. The Nexus Inventory Platform

You are responsible for keeping the **Nexus Inventory Platform** repository healthy.
This is an interdependent, multi-service platform:
- **Inventory Service**: Stock allocation, reservation locks, threshold audits.
- **Order Service**: Transactional coordinator validating users, products, warehouses, and reserving inventory.
- **Product Catalogue**: SKU definitions, pricing, category rules.
- **Warehouse Management**: Facilities, zones, capacity validation.
- **User & Auth Management**: HMAC token verification and role-based permissions.
- **Reporting Engine**: Real-time valuation and gross sales metrics.
- **Event Audit Stream**: Structured audit logs for domain events.
- **Alembic Migrations**: Schema evolution with DAG tracking.

---

## 4. 30 Advanced Engineering Challenges

| Category | Level Range | Focus |
|---|---|---|
| **Category A: Git Internals** | Levels 01 – 05 | Object database, dangling blobs, detached HEAD recovery, reflog forensics, index surgery, commit archaeology (`git log -S`, `blame`, `bisect`). |
| **Category B: Branching Surgery** | Levels 06 – 15 | 3-way simultaneous conflicts, rename/delete conflicts, stacked PR chains, stale 30-commit rebases, interactive 40-commit squash, `rebase --onto`, reverting merge commits (`-m 1`), diverged repair, force-push recovery. |
| **Category C: Distributed Teams** | Levels 16 – 20 | 10 concurrent developers in one module, shared API JSON contracts, conflicting database migrations DAGs, breaking change mainline mitigation, stale PR architecture rescue. |
| **Category D: Release Engineering** | Levels 21 – 25 | Release branch cut (`release/v1.4`), emergency production hotfix & dual-merge, LTS cherry-picking across 3 versions, corrupted release tag recovery, release rollback & re-release. |
| **Category E: Production Incidents** | Levels 26 – 30 | Catastrophic merge recovery, secret exposure history rewrite (`git filter-branch`), dependency supply-chain triage, CI/CD pipeline failure diagnostics, and **Level 30: THE FINAL BOSS**. |

---

## 5. Built-in Tooling & Labs

- **Interactive CLI (`./dojo`)**: Terminal dashboard tracking active levels, attempts, recovery times, and verification results in `.git_dojo/state.json`.
- **Git Forensics Toolkit**: Read-only repository health auditor detecting detached HEADs, uncommitted changes, active merge conflicts, dangling commits, large files, and leaked secrets.
- **Broken Repository Museum**: Dissect classic infamous real-world git disasters (Detached Ghost, Merge Octo-Monster, Phantom Tag, etc.).
- **Automated Verification Engine**: Evaluates your solutions against automated test suites and behavioral invariants with zero fake grading.

---

## 6. Safety & Sandbox Invariants

- **Isolated Sandbox**: All challenges run exclusively in `.git_dojo/playground/nexus-platform/`.
- **Never Touches Your Host Files**: Does not touch external directories or existing projects.
- **Zero Real Credentials**: All secrets and tokens are purely synthetic dummy values.
- **Zero External Dependencies**: Operates 100% offline using standard Python 3.

---

## 7. Documentation & Curriculum Sitemap

- [60-Day Learning Roadmap](docs/60_DAY_ROADMAP.md)
- [GitHub Enterprise Administration & Governance Guide](docs/GITHUB_ADMIN_GUIDE.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Solutions Manual (Levels 01–30)](docs/SOLUTIONS/SOLUTIONS_GUIDE.md)

