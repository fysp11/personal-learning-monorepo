# MicroVM & Container Isolation Technologies

This document covers the virtualization technologies that power cloud-based AI agent sandboxes - Firecracker, gVisor, and WebAssembly.

---

## Firecracker

### Overview

Firecracker is a Virtual Machine Monitor (VMM) developed by AWS to power Lambda and Fargate. It provides microVMs - lightweight VMs that combine security of traditional VMs with speed of containers.

**Used by:** Daytona, E2B, AWS Lambda, AWS Fargate

### Key Specifications

| Specification | Value |
|---------------|-------|
| **Startup Time** | ~125ms |
| **Memory Overhead** | <5 MiB per microVM |
| **VMM Code Size** | ~50,000 lines (Rust) |
| **Guest OS** | Linux (4.14+) |
| **Architecture** | x86_64, aarch64 |

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Host Machine                       │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              KVM (Kernel)                    │   │
│  │                                                │   │
│  │   ┌─────────────┐   ┌──────────────────┐    │   │
│  │   │ Firecracker │   │  Firecracker      │    │   │
│  │   │  MicroVM 1  │   │  MicroVM 2        │    │   │
│  │   │  (vCPU, RAM)│   │  (vCPU, RAM)      │    │   │
│  │   └─────────────┘   └──────────────────┘    │   │
│  │        ↑                   ↑                 │   │
│  │   ┌────────────────────────────────────────┐ │   │
│  │   │     VirtIO Devices (net, block, vsock)  │ │   │
│  │   └────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Components

#### API Thread
- Control plane for the microVM
- REST API over Unix socket
- Handles configuration, start/stop

#### VMM Thread
- Exposes machine model
- Handles VirtIO devices (net, block, vsock)
- I/O rate limiting

#### vCPU Threads
- One per virtual CPU
- Runs guest code
- Processes are considered malicious

### Security Model

#### Multiple Trust Zones

```
Guest vCPU (least trusted)
    ↓ seccomp filters
I/O Thread (copies data, rate limits)
    ↓ VirtIO drivers
Host TAP device
    ↓
Host (most trusted)
```

#### Jailer Component

The jailer provides additional isolation:
- seccomp-bpf filters
- cgroup limits
- chroot isolation
- Privilege dropping

#### Minimal Device Model

Firecracker only emulates:
1. **virtio-net** - Network device
2. **virtio-block** - Block storage
3. **virtio-vsock** - VSOCK communication
4. **Serial console** - Output
5. **Keyboard** - Shutdown only

No BIOS, no PCI, no USB, no display - minimal attack surface.

### Why It Works for AI Agents

1. **Strong isolation** - Separate kernel, not shared
2. **Fast startup** - Pre-warmed pool, ~125ms
3. **Multi-tenant** - Hundreds on one host
4. **Secure** - Hardware virtualization boundary

### Comparison with Containers

| Aspect | Docker | Firecracker |
|--------|--------|------------|
| Isolation | Namespaces (shared kernel) | Separate kernel |
| Startup | ~500ms | ~125ms |
| Memory | 10-100 MB | <5 MB |
| Security | Lower (kernel exploits) | Higher (hardware) |
| Multi-tenant | Risky | Safe |

### Use in AI Sandboxes

#### E2B

```
User request → Create sandbox → Firecracker VM starts
                    ↓
              Clone repo, setup env
                    ↓
              Agent runs code
                    ↓
              Destroy VM
```

- Cold start: ~150ms
- Each sandbox gets:
  - Isolated kernel
  - Filesystem
  - Network namespace

#### Daytona

- Pre-warmed VM pool
- Sub-90ms creation
- Custom resources (CPU, memory, GPU)
- Snapshots for environment restore

---

## gVisor

### Overview

gVisor is Google's user-space kernel - a sandbox that intercepts system calls without using a real kernel. It provides container-like efficiency with stronger isolation.

**Used by:** Google Cloud Run, Modal

### Key Specifications

| Specification | Value |
|---------------|-------|
| **Startup Time** | ~100ms |
| **Memory Overhead** | Higher than containers |
| **Implementation** | Go (user-space) |
| **Syscall Intercept** | ptrace / gofer |

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Application                         │
│         (Python, Node, Go, etc.)                    │
└─────────────────────┬───────────────────────────────┘
                      ↓ syscalls
┌─────────────────────────────────────────────────────┐
│                   gVisor Sentry                     │
│   (User-space kernel - intercepts all syscalls)    │
│                                                    │
│   - File operations                                │
│   - Network stack                                  │
│   - Process management                             │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│                    gofer                           │
│   (Proxy - talks to host filesystem)               │
└─────────────────────────────────────────────────────┘
```

### How It Works

1. **Sentry** - The core component that intercepts syscalls
2. **gofer** - A separate process that handles file I/O securely
3. **Network stack** - Full network stack in user-space

### Syscall Handling

```
App: write(fd, "hello", 5)
       ↓
Sentry: Intercepts write syscall
       ↓
Sentry: Validates against security policy
       ↓
gofer: Performs actual write to host filesystem
       ↓
