# Feature: Migrate Version Bumping Script from Bash to Python (Pure Stdlib)

## Feature Description

Rewrite the DevContainer template version bumping script from Bash to Python using **only Python standard library**, improving cross-platform compatibility, maintainability, and testability. No external dependencies required.

## User Story

作为 DevContainer 模板维护者
我想要使用纯 Python 标准库实现的版本管理脚本
这样我无需安装任何第三方包，获得最大的兼容性和零依赖优势

## Problem Statement

The current bash implementation (`scripts/bump-version.sh`) has several limitations:

1. **Cross-platform compatibility**: Bash-specific features like `mapfile` don't work on macOS's default zsh or older bash versions
2. **Error handling**: Bash error handling is verbose and prone to edge cases
3. **Testing**: Unit testing bash scripts requires specialized frameworks
4. **Dependencies**: Relies on external tools (jq) instead of built-in capabilities
5. **Maintainability**: Bash string manipulation and regex are less readable than Python equivalents

**Current Issues**:
- `mapfile` command fails on macOS zsh
- Requires jq for JSON manipulation (external dependency)
- Color output uses ANSI escape codes directly
- No structured testing framework

## Solution Statement

Migrate to a **pure Python standard library** implementation:

1. Uses Python's built-in `json` module (no external JSON parser)
2. **Manual semver parsing with `re` module** (no semver library)
3. Uses `argparse` for robust CLI argument parsing
4. Implements `pathlib` for cross-platform file operations
5. Uses `subprocess` for git operations
6. **Simple ANSI escape codes** for colored output (no colorama)

**Key Benefits**:
- **Zero dependencies**: Only Python 3.9+ stdlib required
- **Maximum portability**: No pip install needed
- **Type hints**: Better IDE support and static analysis
- **Unit testable**: Use Python's `unittest` (no pytest required)
- **Cross-platform**: Works on macOS, Linux, Windows

## Feature Metadata

**Feature Type**: Refactor
**Estimated Complexity**: Low
**Primary Systems Affected**: Version management scripts
**Dependencies**: **None** (Python 3.9+ stdlib only)

---

## CONTEXT REFERENCES

### Relevant Codebase Files

- `scripts/bump-version.sh` (lines 1-233) - Current bash implementation
- `scripts/publish-templates.sh` (lines 1-115) - Wrapper script
- `src/nanodev-claude-code/devcontainer-template.json` - Target JSON
- `src/nanodev-node/devcontainer-template.json` - Template example
- `src/nanodev-python/devcontainer-template.json` - Template example

### New Files to Create

- `scripts/bump_version.py` - Main Python version bumping script
- `scripts/publish_templates.py` - Python wrapper for publish workflow
- `tests/test_bump_version.py` - Unit tests (using unittest)

### Relevant Documentation

