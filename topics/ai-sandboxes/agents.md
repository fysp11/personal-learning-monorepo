# Agent Sandbox Implementations

This document covers how major AI coding agents implement sandboxing - the security boundaries that let agents operate autonomously without unrestricted access to your system.

---

## Claude Code (Anthropic)

### Overview

Claude Code features native sandboxing that reduces permission prompts by **84%** while maintaining security. It uses OS-level primitives for filesystem and network isolation.

### Sandbox Architecture

#### Two Isolation Layers

1. **Filesystem isolation** - restricts which directories can be accessed
2. **Network isolation** - controls outbound network access

Both must work together - without network isolation, a compromised agent could escape the filesystem sandbox.

#### Platform-Specific Implementation

| Platform | Technology | Details |
|----------|------------|---------|
| **macOS** | Seatbelt | Uses `sandbox-exec` with profile |
| **Linux** | bubblewrap | Uses `bwrap` for namespace isolation |
| **WSL2** | bubblewrap | Requires kernel features |
| **WSL1** | Unsupported | Missing kernel features |

### Sandbox Modes

#### Auto-allow Mode
- Commands that can run inside sandbox are automatically approved
- Commands requiring permissions outside sandbox fall back to normal flow

#### Regular Permissions Mode
- All bash commands go through approval flow
- Same sandbox restrictions, but always asks first

### Configuration

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "failIfUnavailable": false
  }
}
```

#### Filesystem Settings

```json
{
  "sandbox": {
    "filesystem": {
      "allowWrite": ["../shared-lib", "~/reference"],
      "denyRead": ["/etc", "/root"]
    }
  }
}
```

### Security Model

#### What the Sandbox Restricts

- **Read access** - can only read allowed directories
- **Write access** - can only write to current working directory (default)
- **Network access** - blocked by default, configurable allowlist

#### Child Process Inheritance

All subprocesses spawned by Claude Code commands inherit the same sandbox boundaries. This is critical for tools like `git`, `npm`, `pip` that spawn additional processes.

#### Escape Hatch

When a command fails due to sandbox restrictions, Claude Code may:
1. Analyze the failure
2. Retry with `dangerouslyDisableSandbox` (goes through normal permission flow)

This can be disabled with `allowUnsandboxedCommands: false`.

### Cloud Version (codex.ai)

Claude Code on the web runs in **Gvisor-isolated sandboxes** on Anthropic's infrastructure:
- Each session gets a fresh Ubuntu-based container
- Network access configurable (allow package registries)
- No file persistence between tasks

### Open Source

Anthropic has open-sourced the sandbox runtime:
- npm package for building safer agents
- Available at [github.com/anthropics/claude-code-sandbox](https://github.com/anthropics/claude-code-sandbox)

---

## OpenAI Codex

### Overview

Codex takes a **dual-surface approach** - runs differently in the cloud vs locally. The cloud version (Codex app) is more restrictive; local (CLI/IDE) gives more control.

### Two Execution Modes

#### Cloud Threads (Codex App)

- Repository cloned into isolated cloud environment (microVM)
- **No network access** - cannot pip install, call external APIs, exfil code
- Hard security boundary - not soft guidelines
- Output is always PR/diff, never direct edits to working tree

#### Local Threads (CLI/IDE)

- OS-level sandbox enforcement
- Platform-native: Seatbelt (macOS), Landlock+seccomp (Linux), AppContainer (Windows)
- Not prompts - actual OS-level prevention

### Three Sandbox Modes

| Mode | Disk Read | Disk Write | Network | Protected Paths |
|------|-----------|------------|---------|-----------------|
| **ReadOnly** | Full | None | Disabled | N/A |
| **WorkspaceWrite** | Full | cwd + configured roots | Optional | .git, .codex |
| **DangerFullAccess** | Full | Full | Enabled | None |

### Approval Policies

| Policy | Behavior |
|--------|----------|
| **untrusted** | Ask before running any command not in trusted set |
| **on-request** | Work inside sandbox, ask when leaving boundaries |
| **never** | Never ask (full-auto mode) |

### Platform Implementation

#### macOS 12+
- **Seatbelt** via `sandbox-exec`
- Profile corresponds to selected sandbox mode
- Hardcoded path `/usr/bin/sandbox-exec` for security

#### Linux
- **Landlock** - filesystem restrictions
- **seccomp** - syscall filtering
- Falls back to vendored bubblewrap if system bwrap unavailable

#### Windows (Experimental)
- **AppContainer** profile
- Capability-based filesystem access
- Network disabled via proxy/env var overrides
- Limitation: cannot prevent writes in world-writable directories

### Configuration

```toml
# ~/.codex/config.toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"

