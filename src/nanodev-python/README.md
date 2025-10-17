# NanoDev-Python - Python Development Container Template

A batteries-included development container based on the official Python 3.13 image, optimized for modern Python development. Designed for data science, machine learning, backend services, and general Python projects with proper cross-platform support.

## What's Inside

**Languages & Runtimes:**
- **Python 3.13** + pip, venv
- **uv** - Modern Python package manager (faster than pip)
- **Node.js** + npm (for Claude Code CLI)

**Developer Tools:**
- **Claude Code** CLI + ccstatus (AI-powered coding assistant)

**Essential Utilities:**
- ripgrep, fd-find, jq, tree
- build-essential, curl, wget, git

## Why This Template?

### Real Problem #1: Path Mapping for macOS/Linux Hosts

**Problem:** Tools like Claude Code store absolute paths in config files:
- macOS host: `/Users/yourname/project/file.py`
- Linux container: `/home/dev/project/file.py`

When you mount `~/.claude` into the container, paths break.

**Solution:** This template creates symbolic links:
```
/Users/yourname -> /home/dev
/home/yourname -> /home/dev
```

Now config files with host absolute paths work inside the container.

### Real Problem #2: UID/GID Mismatch

**Problem:** Container root creates files, host user can't edit them.

**Solution:** Container user matches host UID/GID (default 1000, configurable).

## Usage

### Quick Start (VS Code)

1. Open Command Palette (`Cmd/Ctrl + Shift + P`)
2. Run: `Dev Containers: Add Dev Container Configuration Files...`
3. Select: `NanoDev Python Container`
4. Rebuild container

### Configuration Options

```json
{
  "userName": "dev",          // Container username (custom user for development)
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
| `~/.ssh` | `/home/dev/.ssh` | SSH keys (read-only) |
| `~/.gitconfig` | `/home/dev/.gitconfig` | Git config |
| `~/.claude` | `/home/dev/.claude` | Claude Code config |
| `~/Downloads` | `/home/dev/Downloads` | Downloads |

**To customize:** Edit `.devcontainer/devcontainer.json` mounts section.

## Networking

Uses `--network=host` for simplicity:
- Container shares host's network stack
- No port forwarding needed
- Service on `localhost:8000` in container = `localhost:8000` on host

**Trade-off:** Less network isolation. Disable if you need strict isolation.

## Platform Support

Tested on:
- **amd64** (Intel/AMD x86_64)
- **arm64** (Apple Silicon M1/M2/M3, ARM servers)

Auto-detects architecture and downloads correct binaries.

## Typical Workflows

### Using uv Package Manager

```bash
# Create new project with uv
uv init my-project
cd my-project

# Add dependencies
uv add requests pandas numpy

# Create virtual environment and install dependencies
uv sync

# Run Python script
uv run python script.py
```

### Traditional pip Workflow

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Data Science with Jupyter

```bash
# Install Jupyter with uv
uv add jupyter notebook pandas matplotlib

# Start Jupyter server
uv run jupyter notebook
```

### FastAPI Backend Development

```bash
# Initialize project
uv init my-api
cd my-api

# Add dependencies
uv add fastapi uvicorn[standard]

# Create main.py and run
uv run uvicorn main:app --reload
```

## Troubleshooting

### File permission issues

Check if container user UID matches host:
```bash
# On host:
id -u

# In container:
id -u
```

If different, rebuild with correct `userUid`/`userGid`.

### Claude Code can't find files

Verify `HOST_USER` build arg:
```bash
# In container, check if symlink exists:
ls -la /Users/$USER  # macOS
ls -la /home/$USER   # Linux
```

Should point to `/home/dev`.

### uv command not found

Verify uv installation:
```bash
# Check uv is in PATH
which uv

# Reinstall if needed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Customization

### Add Python Global Tools

Edit `Dockerfile`, install after uv:
```dockerfile
RUN uv pip install --system \
    your-package-here
```

### Add VS Code Extensions

Edit `devcontainer.json`:
```json
"extensions": [
  "ms-python.python",
  "your-extension-id"
]
```

## Why uv?

**uv** is a modern Python package manager written in Rust:
- **10-100x faster** than pip for dependency resolution
- **Compatible** with pip and requirements.txt
- **Built-in** virtual environment management
- **Single binary** - no separate Python installation needed

Learn more: https://github.com/astral-sh/uv

## Differences from Other Templates

**vs `nanodev` (full-stack):**
- ❌ No Go runtime
- ❌ No CodeGPT CLI
- ❌ No Docker CLI
- ✅ Python 3.12 as primary runtime
- ✅ uv package manager
- ✅ Smaller image size

**vs `nanodev-node` (Node.js focused):**
- ❌ No TypeScript/ts-node
- ❌ No Expo/EAS/Vercel CLI
- ✅ Python 3.12 instead of Node.js as primary
- ✅ uv for modern Python workflow
- ✅ Data science friendly

**Use this template if:**
- You're building Python applications
- You want modern Python tooling (uv)
- You need data science libraries
- You want a lightweight Python environment

**Use `nanodev` if:**
- You need Go + Python + Node.js
- You're working on full-stack projects
- You need Docker CLI in container

**Use `nanodev-node` if:**
- You're building React Native or Next.js apps
- You only need Node.js/TypeScript
- You want frontend/mobile dev tools

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
- **Simple** over clever
- **Working** over perfect
- **Practical** over theoretical

If you need a container that just works for Python development, this is it.
