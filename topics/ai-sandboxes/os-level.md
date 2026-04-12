# OS-Level Sandboxing Technologies

This document covers the operating system primitives used by AI coding agents for local sandboxing - bubblewrap (Linux), Seatbelt (macOS), and Landlock (Linux).

---

## bubblewrap (bwrap)

### Overview

bubblewrap is a low-level unprivileged sandboxing tool used by Flatpak and other projects. It creates isolated environments using Linux kernel namespaces without requiring root access.

**Used by:** Claude Code (Linux), OpenAI Codex (Linux)

### Core Features

| Feature | Description |
|---------|-------------|
| **Namespaces** | User, PID, IPC, Network, UTS, Mount |
| **Filesystem** | Bind mounts (ro/rw), tmpfs, symlinks |
| **Security** | seccomp filters, capability dropping |
| **Unprivileged** | Uses user namespaces without setuid |

### Installation

```bash
# Ubuntu/Debian
sudo apt install bubblewrap

# Fedora/RHEL
sudo dnf install bubblewrap

# From source
git clone https://github.com/containers/bubblewrap.git
cd bubblewrap
meson setup _builddir
meson compile -C _builddir
meson install -C _builddir
```

### Basic Usage

```bash
# Minimal sandbox with read-only system
bwrap \
  --ro-bind /usr /usr \
  --symlink usr/lib64 /lib64 \
  --symlink usr/bin /bin \
  --proc /proc \
  --dev /dev \
  bash

# Network-enabled sandbox with project access
bwrap \
  --ro-bind /usr /usr \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /etc/resolv.conf /etc/resolv.conf \
  --ro-bind /etc/ssl /etc/ssl \
  --proc /proc \
  --dev /dev \
  --tmpfs /tmp \
  --bind "$PWD" "$PWD" \
  --chdir "$PWD" \
  --unshare-pid \
  --share-net \
  bash
```

### Key Options

#### Filesystem Mounts

| Option | Description |
|--------|-------------|
| `--ro-bind /src /dest` | Read-only bind mount |
| `--bind /src /dest` | Read-write bind mount |
| `--tmpfs /path` | Mount tmpfs at path |
| `--symlink target /link` | Create symbolic link |
| `--dir /path` | Create empty directory |

#### Namespace Isolation

| Option | Description |
|--------|-------------|
| `--unshare-user` | New user namespace |
| `--unshare-pid` | New PID namespace |
| `--unshare-net` | New network namespace |
| `--unshare-ipc` | New IPC namespace |
| `--unshare-uts` | New UTS namespace |
| `--unshare-all` | All of the above |

#### Security Options

| Option | Description |
|--------|-------------|
| `--new-session` | Create new terminal session |
| `--die-with-parent` | Kill sandbox when parent exits |
| `--setenv KEY VALUE` | Set environment variable |
| `--chdir /path` | Change working directory |

### Security Considerations

#### TIOCSTI Sandbox Escape (CVE-2017-5226)

**Issue:** Without `--new-session`, processes can use TIOCSTI ioctl to inject characters into the terminal input buffer, potentially escaping the sandbox.

**Fix:** Always use `--new-session` which calls `setson()`.

#### Limitations

- No cgroup support (resource limits)
- Security depends entirely on options passed
- User must determine appropriate configuration

### Agent Usage Examples

#### Claude Code (Linux)

Claude Code uses bubblewrap when available, falls back to vendored version:

```rust
// Codex sandbox implementation
SandboxManager::select_initial() determines sandbox type
Uses bwrap for filesystem + network isolation
```

#### Custom Implementation

```python
import subprocess

def create_sandbox(project_dir):
    cmd = [
        'bwrap',
        '--ro-bind', '/usr', '/usr',
        '--ro-bind', '/lib', '/lib',
        '--ro-bind', '/lib64', '/lib64',
        '--proc', '/proc',
        '--dev', '/dev',
        '--tmpfs', '/tmp',
        '--bind', project_dir, project_dir,
        '--chdir', project_dir,
        '--unshare-pid',
        '--new-session',
        '--die-with-parent',
        '--share-net',  # Enable network
    ]
    return subprocess.Popen(cmd + ['bash'])
```

---

## Seatbelt (macOS)

### Overview

Seatbelt is macOS's built-in sandboxing framework, also known as sandbox-exec. It provides fine-grained control over what processes can access.

**Used by:** Claude Code (macOS), OpenAI Codex (macOS)

### Core Features

| Feature | Description |
|---------|-------------|
| **Sandbox Profiles** | Compile-time policy files (.sb) |
| **Entitlements** | Runtime permission grants |
| **Built-in** | No installation required |
| **System Integration** | Deep macOS integration |

### Basic Usage

```bash
# Check if sandbox-exec is available
which sandbox-exec

# Run command with sandbox profile
sandbox-exec -p <<'EOF'
(version 1)
(allow default)
(deny file-write* (regex #"/etc/passwd"))
EOF
bash
```

### Sandbox Profile Syntax

