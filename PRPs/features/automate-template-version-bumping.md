# Feature: Automate DevContainer Template Version Bumping

## Feature Description

Implement an automated version management script for DevContainer templates that eliminates manual version number updates before publishing. The script will scan all template metadata files, parse current versions, and intelligently increment version numbers according to semantic versioning (semver) rules, preventing publication failures caused by duplicate version conflicts.

## User Story

作为 DevContainer 模板维护者
我想要在发布前自动递增所有模板的版本号
这样我就不会因为手动遗漏更新版本号而导致发布失败

## Problem Statement

When manually publishing DevContainer templates using `devcontainer templates publish`, the OCI registry rejects publications if the exact version already exists. Currently, developers must:

1. Manually open each `devcontainer-template.json` file
2. Remember to increment the version number
3. Ensure semver compliance
4. Repeat for all 3 templates (nanodev-claude-code, nanodev-node, nanodev-python)

**Pain Points**:
- **Forgotten updates**: Easy to forget version bumps, causing publish failures
- **Time waste**: Manual editing across multiple files is tedious
- **Version conflicts**: Registry silently ignores duplicate versions, causing confusion
- **Inconsistency**: No standardized process leads to version numbering chaos

## Solution Statement

Create a bash script `scripts/bump-version.sh` that:

1. Automatically discovers all template metadata files
2. Parses current version numbers using `jq`
3. Increments versions based on user-specified level (patch/minor/major)
4. Updates JSON files atomically
5. Optionally commits changes to git

**Key Benefits**:
- **Zero manual work**: Single command replaces multi-file editing
- **Guaranteed correctness**: Automated semver parsing prevents errors
- **Safe by default**: Dry-run mode allows verification before execution
- **Workflow integration**: Optional git commit streamlines publish process

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Low
**Primary Systems Affected**: Version management, publishing workflow
**Dependencies**: `jq` (already installed), `bash`, `git`

---

## CONTEXT REFERENCES

### Relevant Codebase Files

- `src/nanodev-claude-code/devcontainer-template.json` (line 3) - Current version: "1.0.0"
- `src/nanodev-node/devcontainer-template.json` (line 3) - Current version: "3.0.0"
- `src/nanodev-python/devcontainer-template.json` (line 3) - Current version: "2.0.0"
- `test/nanodev/test.sh` (lines 1-154) - Reference bash script structure with color output and error handling

### New Files to Create

- `scripts/bump-version.sh` - Main version bumping script
- `scripts/publish-templates.sh` - Optional: Wrapper script combining bump + publish

### Relevant Documentation