- [argparse Documentation](https://docs.python.org/3/library/argparse.html) - CLI parsing
- [pathlib Documentation](https://docs.python.org/3/library/pathlib.html) - File operations
- [re Documentation](https://docs.python.org/3/library/re.html) - Regex for semver
- [json Documentation](https://docs.python.org/3/library/json.html) - JSON parsing

### Patterns to Follow

**Semver Parsing (Pure Python)**:
```python
import re
from typing import Tuple

def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse semver string into (major, minor, patch)."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        raise ValueError(f"Invalid semver: {version}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))
```

**Color Output (Simple ANSI)**:
```python
# ANSI color codes (work on macOS/Linux, Windows 10+)
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RESET = '\033[0m'
```

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation
Implement core semver parsing and increment logic using stdlib only.

### Phase 2: Core Implementation
Template discovery, JSON manipulation, file updates.

### Phase 3: Integration
CLI interface, git integration, workflow features.

### Phase 4: Testing & Validation
Unit tests using stdlib `unittest` module.

---

## STEP-BY-STEP TASKS

### CREATE scripts/bump_version.py (Complete Implementation)

- **IMPLEMENT**: Complete Python script with stdlib only
- **PATTERN**: CLI script with argparse, pathlib, json, re, subprocess
- **IMPORTS**: argparse, json, pathlib, re, subprocess, sys
- **GOTCHA**: Windows color support requires `os.system("")` initialization
- **VALIDATE**: `python3 -m py_compile scripts/bump_version.py`

```python
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
```

### CREATE scripts/publish_templates.py

- **IMPLEMENT**: Python wrapper for publish workflow
- **PATTERN**: Subprocess calls to bump_version.py and devcontainer CLI
- **IMPORTS**: argparse, os, subprocess, sys, pathlib
- **GOTCHA**: Use sys.executable for Python subprocess
- **VALIDATE**: `python3 -m py_compile scripts/publish_templates.py`

```python
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
  # Bump patch and publish
  %(prog)s --namespace myorg/myrepo

  # Bump minor and publish
  %(prog)s --level minor --namespace myorg/myrepo
        """
    )

    parser.add_argument(
        "-l", "--level",
        choices=["patch", "minor", "major"],
        default="patch",
        help="Version bump level (default: patch)"
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
    print(f"Registry: {args.registry}")
    print(f"Namespace: {args.namespace}")
    print(f"Bump level: {args.level}")
    print()

    # Step 1: Bump versions
    print(f"{Colors.BLUE}Step 1: Bumping versions...{Colors.RESET}")

    bump_cmd = [
        sys.executable,
        str(SCRIPT_DIR / "bump_version.py"),
        "--level", args.level,
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
    if not args.dry_run:
        print(f"{Colors.BLUE}Step 2: Publishing templates...{Colors.RESET}")
        print(f"{Colors.YELLOW}Publishing to {args.registry}/{args.namespace}...{Colors.RESET}")

        try:
            subprocess.run(
                [
                    "devcontainer", "templates", "publish", "./src",
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
        print(f"Would run: devcontainer templates publish ./src -r {args.registry} -n {args.namespace}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### CREATE tests/test_bump_version.py

- **IMPLEMENT**: Unit tests using stdlib unittest
- **PATTERN**: unittest.TestCase classes
- **IMPORTS**: unittest, sys, pathlib, json, tempfile
- **GOTCHA**: Add scripts to sys.path before importing
- **VALIDATE**: `python3 -m unittest tests/test_bump_version.py`

```python
"""Unit tests for bump_version.py using stdlib unittest."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from bump_version import (
    parse_version,
    increment_version,
    find_templates,
    update_template_version,
)


class TestVersionParsing(unittest.TestCase):
    """Tests for version parsing."""

    def test_parse_valid_version(self):
        """Test parsing valid semver strings."""
        major, minor, patch = parse_version("1.2.3")
        self.assertEqual(major, 1)
        self.assertEqual(minor, 2)
        self.assertEqual(patch, 3)

    def test_parse_invalid_version(self):
        """Test parsing invalid semver raises ValueError."""
        with self.assertRaises(ValueError):
            parse_version("invalid")

    def test_parse_incomplete_version(self):
        """Test parsing incomplete version."""
        with self.assertRaises(ValueError):
            parse_version("1.2")


class TestVersionIncrement(unittest.TestCase):
    """Tests for version incrementing."""

    def test_increment_patch(self):
        """Test patch version increment."""
        self.assertEqual(increment_version("1.2.3", "patch"), "1.2.4")

    def test_increment_minor(self):
        """Test minor version increment."""
        self.assertEqual(increment_version("1.2.3", "minor"), "1.3.0")

    def test_increment_major(self):
        """Test major version increment."""
        self.assertEqual(increment_version("1.2.3", "major"), "2.0.0")

    def test_increment_invalid_level(self):
        """Test invalid level raises ValueError."""
        with self.assertRaises(ValueError):
            increment_version("1.2.3", "invalid")


class TestTemplateFinding(unittest.TestCase):
    """Tests for template discovery."""

    def test_find_single_template(self):
        """Test finding single template file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            template.write_text('{"version": "1.0.0"}')

            templates = find_templates(template)
            self.assertEqual(len(templates), 1)
            self.assertEqual(templates[0], template)

    def test_find_multiple_templates(self):
        """Test finding multiple templates in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "template1").mkdir()
            (tmp_path / "template1" / "devcontainer-template.json").write_text('{}')

            (tmp_path / "template2").mkdir()
            (tmp_path / "template2" / "devcontainer-template.json").write_text('{}')

            templates = find_templates(tmp_path)
            self.assertEqual(len(templates), 2)

    def test_find_no_templates(self):
        """Test error when no templates found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                find_templates(Path(tmpdir))

    def test_find_nonexistent_path(self):
        """Test error when path doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            find_templates(Path("/nonexistent/path"))


class TestTemplateUpdate(unittest.TestCase):
    """Tests for template version updating."""

    def test_update_template_success(self):
        """Test successful template update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            template.write_text(json.dumps({
                "id": "test-template",
                "version": "1.0.0"
            }))

            result = update_template_version(template, "patch", dry_run=False)
            self.assertTrue(result)

            # Verify file was updated
            with open(template) as f:
                data = json.load(f)
            self.assertEqual(data["version"], "1.0.1")

    def test_update_template_dry_run(self):
        """Test dry-run doesn't modify file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            original_content = json.dumps({"id": "test", "version": "1.0.0"})
            template.write_text(original_content)

            result = update_template_version(template, "patch", dry_run=True)
            self.assertTrue(result)

            # Verify file was NOT updated
            self.assertEqual(template.read_text(), original_content)

    def test_update_template_invalid_json(self):
        """Test handling of invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            template.write_text("invalid json")

            result = update_template_version(template, "patch", dry_run=False)
            self.assertFalse(result)

    def test_update_template_missing_version(self):
        """Test handling of missing version field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            template = tmp_path / "devcontainer-template.json"
            template.write_text(json.dumps({"id": "test"}))

            result = update_template_version(template, "patch", dry_run=False)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
```

### UPDATE README.md

- **IMPLEMENT**: Update documentation for Python scripts
- **PATTERN**: Keep existing structure, change examples
- **IMPORTS**: None
- **GOTCHA**: Emphasize zero dependencies
- **VALIDATE**: Read updated section

Find the "Version Management" section and replace with:

```markdown
## Version Management

### Bumping Template Versions

Before publishing templates, you must increment version numbers to avoid conflicts with existing published versions.

**No dependencies required** - pure Python 3.9+ stdlib:

```bash
# Bump patch version (1.0.0 -> 1.0.1) for all templates
python3 scripts/bump_version.py

# Bump minor version (1.0.0 -> 1.1.0)
python3 scripts/bump_version.py --level minor

# Bump major version (1.0.0 -> 2.0.0)
python3 scripts/bump_version.py --level major

# Preview changes without applying
python3 scripts/bump_version.py --dry-run

# Bump and commit to git
python3 scripts/bump_version.py --commit
```

### Publishing Templates

After bumping versions:

```bash
# Publish all templates
devcontainer templates publish ./src -r ghcr.io -n <your-org>/<repo>

# Or use the automated workflow
python3 scripts/publish_templates.py --namespace <your-org>/<repo>
```
```

---

## VALIDATION COMMANDS

### Level 1: Syntax & No Dependencies

```bash
# Verify Python syntax
python3 -m py_compile scripts/bump_version.py
python3 -m py_compile scripts/publish_templates.py

# Verify no imports except stdlib
python3 -c "import scripts.bump_version" 2>&1 | grep -i "ModuleNotFoundError" && echo "ERROR: Missing stdlib module" || echo "✓ All imports are stdlib"

# Verify all templates are valid JSON
python3 -c "import json; from pathlib import Path; [json.loads(p.read_text()) for p in Path('src').rglob('devcontainer-template.json')]; print('✓ All JSON valid')"
```

### Level 2: Unit Tests

```bash
# Run all unit tests
python3 -m unittest tests/test_bump_version.py -v

# Run specific test classes
python3 -m unittest tests.test_bump_version.TestVersionIncrement -v
python3 -m unittest tests.test_bump_version.TestTemplateUpdate -v
```

### Level 3: Integration Tests

```bash
# Test dry-run mode (should not modify files)
cp -r src src-backup
python3 scripts/bump_version.py --dry-run
diff -r src src-backup && echo "✓ Dry-run does not modify files"
rm -rf src-backup

# Test actual bump
BEFORE=$(python3 -c "import json; print(json.load(open('src/nanodev-node/devcontainer-template.json'))['version'])")
python3 scripts/bump_version.py --target src/nanodev-node --level patch
AFTER=$(python3 -c "import json; print(json.load(open('src/nanodev-node/devcontainer-template.json'))['version'])")
echo "Version changed: $BEFORE -> $AFTER"

# Revert
git checkout src/nanodev-node/devcontainer-template.json
```

### Level 4: Manual Validation

```bash
# Test help output
python3 scripts/bump_version.py --help
python3 scripts/publish_templates.py --help

# Make scripts executable
chmod +x scripts/bump_version.py scripts/publish_templates.py

# Test shebang
./scripts/bump_version.py --help
```

---

## ACCEPTANCE CRITERIA

- [x] Zero external dependencies (pure stdlib)
- [x] Python script parses all template versions correctly
- [x] Correct semver increment logic (patch/minor/major)
- [x] Atomic JSON file updates
- [x] Dry-run mode works correctly
- [x] Colored output (simple ANSI codes)
- [x] Graceful error handling
- [x] All unit tests pass (unittest)
- [x] Documentation updated
- [x] Cross-platform compatible

---

## COMPLETION CHECKLIST

- [ ] `scripts/bump_version.py` created
- [ ] `scripts/publish_templates.py` created
- [ ] `tests/test_bump_version.py` created
- [ ] Scripts are executable
- [ ] All unit tests pass
- [ ] All validation commands pass
- [ ] Dry-run verified
- [ ] README updated
- [ ] No external dependencies

---

## NOTES

### Why No External Dependencies?

1. **Maximum portability**: Works anywhere Python 3.9+ is installed
2. **No pip install**: Simpler deployment and CI/CD
3. **Fewer security risks**: No supply chain attacks via dependencies
4. **Faster startup**: No import overhead from external packages

### Manual Semver Implementation

Simple regex pattern `^(\d+)\.(\d+)\.(\d+)$` captures major.minor.patch components. This is sufficient for our use case and avoids the complexity of a full semver library.

### Simple Color Support

ANSI escape codes work on:
- macOS/Linux terminals
- Windows 10+ (after `os.system("")` initialization)
- Most modern CI/CD environments

For environments without color support, the codes are harmless (just extra characters).

<!-- EOF -->
