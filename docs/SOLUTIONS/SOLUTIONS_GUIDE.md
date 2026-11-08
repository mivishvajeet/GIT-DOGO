# Git Dojo: Comprehensive Solutions Manual (Levels 01 – 30)
### Step-by-Step Recovery Procedures, Internal Mechanics & Architectural Takeaways

> **WARNING**: This solutions guide is provided for post-challenge review and interview study. Do not read the solution prior to attempting the level in `./dojo`!

---

## Category A — Git Internals (Levels 01 – 05)

### Level 01: Git Object Database Investigation
- **Target**: Find an unreferenced dangling blob in `.git/objects` and extract the secret token into `RECOVERED_SECRET.txt`.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git fsck --lost-found
  # Output shows: dangling blob <sha>
  git cat-file -p <sha>
  # Shows: NEXUS-CORP-SECRET-99812-TOKEN
  echo "NEXUS-CORP-SECRET-99812-TOKEN" > RECOVERED_SECRET.txt
  ```
- **Takeaway**: Objects written to `.git/objects` exist independently of branch pointers until garbage collected.

---

### Level 02: Detached HEAD Recovery
- **Target**: Recover 2 commits made in detached HEAD state onto branch `feature/recovered-work`.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git reflog
  # Identify the commit SHA of 'test(inventory): add concurrency test' (e.g. HEAD@{1} or sha)
  git checkout -b feature/recovered-work <sha>
  git status
  ```
- **Takeaway**: Detached HEAD commits are never lost as long as they reside in `git reflog`.

---

### Level 03: Reflog Forensic Investigation
- **Target**: Recover tip of `main` after accidental `git reset --hard HEAD~3`, and restore deleted branch `feature/critical-fix`.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git reflog
  # 1. Reset main to tip before the reset
  git reset --hard HEAD@{4} # Or specific commit SHA for 'feat(orders): add bulk order processing'
  # 2. Restore deleted branch pointing to its lost commit
  git branch feature/critical-fix <sha_of_auth_fix>
  ```
- **Takeaway**: `git branch -D` only deletes the pointer file in `.git/refs/heads/`. The commits remain intact in `.git/objects`.

---

### Level 04: Git Index Surgery
- **Target**: Unstage mixed changes; commit only `orders.py`; leave `main.py` unstaged; remove `scratch_test.py`.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git restore --staged nexus_platform/app/main.py
  git restore --staged scratch_test.py
  rm scratch_test.py
  git commit -m "fix(orders): validate stock before reserving"
  ```
- **Takeaway**: `git restore --staged` manipulates the index without mutating the working directory.

---

### Level 05: Advanced Commit Archaeology
- **Target**: Find the commit that introduced the `BUGGED_AUTH` security vulnerability across 40 commits; write SHA to `CULPRIT_COMMIT.txt`.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git log -p -S 'BUGGED_AUTH' nexus_platform/app/services/auth.py
  # Extract the 40-character SHA
  git log -1 --format=%H <commit_hash> > CULPRIT_COMMIT.txt
  ```
- **Takeaway**: The pickaxe (`-S`) detects commits that altered the frequency of a string.

---

## Category B — Branching & History Surgery (Levels 06 – 15)

### Level 06: Multiple Simultaneous Merge Conflicts
- **Target**: Merge `feature/order-discount-engine` into `main`, resolving conflicts across 3 files.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git merge feature/order-discount-engine
  # Open conflicted files: config.py, orders.py
  # Keep both DISCOUNT_MAX_PERCENT and API_V2_PREFIX in config.py
  # Keep both apply_order_discount and validate_order_limits in orders.py
  git add .
  git commit -m "Merge feature/order-discount-engine into main"
  ```

---

### Level 07: Three-Way Merge with Rename/Delete Conflicts
- **Target**: Resolve rename of `config.py` to `settings.py` while integrating changes to `config.py`.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git merge feature/refactor-config
  # Copy CORS_ALLOWED_ORIGINS from config.py into settings.py
  git rm nexus_platform/app/config.py
  git add nexus_platform/app/settings.py
  git commit -m "Merge feature/refactor-config resolving rename conflict"
  ```

---

### Level 08: Stacked PRs Across 5 Dependent Branches
- **Target**: Rebase dependent branches in sequence after base branch was amended.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git checkout pr2-models && git rebase pr1-base
  git checkout pr3-api && git rebase pr2-models
  git checkout pr4-tests && git rebase pr3-api
  git checkout pr5-docs && git rebase pr4-tests
  ```

---

### Level 09: Rebase an Extremely Stale Branch (30 Commits Behind)
- **Target**: Rebase `feature/warehouse-automation` cleanly on top of `main`.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git checkout feature/warehouse-automation
  git rebase main
  ```

---

### Level 10: Interactive Rebase (Squash 40 Commits into 3 Atomic Commits)
- **Target**: Consolidate 40 noisy commits into 3 pristine commits matching exact titles.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git checkout feature/event-pipeline
  git reset --soft main
  git add nexus_platform/app/event_chunk_1*.py
  git commit -m "feat(events): implement event bus architecture"
  git add nexus_platform/app/event_chunk_2*.py nexus_platform/app/event_chunk_3*.py
  git commit -m "feat(events): add event serialization and persistence"
  git add .
  git commit -m "test(events): add comprehensive event pipeline tests"
  ```

---

