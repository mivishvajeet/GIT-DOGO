# 60-Day Master Roadmap: Git Internals, Release Engineering & Production SRE
### From Senior Developer to Staff / Principal DevOps & Release Engineer

This structured 60-day curriculum combines deliberate hands-on practice in **Git Dojo** with architectural deep dives, real-world case studies, and senior staff interview preparation.

---

## Phase 1: Days 01–15 — The Physics of Git (Internals & Storage)

### Objectives:
Master the object database, Directed Acyclic Graph (DAG) mechanics, tree traversal, content-addressable storage, and reflog forensics.

- **Day 01–03: The Object Database Deep Dive**
  - Read: Linus Torvalds' original Git architecture notes; Pro Git Chapter 10 (Git Internals).
  - Dojo Lab: **Level 01 (Git Object Database Investigation)**.
  - Hands-on: Manually construct a blob, tree, and commit using `git hash-object`, `git mktree`, and `git commit-tree` without running `git commit`.
- **Day 04–06: The Index, Detached HEAD & Pointers**
  - Dojo Lab: **Level 02 (Detached HEAD Recovery)** & **Level 04 (Git Index Surgery)**.
  - Hands-on: Deconstruct `.git/index` binary format. Discard staged changes safely while preserving unstaged work.
- **Day 07–09: Reflog & Garbage Collection Forensics**
  - Dojo Lab: **Level 03 (Reflog Forensic Investigation)**.
  - Theory: `git gc`, `--prune=now`, loose objects vs. packfiles (`.pack` and `.idx`), reachability bitmaps.
- **Day 10–12: Commit Archaeology & Debugging Regressions**
  - Dojo Lab: **Level 05 (Advanced Commit Archaeology)**.
  - Hands-on: Master `git log -S` (pickaxe), `git log -G` (regex diff), `git log -L` (line-history trace), `git bisect run <test_script.sh>`.
- **Day 13–15: Phase 1 Review & Museum Inspection**
  - Dojo Lab: **Broken Repository Museum (Exhibits 01 & 03)**.
  - Interview Prep: Practice explaining packfile delta compression, loose object layout, and SHA hash collisions.

---

## Phase 2: Days 16–30 — History Surgery & Branching Topology

### Objectives:
Master 3-way merges, merge base algorithms, rename detection, stacked pull requests, interactive rebasing, and emergency force-push recovery.

- **Day 16–18: Merge Algorithms & Conflict Triage**
  - Dojo Lab: **Level 06 (Simultaneous Merge Conflicts)** & **Level 07 (Rename/Delete Conflicts)**.
  - Theory: Recursive vs. ORT merge strategies, `merge-base --octopus`, rename threshold tuning (`-X rename-threshold`).
- **Day 19–21: Stacked PRs & Surgical Transplants**
  - Dojo Lab: **Level 08 (Stacked Pull Requests)** & **Level 11 (Rebase --onto)**.
  - Hands-on: Maintain 5 dependent review branches; use `git rebase --onto` to replay diffs across shifting baselines.
- **Day 22–24: Large-Scale Interactive Rebasing**
  - Dojo Lab: **Level 09 (Extremely Stale Rebase)** & **Level 10 (Interactive Rebase across 40 Commits)**.
  - Practice: Squashing, splitting, reordering commits, and resolving mid-rebase conflicts without aborting.
- **Day 25–27: Revert Invariants & Diverged History**
  - Dojo Lab: **Level 12 (Reverting Merge Commits)** & **Level 14 (Diverged Branch Repair)**.
  - Deep Dive: Why `git revert -m 1` requires reverting the revert to re-merge in the future.
- **Day 28–30: Disaster Recovery: Force-Push Forensics**
  - Dojo Lab: **Level 13 (Duplicate Cherry-Picks)** & **Level 15 (Accidental Force-Push Recovery)**.
  - Practice: Recovering overwritten remote branches via local reflogs; setting up `--force-with-lease` aliases.

---

## Phase 3: Days 31–45 — Distributed Teams & Enterprise Governance

### Objectives:
Manage 100+ developer organizations, concurrent module edits, API schema versioning, database migration DAGs, and GitHub enterprise governance.

- **Day 31–33: Multi-Developer High Concurrency**
  - Dojo Lab: **Level 16 (10 Concurrent Developers in One Module)**.
  - Hands-on: Git worktrees (`git worktree add / prune`) for multi-branch concurrent development without multiple clones.
- **Day 34–36: API Schema Integration & Migration DAGs**
  - Dojo Lab: **Level 17 (Shared API Contracts)** & **Level 18 (Conflicting Database Migrations)**.
  - Architectural Practice: Linearizing Alembic migration revisions; semantic JSON/YAML merge protocols.
- **Day 37–39: Mitigating Breaking Changes & Stale PRs**
  - Dojo Lab: **Level 19 (Breaking Change Merged into Main)** & **Level 20 (Rescuing Stale PRs After Monolith Refactor)**.
  - Theory: Expand-and-contract pattern; evolutionary database design.
- **Day 40–42: Enterprise GitHub Governance & Policies**
  - Reading: `docs/GITHUB_ADMIN_GUIDE.md`.
  - Architecture: Rulesets vs. branch protection, CODEOWNERS hierarchies, signed commits, GitHub audit log streaming.
- **Day 43–45: Merge Queues & High-Throughput CI**
  - Design: Implementing GitHub Merge Queues to prevent main breakage under 100 daily merges.

---

## Phase 4: Days 46–60 — Release Engineering & Production Incidents (Final Boss)

### Objectives:
Master semantic versioning release trains, maintenance backports, secret sanitization, supply-chain triage, CI pipeline restoration, and repository catastrophe resolution.

- **Day 46–48: Release Trains & Dual-Merge Hotfixes**
  - Dojo Lab: **Level 21 (Release Cut & Stabilization)** & **Level 22 (Emergency Hotfix & Dual-Merge)**.
  - Practice: Cutting release branches, semantic version tagging, changelog automation, dual-merging back to trunk.
- **Day 49–51: Multi-Version LTS Backporting & Rollbacks**
  - Dojo Lab: **Level 23 (Cherry-Pick Across 3 Releases)**, **Level 24 (Broken Release Tag)** & **Level 25 (Failed Release Rollback)**.
  - Practice: Maintaining `release/v1.2`, `v1.3`, `v1.4` LTS branches simultaneously.
- **Day 52–54: Production Incidents & Security Scrubs**
  - Dojo Lab: **Level 26 (The Catastrophic Merge)** & **Level 27 (Secret Exposure & History Purge)**.
  - Hands-on: Rewriting history with `git filter-branch` / `git-filter-repo`; credential rotation runbooks.
- **Day 55–57: Supply-Chain & CI/CD Pipeline Restoration**
  - Dojo Lab: **Level 28 (Dependency Vulnerability Triage)** & **Level 29 (CI/CD Pipeline Failure)**.
  - Practice: Pinning dependencies, generating SHA lockfiles, fixing broken GitHub Actions workflows and permissions.
- **Day 58–60: THE FINAL BOSS: REPOSITORY CATASTROPHE**
  - Dojo Lab: **Level 30 (THE FINAL BOSS — Complete Repository Disaster)**.
  - Capstone: 20 open PRs, 3 conflicting migrations, 2 bad merges, leaked secret, broken dependency, corrupted tag, lost financial commit.
  - Output: Full repository restoration, 100% passing tests, and published `INCIDENT_REPORT.md`.
