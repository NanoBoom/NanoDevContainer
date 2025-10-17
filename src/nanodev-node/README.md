# NanoDev-Node - Node.js Development Container Template

A batteries-included development container based on the official Node.js 24 image, optimized for frontend and mobile development. Designed for React Native/Expo and Next.js projects with proper cross-platform support.

## What's Inside

**Languages & Runtimes:**
- **Node.js** LTS + npm, yarn, pnpm
- **Python 3** + [uv](https://github.com/astral-sh/uv) (for AI MCP servers)

**Node.js Global Tools:**
- **TypeScript** + ts-node (global `tsc` and `ts-node` commands)
- **Expo CLI** + **EAS CLI** (React Native/Expo development)
- **Vercel CLI** (Next.js deployment)
- **Claude Code** CLI + ccstatus

**Essential Utilities:**
- ripgrep, fd-find, jq, tree
- build-essential, curl, wget, git

## Why This Template?

### Real Problem #1: Path Mapping for macOS/Linux Hosts

**Problem:** Tools like Claude Code store absolute paths in config files:
- macOS host: `/Users/yourname/project/file.py`
- Linux container: `/home/node/project/file.py`

When you mount `~/.claude` into the container, paths break.

**Solution:** This template creates symbolic links:
```
/Users/yourname -> /home/node
/home/yourname -> /home/node
```

Now config files with host absolute paths work inside the container.

### Real Problem #2: UID/GID Mismatch

**Problem:** Container root creates files, host user can't edit them.

**Solution:** Container user matches host UID/GID (default 1000, configurable).

## Usage

### Quick Start (VS Code)

1. Open Command Palette (`Cmd/Ctrl + Shift + P`)
2. Run: `Dev Containers: Add Dev Container Configuration Files...`
3. Select: `NanoDev Node.js Container`
4. Rebuild container

### Configuration Options

```json
{
  "userName": "node",         // Container username (uses official Node.js image's default)
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
- Service on `localhost:3000` in container = `localhost:3000` on host

**Trade-off:** Less network isolation. Disable if you need strict isolation.

## Platform Support

Tested on:
- **amd64** (Intel/AMD x86_64)
- **arm64** (Apple Silicon M1/M2/M3, ARM servers)

Auto-detects architecture and downloads correct binaries.

## Typical Workflows

### React Native with Expo

```bash
# Initialize new Expo project
npx create-expo-app my-app
cd my-app

# Start development server
npm start

# Build and deploy
eas build --platform ios
eas submit --platform ios
```

### Next.js Project

```bash
# Create Next.js app
npx create-next-app@latest my-app
cd my-app

# Development
npm run dev

# Deploy to Vercel
vercel deploy
```

### TypeScript Development

```bash
# Compile TypeScript
tsc file.ts

# Run TypeScript directly
ts-node script.ts
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

Should point to `/home/node`.

## Customization

### Add More Node.js Global Tools

Edit `Dockerfile`, add to the npm install line:
```dockerfile
&& npm install -g \
    your-package-here \
```

### Add VS Code Extensions

Edit `devcontainer.json`:
```json
"extensions": [
  "dbaeumer.vscode-eslint",
  "your-extension-id"
]
```

## Differences from `nanodev` Template

This template is a **lightweight variant** of the full-stack `nanodev` template:

**Removed:**
- Go runtime and toolchain
- CodeGPT CLI

**Added:**
- TypeScript + ts-node (global commands)
- Vercel CLI (Next.js deployment)

**Retained:**
- Python + uv (for AI MCP servers)
- All essential dev tools

**Use this template if:**
- You only need Node.js/TypeScript
- You're building React Native or Next.js apps
- You want a smaller, faster-building image

**Use `nanodev` if:**
- You need Go for backend services
- You're working on full-stack projects
- You need CodeGPT CLI

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

If you need a container that just works for Node.js development, this is it.