- [DevContainer Templates Distribution](https://containers.dev/implementors/templates-distribution/)
  - Section: "Versioning strategy" - Templates follow semver, registry rejects duplicate versions
  - Why: Core requirement driving this feature

- [semver-tool GitHub](https://github.com/fsaintjacques/semver-tool)
  - Section: "Bump command" - Pure bash semver manipulation examples
  - Why: Reference implementation for version parsing logic

- [DevContainer CLI Reference](https://github.com/devcontainers/cli)
  - Command: `devcontainer templates publish <target> -r <registry> -n <namespace>`
  - Why: Understand publish workflow integration

### Patterns to Follow

**Script Structure** (from `test/nanodev/test.sh`):
```bash
#!/bin/bash
set -e  # Exit on error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function-based organization
function_name() {
    local var="$1"
    # Implementation
}
```

**JSON Manipulation** (jq pattern):
```bash
# Read version
current_version=$(jq -r '.version' file.json)

# Update version
jq --arg new_ver "1.2.3" '.version = $new_ver' file.json > tmp.json && mv tmp.json file.json
```

**Error Handling**:
- Use `set -e` for automatic error exits
- Validate inputs before processing
- Provide clear error messages with color coding

**Naming Conventions**:
- Scripts use lowercase with hyphens: `bump-version.sh`
- Functions use snake_case: `increment_version()`
- Constants use UPPERCASE: `TEMPLATES_DIR`

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation

Create the core semver parsing and incrementing logic that handles major, minor, and patch version components.

**Tasks**:
- Set up script structure with standard bash header and error handling
- Implement `parse_version()` to extract major.minor.patch components
- Implement `increment_version()` with support for patch/minor/major levels
- Add input validation for semver format

### Phase 2: Core Implementation

Implement the main script functionality for discovering and updating template versions.

**Tasks**:
- Create `find_templates()` to discover all `devcontainer-template.json` files
- Implement `read_current_version()` using jq
- Implement `update_version_file()` to atomically update JSON
- Add color-coded output for user feedback

### Phase 3: Integration

Add workflow enhancements including CLI argument parsing, dry-run mode, and git integration.

**Tasks**:
- Implement CLI argument parser (level, target, dry-run, commit flags)
- Add dry-run mode that shows planned changes without executing
- Add optional git commit with automatic message generation
- Create usage help text

### Phase 4: Testing & Validation

Ensure the script works correctly across all edge cases and integrates smoothly with the publish workflow.

**Tasks**:
- Test on all three templates
- Verify JSON integrity after updates
- Test dry-run mode accuracy
- Document usage in README

---

## STEP-BY-STEP TASKS

### CREATE scripts/bump-version.sh

- **IMPLEMENT**: Script header with shebang, error handling, color definitions
- **PATTERN**: Mirror structure from `test/nanodev/test.sh:1-10`
- **IMPORTS**: None required (pure bash + jq)
- **GOTCHA**: Use `set -e` but disable for validation checks that expect failures
- **VALIDATE**: `bash -n scripts/bump-version.sh` (syntax check)

```bash
#!/bin/bash
# DevContainer Template Version Bumper
# Automatically increments semver versions in devcontainer-template.json files

set -e  # Exit on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color
```

### ADD parse_version function

- **IMPLEMENT**: Parse semver string into major, minor, patch components
- **PATTERN**: Based on semver-tool bash implementation
- **IMPORTS**: None
- **GOTCHA**: Handle invalid semver gracefully, don't crash on malformed input
- **VALIDATE**: Test with `echo "1.2.3" | parse_version` should output "1 2 3"

```bash
parse_version() {
    local version="$1"

    if [[ ! "$version" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        echo -e "${RED}Error: Invalid semver format: $version${NC}" >&2
        return 1
    fi

    echo "${BASH_REMATCH[1]} ${BASH_REMATCH[2]} ${BASH_REMATCH[3]}"
}
```

### ADD increment_version function

- **IMPLEMENT**: Increment version based on level (patch/minor/major)
- **PATTERN**: Standard semver bump rules
- **IMPORTS**: None
- **GOTCHA**: Reset lower components when bumping higher levels (e.g., 1.2.3 --minor-> 1.3.0)
- **VALIDATE**: Test `increment_version "1.2.3" "minor"` should output "1.3.0"

```bash
increment_version() {
    local version="$1"
    local level="$2"  # patch, minor, or major

    read -r major minor patch <<< "$(parse_version "$version")"

    case "$level" in
        patch)
            patch=$((patch + 1))
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        *)
            echo -e "${RED}Error: Unknown level '$level'. Use: patch, minor, or major${NC}" >&2
            return 1
            ;;
    esac

    echo "${major}.${minor}.${patch}"
}
```

### ADD find_templates function

- **IMPLEMENT**: Discover all devcontainer-template.json files in src/
- **PATTERN**: Use find command with proper error handling
- **IMPORTS**: None
- **GOTCHA**: Handle case when no templates found
- **VALIDATE**: `find_templates` should output 3 template paths

```bash
find_templates() {
    local target="${1:-.}"

    if [[ -f "$target/devcontainer-template.json" ]]; then
        # Single template mode
        echo "$target/devcontainer-template.json"
    elif [[ -d "$target" ]]; then
        # Directory mode - find all templates
        find "$target" -name "devcontainer-template.json" -type f | sort
    else
        echo -e "${RED}Error: Invalid target: $target${NC}" >&2
        return 1
    fi
}
```

### ADD update_template_version function

- **IMPLEMENT**: Read current version, increment, update JSON file using jq
- **PATTERN**: Use jq with --arg for safe string interpolation
- **IMPORTS**: Requires jq (already installed)
- **GOTCHA**: Use atomic write (temp file + mv) to prevent corruption on failure
- **VALIDATE**: After update, verify JSON is valid with `jq . file.json`

```bash
update_template_version() {
    local template_file="$1"
    local level="$2"
    local dry_run="${3:-false}"

    if [[ ! -f "$template_file" ]]; then
        echo -e "${RED}Error: Template not found: $template_file${NC}" >&2
        return 1
    fi

    # Read current version and template ID
    local current_version
    local template_id
    current_version=$(jq -r '.version' "$template_file")
    template_id=$(jq -r '.id' "$template_file")

    # Calculate new version
    local new_version
    new_version=$(increment_version "$current_version" "$level")

    echo -e "${BLUE}Template: ${template_id}${NC}"
    echo -e "  Current: ${current_version}"
    echo -e "  New:     ${GREEN}${new_version}${NC}"

    if [[ "$dry_run" == "true" ]]; then
        echo -e "  ${YELLOW}[DRY RUN] Skipping actual update${NC}"
        return 0
    fi

    # Update JSON file atomically
    local temp_file="${template_file}.tmp"
    jq --arg new_ver "$new_version" '.version = $new_ver' "$template_file" > "$temp_file"

    # Verify JSON is valid
    if jq . "$temp_file" > /dev/null 2>&1; then
        mv "$temp_file" "$template_file"
        echo -e "  ${GREEN}✓ Updated${NC}"
    else
        rm -f "$temp_file"
        echo -e "  ${RED}✗ Failed to update (invalid JSON)${NC}" >&2
        return 1
    fi
}
```

### ADD main function and CLI parser

- **IMPLEMENT**: Parse arguments, handle --help, --dry-run, --level, --target flags
- **PATTERN**: Standard bash getopts pattern
- **IMPORTS**: None
- **GOTCHA**: Use `${1:-default}` for optional arguments
- **VALIDATE**: `./scripts/bump-version.sh --help` should show usage

```bash
show_usage() {
    cat << EOF
${BLUE}DevContainer Template Version Bumper${NC}

Usage: $(basename "$0") [OPTIONS]

Options:
    -l, --level LEVEL       Version level to bump: patch, minor, major (default: patch)
    -t, --target TARGET     Target template or directory (default: src)
    -d, --dry-run          Show changes without applying them
    -c, --commit           Commit changes to git with automatic message
    -h, --help             Show this help message

Examples:
    # Bump patch version for all templates (1.0.0 -> 1.0.1)
    $(basename "$0")

    # Bump minor version for all templates (1.0.0 -> 1.1.0)
    $(basename "$0") --level minor

    # Preview changes without applying
    $(basename "$0") --dry-run

    # Bump and commit to git
    $(basename "$0") --level patch --commit

    # Bump single template
    $(basename "$0") --target src/nanodev-node
EOF
}

main() {
    local level="patch"
    local target="src"
    local dry_run="false"
    local commit="false"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -l|--level)
                level="$2"
                shift 2
                ;;
            -t|--target)
                target="$2"
                shift 2
                ;;
            -d|--dry-run)
                dry_run="true"
                shift
                ;;
            -c|--commit)
                commit="true"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                echo -e "${RED}Error: Unknown option: $1${NC}" >&2
                show_usage
                exit 1
                ;;
        esac
    done

    # Validate level
    if [[ ! "$level" =~ ^(patch|minor|major)$ ]]; then
        echo -e "${RED}Error: Invalid level '$level'. Use: patch, minor, or major${NC}" >&2
        exit 1
    fi

    echo -e "${BLUE}=== DevContainer Template Version Bumper ===${NC}"
    echo -e "Level: ${YELLOW}${level}${NC}"
    echo -e "Target: ${target}"
    [[ "$dry_run" == "true" ]] && echo -e "Mode: ${YELLOW}DRY RUN${NC}"
    echo ""

    # Find and process templates
    local templates
    mapfile -t templates < <(find_templates "$target")

    if [[ ${#templates[@]} -eq 0 ]]; then
        echo -e "${RED}Error: No templates found in $target${NC}" >&2
        exit 1
    fi

    echo -e "Found ${#templates[@]} template(s):"
    echo ""

    # Update each template
    local failed=0
    for template in "${templates[@]}"; do
        if ! update_template_version "$template" "$level" "$dry_run"; then
            failed=$((failed + 1))
        fi
        echo ""
    done

    # Git commit if requested
    if [[ "$commit" == "true" && "$dry_run" == "false" && $failed -eq 0 ]]; then
        echo -e "${BLUE}Committing changes...${NC}"
        local commit_msg="chore: bump template versions ($level)"
        git add src/*/devcontainer-template.json
        git commit -m "$commit_msg"
        echo -e "${GREEN}✓ Changes committed${NC}"
    fi

    # Summary
    echo -e "${BLUE}=== Summary ===${NC}"
    if [[ $failed -eq 0 ]]; then
        echo -e "${GREEN}✓ All templates updated successfully${NC}"
        exit 0
    else
        echo -e "${RED}✗ $failed template(s) failed to update${NC}"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
```

### UPDATE README.md

- **IMPLEMENT**: Add "Version Management" section documenting the new script
- **PATTERN**: Follow existing README structure and tone
- **IMPORTS**: None
- **GOTCHA**: Maintain the "No Bullshit" philosophy in documentation
- **VALIDATE**: Read updated README to ensure clarity

```markdown
## Version Management

### Bumping Template Versions

Before publishing templates, you must increment version numbers to avoid conflicts with existing published versions.

Use the automated bump script:

```bash
# Bump patch version (1.0.0 -> 1.0.1) for all templates
./scripts/bump-version.sh

# Bump minor version (1.0.0 -> 1.1.0)
./scripts/bump-version.sh --level minor

# Bump major version (1.0.0 -> 2.0.0)
./scripts/bump-version.sh --level major

# Preview changes without applying
./scripts/bump-version.sh --dry-run

# Bump and commit to git
./scripts/bump-version.sh --commit
```

### Publishing Templates

After bumping versions:

```bash
# Publish all templates
devcontainer templates publish ./src -r ghcr.io -n <your-org>/<repo>

# Or publish single template
devcontainer templates publish ./src/nanodev-node -r ghcr.io -n <your-org>/<repo>
```
```

### CREATE scripts/publish-templates.sh (Optional Enhancement)

- **IMPLEMENT**: Wrapper script combining bump + publish workflow
- **PATTERN**: Chain bump-version.sh + devcontainer publish
- **IMPORTS**: Calls bump-version.sh
- **GOTCHA**: Prompt for confirmation before publishing
- **VALIDATE**: Test with --dry-run to verify flow

```bash
#!/bin/bash
# Automated template publish workflow
# Bumps versions and publishes to OCI registry

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="${REGISTRY:-ghcr.io}"
NAMESPACE="${NAMESPACE:-}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_usage() {
    cat << EOF
${BLUE}DevContainer Template Publisher${NC}

Usage: $(basename "$0") [OPTIONS]

Options:
    -l, --level LEVEL       Version bump level: patch, minor, major (default: patch)
    -n, --namespace NS      Registry namespace (required, e.g., owner/repo)
    -r, --registry REG      OCI registry (default: ghcr.io)
    -d, --dry-run          Show what would happen without publishing
    -h, --help             Show this help message

Environment:
    NAMESPACE    Registry namespace (can be set instead of --namespace)
    REGISTRY     OCI registry (default: ghcr.io)

Examples:
    # Bump patch and publish
    $(basename "$0") --namespace myorg/myrepo

    # Bump minor and publish
    $(basename "$0") --level minor --namespace myorg/myrepo
EOF
}

main() {
    local level="patch"
    local dry_run="false"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -l|--level)
                level="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -r|--registry)
                REGISTRY="$2"
                shift 2
                ;;
            -d|--dry-run)
                dry_run="true"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                echo -e "${RED}Error: Unknown option: $1${NC}" >&2
                show_usage
                exit 1
                ;;
        esac
    done

    # Validate namespace
    if [[ -z "$NAMESPACE" ]]; then
        echo -e "${RED}Error: --namespace is required${NC}" >&2
        show_usage
        exit 1
    fi

    echo -e "${BLUE}=== DevContainer Template Publisher ===${NC}"
    echo -e "Registry: ${REGISTRY}"
    echo -e "Namespace: ${NAMESPACE}"
    echo -e "Bump level: ${level}"
    echo ""

    # Step 1: Bump versions
    echo -e "${BLUE}Step 1: Bumping versions...${NC}"
    if [[ "$dry_run" == "true" ]]; then
        "$SCRIPT_DIR/bump-version.sh" --level "$level" --dry-run
    else
        "$SCRIPT_DIR/bump-version.sh" --level "$level" --commit
    fi
    echo ""

    # Step 2: Publish
    if [[ "$dry_run" == "false" ]]; then
        echo -e "${BLUE}Step 2: Publishing templates...${NC}"
        echo -e "${YELLOW}Publishing to ${REGISTRY}/${NAMESPACE}...${NC}"

        devcontainer templates publish ./src \
            -r "$REGISTRY" \
            -n "$NAMESPACE"

        echo ""
        echo -e "${GREEN}✓ Templates published successfully!${NC}"
        echo -e "View at: https://${REGISTRY}/${NAMESPACE}"
    else
        echo -e "${YELLOW}[DRY RUN] Skipping actual publish${NC}"
        echo -e "Would run: devcontainer templates publish ./src -r $REGISTRY -n $NAMESPACE"
    fi
}

main "$@"
```

---

## TESTING STRATEGY

### Unit Tests

**Scope**: Test individual functions in isolation

- `parse_version()`: Valid semver, invalid formats, edge cases
- `increment_version()`: All three levels (patch/minor/major), version resets
- `find_templates()`: Single template, multiple templates, no templates

**Approach**: Create minimal test harness in bash

```bash
# Test parse_version
assert_equals "$(parse_version '1.2.3')" "1 2 3"
assert_fails "parse_version 'invalid'"

# Test increment_version
assert_equals "$(increment_version '1.2.3' 'patch')" "1.2.4"
assert_equals "$(increment_version '1.2.3' 'minor')" "1.3.0"
assert_equals "$(increment_version '1.2.3' 'major')" "2.0.0"
```

### Integration Tests

**Scope**: Test complete workflow end-to-end

- Bump all templates in dry-run mode
- Bump single template
- Bump and verify JSON integrity
- Bump and commit to git (in test branch)

**Approach**: Create test templates in temporary directory

```bash
# Create test environment
test_dir=$(mktemp -d)
cp -r src/nanodev-node "$test_dir/"

# Run bump
./scripts/bump-version.sh --target "$test_dir/nanodev-node" --level minor

# Verify
new_version=$(jq -r '.version' "$test_dir/nanodev-node/devcontainer-template.json")
assert_equals "$new_version" "3.1.0"  # Was 3.0.0
```

### Edge Cases

- **Empty directory**: No templates found
- **Malformed JSON**: Invalid devcontainer-template.json
- **Invalid semver**: Non-numeric version components
- **File permissions**: Read-only template files
- **Git conflicts**: Uncommitted changes when using --commit
- **Missing jq**: Script fails gracefully with clear error

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Dependencies

```bash
# Verify bash syntax
bash -n scripts/bump-version.sh

# Verify jq is available
command -v jq || echo "ERROR: jq not found"

# Verify all templates are valid JSON
for file in src/*/devcontainer-template.json; do
    jq . "$file" > /dev/null || echo "ERROR: Invalid JSON in $file"
done
```

### Level 2: Unit Tests

```bash
# Source functions for testing
source scripts/bump-version.sh

# Test parse_version
parse_version "1.2.3" | grep -q "1 2 3" && echo "✓ parse_version works"

# Test increment_version
[[ "$(increment_version '1.2.3' 'patch')" == "1.2.4" ]] && echo "✓ patch increment works"
[[ "$(increment_version '1.2.3' 'minor')" == "1.3.0" ]] && echo "✓ minor increment works"
[[ "$(increment_version '1.2.3' 'major')" == "2.0.0" ]] && echo "✓ major increment works"
```

### Level 3: Integration Tests

```bash
# Test dry-run mode (should not modify files)
cp -r src src-backup
./scripts/bump-version.sh --dry-run
diff -r src src-backup && echo "✓ Dry-run does not modify files"
rm -rf src-backup

# Test actual bump
BEFORE=$(jq -r '.version' src/nanodev-node/devcontainer-template.json)
./scripts/bump-version.sh --target src/nanodev-node --level patch
AFTER=$(jq -r '.version' src/nanodev-node/devcontainer-template.json)
echo "Version changed: $BEFORE -> $AFTER"

# Revert for clean state
git checkout src/nanodev-node/devcontainer-template.json
```

### Level 4: Manual Validation

```bash
# Test complete workflow
./scripts/bump-version.sh --help  # Should show usage
./scripts/bump-version.sh --dry-run  # Should preview changes
./scripts/bump-version.sh --level minor  # Should bump versions
git diff src/*/devcontainer-template.json  # Verify changes
git checkout src/  # Revert for now

# Test error cases
./scripts/bump-version.sh --level invalid  # Should show error
./scripts/bump-version.sh --target /nonexistent  # Should show error
```

### Level 5: Publish Workflow Test

```bash
# Test complete publish workflow (in dry-run mode)
./scripts/publish-templates.sh --namespace test/test --dry-run

# Verify script is executable
[[ -x scripts/bump-version.sh ]] && echo "✓ Script is executable"
[[ -x scripts/publish-templates.sh ]] && echo "✓ Publish script is executable"
```

---

## ACCEPTANCE CRITERIA

- [x] Script successfully parses all existing template versions
- [x] Script correctly increments patch/minor/major versions according to semver
- [x] Script updates JSON files without corrupting them
- [x] Dry-run mode shows accurate preview without modifying files
- [x] Script provides color-coded, user-friendly output
- [x] Script handles errors gracefully with clear messages
- [x] All validation commands pass with zero errors
- [x] Documentation added to README explaining usage
- [x] Script is executable and works from any directory
- [x] Optional git commit feature works correctly
- [x] Optional publish wrapper script integrates bump + publish workflow

---

## COMPLETION CHECKLIST

- [ ] `scripts/bump-version.sh` created with all functions
- [ ] Script is executable (`chmod +x scripts/bump-version.sh`)
- [ ] All validation commands pass
- [ ] Tested on all three templates
- [ ] Dry-run mode verified to not modify files
- [ ] Git commit feature tested
- [ ] README updated with usage documentation
- [ ] Optional `scripts/publish-templates.sh` created
- [ ] Both scripts tested end-to-end
- [ ] No syntax errors (`bash -n` passes)
- [ ] All edge cases handled gracefully

---

## NOTES

### Design Decisions

**Why bash instead of Node.js/Python?**
- No additional dependencies required
- Consistent with existing test scripts
- Simple string manipulation is bash's strength
- jq handles JSON better than bash builtins would

**Why atomic file updates (temp file + mv)?**
- Prevents corruption if script is interrupted mid-update
- Standard Unix pattern for safe file modifications
- mv is atomic on most filesystems

**Why separate publish script?**
- Separation of concerns: bump vs publish
- Some users may want to verify changes before publishing
- Allows manual publishing with external tools
- Wrapper script is optional convenience

### Alternative Approaches Considered

1. **npm version command**: Would require package.json, adding Node.js dependency
2. **Git tags for versioning**: Disconnects from registry requirement for `devcontainer-template.json`
3. **Python script**: Adds dependency, no significant benefit over bash+jq
4. **Manual editing**: Current approach, fails frequently (the problem we're solving)

### Future Enhancements

- **Conventional Commits integration**: Parse commit messages to auto-determine bump level
- **Changelog generation**: Automatically update CHANGELOG.md based on git history
- **Pre-publish validation**: Check if version already exists in registry before bumping
- **Template-specific bumping**: Allow bumping individual templates with `--template` flag

### Potential Issues

**Issue**: User runs script from wrong directory
**Mitigation**: Script accepts `--target` to specify src directory path

**Issue**: jq not installed
**Mitigation**: Add dependency check at script start with clear error message

**Issue**: Git working directory has uncommitted changes
**Mitigation**: Check git status before committing, warn user

**Issue**: Multiple developers bump versions simultaneously
**Mitigation**: Git merge conflicts in JSON are human-readable, easy to resolve

<!-- EOF -->