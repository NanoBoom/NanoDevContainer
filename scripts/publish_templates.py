#!/usr/bin/env python3
"""Automated template publish workflow.

Bumps versions and publishes to OCI registry.
Pure Python stdlib implementation - no external dependencies.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


# Simple color support (copied from bump_version.py)
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RESET = '\033[0m'

    @classmethod
    def init(cls):
        import platform
        if platform.system() == 'Windows':
            os.system("")


SCRIPT_DIR = Path(__file__).parent.resolve()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="DevContainer Template Publisher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Publish all templates (no version bump)
  %(prog)s --namespace myorg/myrepo

  # Publish specific template only
  %(prog)s src/nanodev-python --namespace myorg/myrepo

  # Bump patch version for all templates and publish
  %(prog)s -u --namespace myorg/myrepo

  # Bump minor version for specific template and publish
  %(prog)s -u --level minor src/nanodev-node --namespace myorg/myrepo

  # Dry run with version bump
  %(prog)s -u --dry-run --namespace myorg/myrepo
        """
    )

    parser.add_argument(
        "target",
        nargs="?",
        default="./src",
        help="Target template directory or specific template (default: ./src)"
    )

    parser.add_argument(
        "-u", "--update-version",
        action="store_true",
        help="Update version before publishing (default: False)"
    )

    parser.add_argument(
        "-l", "--level",
        choices=["patch", "minor", "major"],
        default="patch",
        help="Version bump level (default: patch, only used with -u)"
    )

    parser.add_argument(
        "-n", "--namespace",
        required=True,
        help="Registry namespace (e.g., owner/repo)"
    )

    parser.add_argument(
        "-r", "--registry",
        default=os.environ.get("REGISTRY", "ghcr.io"),
        help="OCI registry (default: ghcr.io)"
    )

    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show what would happen without publishing"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    Colors.init()
    args = parse_arguments()

    print(f"{Colors.BLUE}=== DevContainer Template Publisher ==={Colors.RESET}")
    print(f"Target: {args.target}")
    print(f"Registry: {args.registry}")
    print(f"Namespace: {args.namespace}")
    if args.update_version:
        print(f"Update version: {Colors.YELLOW}Yes{Colors.RESET} (level: {args.level})")
    else:
        print(f"Update version: {Colors.YELLOW}No{Colors.RESET}")
    print()

    # Step 1: Bump versions (only if -u is specified)
    if args.update_version:
        print(f"{Colors.BLUE}Step 1: Bumping versions...{Colors.RESET}")

        bump_cmd = [
            sys.executable,
            str(SCRIPT_DIR / "bump_version.py"),
            "--level", args.level,
            "--target", args.target,
        ]

        if args.dry_run:
            bump_cmd.append("--dry-run")
        else:
            bump_cmd.append("--commit")

        try:
            subprocess.run(bump_cmd, check=True)
        except subprocess.CalledProcessError:
            return 1

        print()

    # Step 2: Publish
    step_num = 2 if args.update_version else 1
    if not args.dry_run:
        print(f"{Colors.BLUE}Step {step_num}: Publishing templates...{Colors.RESET}")
        print(f"{Colors.YELLOW}Publishing to {args.registry}/{args.namespace}...{Colors.RESET}")

        try:
            subprocess.run(
                [
                    "devcontainer", "templates", "publish", args.target,
                    "-r", args.registry,
                    "-n", args.namespace
                ],
                check=True
            )
        except subprocess.CalledProcessError:
            return 1
        except FileNotFoundError:
            print(f"{Colors.RED}Error: devcontainer command not found{Colors.RESET}", file=sys.stderr)
            return 1

        print()
        print(f"{Colors.GREEN}✓ Templates published successfully!{Colors.RESET}")
        print(f"View at: https://{args.registry}/{args.namespace}")
    else:
        print(f"{Colors.YELLOW}[DRY RUN] Skipping actual publish{Colors.RESET}")
        print(f"Would run: devcontainer templates publish {args.target} -r {args.registry} -n {args.namespace}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