Sentry: Returns success to app
```

### Security Model

| Layer | Protection |
|-------|------------|
| **Syscall filtering** | Only safe syscalls allowed |
| **Capability dropping** | No privileged operations |
| **Address space** | Separate from host |
| **Network** | NAT in user-space |

### Advantages

1. **No shared kernel** - Unlike containers
2. **Lightweight** - More efficient than VMs
3. **Portable** - Runs anywhere
4. **Controlled** - Full syscall control

### Disadvantages

1. **Performance overhead** - Some syscalls slower
2. **Compatibility** - Not all syscalls supported
3. **Memory** - Higher than containers

### Use in Modal

Modal uses gVisor for container isolation:

```python
# Modal's container isolation
# Uses gVisor to run containers securely
# Without sharing host kernel
```

### Comparison with Firecracker

| Aspect | Firecracker | gVisor |
|--------|-------------|--------|
| Isolation | Hardware (KVM) | User-space |
| Startup | ~125ms | ~100ms |
| Memory | <5 MB | Higher |
| Overhead | Lower | Higher |
| Compatibility | Full Linux | Limited syscalls |

---

## WebAssembly (Wasm)

### Overview

WebAssembly provides a sandbox at the language runtime level - code runs in a virtual machine with its own linear memory and limited system access.

**Used by:** Wasmer, Edge.js, Cloudflare Workers

### Key Specifications

| Specification | Value |
|---------------|-------|
| **Startup Time** | Sub-millisecond |
| **Memory** | Linear memory (configurable) |
| **Languages** | Rust, C/C++, Go, Python (wasi) |
| **Sandboxing** | Language VM boundary |

### How It Works

```
┌─────────────────────────────────────────────────────┐
│                  Wasm Runtime                       │
│   (Wasmer, Wasmtime, WasmEdge)                     │
│                                                    │
│   ┌─────────────────────────────────────────┐     │
│   │         Wasm Module                      │     │
│   │   - Linear memory (isolated)              │     │
│   │   - No direct filesystem                 │     │
│   │   - No network (unless enabled)          │     │
│   └─────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
```

### Sandboxing Model

| Feature | Default | Configurable |
|---------|---------|---------------|
| **Filesystem** | No access | WASI filesystem |
| **Network** | No access | HTTP via WASI |
| **Memory** | Isolated | Max size configurable |
| **Syscalls** | None | WASI syscalls only |

### WASI (WebAssembly System Interface)

WASI provides standardized system access:

```rust
// Rust with WASI
use std::fs::File;
use std::io::Write;

fn main() {
    // Only works with WASI filesystem
    let mut file = File::create("/output/data.txt").unwrap();
    file.write_all(b"Hello").unwrap();
}
```

### Use Cases for AI Agents

#### Lightweight Isolation

For simple script execution, Wasm provides:
- Sub-millisecond startup
- Minimal resource usage
- Strong isolation

#### Edge Computing

Cloudflare Workers, etc.:
- Code runs close to users
- Strong isolation by default
- Limited capabilities

### Implementation: Edge.js

```javascript
// Edge.js - run Node.js in Wasm
const edge = require('edge.js');

const result = edge.run({
  wasm: './my-function.wasm',
  memory: { min: 1, max: 16 },  // MB
});
```

### Comparison with Other Approaches

| Aspect | Firecracker | gVisor | Wasm |
|--------|-------------|--------|------|
| Startup | ~125ms | ~100ms | <1ms |
| Isolation | Kernel | User-kernel | Language VM |
| Resource | Medium | Low | Very low |
| Compatibility | Full Linux | Linux subset | WASI only |

---

## Comparison & Selection Guide

### When to Use Each

| Scenario | Technology | Reason |
|----------|------------|--------|
| **Multi-tenant AI agent hosting** | Firecracker | Strongest isolation, fast |
| **Serverless functions** | Firecracker/gVisor | Fast startup, scalable |
| **Untrusted code execution** | Firecracker | Hardware isolation |
| **Lightweight scripting** | Wasm | Instant startup |
| **Container compatibility** | gVisor | Docker-like, more secure |

### Decision Tree

```
Need to run untrusted code?
    │
    ├─► Yes → High security required?
    │           │
    │           ├─► Yes → Firecracker (Daytona, E2B)
    │           └─► No → gVisor (Modal)
    │
    └─► No → Need Linux compatibility?
                │
                ├─► Yes → gVisor (Modal)
                └─► No → Wasm (Edge computing)
```

### Performance Tradeoffs

| Technology | CPU | Memory | Startup | Isolation |
|------------|-----|--------|---------|------------|
| **Firecracker** | Best | Good | ~125ms | Highest |
| **gVisor** | Good | Good | ~100ms | Medium-High |
| **Wasm** | Best | Best | <1ms | Medium |
| **Docker** | Good | Good | ~500ms | Low |

### Cost Implications

- **Firecracker** - More memory per VM, but better isolation
- **gVisor** - Lower memory, but more CPU overhead
- **Wasm** - Lowest resource, limited capability

---

## References

- [Firecracker Documentation](https://firecracker-microvm.github.io/)
- [Firecracker GitHub](https://github.com/firecracker-microvm/firecracker)
- [gVisor Documentation](https://gvisor.dev/docs/)
- [WASI Specification](https://github.com/WebAssembly/WASI)
- [Landlock vs gVisor comparison](https://landing.googleusercontent.com/siteresources.googleusercontent.com)
- [AWS Lambda Firecracker paper](https://www.amazon.science/blog/how-awss-firecracker-virtual-machines-work)