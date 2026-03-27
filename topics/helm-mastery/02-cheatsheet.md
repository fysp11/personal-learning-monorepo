# Helm Cheatsheet — Quick Reference
Generated: 2026-03-27

## Templating

```yaml
# Always include, never template
{{- include "chart.labels" . | nindent 4 }}

# tpl: render string as template
{{ tpl .Values.someStringWithTemplate . }}

# Pass multiple args to named template
{{ include "chart.fn" (dict "ctx" . "key" .Values.thing) }}

# toYaml for blocks
{{ .Values.env | toYaml | nindent 12 }}

# Conditional block
{{- if .Values.ingress.enabled }}
...
{{- end }}

# Range over map
{{- range $key, $val := .Values.labels }}
{{ $key }}: {{ $val }}
{{- end }}
```

## Values Precedence (highest → lowest)
1. `--set` (CLI)
2. `-f custom.yaml` (last file wins)
3. Chart's `values.yaml`

## Subchart Values
```yaml
# values.yaml parent
redis:            # ← subchart name
  replicaCount: 3
global:           # ← available in all subcharts
  imageRegistry: "my.registry.io"
```

## CLI Patterns

```bash
# Idempotent install/upgrade
helm upgrade --install NAME CHART -f values.yaml \
  --set image.tag=v1.2 \
  --atomic --wait --timeout 5m \
  --namespace ns --create-namespace

# Debug / dry run
helm template NAME CHART -f values.yaml        # render only
helm diff upgrade NAME CHART -f values.yaml    # requires helm-diff plugin
helm lint ./mychart                            # lint
helm upgrade NAME CHART --dry-run              # simulate

# Release management
helm list -A                                   # all namespaces
helm history NAME                              # release history
helm rollback NAME [REVISION]                  # rollback
helm uninstall NAME                            # delete release

# Dependency management
helm dependency update ./chart                 # fetch charts/
helm dependency build ./chart                  # rebuild from Chart.lock

# OCI
helm push mychart-1.0.0.tgz oci://registry/org/charts
helm install NAME oci://registry/org/charts/mychart --version 1.0.0
```

## Hooks

```yaml
metadata:
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

Hook types: `pre/post-install`, `pre/post-upgrade`, `pre/post-delete`, `pre/post-rollback`, `test`

Delete policies: `before-hook-creation` | `hook-succeeded` | `hook-failed`

## Helmfile

```bash
helmfile diff                      # what would change
helmfile apply                     # safe: diff + sync
helmfile sync                      # apply all releases
helmfile -e production apply       # specific environment
helmfile -l app=api apply          # label selector
```

```yaml
# helmfile.yaml skeleton
environments:
  production:
    values: [envs/prod.yaml]
releases:
  - name: api
    chart: ./charts/api
    needs: [postgresql]
    values: [values/api.yaml]
    set:
      - name: image.tag
        value: {{ env "IMAGE_TAG" }}
```

## Schema Validation (values.schema.json)
```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "required": ["image"],
  "properties": {
    "image": {
      "required": ["repository", "tag"],
      "properties": {
        "repository": { "type": "string" },
        "tag": { "type": "string" }
      }
    }
  }
}
```