```
(version 1)

; Allow basic operations
(allow default)

; Deny specific paths
(deny file-write* (regex #"/private/etc/.*"))

; Allow network outbound
(allow network*)

; Allow file read in home
(allow file-read* (regex #"$HOME/.*"))
```

### Agent Usage Examples

#### Claude Code (macOS)

```rust
// Claude Code sandbox-exec invocation
// Path is hardcoded for security: /usr/bin/sandbox-exec
let profile = match sandbox_policy {
    SandboxPolicy::ReadOnly => generate_readonly_profile(),
    SandboxPolicy::WorkspaceWrite => generate_workspace_profile(roots),
    SandboxPolicy::DangerFullAccess => "",  // No sandbox
};

// Execute with sandbox
Command::new("sandbox-exec")
    .args(["-p", &profile, "bash", "-c", &cmd])
```

#### Profile Examples

**Read-only:**

```
(version 1)
(allow default)
(deny file-write*)
(deny network*)
```

**Workspace-write:**

```
(version 1)
(allow default)
(deny file-write* (regex #"^\.git/.*"))
(deny file-write* (regex #"^\.codex/.*"))
```

### Security Considerations

- Profiles are compiled (not interpreted)
- Entitlements system provides runtime permissions
- System-protected resources require specific entitlements

---

## Landlock

### Overview

Landlock is a Linux Security Module (LSM) introduced in kernel 5.13. It enables unprivileged processes to create filesystem access restrictions.

**Used by:** OpenAI Codex (Linux), some hardening tools

### Core Features

| Feature | Description |
|---------|-------------|
| **Unprivileged** | Any user can use it |
| **Filesystem-focused** | Path-based access control |
| **Stackable** | Multiple policies can combine |
| **No eBPF** | Dedicated syscall-based API |

### Comparison with Other LSMs

| Aspect | SELinux | AppArmor | Landlock |
|--------|---------|----------|----------|
| Privileged only | Yes | Yes | No |
| Filesystem only | No | No | Yes |
| Policy language | Labels | Paths | Paths |
| Complexity | High | Medium | Low |

### How It Works

1. Create a ruleset with allowed accesses
2. Add filesystem rules (directories/files)
3. Enforce the ruleset on current process
4. Rules are inherited by child processes

### Basic Usage (C)

```c
#define _GNU_SOURCE
#include <linux/landlock.h>
#include <sys/syscall.h>

int main() {
    // Create ruleset
    int ruleset_fd = syscall(SYS_landlock_create_ruleset,
        &(struct landlock_ruleset_attr){
            .handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE |
                                 LANDLOCK_ACCESS_FS_WRITE_FILE,
        }, 0, 0);
    
    // Add filesystem rule
    struct landlock_path_beneath_attr rule = {
        .parent_fd = open("/tmp", O_PATH),
        .allowed = LANDLOCK_ACCESS_FS_READ_FILE |
                   LANDLOCK_ACCESS_FS_WRITE_FILE,
    };
    syscall(SYS_landlock_add_rule, ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &rule);
    
    // Enforce
    syscall(SYS_landlock_enforce_ruleset, ruleset_fd);
    
    // Now restricted!
}
```

### Python Example

```python
# Using landlock Python bindings
import os
import ctypes

libc = ctypes.CDLL("libc.so.6", use_errno=True)

# Simplified - actual implementation requires more code
# See python-landlock package
```

### Usage in Codex

OpenAI Codex uses Landlock for filesystem restrictions on Linux:

```rust
// Codex landlock implementation
use crate::landlock::{LandlockManager, AccessFlag};

let ruleset = LandlockManager::new()
    .add_path("/home/user/project", AccessFlag::READ_WRITE)
    .add_path("/tmp", AccessFlag::READ_WRITE)
    .enforce()?;
```

### Kernel Requirements

- Linux 5.13+ for basic filesystem support
- Linux 6.15+ for audit integration (logging denials)
- CONFIG_SECURITY_LANDLOCK=y

### Security Considerations

- Only filesystem access - no network control
- Rules are additive (only more restrictive)
- Inherited by children by default

---

## Comparison Matrix

| Technology | Platform | Privileged? | Use Case |
|-----------|----------|-------------|----------|
| **bubblewrap** | Linux | No (user ns) | General sandboxing |
| **Seatbelt** | macOS | No | macOS sandboxing |
| **Landlock** | Linux 5.13+ | No | Filesystem hardening |

### When to Use Each

| Scenario | Technology |
|----------|------------|
| Running untrusted code | bubblewrap |
| macOS development | Seatbelt |
| Additional hardening | Landlock |
| Cloud sandbox (AI agents) | Firecracker (see microvm.md) |

---

## References

- [bubblewrap GitHub](https://github.com/containers/bubblewrap)
- [Seatbelt/Sandbox Documentation](https://developer.apple.com/documentation/security)
- [Landlock Documentation](https://landlock.io)
- [Linux Kernel Landlock Docs](https://www.kernel.org/doc/html/latest/security/landlock.html)