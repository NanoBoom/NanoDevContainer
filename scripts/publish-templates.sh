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
