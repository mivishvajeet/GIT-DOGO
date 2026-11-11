"""Interactive terminal interface and menu system for Git Dojo."""

import sys
import time
from pathlib import Path
from typing import List, Optional

from ..challenges import get_all_challenges, get_challenge, ChallengeCategory
from ..core.config import config
from ..core.state import state_manager
from ..core.repo_manager import repo_manager
from ..organization.teams import TEAMS
from ..organization.developers import DEVELOPERS
from ..forensics.inspector import ForensicInspector
from ..forensics.report import ForensicReportRenderer
from ..museum.exhibits import EXHIBITS, MuseumManager


class DojoCli:
    """Master interactive terminal controller for Git Dojo."""

    # ANSI Colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"

    def print_banner(self) -> None:
        print(f"\n{self.CYAN}{'=' * 75}{self.RESET}")
        print(f"{self.BOLD}{self.MAGENTA}          GIT DOJO — ELITE ENGINEERING SIMULATION LABORATORY{self.RESET}")
        print(f"{self.CYAN}    Advanced Git, GitHub, DevOps, CI/CD, Release Engineering & SRE Lab{self.RESET}")
        print(f"{self.CYAN}{'=' * 75}{self.RESET}\n")

    def run(self) -> None:
        config.ensure_directories()
        while True:
            self.print_banner()
            total_levels = len(get_all_challenges())
            completed_count = state_manager.total_completed
            pct = round((completed_count / total_levels) * 100) if total_levels else 0
            active = state_manager.active_level or "None"

            print(f"  {self.BOLD}Active Scenario  :{self.RESET} {self.YELLOW}{active}{self.RESET}")
            print(f"  {self.BOLD}Progress         :{self.RESET} {self.GREEN}{completed_count}/{total_levels} ({pct}% Completed){self.RESET}")
            print(f"  {self.BOLD}Playground Path  :{self.RESET} {config.playground_repo}\n")
            print(f"{self.CYAN}{'-' * 75}{self.RESET}")
            print(f" {self.BOLD}0.{self.RESET}  {self.GREEN}{self.BOLD}🌐 Launch Nexus Cockpit Web Dashboard (http://localhost:8080){self.RESET}")
            print(f" {self.BOLD}1.{self.RESET}  Git Internals Lab (Levels 01 - 05)")
            print(f" {self.BOLD}2.{self.RESET}  Branching & Rebase Surgery Lab (Levels 06 - 15)")
            print(f" {self.BOLD}3.{self.RESET}  Distributed Team Collaboration Lab (Levels 16 - 20)")
            print(f" {self.BOLD}4.{self.RESET}  Release Engineering Lab (Levels 21 - 25)")
            print(f" {self.BOLD}5.{self.RESET}  Production Incident Lab (Levels 26 - 29)")
            print(f" {self.BOLD}6.{self.RESET}  Broken Repository Museum")
            print(f" {self.BOLD}7.{self.RESET}  Simulate 100 Developers & 15 Teams")
            print(f" {self.BOLD}8.{self.RESET}  Git Forensics Toolkit (Inspect Playground)")
            print(f" {self.BOLD}9.{self.RESET}  CI/CD Failure Lab")
            print(f" {self.BOLD}10.{self.RESET} {self.RED}{self.BOLD}THE FINAL BOSS — REPOSITORY DISASTER (Level 30){self.RESET}")
            print(f" {self.BOLD}11.{self.RESET} View Full Progress & Analytics")
            print(f" {self.BOLD}12.{self.RESET} Run Verification on Active Scenario")
            print(f" {self.BOLD}13.{self.RESET} Reset Current Scenario")
            print(f" {self.BOLD}14.{self.RESET} Documentation & Interview Questions")
            print(f" {self.BOLD}15.{self.RESET} Exit")
            print(f"{self.CYAN}{'-' * 75}{self.RESET}")

            choice = input(f"\n{self.BOLD}Select an option (0-15): {self.RESET}").strip()

            if choice in ["0", "w", "web"]:
                from ..web.server import start_server
                start_server()
            elif choice == "1":
                self.category_menu(ChallengeCategory.A_INTERNALS, "Git Internals Lab")
            elif choice == "2":
                self.category_menu(ChallengeCategory.B_BRANCHING, "Branching & Rebase Surgery Lab")
            elif choice == "3":
                self.category_menu(ChallengeCategory.C_DISTRIBUTED, "Distributed Team Collaboration Lab")
            elif choice == "4":
                self.category_menu(ChallengeCategory.D_RELEASE, "Release Engineering Lab")
            elif choice == "5":
                self.category_menu(ChallengeCategory.E_INCIDENTS, "Production Incident Lab", exclude_boss=True)
            elif choice == "6":
                self.museum_menu()
            elif choice == "7":
                self.view_organization_menu()
            elif choice == "8":
                self.run_forensics()
            elif choice == "9":
                self.launch_level("level_29")
            elif choice == "10":
                self.launch_level("level_30")
            elif choice == "11":
                self.view_progress()
            elif choice == "12":
                self.verify_active()
            elif choice == "13":
                self.reset_active()
            elif choice == "14":
                self.view_docs()
            elif choice == "15":
                print(f"\n{self.GREEN}Stay sharp, Engineer. Dojo standing by.{self.RESET}\n")
                sys.exit(0)
            else:
                print(f"{self.RED}Invalid option. Please enter 0-15.{self.RESET}")
                time.sleep(1)

    def category_menu(self, category: ChallengeCategory, title: str, exclude_boss: bool = False) -> None:
        while True:
            print(f"\n{self.CYAN}{'=' * 75}{self.RESET}")
            print(f"{self.BOLD}  {title.upper()}{self.RESET}")
            print(f"{self.CYAN}{'=' * 75}{self.RESET}\n")
            challenges = [c for c in get_all_challenges() if c.category == category]
            if exclude_boss:
                challenges = [c for c in challenges if c.level_id != "level_30"]

            for c in challenges:
                status = f"{self.GREEN}[COMPLETED]{self.RESET}" if state_manager.is_completed(c.level_id) else f"{self.YELLOW}[NOT STARTED]{self.RESET}"
                print(f"  {self.BOLD}{c.number:02d}.{self.RESET} {c.title:<42} | Diff: {c.difficulty:<9} | {status}")

            print(f"\n  {self.BOLD}0. Back to Main Menu{self.RESET}")
            sel = input(f"\n{self.BOLD}Enter level number to launch (or 0 to return): {self.RESET}").strip()
            if sel == "0":
                break

            target = next((c for c in challenges if f"{c.number}" == sel or f"{c.number:02d}" == sel), None)
            if target:
                self.launch_level(target.level_id)
                break
            else:
                print(f"{self.RED}Invalid selection.{self.RESET}")

    def launch_level(self, level_id: str) -> None:
        challenge = get_challenge(level_id)
        if not challenge:
            print(f"{self.RED}Challenge '{level_id}' not found.{self.RESET}")
            return

        print(f"\n{self.CYAN}{'=' * 75}{self.RESET}")
        print(f"{self.BOLD}LAUNCHING LEVEL {challenge.number:02d}: {challenge.title.upper()}{self.RESET}")
        print(f"{self.CYAN}{'=' * 75}{self.RESET}")
        print(f"{self.BOLD}Difficulty       :{self.RESET} {challenge.difficulty}")
        print(f"{self.BOLD}Estimated Time   :{self.RESET} {challenge.estimated_time}")
        print(f"\n{self.BOLD}Scenario Description:{self.RESET}\n{challenge.description}\n")
        print(f"{self.BOLD}Initial State    :{self.RESET} {challenge.initial_state_desc}")
        print(f"{self.BOLD}Expected Outcome :{self.RESET} {challenge.expected_outcome}\n")

        confirm = input(f"{self.YELLOW}Initialize scenario in playground repo? (y/n): {self.RESET}").strip().lower()
        if confirm == "y":
            print(f"\n{self.CYAN}[*] Provisioning isolated scenario in {config.playground_repo}...{self.RESET}")
            challenge.setup()
            state_manager.start_level(level_id)
            print(f"{self.GREEN}[✓] Scenario ready!{self.RESET}")
            print(f"\n{self.BOLD}To work on this scenario:{self.RESET}")
            print(f"  cd \"{config.playground_repo}\"")
            print(f"\nWhen completed, return to this terminal and select option 12 (Run Verification).")
            input(f"\n{self.BOLD}Press Enter to return to menu...{self.RESET}")

    def verify_active(self) -> None:
        active_id = state_manager.active_level
        if not active_id:
            print(f"{self.YELLOW}No active scenario loaded. Launch a level first.{self.RESET}")
            input("Press Enter...")
            return

        challenge = get_challenge(active_id)
        if not challenge:
            print(f"{self.RED}Active level '{active_id}' not recognized.{self.RESET}")
            input("Press Enter...")
            return

        print(f"\n{self.CYAN}[*] Running automated verification for {challenge.title}...{self.RESET}")
        success, message = challenge.verify()
        state_manager.record_attempt(active_id, success, message)

        if success:
            print(f"\n{self.GREEN}{self.BOLD}[✓] VERIFICATION PASSED!{self.RESET}")
            print(f"{self.GREEN}{message}{self.RESET}\n")
            print(f"{self.CYAN}{'-' * 75}{self.RESET}")
            print(f"{self.BOLD}INTERVIEW DEEP DIVE:{self.RESET}")
            for q in challenge.interview_questions:
                print(f"\n{self.YELLOW}Q: {q.question}{self.RESET}")
                for pt in q.key_points:
                    print(f"  • {pt}")
                print(f"  {self.CYAN}Architectural Context:{self.RESET} {q.in_depth_explanation}")
        else:
            print(f"\n{self.RED}{self.BOLD}[✗] VERIFICATION FAILED{self.RESET}")
            print(f"{self.RED}{message}{self.RESET}\n")
            print(f"{self.YELLOW}HINTS:{self.RESET}")
            for h in challenge.hints:
                print(f"  • {h}")

        input(f"\n{self.BOLD}Press Enter to continue...{self.RESET}")

    def reset_active(self) -> None:
        active_id = state_manager.active_level
        if not active_id:
            print(f"{self.YELLOW}No active scenario to reset.{self.RESET}")
            input("Press Enter...")
            return

        confirm = input(f"{self.RED}Are you sure you want to reset scenario '{active_id}'? Working tree changes will be wiped! (y/n): {self.RESET}").strip().lower()
        if confirm == "y":
            challenge = get_challenge(active_id)
            if challenge:
                challenge.reset()
                print(f"{self.GREEN}[✓] Scenario successfully reset.{self.RESET}")
            input("Press Enter...")

    def run_forensics(self) -> None:
        print(f"\n{self.CYAN}[*] Running deep forensic analysis on playground repo...{self.RESET}\n")
        inspector = ForensicInspector(config.playground_repo)
        report = inspector.analyze()
        rendered = ForensicReportRenderer.render(report)
        print(rendered)
        input(f"\n{self.BOLD}Press Enter to return to menu...{self.RESET}")

    def museum_menu(self) -> None:
        while True:
            print(f"\n{self.CYAN}{'=' * 75}{self.RESET}")
            print(f"{self.BOLD}  THE BROKEN REPOSITORY MUSEUM{self.RESET}")
            print(f"{self.CYAN}{'=' * 75}{self.RESET}\n")
            for idx, ex in enumerate(EXHIBITS, 1):
                print(f"  {self.BOLD}{idx}.{self.RESET} {ex.name} [{ex.incident_severity}]")
                print(f"     Context : {ex.historical_context}")
                print(f"     Lesson  : {ex.educational_lesson}\n")
            print(f"  {self.BOLD}0. Back to Main Menu{self.RESET}")
            sel = input(f"\n{self.BOLD}Load exhibit into playground? (1-{len(EXHIBITS)} or 0): {self.RESET}").strip()
            if sel == "0":
                break
            try:
                idx = int(sel)
                if 1 <= idx <= len(EXHIBITS):
                    ex = EXHIBITS[idx - 1]
                    print(f"\n{self.CYAN}[*] Loading Exhibit: {ex.name}...{self.RESET}")
                    MuseumManager.load_exhibit(ex.id)
                    print(f"{self.GREEN}[✓] Exhibit loaded at {config.playground_repo}{self.RESET}")
                    print(f"Inspect it with: `cd \"{config.playground_repo}\" && git status && git log`")
                    input(f"\nPress Enter...")
                    break
            except Exception as e:
                print(f"{self.RED}Error: {e}{self.RESET}")

    def view_organization_menu(self) -> None:
        print(f"\n{self.CYAN}{'=' * 75}{self.RESET}")
        print(f"{self.BOLD}  NEXUS ENGINEERING: 15 TEAMS & 100 DEVELOPERS{self.RESET}")
        print(f"{self.CYAN}{'=' * 75}{self.RESET}\n")
        print(f"{self.BOLD}15 Engineering Teams:{self.RESET}")
        for t in TEAMS:
            print(f"  • {self.BOLD}{t.name:<25}{self.RESET} : {t.description}")

        print(f"\n{self.BOLD}Sample Developers (Total: {len(DEVELOPERS)}):{self.RESET}")
        for dev in DEVELOPERS[:12]:
            print(f"  • {dev.name:<22} | {dev.email:<30} | {dev.team_id:<12} | {dev.role:<22} | Behavior: {dev.behavior.value}")

        print(f"\n  (100 deterministic fictional developer identities active)")
        input(f"\n{self.BOLD}Press Enter to return to menu...{self.RESET}")

    def view_progress(self) -> None:
        print(f"\n{self.CYAN}{'=' * 75}{self.RESET}")
        print(f"{self.BOLD}  GIT DOJO PROGRESS & ANALYTICS{self.RESET}")
        print(f"{self.CYAN}{'=' * 75}{self.RESET}\n")
        for c in get_all_challenges():
            p = state_manager.levels.get(c.level_id, {})
            status = f"{self.GREEN}COMPLETED{self.RESET}" if p.get("completed") else f"{self.YELLOW}PENDING{self.RESET}"
            best_time = f"{p.get('best_recovery_time_seconds')}s" if p.get("best_recovery_time_seconds") else "N/A"
            attempts = p.get("attempts", 0)
            print(f"  Level {c.number:02d}: {c.title:<38} | {status:<18} | Attempts: {attempts:<3} | Best Time: {best_time}")

        input(f"\n{self.BOLD}Press Enter to return to menu...{self.RESET}")

    def view_docs(self) -> None:
        print(f"\n{self.CYAN}{'=' * 75}{self.RESET}")
        print(f"{self.BOLD}  DOCUMENTATION & ARCHITECTURE SITEMAP{self.RESET}")
        print(f"{self.CYAN}{'=' * 75}{self.RESET}\n")
        print(f"  1. 60-Day Curriculum Roadmap : docs/60_DAY_ROADMAP.md")
        print(f"  2. GitHub Admin Guide        : docs/GITHUB_ADMIN_GUIDE.md")
        print(f"  3. Solutions Repository      : docs/SOLUTIONS/")
        print(f"  4. Nexus Platform Specs      : docs/ARCHITECTURE.md")
        print(f"  5. CI/CD Pipeline Reference  : .github/workflows/ci.yml")
        input(f"\n{self.BOLD}Press Enter to return to menu...{self.RESET}")

