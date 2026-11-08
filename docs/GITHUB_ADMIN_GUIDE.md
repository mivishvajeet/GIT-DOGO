# Nexus Engineering: GitHub Enterprise & Organization Administration Guide
### Advanced Repository Governance, Branch Rulesets, CI/CD Security, and Release Gates

This document serves as the architectural reference for Phase 2 GitHub integration for **Nexus Engineering**.

---

## 1. Branch Protection Rules vs. Repository Rulesets

### Legacy Branch Protection vs. Modern Rulesets (2024+)
| Capability | Branch Protection Rules | Repository Rulesets (Modern) |
|---|---|---|
| Scope | Single branch pattern per rule | Multiple targets, tags, branches, and regex combinations |
| Inheritance | Repository level only | Organization-wide, Enterprise-wide, or Repository-level |
| Bypass Control | Limited (Admin override boolean) | Granular bypass list (specific Roles, Teams, or GitHub Apps) |
| Evaluation Mode | Active only | **Active** or **Evaluate Mode** (logs violations without blocking) |
| Tag Protection | Basic tag protection | Full semantic tag lifecycle rules (prevent force-push/deletion) |

### Recommended Ruleset Configuration for `main`
```json
{
  "name": "Production Mainline Governance",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main", "refs/heads/release/*"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 2,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "lint-and-typecheck" },
          { "context": "unit-and-integration-tests" },
          { "context": "security-dependency-scan" },
          { "context": "docker-build-validation" }
        ]
      }
    },
    { "type": "required_signatures" }
  ]
}
```

---

## 2. CODEOWNERS Architecture for Nexus Engineering

Store at `.github/CODEOWNERS`:
```ini
# Global repository fallback owners
* @nexus-engineering/architecture-leads

# Core Platform Infrastructure & Containers
Dockerfile @nexus-engineering/platform
docker-compose.yml @nexus-engineering/platform
.github/workflows/ @nexus-engineering/devops

# Database Models & Alembic Migrations
nexus_platform/app/models/ @nexus-engineering/database
nexus_platform/app/migrations/ @nexus-engineering/database

# Core Business Domain Services
nexus_platform/app/services/inventory.py @nexus-engineering/backend
nexus_platform/app/services/orders.py @nexus-engineering/backend
nexus_platform/app/services/auth.py @nexus-engineering/security @nexus-engineering/backend

# API Schemas & REST Contracts
nexus_platform/app/api/ @nexus-engineering/api-engineering
contracts/ @nexus-engineering/api-engineering @nexus-engineering/frontend

# Security & Secret Scanning Baseline
.secrets.baseline @nexus-engineering/security
security/ @nexus-engineering/security
.github/dependabot.yml @nexus-engineering/security

# Release & Changelogs
RELEASE.md @nexus-engineering/release-engineering
CHANGELOG.md @nexus-engineering/release-engineering
version.txt @nexus-engineering/release-engineering
```

---

## 3. GitHub Merge Queues & Merge Policies

### Merge Queue Mechanics
In high-velocity organizations (like Nexus Engineering with 100 concurrent developers), standard PR validation causes merge races: PR A passes CI, PR B passes CI, PR A merges, but when PR B merges, the combination breaks `main`.

A **Merge Queue** solves this by:
1. Placing approved PRs into an automated FIFO queue.
2. Speculatively combining PRs into temporary `gh-readonly-queue/main/pr-...` branches.
3. Running required CI checks against the speculative merge.
4. Fast-forwarding `main` atomically only when the test suite passes.

### Merge Methods Comparison
- **Merge Commit (`--no-ff`)**: Preserves the complete branch shape and dual parents. Ideal for auditing release branches.
- **Squash and Merge**: Collapses all PR commits into a single atomic commit on `main`. Best for trunk-based development with micro-features.
- **Rebase and Merge**: Replays PR commits individually onto `main`. Preserves commit granularity but requires strict commit hygiene (interactive rebase before merge).

---

## 4. GitHub Environments, Secrets & Deployment Protection Rules

### Environments: `staging` vs. `production`
- **Staging**:
  - Auto-deployed on PR merge to `main`.
  - Open deployment permissions for continuous integration verification.
- **Production**:
  - Gated by **Required Reviewers** (Release Engineering or SRE on-call).
  - Protected by **Wait Timers** (e.g. 15-minute soak test period in staging).
  - Restricted to specific branches (`refs/heads/main` or `refs/heads/release/*`).

### OIDC (OpenID Connect) Cloud Federation
**Never store long-lived cloud credentials in GitHub Secrets.** Use OpenID Connect (OIDC) to authenticate GitHub Actions directly with AWS IAM or Google Cloud Workload Identity Federation:
```yaml
permissions:
  id-token: write # Required for requesting the JWT
  contents: read

steps:
  - name: Authenticate to Cloud via OIDC
    uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: 'projects/123456/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
      service_account: 'github-deployer@nexus-prod.iam.gserviceaccount.com'
```

---

## 5. Security Scanning, Dependabot & Push Protection

1. **Secret Scanning & Push Protection**:
   - Blocks developers from running `git push` if an API token, private key, or cloud credential is found in any committed file or commit message.
   - Operates client-side and server-side before the ref is updated.
2. **Dependabot Version & Security Updates**:
   - Configured via `.github/dependabot.yml`.
   - Automated pull requests for CVE vulnerabilities and quarterly minor updates.
3. **Audit Log Forensics**:
   - Enterprise audit log streams events via REST/GraphQL/Splunk/S3.
   - Monitors: `repo.create`, `org.add_member`, `protected_branch.destroy`, `secret_scanning.bypass`.

---

## 6. GitHub Plan & Visibility Matrix

| Feature | Public Repositories | Private (GitHub Free) | Private (GitHub Team) | Private (GitHub Enterprise) |
|---|---|---|---|---|
| Branch Protection Rules | Yes | No | Yes | Yes |
| Repository Rulesets | Yes | No | Yes | Yes |
| CODEOWNERS Required Reviews | Yes | No | No | **Yes** |
| Merge Queues | Yes | No | No | **Yes** |
| Deployment Protection Rules | Yes | No | No | **Yes** |
| Secret Scanning Push Protection | Yes | No | Add-on (GHAS) | **Yes (GHAS)** |
| SAML SSO / Audit Log Streaming | N/A | No | No | **Yes** |
