#!/usr/bin/env python3
"""DevContainer Template Version Bumper.

Automatically increments semver versions in devcontainer-template.json files.
Pure Python 3.9+ stdlib implementation - no external dependencies.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for cross-platform colored output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RESET = '\033[0m'

    @classmethod
    def init(cls):
        """Initialize color support (for Windows)."""
        import os
        import platform
        if platform.system() == 'Windows':
            # Enable ANSI escape sequences on Windows 10+
            os.system("")


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse a semver string into (major, minor, patch) tuple.

    Args:
        version: Version string like "1.2.3"

    Returns:
        Tuple of (major, minor, patch) integers

    Raises:
        ValueError: If version string is invalid semver format
    """
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        raise ValueError(f"Invalid semver format: {version}")

    return (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3))
    )


def increment_version(version: str, level: str) -> str:
    """Increment a version string by the specified level.

    Args:
        version: Current version like "1.2.3"
        level: One of "patch", "minor", "major"

    Returns:
        New version string

    Raises:
        ValueError: If level is invalid or version is malformed
    """
    major, minor, patch = parse_version(version)

    if level == "patch":
        patch += 1
    elif level == "minor":
        minor += 1
        patch = 0
    elif level == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Unknown level '{level}'. Use: patch, minor, or major")

    return f"{major}.{minor}.{patch}"


def find_templates(target: Path) -> List[Path]:
    """Find all devcontainer-template.json files in target.

    Args:
        target: Path to directory or single template file

    Returns:
        Sorted list of template file paths

    Raises:
        FileNotFoundError: If target doesn't exist
        ValueError: If no templates found
    """
    if not target.exists():
        raise FileNotFoundError(f"Target not found: {target}")

    if target.is_file() and target.name == "devcontainer-template.json":
        # Single template mode
        return [target]
    elif target.is_dir():
        # Directory mode - find all templates recursively
        templates = sorted(target.rglob("devcontainer-template.json"))
        if not templates:
            raise ValueError(f"No templates found in {target}")
        return templates
    else:
        raise ValueError(f"Invalid target: {target}")


def update_template_version(
    template_file: Path,
    level: str,
    dry_run: bool = False
) -> bool:
    """Update version in a template file.

    Args:
        template_file: Path to devcontainer-template.json
        level: Version bump level (patch/minor/major)
        dry_run: If True, only show changes without applying

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read current version and template ID
        with open(template_file, encoding='utf-8') as f:
            data = json.load(f)

        current_version = data.get("version")
        template_id = data.get("id", "unknown")

        if not current_version:
            print(
                f"{Colors.RED}Error: No version field in {template_file}{Colors.RESET}",
                file=sys.stderr
            )
            return False

        # Calculate new version
        try:
            new_version = increment_version(current_version, level)
        except ValueError as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}", file=sys.stderr)
            return False

        # Display changes
        print(f"{Colors.BLUE}Template: {template_id}{Colors.RESET}")
        print(f"  Current: {current_version}")
        print(f"  New:     {Colors.GREEN}{new_version}{Colors.RESET}")

        if dry_run:
            print(f"  {Colors.YELLOW}[DRY RUN] Skipping actual update{Colors.RESET}")
            return True

        # Update JSON file atomically
        data["version"] = new_version
        temp_file = template_file.with_suffix('.tmp')

        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            f.write('\n')  # Add trailing newline

        # Verify JSON is valid
        with open(temp_file, encoding='utf-8') as f:
            json.load(f)  # Will raise if invalid

        # Atomic replace
        temp_file.replace(template_file)
        print(f"  {Colors.GREEN}✓ Updated{Colors.RESET}")
        return True

    except json.JSONDecodeError as e:
        print(
            f"{Colors.RED}Error: Invalid JSON in {template_file}: {e}{Colors.RESET}",
            file=sys.stderr
        )
        return False
    except Exception as e:
        print(
            f"{Colors.RED}Error updating {template_file}: {e}{Colors.RESET}",
            file=sys.stderr
        )
        return False


def commit_changes(level: str) -> bool:
    """Commit template version changes to git.

    Args:
        level: Version bump level for commit message

    Returns:
        True if successful, False otherwise
    """
    try:
        commit_msg = f"chore: bump template versions ({level})"

        # Add changed files
        subprocess.run(
            ["git", "add", "src/*/devcontainer-template.json"],
            check=True,
            capture_output=True,
            text=True
        )

        # Commit
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True,
            capture_output=True,
            text=True
        )

        print(f"{Colors.GREEN}✓ Changes committed{Colors.RESET}")
        return True

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else "Unknown error"
        print(f"{Colors.RED}Git error: {stderr}{Colors.RESET}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"{Colors.RED}Error: git command not found{Colors.RESET}", file=sys.stderr)
        return False


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="DevContainer Template Version Bumper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Bump patch version for all templates (1.0.0 -> 1.0.1)
  %(prog)s

  # Bump minor version for all templates (1.0.0 -> 1.1.0)
  %(prog)s --level minor

  # Preview changes without applying
  %(prog)s --dry-run

  # Bump and commit to git
  %(prog)s --level patch --commit

  # Bump single template
  %(prog)s --target src/nanodev-node
        """
    )

    parser.add_argument(
        "-l", "--level",
        choices=["patch", "minor", "major"],
        default="patch",
        help="Version level to bump (default: patch)"
    )

    parser.add_argument(
        "-t", "--target",
        type=Path,
        default=Path("src"),
        help="Target template or directory (default: src)"
    )

    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show changes without applying them"
    )

    parser.add_argument(
        "-c", "--commit",
        action="store_true",
        help="Commit changes to git with automatic message"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Initialize colors
    Colors.init()

    args = parse_arguments()

    print(f"{Colors.BLUE}=== DevContainer Template Version Bumper ==={Colors.RESET}")
    print(f"Level: {Colors.YELLOW}{args.level}{Colors.RESET}")
    print(f"Target: {args.target}")
    if args.dry_run:
        print(f"Mode: {Colors.YELLOW}DRY RUN{Colors.RESET}")
    print()

    # Find templates
    try:
        templates = find_templates(args.target)
    except (FileNotFoundError, ValueError) as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}", file=sys.stderr)
        return 1

    print(f"Found {len(templates)} template(s):")
    print()

    # Update each template
    failed = 0
    for template in templates:
        if not update_template_version(template, args.level, args.dry_run):
            failed += 1
        print()

    # Git commit if requested
    if args.commit and not args.dry_run and failed == 0:
        print(f"{Colors.BLUE}Committing changes...{Colors.RESET}")
        if not commit_changes(args.level):
            failed += 1

    # Summary
    print(f"{Colors.BLUE}=== Summary ==={Colors.RESET}")
    if failed == 0:
        print(f"{Colors.GREEN}✓ All templates updated successfully{Colors.RESET}")
        return 0
    else:
        print(f"{Colors.RED}✗ {failed} template(s) failed to update{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
