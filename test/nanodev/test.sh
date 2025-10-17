#!/bin/bash
# NanoDev Template Test Script
# Tests all installed tools and validates configuration

set -e  # Exit on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED_TESTS=()

# Test function wrapper
test_command() {
    local name="$1"
    local command="$2"
    local expected_pattern="$3"

    echo -n "Testing ${name}... "

    if output=$($command 2>&1); then
        if [[ -z "$expected_pattern" ]] || echo "$output" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}✓${NC}"
            return 0
        else
            echo -e "${RED}✗${NC} (unexpected output: $output)"
            FAILED_TESTS+=("$name")
            return 1
        fi
    else
        echo -e "${RED}✗${NC} (command failed)"
        FAILED_TESTS+=("$name")
        return 1
    fi
}

# Test function for checking file existence
test_file() {
    local name="$1"
    local file="$2"

    echo -n "Checking ${name}... "

    if [[ -e "$file" ]]; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC} (not found: $file)"
        FAILED_TESTS+=("$name")
        return 1
    fi
}

echo "=========================================="
echo "NanoDev Template Installation Test"
echo "=========================================="
echo ""

# Test shell
echo "=== Shell & Environment ==="
test_command "Bash" "bash --version" "bash"

echo ""

# Test languages
echo "=== Programming Languages ==="
test_command "Go" "go version" "go version"
test_command "Node.js" "node --version" "v"
test_command "npm" "npm --version" ""
test_command "yarn" "yarn --version" ""
test_command "pnpm" "pnpm --version" ""
test_command "Python 3" "python3 --version" "Python 3"
test_command "uv" "uv --version" "uv"

echo ""

# Test dev tools
echo "=== Development Tools ==="
test_command "Docker CLI" "docker --version" "Docker version"
test_command "Docker Compose" "docker compose version" "Docker Compose version"
test_command "CodeGPT" "codegpt --version" ""
test_command "Git" "git --version" "git version"

echo ""

# Test CLI utilities
echo "=== CLI Utilities ==="
test_command "ripgrep" "rg --version" "ripgrep"
test_command "fd" "fdfind --version" "fd"
test_command "jq" "jq --version" "jq"
test_command "tree" "tree --version" "tree"
test_command "htop" "which htop" "htop"
test_command "curl" "curl --version" "curl"
test_command "wget" "wget --version" "GNU Wget"

echo ""

# Test React Native tools
echo "=== React Native Tools ==="
test_command "Expo CLI" "npx expo --version" ""
test_command "EAS CLI" "eas --version" "eas-cli"

echo ""

# Test user configuration
echo "=== User Configuration ==="
USER_ID=$(id -u)
GROUP_ID=$(id -g)
USERNAME=$(whoami)

echo "User: ${USERNAME}"
echo "UID: ${USER_ID}"
echo "GID: ${GROUP_ID}"
echo "Home: ${HOME}"
echo "Shell: ${SHELL}"

if [[ "$SHELL" == "/bin/bash" ]]; then
    echo -e "Default shell: ${GREEN}✓${NC}"
else
    echo -e "Default shell: ${YELLOW}⚠${NC} (expected /bin/bash, got $SHELL)"
fi

echo ""

# Test path mappings (if HOST_USER is set)
if [[ -n "$HOST_USER" ]]; then
    echo "=== Path Mappings ==="
    test_file "Host user home symlink (Linux)" "/home/$HOST_USER"
    test_file "Host user home symlink (macOS)" "/Users/$HOST_USER"
    echo ""
fi

# Test environment variables
echo "=== Environment Variables ==="
test_command "GOPATH" "echo \$GOPATH" "$HOME/go"
test_command "PATH includes Go" "echo \$PATH | grep go" "go"
test_command "PATH includes cargo" "echo \$PATH | grep cargo" "cargo"

echo ""
echo "=========================================="

if [[ ${#FAILED_TESTS[@]} -eq 0 ]]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    echo "NanoDev container is ready for development."
    exit 0
else
    echo -e "${RED}${#FAILED_TESTS[@]} test(s) failed:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  - $test"
    done
    exit 1
fi
