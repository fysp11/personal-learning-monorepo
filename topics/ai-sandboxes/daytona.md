# Daytona - Cloud Sandbox for AI Agents

Daytona provides secure, elastic infrastructure for running AI-generated code in isolated sandbox environments. Founded in 2023 by the team behind Codeanywhere, it's designed specifically for agentic AI workloads.

---

## Pricing

### Pay-as-you-go (Per Hour)

| Resource | Price |
|----------|-------|
| vCPU | $0.0504/h |
| Memory (GiB) | $0.0162/h |
| Storage (GiB) | $0.000108/h |

### Pay-as-you-go (Per Second)

| Resource | Price |
|----------|-------|
| vCPU | $0.00001400/s |
| Memory (GiB) | $0.00000450/s |
| Storage (GiB) | $0.00000003/s |

### Free Tier

- **$200** free compute credits for new accounts (no credit card required)
- **5 GB** free storage
- Python and TypeScript SDKs
- API access

### Startup Program

- Up to **$50,000** in credits for qualifying startups
- Contact sales for details

### Enterprise

- Custom pricing
- On-premise setup available
- HIPAA, SOC 2, GDPR compliance

---

## Architecture

### Core Technology

Daytona uses **Firecracker microVMs** - the same technology AWS uses for Lambda and Fargate. This provides:

- **Hardware virtualization** - separate kernel, not just namespaces
- **Sub-90ms sandbox creation** - pre-warmed snapshots
- **Multi-region deployment** - global infrastructure

### Default Resources

| Resource | Default | Maximum |
|----------|---------|---------|
| vCPU | 1 | 4 |
| Memory | 1GB | 8GB |
| Disk | 3GiB | 10GiB |

### Network Isolation

- Each sandbox has its own network namespace
- Per-sandbox firewall rules
- Configurable allowed destinations
- No inbound connections by default

### Security Features

- **Isolated runtime protection** - separated from host
- **Process execution with real-time output streaming**
- **Environment snapshots** - pre-configured templates
- **Full API access** - programmatic control

---

## Use Cases

### Ideal For

1. **AI agents running code** - Claude Code, OpenCode, custom agents
2. **Development environments** - full IDE in cloud
3. **Testing/evaluation** - ephemeral, reproducible environments
4. **Code execution** - data analysis, script running

### Integration Examples

#### OpenCode on Daytona

```typescript
import { Daytona } from '@daytona-io/daytona-sdk';

const daytona = Daytona();
const sandbox = await daytona.create({
  resources: { cpu: 2, memory: 4 },
  // Install and run OpenCode server
});
```

#### Run any agent

```python
from daytona import Daytona, Sandbox, CreateSandboxParams

daytona = Daytona()
sandbox = daytona.create(CreateSandboxParams(
    # Custom environment
))
```

---

## Comparison with Alternatives

| Aspect | Daytona | E2B | Modal |
|--------|---------|-----|-------|
| Focus | General agent sandbox | Code execution | GPU compute |
| Isolation | Firecracker | Firecracker | gVisor |
| Startup | ~90ms | ~150ms | ~seconds |
| Storage | 5GB free | Limited | Pay for use |
| Enterprise | Yes | Yes | Yes |

---

## Key Features

1. **Native Git integration** - clone, branch, credential management
2. **Environment snapshots** - save/restore configured environments
3. **Python/TypeScript SDK** - programmatic control
4. **Auto-stop** - configurable inactivity timeout (default: 15 minutes)
5. **Resize resources** - scale up/down running sandboxes

---

## References

- [Daytona Documentation](https://www.daytona.io/docs)
- [Daytona Pricing](https://www.daytona.io/pricing)
- [OpenCode SDK Guide](https://www.daytona.io/docs/en/guides/opencode/opencode-sdk-agent)