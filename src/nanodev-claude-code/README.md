# NanoDev-Claude-Code - Lightweight Claude Code Container

A lightweight development container based on Ubuntu 22.04, optimized specifically for Claude Code AI assistant workflows. Includes Python (uv) and Node.js (npx) for MCP server execution, with streamlined setup for fast startup and focused functionality.

## What's Inside

**Base System:**
- **Ubuntu 22.04** - Stable LTS base with excellent compatibility

**Languages & Runtimes:**
- **Python 3** + pip + **uv** (for Python MCP servers)
- **Node.js** + npm (for Node.js MCP servers with npx)

**Developer Tools:**
- **Claude Code** CLI (installed via official script)

**Essential Utilities:**
- ripgrep, fd, jq, tree
- bash, curl, wget, git

## Why This Template?

### Real Problem #1: Focused Tooling for AI Workflows

**Problem:** Full development containers (400MB+) include unnecessary tooling for AI-assisted workflows.

**Solution:** Ubuntu 22.04 base with only Claude Code essentials.

**Benefits:**
- Fast container startup time
- Lower memory footprint
- Streamlined image (~200MB vs 400MB+ for full stacks)
- Full glibc compatibility (unlike Alpine musl)

### Real Problem #2: MCP Server Compatibility

**Problem:** Claude Code needs Python (uv) and Node.js (npx) to run MCP servers.

**Solution:** Both runtimes pre-installed with system packages.

**Use Cases:**
- File system MCP servers (Python/uv)
- API integration MCP servers (Node.js/npx)
- Database MCP servers (Python)
- Custom tool servers

### Real Problem #3: Path Mapping for macOS/Linux Hosts

**Problem:** Tools like Claude Code store absolute paths in config files:
- macOS host: `/Users/yourname/project/file.py`
- Linux container: `/home/node/project/file.py`

**Solution:** This template creates symbolic links:
```
/Users/yourname -> /home/node
/home/yourname -> /home/node
```

### Real Problem #4: UID/GID Mismatch

**Problem:** Container root creates files, host user can't edit them.

**Solution:** Container user matches host UID/GID (default 1000, configurable).

## Usage

### Quick Start (VS Code)

1. Open Command Palette (`Cmd/Ctrl + Shift + P`)
2. Run: `Dev Containers: Add Dev Container Configuration Files...`
3. Select: `NanoDev Claude Code Container`
4. Rebuild container

### Configuration Options

```json
{
  "userName": "node",         // Container username (consistent with nanodev-node)
  "userUid": "1000",          // Match your host UID (run `id -u`)
  "userGid": "1000"           // Match your host GID (run `id -g`)
}
```

**Find your UID/GID:**
```bash
id -u  # Your user ID
id -g  # Your group ID
```

### What Gets Mounted

By default, these host directories are mounted into the container:

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `~/.ssh` | `/home/node/.ssh` | SSH keys (read-only) |
| `~/.gitconfig` | `/home/node/.gitconfig` | Git config |
| `~/.claude` | `/home/node/.claude` | Claude Code config |
| `~/Downloads` | `/home/node/Downloads` | Downloads |

**To customize:** Edit `.devcontainer/devcontainer.json` mounts section.

## Networking

Uses `--network=host` for simplicity:
- Container shares host's network stack
- No port forwarding needed
- MCP servers on `localhost:8000` in container = `localhost:8000` on host

**Trade-off:** Less network isolation. Disable if you need strict isolation.

## Platform Support

Tested on:
- **amd64** (Intel/AMD x86_64)
- **arm64** (Apple Silicon M1/M2/M3, ARM servers)

Auto-detects architecture and installs correct binaries.

## Typical Workflows

### Using Claude Code with MCP Servers

