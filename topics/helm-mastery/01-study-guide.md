# Helm Mastery — Personalized Study Guide
Generated: 2026-03-27 | Profile: Solid Intermediate (7/10, 2/5)

## How to Use This Guide
- Sections marked 🔴 are your gap areas — prioritize these
- Sections marked ✅ are your strengths — skim for completeness
- Each section links to curated sources and has key concepts to internalize

---

## 🔴 PRIORITY 1: Advanced Templating (include, tpl, pipelines)

### The Core Rule
**Always use `include`, never `template`.**

```yaml
# ❌ template: direct output, cannot pipe
{{- template "mychart.labels" . }}

# ✅ include: returns string, pipeable
{{- include "mychart.labels" . | nindent 4 }}
{{- include "mychart.labels" . | indent 2 }}
{{- include "mychart.labels" . | toYaml | trimSuffix "\n" }}
```

### The `tpl` Function — Dynamic Template Evaluation
`tpl` renders a string value AS a Go template at runtime.

```yaml
# values.yaml
config:
  endpoint: "http://{{ .Release.Name }}.{{ .Values.domain }}"
  domain: "example.com"

# template
{{ tpl .Values.config.endpoint . }}
# renders: "http://myapp.example.com"
```

Use cases:
- Values that reference other values
- Dynamic labels or annotations from values
- Configurable template fragments passed in by users

### Named Template Patterns

```yaml
# _helpers.tpl
{{- define "mychart.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

# Passing multiple args (dict trick)
{{- define "mychart.image" -}}
{{- $ctx := .ctx -}}
{{- $image := .image -}}
{{ $ctx.Values.registry }}/{{ $image.repository }}:{{ $image.tag }}
{{- end }}

# Usage
{{ include "mychart.image" (dict "ctx" . "image" .Values.api.image) }}
```