### Level 11: Surgical History Transplant with `git rebase --onto`
- **Target**: Move 2 production fixes from an experimental branch based on legacy-v1 directly onto main.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  # Identify SHA of 2nd experimental commit: <exp2_sha>
  git checkout -b feature/reporting-fixes feature/experimental-analytics
  git rebase --onto main <exp2_sha> feature/reporting-fixes
  ```

---

### Level 12: Revert a Faulty Merge Commit (`git revert -m 1`)
- **Target**: Revert a broken merge without touching subsequent release commits.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git log --oneline
  # Identify SHA of 'Merge branch feature/payment-v2'
  git revert -m 1 <merge_sha> --no-edit
  ```

---

### Level 13: Resolve Accidental Duplicate Cherry-Pick
- **Target**: Remove duplicate commit on `feature/data-export`.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git checkout feature/data-export
  git rebase -i HEAD~3
  # In editor, delete or change 'pick' to 'drop' for the duplicate commit
  ```

---

### Level 14: Repair Diverged Branches Without Destroying Work
- **Target**: Synchronize diverged branch with remote branch without losing Alice or Bob's work.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git checkout feature/warehouse-v2
  git rebase alice/feature/warehouse-v2
  ```

---

### Level 15: Disaster Recovery: Accidental `git push --force`
- **Target**: Recover Elena's overwritten commits on `feature/auth-sso`.
- **Solution Commands**:
  ```bash
  cd .git_dojo/playground/nexus-platform
  git checkout feature/auth-sso
  git reflog
  # Locate SHA of 'feat(auth): add MFA TOTP authentication'
  git reset --hard <sha>
  ```

---

## Category C — Distributed Teams (Levels 16 – 20)

### Level 16: 10 Developers Editing One Module
- **Solution**: Merge branches `dev/branch-01` through `dev/branch-10` into `main`, keeping all functions in `inventory.py`.

### Level 17: Concurrent PRs on Shared API Contracts
- **Solution**: Merge `pr/frontend-pagination` and `pr/data-analytics`, ensuring `contracts/api-schema.json` is valid JSON with both feature sets.

### Level 18: Conflicting Database Migrations
- **Solution**: Re-link `down_revision` in `004b_add_warehouse_telemetry.py` to point to `004a` instead of `003`.

### Level 19: Mitigating Breaking Changes Merged into Main
- **Solution**: Revert breaking commit or update user service to return both `username` and `user_handle`.

### Level 20: Stale PR After Major Architectural Refactor
- **Solution**: Rebase `feature/bulk-upload` onto main, placing the code in `nexus_platform/app/services/bulk_upload.py`.

---

## Category D — Release Engineering (Levels 21 – 25)

### Level 21: Release Branch Cut & Stabilization
- **Solution**: Branch `release/v1.4.0`, bump `version.txt` to `1.4.0`, update changelog, commit, and create annotated tag `git tag -a v1.4.0 -m "Release v1.4.0"`.

### Level 22: Emergency Production Hotfix & Dual-Merge
- **Solution**: Branch `hotfix/v1.4.1` from `v1.4.0`, apply fix, tag `v1.4.1`, and merge back into `main`.

### Level 23: Backporting Across 3 LTS Branches
- **Solution**: Cherry-pick commit SHA onto `release/v1.2`, `release/v1.3`, and `release/v1.4`.

### Level 24: Recover from Broken Release Tag
- **Solution**: Delete local tag `git tag -d v2.0.0` and recreate pointing to stable commit.

### Level 25: Roll Back Failed Release & Safe Re-Release
- **Solution**: Revert release merge on main, patch deadlock bug in orders.py, bump to `1.6.1`, and tag `v1.6.1`.

---

## Category E — Production Incidents & Final Boss (Levels 26 – 30)

### Level 26: The Catastrophic Merge
- **Solution**: `git revert -m 1 <merge_sha>` to eliminate broken imports while keeping 4 subsequent production patches.

### Level 27: Secret Exposure & History Purge
- **Solution**:
  ```bash
  git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch config/secrets.env' --prune-empty --tag-name-filter cat -- --all
  echo "Credential rotation must occur at secret provider immediately." > docs/INCIDENT_ROTATION.txt
  ```

### Level 28: Dependency Supply-Chain Incident
- **Solution**: Replace loose version wildcards in `nexus_platform/requirements.txt` with exact pins; create `requirements.lock`.

### Level 29: CI/CD Pipeline Failure
- **Solution**: Fix YAML indentation in `.github/workflows/ci.yml`, add `permissions: contents: read`, set test runner to `python3 -m unittest discover -s nexus_platform/tests`.

### Level 30: THE FINAL BOSS — REPOSITORY CATASTROPHE
- **Complete Runbook**:
  1. Inspect `git reflog`: find lost financial ledger commit and cherry-pick onto main.
  2. Fix migrations in `nexus_platform/app/migrations`: make down_revisions linear (`004a` -> `004b` -> `004c`).
  3. Fix broken syntax in `nexus_platform/app/services/orders.py`.
  4. Purge leaked key `AKIA_DISASTER_KEY_8877` from history via `git filter-branch`.
  5. Remove `broken-fake-malicious-pkg` from `requirements.txt`.
  6. Recreate tag `v2.5.0` pointing to clean commit.
  7. Fix YAML syntax in `.github/workflows/ci.yml`.
  8. Run unit test suite: `python3 -m unittest discover -s nexus_platform/tests` (must pass 100%).
  9. Author `INCIDENT_REPORT.md` documenting root causes and resolution.
