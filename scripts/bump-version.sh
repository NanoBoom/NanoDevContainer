#!/bin/bash
# DevContainer Template Version Bumper
# Automatically increments semver versions in devcontainer-template.json files

set -e  # Exit on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

parse_version() {
    local version="$1"

    if [[ ! "$version" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        echo -e "${RED}Error: Invalid semver format: $version${NC}" >&2
        return 1
    fi

    echo "${BASH_REMATCH[1]} ${BASH_REMATCH[2]} ${BASH_REMATCH[3]}"
}

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