### Sources
- [Named Templates | Helm Official Docs](https://helm.sh/docs/chart_template_guide/named_templates/)
- [Chart Tips & Tricks | Helm](https://helm.sh/docs/howto/charts_tips_and_tricks/)
- [Helm include vs template: What's the Difference](https://devopskit.tech/en/posts/helm_tmpl_vs_inc/)
- [How to Use Helm Template Functions: toYaml, tpl, include](https://oneuptime.com/blog/post/2026-02-09-helm-template-functions-toyaml-tpl/view)
- [Using the Helm tpl Function](https://austindewey.com/2021/02/22/using-the-helm-tpl-function-to-refer-values-in-values-files/)
- [Use Named Templates Like Functions in Helm](https://itnext.io/use-named-templates-like-functions-in-helm-charts-641fbcec38da)

---

## 🔴 PRIORITY 2: Subchart Value Scoping

### The Dot Notation Rule
Values are scoped to subcharts by matching the **subchart name or alias**.

```yaml
# values.yaml (parent chart)
redis:               # ← matches subchart name in Chart.yaml
  replicaCount: 3
  auth:
    enabled: true

postgresql:
  primary:
    persistence:
      size: 10Gi
```

```bash
# CLI equivalent
helm install myapp . \
  --set redis.replicaCount=3 \
  --set postgresql.primary.persistence.size=10Gi
```

### Global Values — Cross-Chart Sharing
```yaml
# values.yaml
global:
  imageRegistry: "my-registry.example.com"
  storageClass: "fast-ssd"

# In any subchart template:
{{ .Values.global.imageRegistry }}
```

Globals propagate to ALL subcharts automatically. Use sparingly — only for truly shared config.

### Subchart Cannot Read Parent
A subchart's templates only see their own `.Values`. They cannot reach up to the parent's values.
The data flow is **strictly top-down**: parent overrides child, never the reverse.

### Sources
- [Subcharts and Global Values | Helm Official Docs](https://helm.sh/docs/chart_template_guide/subcharts_and_globals/)
- [Helm 3 Umbrella Charts & Global Values](https://itnext.io/helm-3-umbrella-charts-global-values-in-sub-charts-666437d4ed28)
- [Helm chart dependencies & subcharts](https://medium.com/@claudio.palmisano90/helm-chart-dependencies-subcharts-c497b9c8ab3f)
- [One Chart to Rule Them All (umbrella pattern)](https://medium.com/craftech/one-chart-to-rule-them-all-3f685e0f25a9)

---

## 🔴 PRIORITY 3: Idempotent CLI Patterns

### `upgrade --install` (the CI/CD standard)
```bash
# ❌ Fragile: requires knowing if release exists
helm install myapp ./chart   # fails if exists
helm upgrade myapp ./chart   # fails if doesn't exist

# ✅ Idempotent: install or upgrade, always works
helm upgrade --install myapp ./chart \
  -f values.yaml \
  --set image.tag=$CI_COMMIT_SHA \
  --atomic \           # rollback automatically on failure
  --wait \             # wait for pods to be ready
  --timeout 5m \
  --namespace myns \
  --create-namespace
```

### Key Flags to Know

| Flag | Effect |
|------|--------|
| `--install` | Install if release doesn't exist |
| `--atomic` | Rollback on failure, implies `--wait` |
| `--wait` | Block until all resources are ready |
| `--timeout` | How long to wait (default 5m) |
| `--dry-run` | Render templates only, no cluster changes |
| `--create-namespace` | Create namespace if it doesn't exist |
| `--reuse-values` | Keep existing values, merge new ones |
| `--reset-values` | Use only chart defaults + provided values |
| `--force` | Force resource updates (delete + recreate) |

### Checking What Would Change
```bash
# Render templates locally
helm template myapp ./chart -f values.yaml

# Diff against running release (requires helm-diff plugin)
helm diff upgrade myapp ./chart -f values.yaml
```

---

## 🔴 PRIORITY 4: Helmfile — Multi-Release Orchestration

### Why Not Bash Loops?
```bash
# ❌ Fragile: no dependency ordering, no diff, no state
for chart in api worker db; do
  helm upgrade --install $chart ./charts/$chart
done
```

### Helmfile Structure
```yaml
# helmfile.yaml
repositories:
  - name: bitnami
    url: https://charts.bitnami.com/bitnami

environments:
  production:
    values: [envs/prod.yaml]
  staging:
    values: [envs/staging.yaml]

releases:
  - name: postgresql
    chart: bitnami/postgresql
    version: "13.x.x"
    values:
      - values/postgresql.yaml
      - values/postgresql-{{ .Environment.Name }}.yaml

  - name: api
    chart: ./charts/api
    needs:
      - postgresql        # ← DAG: waits for postgresql first
    values:
      - values/api.yaml
    set:
      - name: image.tag
        value: {{ env "IMAGE_TAG" | default "latest" }}
```

### Core Commands
```bash
helmfile diff           # show what would change
helmfile apply          # diff + sync (safe default)
helmfile sync           # apply all releases
helmfile destroy        # remove all releases
helmfile -e production apply   # target specific environment
helmfile -l app=api apply      # target by label selector
```

### Sources
- [Helmfile Official Docs](https://helmfile.readthedocs.io/)
- [GitHub: helmfile/helmfile](https://github.com/helmfile/helmfile)
- [Managing Multiple Helm Releases with Helmfile](https://oneuptime.com/blog/post/2026-01-17-helmfile-multiple-releases/view)
- [Helmfile: A Declarative Way to Deploy Helm Charts](https://seifrajhi.github.io/blog/helmfile-declarative-helm-charts/)
- [Helmfile Tutorial: Beginner to Advanced](https://www.devopsschool.com/blog/helmfile-tutorial-from-beginner-to-advanced/)
- [What is Helmfile and How Does it Work? (Tanzu)](https://blogs.vmware.com/tanzu/what-is-helmfile-and-how-does-it-work/)

---

## ✅ REFERENCE: Hooks (Strong — keep for reference)

### All Valid Hook Types
```
pre-install     post-install
pre-upgrade     post-upgrade
pre-delete      post-delete
pre-rollback    post-rollback
test
```

### Full Hook Annotation Set
```yaml
metadata:
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"          # lower = runs first
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

### Delete Policies
| Policy | When hook resource is deleted |
|--------|------------------------------|
| `before-hook-creation` | Before new hook runs (default in practice) |
| `hook-succeeded` | After successful completion |
| `hook-failed` | After failure |

### Sources
- [Chart Hooks | Helm Official Docs](https://helm.sh/docs/topics/charts_hooks/)
- [Helm Hooks: Pre/Post Install and Upgrade](https://oneuptime.com/blog/post/2026-01-17-helm-hooks-pre-post-install-upgrade/view)
- [Advanced Helm Hooks](https://oneuptime.com/blog/post/2026-01-30-helm-hooks-advanced/view)
- [Release lifecycle management with Helm](https://craftech.io/blog/release-lifecycle-management-with-helm/)

---

## ✅ REFERENCE: Production Patterns

### Umbrella Charts
```
mycorp-platform/
  Chart.yaml          # type: application, lists dependencies
  values.yaml         # global + per-subchart values
  charts/             # locked chart tarballs (helm dep build)
    api-1.2.0.tgz
    worker-0.8.1.tgz
```

### Schema Validation (`values.schema.json`)
```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["image"],
  "properties": {
    "image": {
      "type": "object",
      "required": ["repository", "tag"],
      "properties": {
        "repository": { "type": "string" },
        "tag": { "type": "string" }
      }
    },
    "replicaCount": {
      "type": "integer",
      "minimum": 1
    }
  }
}
```
Helm validates ALL values (including subchart values) against this schema on install/upgrade.

### OCI Registry (Modern Helm)
```bash
# Push
helm package ./mychart
helm push mychart-1.0.0.tgz oci://ghcr.io/myorg/charts

# Pull & install
helm install myapp oci://ghcr.io/myorg/charts/mychart --version 1.0.0
```

### Sources
- [Helm Best Practices | Official](https://helm.sh/docs/chart_best_practices/)
- [OCI-based Registries | Helm](https://helm.sh/docs/topics/registries/)
- [Helm Charts & Best Practices (Codefresh)](https://codefresh.io/docs/docs/ci-cd-guides/helm-best-practices/)
- [Helm in Production: Lessons and Gotchas](https://blog.sneakybugs.com/helm-production-lessons/)
- [Chart Development Tips & Tricks](https://helm.sh/docs/howto/charts_tips_and_tricks/)

---

## Study Sequence (Recommended Order)

1. `include` vs `template` vs `tpl` → **do exercises, not just reading**
2. Subchart dot notation → set up a parent+child chart and test value scoping
3. `upgrade --install` + flags → use `--dry-run` and `helm template` to observe behavior
4. Helmfile → install locally, manage a 2-release setup across 2 environments
5. Production patterns → umbrella chart, add schema validation, push to OCI

## Quick Reference Cheatsheet
See `02-cheatsheet.md` for condensed command reference.
