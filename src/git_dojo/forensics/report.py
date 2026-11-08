"""Terminal-based Forensic Health Report Renderer."""

from .inspector import ForensicReport


class ForensicReportRenderer:
    """Formats forensic inspection results into clean ANSI terminal dashboards."""

    @staticmethod
    def render(report: ForensicReport) -> str:
        lines = []
        border = "=" * 70
        divider = "-" * 70

        status_color = "\033[92m" if report.health_status == "EXCELLENT" else (
            "\033[93m" if report.health_status in ["DEGRADED", "WARNING"] else "\033[91m"
        )
        reset = "\033[0m"
        bold = "\033[1m"
        cyan = "\033[96m"

        lines.append(f"{cyan}{border}{reset}")
        lines.append(f"{bold}           GIT DOJO FORENSICS: REPOSITORY HEALTH REPORT{reset}")
        lines.append(f"{cyan}{border}{reset}")
        lines.append(f"Target Repository : {report.repo_path}")
        lines.append(f"Health Status     : {status_color}{bold}{report.health_status} ({report.health_score}/100){reset}")
        lines.append(f"Current Ref       : {'DETACHED HEAD' if report.is_detached else report.current_branch} (HEAD: {report.head_commit[:10] if report.head_commit else 'None'})")
        lines.append(f"{divider}")

        # Working Tree Section
        lines.append(f"{bold}[1] WORKING TREE & INDEX INTEGRITY{reset}")
        lines.append(f"  Uncommitted changes : {report.uncommitted_changes_count}")
        lines.append(f"  Untracked files     : {report.untracked_files_count}")
        lines.append(f"  Active conflicts    : {'YES (' + ', '.join(report.conflicted_files) + ')' if report.has_merge_conflicts else 'None (Clean)'}")
        lines.append(f"{divider}")

        # Branches & Tags
        lines.append(f"{bold}[2] BRANCH & RELEASE INVENTORY{reset}")
        lines.append(f"  Local branches ({len(report.local_branches)}): {', '.join(report.local_branches[:6])}{'...' if len(report.local_branches) > 6 else ''}")
        lines.append(f"  Release tags ({len(report.tags)})  : {', '.join(report.tags[:6])}{'...' if len(report.tags) > 6 else ''}")
        lines.append(f"{divider}")

        # Forensic Audit
        lines.append(f"{bold}[3] FORENSIC ANOMALY AUDIT{reset}")
        lines.append(f"  Dangling/Lost commits : {len(report.dangling_commits)}")
        if report.dangling_commits:
            lines.append(f"    Sample: {', '.join(report.dangling_commits[:4])}")
        
        lines.append(f"  Large files (>1MB)    : {len(report.large_files)}")
        for lf in report.large_files[:3]:
            lines.append(f"    - {lf['path']} ({lf['size_mb']} MB)")

        lines.append(f"  Security / Secrets    : {'CLEAN' if not report.suspicious_findings else '\033[91mALERT (' + str(len(report.suspicious_findings)) + ' detected)\033[0m'}")
        for sec in report.suspicious_findings[:3]:
            lines.append(f"    \033[91m! {sec}\033[0m")
        lines.append(f"{divider}")

        # Contributor Distribution
        lines.append(f"{bold}[4] CONTRIBUTOR ACTIVITY DYNAMICS{reset}")
        for author, count in list(report.contributor_activity.items())[:5]:
            lines.append(f"  {author:<35} : {count} commits")
        lines.append(f"{cyan}{border}{reset}")

        return "\n".join(lines)