[sandbox_workspace_write]
writable_roots = ["/Users/cobus/projects/my-app/src"]
network_access = true
```

### Security Features

#### Protected Paths
- `.git/` and `.codex/` automatically protected in writable roots
- Prevents modifying git hooks or sandbox config

#### Process Hardening
- Runs before main() via constructor
- macOS: hardened runtime + library validation

#### Environment Filtering
- `CODEX_`-prefixed variables filtered from .env

#### Windows Limitations
- Cannot prevent writes to world-writable folders
- Active development on improvements

---

## OpenCode (Anomaly)

### Overview

OpenCode **does not have built-in sandboxing**. It's designed to run locally with user permission prompts, not OS-level isolation. For true security, run OpenCode inside Docker, Modal, or Daytona.

### Native Security Model

#### No Sandbox

From official security docs:
> OpenCode does not sandbox the agent. The permission system exists as a UX feature to help users stay aware of what actions the agent is taking - it prompts for confirmation before executing commands, writing files, etc. However, it is not designed to provide security isolation.

#### Server Mode

- Opt-in only
- Requires `OPENCODE_SERVER_PASSWORD` for HTTP Basic Auth
- Without password, runs unauthenticated (with warning)

### Available Tools

| Tool | Description |
|------|-------------|
| Bash | Execute shell commands |
| Read | Read files |
| Write | Write files |
| Search | Search code (ripgrep integration) |
| Fetch | Web requests |
| MCP | Model Context Protocol servers |

### Banned Commands

```go
var bannedCommands = []string{
    "alias", "curl", "wget", "nc", "telnet", "lynx",
    "chrome", "firefox", "safari",
}
```

These are blocked at the tool level, not OS-level.

### External Sandbox Integration

Since OpenCode lacks native sandboxing, it integrates with external providers:

#### 1. Docker Sandbox (opencode-sandbox)
- Network isolation via squid proxy
- Domain whitelisting
- Filesystem isolation (project directory only)
- Auto-cleanup on exit

```
┌─────────────────┐     ┌─────────────────┐
│  Proxy (squid)  │◄────│ Agent Container │
│  Domain allow  │     │    (opencode)   │
└─────────────────┘     └─────────────────┘
```

#### 2. Vercel Sandbox
- MicroVM isolation
- Network policy via `updateNetworkPolicy()`
- Credential brokering at firewall level

#### 3. E2B Integration
- Firecracker microVMs
- codecloud uses this in production

#### 4. Daytona Integration
- Official SDK example
- Full sandbox lifecycle management

#### 5. Modal Integration
- Official example from Modal docs
- GPU-enabled sandboxes

### Recommendations for Running OpenCode

For security-sensitive use cases:

1. **Use Docker** - `opencode-sandbox` wrapper
2. **Network isolation** - proxy with domain allowlist
3. **Ephemeral environments** - destroy after each session
4. **Credential management** - don't expose keys in sandbox

---

## Hermes (Nous Research)

### Overview

Hermes provides multiple sandbox options:
- **execute_code** - local Python sandbox with RPC tool calling
- **terminal backends** - docker, modal, daytona, singularity, ssh, local

### Code Execution (execute_code)

#### How It Works

1. Agent writes Python script using `from hermes_tools import ...`
2. Hermes generates RPC stub module
3. Opens Unix domain socket, starts listener thread
4. Script runs in child process - tool calls over socket
5. Only `print()` output returns to LLM

#### Available Tools in Sandbox

- `web_search`, `web_extract`
- `read_file`, `write_file`, `search_files`, `patch`
- `terminal` (foreground only)

#### What Doesn't Enter Context

- Intermediate tool results
- Only final `print()` output comes back

This is programmatic tool calling - reduces context window usage.

### Resource Limits

| Resource | Limit | Notes |
|----------|-------|-------|
| Timeout | 5 minutes (300s) | SIGTERM then SIGKILL after 5s |
| Max tool calls | 100 | Configurable |
| Output size | 100KB | Configurable |

### Terminal Backends

| Backend | Isolation | Dangerous Cmd Check | Best For |
|---------|-----------|---------------------|----------|
| local | None | ✅ Yes | Development |
| ssh | Remote machine | ✅ Yes | Remote servers |
| docker | Container | ❌ Skipped | Production |
| singularity | Container | ❌ Skipped | HPC |
| modal | Cloud sandbox | ❌ Skipped | Scalable cloud |
| daytona | Cloud sandbox | ❌ Skipped | Persistent workspaces |

### Docker Security Settings

```python
_SECURITY_ARGS = [
    "--cap-drop=ALL",
    "--security-opt=no-new-privileges",
    # ... more hardening
]
```

### Environment Variable Filtering

Both `execute_code` and `terminal` strip sensitive variables:

**Blocked patterns:**
- `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL`, `PASSWD`, `AUTH`

**Allowed by default:**
- `PATH`, `HOME`, `LANG`, `SHELL`, `PYTHONPATH`, `VIRTUAL_ENV`

**Skill passthrough:**
- Skills can declare `required_environment_variables` in frontmatter
- Automatically passed to sandbox

### Security Model Summary

1. **User authorization** - allowlists, DM pairing
2. **Dangerous command approval** - human-in-the-loop
3. **Container isolation** - Docker/Singularity/Modal/Daytona
4. **MCP credential filtering** - env var isolation
5. **Context file scanning** - prompt injection detection
6. **Cross-session isolation** - sessions cannot access each other

---

## Comparison Matrix

| Agent | Native Sandbox | Primary Tech | Network Control | Cloud Version |
|-------|---------------|--------------|-----------------|----------------|
| Claude Code | ✅ Yes | Seatbelt/bubblewrap | Configurable | ✅ (Gvisor) |
| OpenAI Codex | ✅ Yes | Seatbelt/Landlock | Off by default | ✅ (microVM) |
| OpenCode | ❌ No | External only | Depends on sandbox | ❌ |
| Hermes | ✅ Yes | execute_code + backends | Per-backend | ❌ |

---

## Key Patterns Across Agents

### 1. Dual-Layer Security

All agents use two independent controls:
- **Technical sandbox** - OS-level enforcement
- **Approval policy** - human authorization

### 2. Child Process Inheritance

Sandbox boundaries must apply to all spawned processes, not just the agent itself.

### 3. Network as Primary Escape Vector

Without network isolation, filesystem sandbox can be escaped. All cloud implementations disable network by default.

### 4. Zero-Trust Assumption

Assume the agent will eventually be compromised. Design for:
- Limited blast radius
- Credential expiration
- Audit logging
- Data segmentation

---

## References

- [Claude Code Sandboxing](https://docs.anthropic.com/en/docs/claude-code/sandboxing)
- [OpenAI Codex Sandboxing](https://developers.openai.com/codex/concepts/sandboxing)
- [OpenCode Security](https://github.com/anomalyco/opencode/security)
- [Hermes Code Execution](https://hermes-agent.nousresearch.com/docs/user-guide/features/code-execution/)
- [Hermes Security](https://hermes-agent.nousresearch.com/docs/user-guide/security/)