```bash
# Claude Code automatically detects uv and npx

# Python MCP server example (using uv)
claude-code --mcp filesystem

# Node.js MCP server example (using npx)
claude-code --mcp @modelcontextprotocol/server-github

# Custom MCP server configuration in ~/.claude/mcp_settings.json
{
  "mcpServers": {
    "my-server": {
      "command": "uv",
      "args": ["run", "python", "-m", "my_mcp_server"]
    }
  }
}
```

### Basic Development Tasks

```bash
# Edit configuration files
vim ~/.bashrc

# Search code with ripgrep
rg "TODO" .

# Find files with fd
fd -e py

# Process JSON with jq
curl -s https://api.example.com | jq '.data'

# Git operations
git clone https://github.com/user/repo.git
cd repo
git status
```

### Installing Additional Tools

```bash
# Ubuntu package manager
sudo apt-get update && sudo apt-get install -y htop tmux

# Python packages (system-wide)
sudo pip3 install requests

# Python packages (uv virtual environment)
uv venv
uv pip install fastapi

# Node.js packages (global)
sudo npm install -g typescript
```

## Troubleshooting

### MCP server fails to start (Python)

Check uv installation:
```bash
# Verify uv is installed
uv --version

# Reinstall if needed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### MCP server fails to start (Node.js)

Check npm/npx installation:
```bash
# Verify Node.js tools
node --version
npm --version
npx --version

# Check npm global path
npm config get prefix
```

### File permission issues

Check if container user UID matches host:
```bash
# On host:
id -u

# In container:
id -u
```

If different, rebuild with correct `userUid`/`userGid`.

### Claude Code path issues

Verify `HOST_USER` build arg:
```bash
# In container, check if symlink exists:
ls -la /Users/$USER  # macOS
ls -la /home/$USER   # Linux
```

Should point to `/home/node`.

## Customization

### Add Ubuntu Packages

Edit `Dockerfile`:
```dockerfile
RUN apt-get update && apt-get install -y \
    your-package-here \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

### Add Python Packages (System-Wide)

Edit `Dockerfile`:
```dockerfile
RUN pip3 install --no-cache-dir \
    your-package-here
```

### Add Node.js Packages (Global)

Edit `Dockerfile`:
```dockerfile
RUN npm install -g \
    your-package-here \
    && npm cache clean --force
```

### Add VS Code Extensions

Edit `devcontainer.json`:
```json
"extensions": [
  "ms-python.python",
  "your-extension-id"
]
```

## Differences from Other Templates

**vs `nanodev-node` (Node.js focused):**
- ✅ ~50% smaller image size
- ✅ Faster startup
- ❌ No TypeScript/Expo/Vercel tools
- ✅ Full glibc compatibility
- ✅ Optimized for Claude Code workflows

**vs `nanodev-python` (Python focused):**
- ✅ ~55% smaller image size
- ✅ Ubuntu base (same compatibility)
- ❌ No data science libraries
- ✅ Focused on AI-assisted editing

**Use this template if:**
- You primarily use Claude Code for development
- You want a lightweight, focused container
- You need MCP server support (Python/Node.js)
- You're doing configuration/script editing
- You value fast startup and low resource usage

**Use `nanodev-node` if:**
- You need full TypeScript/React Native tooling
- You want maximum compatibility
- You're building production applications

**Use `nanodev-python` if:**
- You need data science libraries
- You want Python 3.13
- You're doing heavy Python development

## Contributing

Found a bug? Have a real use case that's not covered?

**Before requesting features:**
- Is this a real problem you've actually encountered?
- Can you solve it by editing the generated files?
- Would this benefit most users, or just your specific case?

We prioritize simplicity over flexibility. Most requests should be:
"Here's a real problem [describe], here's how to fix it [patch]."

Not:
"Add support for every possible X because someone might need it."

## License

MIT - Do whatever you want with it.

## Credits

Built for teams who value:
- **Focused** over bloated
- **Fast** over comprehensive
- **Practical** over theoretical

If you need a lightweight container optimized for Claude Code workflows, this is it.
