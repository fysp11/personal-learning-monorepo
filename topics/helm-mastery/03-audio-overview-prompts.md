# NotebookLM Audio Overview — Custom Prompts
Generated: 2026-03-27

Four custom prompts for the "Helm Charts Mastery: From Intermediate to Pro" notebook.
One per format type. Paste directly into the "What should the AI hosts focus on?" field.

---

## 1. Deep Dive

```
Target audience: A Kubernetes engineer who scored 7/10 on a Helm assessment — solid on basics, chart structure, values precedence, dependencies, debugging, library charts, and hook lifecycle. Has specific gaps in four areas. Focus the entire episode on closing those gaps.

Gap 1 — include vs template vs tpl:
Explain why `template` cannot be piped and `include` can, using a concrete broken vs fixed example. Then cover `tpl`: show what happens when a values.yaml entry contains Go template syntax like `"http://{{ .Release.Name }}.example.com"` and you render it with vs without `tpl`. Demonstrate the dict trick for passing multiple arguments to a named template in _helpers.tpl.

Gap 2 — Subchart value dot notation:
Explain why `--set charts.redis.replicaCount=3` silently does nothing, and why `--set redis.replicaCount=3` works. Cover how the key in values.yaml must match the subchart's name or alias in Chart.yaml — not a path prefix. Then explain global values: when they propagate automatically, why the data flow is strictly top-down (subchart cannot read parent), and when globals are appropriate vs overused.

Gap 3 — upgrade --install idempotency:
Explain what exactly happens when you run `helm upgrade --install` on a release that doesn't exist yet vs one that does. Contrast with the brittle pattern of branching between install and upgrade in CI/CD. Cover the key flags: --atomic (implies --wait, auto-rollbacks on failure), --wait, --timeout, --create-namespace, --reuse-values vs --reset-values and how they interact with values precedence.

Gap 4 — Helmfile:
Explain why bash loops over helm upgrade commands fail in production (no dependency ordering, no diffing, no state). Show how helmfile.yaml structures repositories, environments, and releases. Focus on the `needs:` field for DAG-based dependency ordering. Contrast `helmfile apply` (diff + sync, safer) vs `helmfile sync` (always applies). Clarify why Helmfile is the right tool here and Kustomize is not (Kustomize is kubectl-native overlay, not a Helm release manager).

Connect the four gaps where possible — for example, how tpl enables dynamic values in multi-environment Helmfile setups, or how subchart scoping interacts with umbrella chart patterns.
```

---

## 2. Brief

```
Target audience: A Kubernetes engineer who already knows Helm basics well. This episode is a rapid-fire mental model refresh on exactly four gap areas. No introductions to what Helm is. Go straight to the concepts.

Cover each gap in order, spending roughly equal time on each:

1. include vs tpl: The one-sentence rule for include (returns a string, so it's pipeable — always use include over template). Then the one-sentence rule for tpl (renders a value string as a Go template at runtime — use when your values.yaml itself contains template expressions).

2. Subchart dot notation: The one rule — the key in values.yaml must match the subchart name or alias in Chart.yaml exactly, with no prefix. Global values propagate down automatically. Data flows top-down only.

3. upgrade --install: It's an idempotent upsert. Install if new, upgrade if exists. --atomic means auto-rollback on failure and implies --wait. This is the CI/CD standard.

4. Helmfile: Declarative multi-release orchestration. `needs:` gives you DAG ordering. `helmfile apply` is diff-then-sync. Not the same as Kustomize.

End with a 30-second summary connecting all four: these are the four things an intermediate Helm user gets wrong that a production engineer gets right.
```

---

## 3. Critique

```
You are reviewing a Helm chart and CI/CD pipeline written by an intermediate engineer. The chart has real problems — find them and explain how to fix each one constructively.

Scenario: The engineer built an umbrella chart with two subcharts (api, redis). They have a CI/CD pipeline deploying it. Here are the problems embedded in their work — critique each one:

Problem 1 — In _helpers.tpl they defined a labels helper and used it like this: `{{- template "mychart.labels" . | nindent 4 }}`. This silently fails. Explain why, what the engineer was thinking, and the correct fix.

Problem 2 — They wanted dynamic endpoint values per environment, so they put `endpoint: "http://myapp.example.com"` in values.yaml and reference it with `{{ .Values.endpoint }}`. It works, but they missed the opportunity to make it truly dynamic. Explain what tpl unlocks here and show the improved pattern.

Problem 3 — Their values.yaml overrides Redis config like this:
```
charts:
  redis:
    replicaCount: 3
```
Redis is ignoring it. The engineer is confused. Explain the dot notation rule they got wrong and show the correct structure.

Problem 4 — Their CI/CD pipeline does:
```
helm install myapp ./chart || helm upgrade myapp ./chart
```
Explain why this is fragile and what the idiomatic replacement is, including which flags to add for production safety.

Problem 5 — They deploy three releases with a bash loop. The database occasionally isn't ready when the API starts. Explain what tool solves this and how `needs:` provides proper DAG ordering.

Be constructive — acknowledge what they got right (the chart structure, values precedence usage, hook annotations) before diving into each issue.
```

---

## 4. Debate

```
Host A argues for pragmatic simplicity. Host B argues for production rigor. Debate the following four Helm decisions, with each host making their strongest case before reaching a nuanced conclusion.

Debate 1 — "Just use `template`, not `include`"
Host A: template is simpler, more readable, works fine for straightforward helpers.
Host B: include is strictly better — it returns a string that can be piped to nindent, indent, toYaml. The day you need to pipe is the day template breaks silently. The correct rule is always use include.
Conclude: is there any legitimate case for template, or is include always the right default?

Debate 2 — "Hardcode values instead of using tpl"
Host A: tpl adds cognitive overhead. Most engineers don't need values that reference other values. Just hardcode per-environment values.
Host B: tpl enables powerful patterns — dynamic endpoints, configurable template fragments, DRY multi-environment values. The endpoint example (http://{{ .Release.Name }}.{{ .Values.domain }}) is a real production need.
Conclude: when is tpl genuinely worth the complexity vs over-engineering?

Debate 3 — "Global values vs dot notation for subchart config"
Host A: globals are convenient — set once, available everywhere. Less duplication across values.yaml.
Host B: globals create invisible coupling. Subcharts should be independently deployable. Use dot notation to scope values explicitly. Use globals only for truly shared infrastructure config like imageRegistry or storageClass.
Conclude: what's the practical rule for when to reach for global vs scoped dot notation?

Debate 4 — "Helmfile vs just using helm upgrade --install in CI/CD scripts"
Host A: Helmfile is another tool to learn and maintain. A well-written CI script with helm upgrade --install handles 90% of real cases.
Host B: Helmfile gives you DAG ordering, environment management, declarative diffs, and `helmfile apply` safety. Bash loops have no dependency resolution and no state awareness. At 3+ releases, Helmfile pays for itself.
Conclude: at what point does the complexity of Helmfile become worth it over scripted helm commands?
```

---

## Usage Notes

- Paste one prompt per audio overview generation
- Suggested length setting: Deep Dive → Long, Brief → Short, Critique → Medium, Debate → Medium/Long
- Language: English
