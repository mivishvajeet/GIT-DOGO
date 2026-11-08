"""15 Teams of NEXUS ENGINEERING."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Team:
    id: str
    name: str
    description: str
    primary_ownership: List[str]


TEAMS: List[Team] = [
    Team(
        id="platform",
        name="Platform Engineering",
        description="Core developer platform, base containers, service templates, shared libraries.",
        primary_ownership=["nexus_platform/app/config.py", "Dockerfile", "docker-compose.yml"],
    ),
    Team(
        id="backend",
        name="Backend Engineering",
        description="Core business domain services, business workflows, transactions.",
        primary_ownership=["nexus_platform/app/services/inventory.py", "nexus_platform/app/services/orders.py"],
    ),
    Team(
        id="frontend",
        name="Frontend Engineering",
        description="Client dashboards, web portals, consumer-facing UI contracts.",
        primary_ownership=["frontend/", "contracts/api-schema.json"],
    ),
    Team(
        id="data",
        name="Data Engineering",
        description="Data ingestion pipelines, reporting aggregations, ETL pipelines.",
        primary_ownership=["nexus_platform/app/services/reporting.py", "nexus_platform/app/api/reporting.py"],
    ),
    Team(
        id="devops",
        name="DevOps",
        description="CI/CD pipelines, container registries, build caches, environment parity.",
        primary_ownership=[".github/workflows/ci.yml", ".github/workflows/release.yml"],
    ),
    Team(
        id="sre",
        name="SRE",
        description="Site reliability, incident command, SLO/SLA management, automated rollbacks.",
        primary_ownership=["ops/runbooks/", "ops/alerts.yaml"],
    ),
    Team(
        id="security",
        name="Security Engineering",
        description="AppSec, secrets management, static analysis, dependency vulnerability triage.",
        primary_ownership=[".github/dependabot.yml", "security/audit.py", ".secrets.baseline"],
    ),
    Team(
        id="qa",
        name="QA Automation",
        description="End-to-end testing, integration test suites, regression test frameworks.",
        primary_ownership=["nexus_platform/tests/", "tests/e2e/"],
    ),
    Team(
        id="infra",
        name="Infrastructure",
        description="Cloud provider provisioning, networking, Kubernetes manifests, terraform.",
        primary_ownership=["infra/terraform/", "infra/k8s/"],
    ),
    Team(
        id="database",
        name="Database Engineering",
        description="Relational database schemas, migrations, index optimization, query tuning.",
        primary_ownership=["nexus_platform/app/migrations/", "nexus_platform/app/models/"],
    ),
    Team(
        id="api",
        name="API Engineering",
        description="RESTful contracts, OpenAPI schemas, API gateway, authentication middleware.",
        primary_ownership=["nexus_platform/app/api/", "nexus_platform/app/schemas/"],
    ),
    Team(
        id="observability",
        name="Observability",
        description="Telemetry, Prometheus metrics, OpenTelemetry traces, structured log standards.",
        primary_ownership=["nexus_platform/app/logging_config.py", "ops/monitoring/"],
    ),
    Team(
        id="release",
        name="Release Engineering",
        description="Release trains, semver tagging, changelogs, hotfix cherry-picking, deployment gates.",
        primary_ownership=["RELEASE.md", "CHANGELOG.md", "version.txt"],
    ),
    Team(
        id="dx",
        name="Developer Experience",
        description="Local dev environment, pre-commit hooks, linters, developer tooling.",
        primary_ownership=[".pre-commit-config.yaml", "Makefile", "scripts/dev_setup.sh"],
    ),
    Team(
        id="architecture",
        name="Architecture",
        description="Cross-cutting architectural standards, technical RFCs, breaking change reviews.",
        primary_ownership=["docs/architecture/", "docs/adr/"],
    ),
]

TEAMS_BY_ID = {team.id: team for team in TEAMS}
