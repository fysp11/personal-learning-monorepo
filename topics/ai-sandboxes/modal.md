# Modal - Serverless GPU Compute for AI Workloads

Modal provides serverless cloud for running GPU-intensive AI workloads. It's designed for teams that need flexible, scalable compute without managing infrastructure.

---

## Pricing

### Subscription Plans

| Plan | Monthly Fee | Included Credits | Limits |
|------|------------|-------------------|--------|
| **Starter** | $0 | $30/month | 100 containers, 10 GPU concurrency |
| **Team** | $250 | $100/month | 1000 containers, 50 GPU concurrency |
| **Enterprise** | Custom | Custom | Custom |

### Compute Costs (Per Second)

#### GPU Pricing

| GPU Type | Per Second | Per Hour | Best For |
|----------|-------------|----------|----------|
| NVIDIA T4 | $0.000164 | $0.59/hr | Lightweight inference |
| NVIDIA A10G | $0.000306 | $1.10/hr | Inference workloads |
| NVIDIA A100 (40GB) | $0.001036 | $3.73/hr | Fine-tuning models |
| NVIDIA H100 | $0.002778 | $10.00/hr | Large-scale training |

#### CPU/Memory (Team Plan)

| Resource | Per Second |
|----------|------------|
| CPU (physical core) | $0.00003942 |
| Memory (GiB) | $0.00000672 |

### Key Notes

- Pay-per-second billing - only pay for what you use
- No minimum usage time
- $30/month free credits on Starter plan (recurring)
- GPU prices reduced 15-30% in August 2024

---

## Architecture

### Core Technology

Modal uses **gVisor** (Google's user-space kernel) for container isolation:

- Runs containers without sharing host kernel
- Provides syscall filtering
- Lower overhead than full VMs

### Serverless Model

- **Instant autoscale** - up and down based on demand
- **No idle costs** - only pay for actual compute
- **Per-second billing** - granular cost control

### Products

| Product | Use Case |
|---------|----------|
| **Modal Inference** | Serve custom or open-source AI models |
| **Modal Sandboxes** | Secure dev environments for agents |
| **Modal Training** | Scale single/multi-node GPU experiments |
| **Modal Batch** | Parallel job processing |
| **Modal Notebooks** | Interactive Jupyter environments |

---

## Use Cases

### Ideal For

1. **Model serving** - deploy LLMs with sub-second cold starts
2. **Training/fine-tuning** - GPU workloads on demand
3. **Batch processing** - millions of parallel jobs
4. **AI agents** - run OpenCode, custom agents in cloud
5. **Notebooks** - interactive ML development

### OpenCode on Modal

```python
import modal

image = modal.Image.from_dockerfile("Dockerfile")
# Dockerfile includes OpenCode installation

@app.function(image=image)
def run_opencode():
    # Clone repo, start OpenCode server
    pass
```

Modal provides an official example for running OpenCode in a sandbox:
- Clones GitHub repo into container
- Provides Modal credentials access
- Password-protected server access

---

## Comparison with Daytona

| Aspect | Modal | Daytona |
|--------|-------|---------|
| Focus | GPU compute, ML | Agent sandboxes |
| Isolation | gVisor | Firecracker |
| GPU support | Full (T4→H100) | Available |
| Cold start | ~seconds (GPU) | ~90ms |
| Free tier | $30/mo (recurring) | $200 (one-time) |

---

## Key Features

1. **Python-first SDK** - define infrastructure as code
2. **GPU access** - instant access to thousands of GPUs
3. **Persistent volumes** - mount cloud storage
4. **Cron jobs** - scheduled workloads
5. **Webhooks** - event-driven functions
6. **Custom domains** - production deployments
7. **Region selection** - control where workloads run

---

## Enterprise Features

- **VPC deployment** - private cloud connectivity
- **Custom SLA** - guaranteed performance
- **Dedicated support** - priority assistance
- **Invoice billing** - monthly billing with credits

---

## References

- [Modal Pricing](https://modal.com/pricing)
- [Modal Documentation](https://modal.com/docs)
- [OpenCode on Modal Example](https://modal.com/docs/examples/opencode_server)