# AI Engineer Interview Prep — Key Concepts & Career Strategy

> Sources: [22 AI Engineer Interview Questions](https://youtu.be/leXRiJ5TuQo) + [How to Become a Highly Paid AI Engineer](https://youtu.be/Lzc9--aJjKU) — self-taught senior AI engineer at a top YC startup (former real estate agent)

---

## Part 1: Technical Interview Questions & Concepts

### 1. GenAI vs Traditional Programming
- **Traditional**: rule-based, explicit, predictable — logic is hard-coded
- **GenAI**: data-driven, probabilistic — logic is *learned* not coded
- Use traditional when you have predictable inputs/outputs
- Don't slap AI on problems that don't need it — adds cost, latency, unpredictable bugs
- Many AI startups use AI unnecessarily just to raise VC money

### 2. Designing Scalable Automation Workflows
- **Modularity**: each node = one instruction; split LLM calls into multiple smaller ones
- **Decoupling**: use task queues (RabbitMQ, Kafka) — components operate at their own pace
- **Async programming**: critical for GenAI latency; things happen concurrently
- One master node doing everything → harder to scale and debug

### 3. Optimizing Existing Workflows
- Always **benchmark first** → find baseline → identify bottleneck
- Common bottleneck: LLM calls themselves — benchmark each call
- **Split multi-task prompts**: e.g. "write blog + translate" → blog in English (big model) + translate (smaller/faster model)
- Saves API costs + minimizes latency
- Always **mention results**: latency delta, cost savings, stakeholder feedback

### 4. AI Agents
- Autonomous, goal-oriented system using LLM as brain + tools
- Has memory of past conversations for context
- **Reality check**: you often don't need an agent — predefined workflows with LLM calls suffice
- Don't fall for "shiny object syndrome" — using agents everywhere
- Showing you understand agent pitfalls impresses interviewers

### 5. Ensuring Consistent & Accurate LLM Outputs
- **Decomposition/modularity** — smaller, specific components
- **Structured output** — e.g. OpenAI schema enforcement (no need to specify JSON in prompt)
- **RAG** — supply factual data as source of truth; require source citations for every claim
- **Guardrails** — filter PII, malicious content at input and output stages
- **Golden dataset** — reference inputs/outputs for regression testing when changing prompts/systems
- Frameworks: LangChain/LangGraph do heavy lifting (Anthropic recommends building from scratch — both have pros)

### 6. Python Concurrency & GIL
- Know **concurrency vs parallelism** and the **Global Interpreter Lock**
- These are advanced Python concepts commonly tested in AI engineer interviews
- Focus on: asyncio, race conditions, memory management

### 7. LLM Guardrails
- **Input stage**: PII filtering (names, addresses, credit cards), prompt injection detection, dedicated classifier model for malicious/hateful content
- **Output stage**: format validation (ensure JSON when expecting JSON), factual cross-referencing with knowledge base, hallucination flagging
- **When to implement**: risk of unsafe content (harmful/toxic/illegal), hallucination risk (financial/medical apps), data leakage risk (patient data)

### 8. RLHF (Reinforcement Learning from Human Feedback)
- **Step 1**: Supervised fine-tuning — train on small, high-quality human-written demonstrations
- **Step 2**: Train reward model — humans rank multiple responses; model learns to predict human preferences
- **Step 3**: RL fine-tuning — reward model acts as critic, LLM learns to maximize reward
- Makes models helpful, honest, harmless — goes beyond next-token prediction
- Reduces bias and harmful content

### 9. Document Chunking Context Loss
- **Problem**: chunking breaks cross-page context (e.g. "amounts in thousands" on page 1 lost by page 2 → $35 instead of $35,000)
- **Solutions**:
  - (a) Metadata pass — extract doc-wide metadata, attach to each chunk
  - (b) Chunk summaries — summarize each chunk, use summaries for retrieval first, then use full chunk

### 10. LLM Benchmarking Metrics
- **Relevance** — does output address the query? (especially critical in RAG)
- **Time to first token (TTFT)** — critical latency/UX metric; high TTFT = high bounce rate
- **Hallucination rate** — count of prompts producing hallucinated outputs; flag with human review
- **Cost per call / tokens per call** — track API spend efficiency

### 11. Challenging Prompt Engineering
- Open-ended question — have a real project with a journal
- Techniques: multi-shot prompting, persona/tone setting, context + constraints
- Always **mention results** — not just the solution

---

## Part 2: Career Strategy — How to Become a Highly Paid AI Engineer

### Three Pillars

#### Pillar 1: Software Developer Fundamentals
- Ideally 2+ years web dev experience
- **Key skills for AI engineering**: async programming, memory management, race conditions
- **90% of the time**: need strong Python skills
- Don't get stuck choosing the "perfect" course — just start, get momentum
- Expect 6 months minimum for transition; 3 months if lucky

#### Pillar 2: GenAI Knowledge
- Start with ML fundamentals (DeepLearning.ai specialization recommended — gives low-level understanding even if some math won't be used on the job)
- Don't stay in theory too long — start building projects ASAP
- **Starter project**: chatbot using SQL DB + vector DB + APIs → agent that answers user questions
- Projects should solve **real business cases**, not generic "AI social media manager"
- **Bonus**: add **evals** (evaluations) to your project — very few candidates know how to make GenAI apps testable and scalable
  - Start basic; even labeling good results in LangSmith counts
- Debugging and exception handling = very in-demand skill

#### Pillar 3: Set Yourself Apart (Differentiation)

**Domain Arbitrage** — the #1 differentiator:
- AI is automating coding → companies need AI engineers who understand **industries and business needs**
- If you know an industry's struggles, you become uniquely valuable (product engineer mindset)
- Example: real estate background → prop tech expertise → instant credibility
- Set Google Alerts for your target industry to stay current

**Other differentiation tactics**:
- Contribute to open source (e.g. CPython sprints → "Python contributor" on resume)
- Content creation (YouTube, X/LinkedIn posts) — drives traffic to projects, grows network
- Ambassador programs (LangChain, Lovable) — network + credential
- AI makes everyone code/sound the same → uniqueness is the scarce asset

### Resume & LinkedIn Tips
- Use LaTeX (Overleaf, Jake's Resume template) — preserves formatting, possibly better for resume parsers
- **About section** = 15-second elevator pitch — hook the reviewer into reading the rest
- **Bold keywords**: LLM, RAG, Python, etc. — reviewers scan for these
- **Quantify claims** and explain *how* you achieved them ("increased productivity by 50% by implementing X" not just "increased by 50%")
- Mirror job listing language in your bullet points
- Work experience > education (put it first)
- Non-tech degrees still count (shows you went to university)
- Certificates/specializations = Stanford-branded courses = hook ("Stanford?!" → "oh, just a course" → but they're already reading)
- Skills section: **less is more** — don't list 10 languages; keep it authentic
- Include unique personal details (languages spoken, etc.) — conversation starters

### Job Application Strategy
- **Apply fast** — sort LinkedIn jobs by last 24 hours
- Use **boolean searches** in LinkedIn posts to find unlisted jobs (not on the job board feature)
- Get **LinkedIn Premium** — InMail to hiring managers, gold badge
- **Message the hiring manager** after applying — 2 sentences on why you're unique + perfect fit
- Find common ground with employees for referrals (same school, same interests)
- **Build a demo** for the target company — show you've thought about their problems
- Persistence > intelligence — the dedicated and patient win

---

## Cross-Cutting Themes

| Theme | Application |
|-------|-------------|
| **Modularity** | Split monolithic LLM calls into single-purpose nodes |
| **Don't over-engineer** | Workflows > agents when agents aren't needed |
| **Guardrails + RAG** | Reliability stack for production GenAI |
| **Benchmark first** | Always measure before optimizing |
| **Show results** | Quantify impact in interviews and on resume |
| **Domain expertise** | Industry knowledge > pure coding skill in the AI era |
| **Evals** | Making GenAI testable is rare and highly valued |
| **Uniqueness** | AI makes everyone same — differentiate or blend in |

---

## Part 3: What AI Teams Actually Look For When Hiring (Industry Perspective)

> Source: [How We Train AI Engineers — Building AI Teams](https://youtu.be/D7Xy89PDik8) — Oliver (AI engineering team lead) + host (senior AI engineer, former real estate agent), discussing hiring from real practice across 8 engineers trained in-house

### You Don't Need ML/Stats Background
- AI engineering ≠ ML engineering — you can go far with software engineering skills + creativity
- Easier to convert a **software engineer → AI engineer** than the reverse
- ML engineers often lack: architecture thinking, queues, data structures, scalability, the "full picture"
- GenAI is so new that you can't expect prior experience — teams train internally

### Top Trait: Creativity & R&D Mindset
- **Creativity > specific framework knowledge** — frameworks change constantly, some don't exist months later
- The biggest AI shifts (e.g. agentic AI) came from **developer creativity** in how information flows, not from model changes
- Looking for: drive to test things, validate things, try new products/tools on weekends
- Even vibe-coded weekend projects are valuable if you can explain them

### What Makes a Portfolio Project Stand Out
- **Volume doesn't matter** — 100 projects on a website loses all value
- AI can build what already exists — so building something **new** stands out
- Examples of impressive projects: new chunking strategies for RAG, novel approaches AI wouldn't generate on its own
- AI defaults to existing patterns (e.g. asks for GPT-5 → falls back to GPT-4o because "5 doesn't exist") — pushing past that shows skill
- **Explainability test**: can you explain what you built and why? Even vibe-coded apps — if you can articulate the problem + solution, that's valuable
- Look for code quality signals: spaghetti code = bad prompting, no system prompt = bad setup

### Business Value > Clean Architecture
- The shift: from "write cleanest architecture" → "make or save money"
- Product-minded developers who understand business problems > code purists
- Developers are becoming more like **project owners** — setting rules for agents, defining what gets output
- Real business value in a project is more impressive than technical perfection

### Mindset > Competence
- **Mindset is harder to change than competence** — the #1 hiring signal
- Looking for: willingness to learn, improve, adapt continuously
- Enterprise software engineering experience + agentic curiosity = ideal combination
- Focus more on: "has been a software engineer AND creative on the side" than specific tech stack

### Key Differentiator: Novelty in Projects
- Standard apps (JS calculator, another chatbot) = no signal anymore
- Projects that solve **new problems** or use **new techniques** = strong signal
- Being able to prompt AI past its defaults = demonstrates real engineering judgment
- Red flag in vibe-coded projects: no system prompts, no guidelines for the agent = shows lack of architectural thinking
