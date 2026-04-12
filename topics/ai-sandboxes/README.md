# AI Sandboxes for Coding Agents

This topic covers cloud-based and local sandbox infrastructure for running AI coding agents securely. It documents pricing, architecture patterns, and implementation details for engineers building agentic AI systems.

## Overview

AI coding agents execute arbitrary code - they need isolation to prevent accidental or malicious damage to host systems. This topic covers:

- **Cloud sandboxes** (Daytona, Modal, E2B) - managed infrastructure for running agent code
- **Local sandbox implementations** - OS-level isolation (bubblewrap, Seatbelt, Landlock)
- **Agent architectures** - how Claude Code, Codex, OpenCode, Hermes implement sandboxing

---

## Pricing Comparison

### Cloud Sandbox Providers

| Provider | Free Tier | Pay-as-you-go | Enterprise |
|----------|-----------|---------------|------------|
| **Daytona** | $200 one-time | vCPU: $0.0504/h, Memory: $0.0162/GiB/h, Storage: $0.000108/GiB/h | Custom |
| **Modal** | $30/month (recurring) | GPU T4: $0.59/hr, A10G: $1.10/hr, A100: $3.73/hr, H100: $10.00/hr | Custom |
| **E2B** | $100 one-time | Sandbox runtime per-second | Custom |

### Key Differences

| Aspect | Daytona | Modal | E2B |
|--------|---------|-------|-----|
| Focus | AI code execution sandboxes | Serverless GPU compute | Code execution sandboxes |
| Isolation | Firecracker microVM | gVisor (user-space kernel) | Firecracker microVM |
| Cold start | ~90ms | ~seconds (GPU), ~500ms (CPU) | ~150ms |
| Use case | Agentic AI workloads | ML training/inference | Code execution |

---

## Core Concepts

### Why Sandboxing Matters

AI agents with code execution capabilities are **Turing-complete** - once they can run arbitrary code, they can theoretically do anything. This creates security risks:

1. **Prompt injection** - malicious code in context can manipulate agent behavior
2. **Accidental damage** - bugs can delete or corrupt files
3. **Credential exfiltration** - agents can access environment variables
4. **Network egress** - agents can send data to external servers

Sandboxing provides **technical enforcement** of boundaries - not just prompts or policies, but OS-level restrictions.

### Isolation Spectrum

```
Lightweight                          Heavyweight
┌─────────────┬────────────┬─────────────┬─────────────┐
│   No Sandbox│  OS-level  │  Containers │  MicroVMs   │
│  (default)  │ (bubblewrap│  (Docker)   │(Firecracker)│
│             │  Seatbelt) │             │             │
└─────────────┴────────────┴─────────────┴─────────────┘
Risk: High              →→→→→→→→→→→→→→→→→→→→→→→→→ Low
Cost:  Low              →→→→→→→→→→→→→→→→→→→→→→→→→ High
```

### Sandbox Types for Agents

| Type | Technology | Startup | Isolation | Best For |
|------|-----------|---------|-----------|----------|
| **Code Execution** | E2B, Daytona | ~150ms | MicroVM | Data analysis, scripts |
| **Full Dev Environment** | Modal, Docker | ~seconds | Container/VM | Full projects, debugging |
| **Browser** | Browser automation | ~seconds | Tab isolation | Web interactions |

---

## Research Topic Matrix

| Category | Topic | Status | Key Insights |
|----------|-------|--------|--------------|
| **Cloud Providers** | | | |
| | Daytona | ✅ Done | Firecracker-based, $200 free credits, ~90ms startup |
| | Modal | ✅ Done | gVisor-based, GPU focus, $30/mo free tier |
| | E2B | ✅ Done | Firecracker-based, code execution specific |
| **Agent Implementations** | | | |
| | Claude Code | ✅ Done | OS-level (Seatbelt/bubblewrap), 84% reduction in permission prompts |
| | OpenAI Codex | ✅ Done | Dual: cloud (Gvisor) + local (Seatbelt/Landlock), 3 sandbox modes |
| | OpenCode | ✅ Done | No built-in sandbox - relies on external (Docker/Modal/Daytona) |
| | Hermes | ✅ Done | execute_code sandbox + docker/modal/daytona backends |
| **OS-level Isolation** | | | |
| | bubblewrap (Linux) | ✅ Done | Unprivileged, namespaces, used by Claude Code, Codex |
| | Seatbelt (macOS) | ✅ Done | Native macOS sandbox, used by Claude Code, Codex |
| | Landlock (Linux) | ✅ Done | Filesystem restrictions, kernel 5.13+, Codex uses it |
| **MicroVM Tech** | | | |
| | Firecracker | ✅ Done | AWS Lambda, Daytona, E2B - 125ms startup |
| | gVisor | ✅ Done | Google Cloud Run, Modal - user-space kernel |
| | Wasm | ✅ Done | WASI, Edge computing - sub-ms startup |

- [Daytona](daytona.md) - Cloud sandbox for AI agents, Firecracker-based
- [Modal](modal.md) - Serverless GPU compute, gVisor isolation
- [Agent Sandboxing](agents.md) - How Claude Code, Codex, OpenCode, Hermes implement security

---

## Key Patterns for Engineers

### 1. Dual-Layer Security

Combine sandbox modes with approval policies:
- **Sandbox** = technical enforcement (what's *possible*)
- **Approval** = human-in-the-loop (what's *allowed*)

### 2. Network Isolation First

Without network isolation, agents can escape filesystem sandbox by reaching external servers. Always pair filesystem + network controls.

### 3. Zero-Trust Architecture

Assume the agent *will* be compromised eventually. Design boundaries that:
- Limit blast radius
- Expire credentials quickly
- Log everything
- Segment data

### 4. Container vs MicroVM Tradeoffs

| Factor | Containers | MicroVMs |
|--------|------------|----------|
| Isolation | Shared kernel | Separate kernel |
| Startup | ~500ms | ~150ms |
| Memory | Tens of MB | ~1GB default |
| Security | Lower (kernel exploits) | Higher (hardware virtualization) |

---

## References

- [Daytona Documentation](https://www.daytona.io/docs)
- [Modal Pricing](https://modal.com/pricing)
- [Claude Code Sandboxing](https://docs.anthropic.com/en/docs/claude-code/sandboxing)
- [OpenAI Codex Sandboxing](https://developers.openai.com/codex/concepts/sandboxing)
- [E2B Documentation](https://e2b.dev/docs)
- [Hermes Code Execution](https://hermes-agent.nousresearch.com/docs/user-guide/features/code-execution/)