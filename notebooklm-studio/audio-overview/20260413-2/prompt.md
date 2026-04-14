# Audio Overview 2: AI Design Patterns & Architectures

Create an audio overview on how to design reliable AI systems for production, especially in financial or workflow-heavy environments.

Explain staged workflows versus single agents, and why staged workflows are required when failure modes are heterogeneous and trust levels differ across steps. Cover the deterministic versus AI boundary using the principle that policy and compliance-critical logic must be code, while ambiguous interpretation can be AI-powered. Explain confidence routing with three zones: auto-act, propose, and reject or review, and why the middle proposal zone is where autonomy is earned rather than assumed.

Cover calibration and Expected Calibration Error (ECE), including why routing thresholds are meaningless if confidence scores are not calibrated. Explain the automation maturity ladder from shadow mode to full automation, and why progression should be based on measured performance rather than enthusiasm. Include the key invariants of a production workflow: terminal state, idempotency, and auditability. Use MarketConfig or policy modules as a concrete example of keeping market-specific rules in code rather than prompts.

Keep the tone precise and architectural. Focus on failure modes, control points, invariants, and production decision-making rather than generic AI pattern vocabulary.
