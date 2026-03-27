# Helm Knowledge Assessment — 2026-03-27

## Score: 7/10 — Solid Intermediate

## Results

| Q  | Topic                        | Answer | Correct | Result |
|----|------------------------------|--------|---------|--------|
| 1  | Basics (helm install)        | B      | B       | ✅     |
| 2  | Chart structure              | C      | C       | ✅     |
| 3  | Templating (default)         | C      | C       | ✅     |
| 4  | Values precedence            | C      | C       | ✅     |
| 5  | include vs template          | D      | B       | ❌     |
| 6  | Hooks lifecycle              | B      | A       | ❌     |
| 7  | Dependencies                 | B      | B       | ✅     |
| 8  | Debugging (helm template)    | B      | B       | ✅     |
| 9  | Library charts               | B      | B       | ✅     |
| 10 | Production orchestration     | B      | C       | ❌     |

## Strengths
- Chart structure and anatomy
- Templating fundamentals (values, default, flow control)
- Values precedence and override chain
- Dependencies management
- Debugging workflows
- Library charts concept

## Gaps to Focus On

### 1. Template Functions & Piping (Q5)
`include` captures output as a string so you can pipe it:
```yaml
# ✅ Works — include returns a string
{{ include "mychart.labels" . | indent 4 }}
{{ include "mychart.labels" . | nindent 4 }}
{{ include "mychart.labels" . | toYaml }}

# ❌ Cannot pipe — template outputs directly to stream
{{ template "mychart.labels" . }}
```
Both work in any file, not just `_helpers.tpl`. Rule: **always use `include` over `template`**.

### 2. Hooks & Lifecycle (Q6)
Valid Helm hooks:
```
pre-install    → before any resources created
post-install   → after all resources created (Q6 answer)
pre-upgrade    → before upgrade begins
post-upgrade   → after upgrade completes
pre-delete     → before deletion begins
post-delete    → after deletion completes
pre-rollback   → before rollback begins
post-rollback  → after rollback completes
test           → when `helm test` is invoked
```
`pre-release` does NOT exist. Hook annotations go on the resource:
```yaml
metadata:
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": hook-succeeded
```

### 3. Multi-Release Orchestration — Helmfile (Q10)
Helmfile is purpose-built for managing multiple Helm releases:
```yaml
# helmfile.yaml
environments:
  production:
    values: [envs/prod.yaml]
  staging:
    values: [envs/staging.yaml]

releases:
  - name: api
    chart: ./charts/api
    values: [values/api.yaml]
  - name: worker
    chart: ./charts/worker
    values: [values/worker.yaml]
```
Kustomize is kubectl-native overlays — it doesn't manage Helm releases.

## Round 2 Score: 2/5

| Q  | Topic                          | Answer | Correct | Result |
|----|-------------------------------|--------|---------|--------|
| 11 | `tpl` function                 | A      | B       | ❌     |
| 12 | Hook weight ordering           | B      | B       | ✅     |
| 13 | `upgrade --install` (upsert)   | A      | B       | ❌     |
| 14 | Subchart value dot notation    | D      | B       | ❌     |
| 15 | Hooks & rollback               | B      | B       | ✅     |

### Round 2 Corrections

**Q11 — `tpl`** renders a string as a Go template at runtime:
```yaml
# values.yaml
greeting: "Hello {{ .Release.Name }}"
# template
{{ tpl .Values.greeting . }}  # → "Hello myapp"
```

**Q13 — `upgrade --install`** is idempotent upsert: installs if not exists, upgrades if exists.
Standard CI/CD pattern — no branching logic needed.

**Q14 — Subchart value dot notation:**
```bash
--set redis.replicaCount=3
# or in values.yaml:
redis:
  replicaCount: 3
```
No `charts.` or `dependencies.` prefix. Key = subchart name/alias in Chart.yaml.

### Confirmed Strong (Round 2)
- Hook weight ordering (lowest runs first, negative to positive)
- Hook rollback behavior (hooks untracked by default unless delete-policy annotated)

### Updated Gap Map

| Area                                 | Status   |
|--------------------------------------|----------|
| Basics, structure, values            | ✅ Strong |
| Dependencies, debugging              | ✅ Strong |
| Library charts                       | ✅ Strong |
| Hook lifecycle (types, ordering)     | ✅ Strong |
| Hook rollback behavior               | ✅ Strong |
| **`tpl` and dynamic templating**     | 🔴 Gap   |
| **`include` vs `template` piping**   | 🔴 Gap   |
| **`upgrade --install` CLI pattern**  | 🔴 Gap   |
| **Subchart value dot notation**      | 🔴 Gap   |
| **Helmfile multi-release**           | 🔴 Gap   |

## Personalized Learning Plan
Focus notebook sources on:
1. **Advanced templating** — `include` vs `template`, `tpl`, pipelines, named template patterns
2. **Subchart scoping** — dot notation, globals, parent→child value flow
3. **Idempotent CLI patterns** — `upgrade --install`, `--atomic`, `--wait`, `--timeout`
4. **Helmfile** — declarative multi-release, environment management, DAG ordering
5. **Production patterns** — umbrella charts, schema validation, OCI registries, CI/CD
6. Light coverage of basics (already strong)
