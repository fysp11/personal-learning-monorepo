"""
RAG-Augmented Categorization — Production Pattern

The production categorizer for Finom is not a keyword matcher.
It uses retrieval over a business's own transaction history to provide
high-quality context to the LLM before it makes a category proposal.

Why RAG for categorization:
  - The same merchant can map to different accounts for different businesses
    (e.g., "Amazon" = 4940 IT costs for a dev shop, 4800 office supplies for a law firm)
  - Transaction history is the ground truth for how this specific business books things
  - RAG enables few-shot examples that are relevant to the exact merchant + business context

Pipeline:
  1. Query rewrite: normalize the merchant + context into a canonical search form
  2. Retrieve: find similar past transactions from this business's history
  3. Re-rank: filter to high-signal, high-similarity evidence
  4. LLM call: categorize with retrieved examples as context
  5. Evidence gate: require evidence support before auto-book

Run:
    python3 rag_categorizer.py
"""

import math
import random
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────
# Transaction history store (mock vector DB)
# ─────────────────────────────────────────

@dataclass
class HistoricalTransaction:
    id: str
    merchant: str
    description: str
    account_code: str
    human_verified: bool
    embedding: list[float] = field(default_factory=list)   # simulated


@dataclass
class RetrievedExample:
    transaction: HistoricalTransaction
    similarity: float   # cosine similarity [0, 1]
    is_high_signal: bool  # similarity above re-rank threshold


# Simulated transaction history for business "biz-001"
TRANSACTION_HISTORY: list[HistoricalTransaction] = [
    HistoricalTransaction(
        id="h1", merchant="Amazon Web Services",
        description="EC2 + S3 monthly", account_code="4940",
        human_verified=True,
    ),
    HistoricalTransaction(
        id="h2", merchant="AWS EMEA",
        description="CloudFront charges", account_code="4940",
        human_verified=True,
    ),
    HistoricalTransaction(
        id="h3", merchant="Lieferando",
        description="team lunch for sprint review", account_code="4650",
        human_verified=True,
    ),
    HistoricalTransaction(
        id="h4", merchant="Uber Deutschland",
        description="airport pickup", account_code="4670",
        human_verified=True,
    ),
    HistoricalTransaction(
        id="h5", merchant="Deutsche Telekom",
        description="monthly mobile contract", account_code="4920",
        human_verified=False,   # not human-verified — lower trust
    ),
    HistoricalTransaction(
        id="h6", merchant="IONOS SE",
        description="web hosting", account_code="4940",
        human_verified=True,
    ),
]


def embed(text: str) -> list[float]:
    """
    Mock embedding: token overlap bag-of-words vector.
    Semantically similar texts share tokens → higher cosine similarity.
    In production: replace with text-embedding-3-small API call.
    """
    tokens = set(text.lower().split())
    vocabulary = [
        "amazon", "web", "services", "aws", "cloud", "ec2", "s3", "hosting",
        "lieferando", "lunch", "food", "meal", "delivery",
        "uber", "travel", "airport", "transport", "ride",
        "telekom", "mobile", "phone", "telecom", "contract",
        "consulting", "advisory", "professional", "legal", "notary",
        "office", "supplies", "stationery", "ionos", "hosting",
    ]
    return [1.0 if word in tokens else 0.0 for word in vocabulary]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def normalize_to_01(x: float) -> float:
    """Map cosine similarity from [-1,1] to [0,1]."""
    return (x + 1) / 2


# ─────────────────────────────────────────
# Stage 1: Query rewrite
# Normalize the raw merchant + description into a canonical search query.
# Prevents trivial mismatches ("AWS" vs "Amazon Web Services EMEA").
# ─────────────────────────────────────────

MERCHANT_ALIASES: dict[str, str] = {
    "aws": "amazon web services",
    "amazon.de": "amazon web services",
    "amzn": "amazon web services",
    "gls": "gls parcel service",
    "dt ag": "deutsche telekom",
}

def rewrite_query(merchant: str, description: str) -> str:
    """
    Canonicalizes the query so the retriever finds related variants.
    In production: LLM call with few-shot normalization examples.
    """
    normalized = MERCHANT_ALIASES.get(merchant.lower().strip(), merchant.lower())
    return f"{normalized} {description}".strip()


# ─────────────────────────────────────────
# Stage 2: Retrieve from history
# ─────────────────────────────────────────

RETRIEVAL_THRESHOLD = 0.55   # minimum similarity to include in context
RERANK_THRESHOLD = 0.70      # above this: high-signal evidence


def retrieve_similar(
    query: str,
    history: list[HistoricalTransaction],
    top_k: int = 3,
) -> list[RetrievedExample]:
    """
    Retrieve top-k most similar transactions from history.
    Re-rank: mark examples above threshold as high-signal.
    """
    query_embedding = embed(query)

    scored = []
    for tx in history:
        tx_text = f"{tx.merchant} {tx.description}"
        tx_embedding = embed(tx_text)
        sim = normalize_to_01(cosine_similarity(query_embedding, tx_embedding))
        if sim >= RETRIEVAL_THRESHOLD:
            scored.append((tx, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [
        RetrievedExample(
            transaction=tx,
            similarity=sim,
            is_high_signal=sim >= RERANK_THRESHOLD,
        )
        for tx, sim in scored[:top_k]
    ]


# ─────────────────────────────────────────
# Stage 3: LLM categorization with retrieved context
# ─────────────────────────────────────────

@dataclass
class CategoryProposal:
    account_code: str
    confidence: float
    evidence: str
    retrieval_support: bool   # True if at least one high-signal example was found


def categorize_with_rag(
    merchant: str,
    description: str,
    retrieved: list[RetrievedExample],
) -> CategoryProposal:
    """
    Mock LLM categorization with retrieved examples as context.
    In production: LLM call with system prompt + retrieved examples + current transaction.

    Evidence gate: confidence is elevated only when high-signal retrieved examples agree.
    Unsupported certainty = medium confidence at best — never high enough for auto-book.
    """
    high_signal = [r for r in retrieved if r.is_high_signal and r.transaction.human_verified]

    if high_signal:
        # Use the most similar verified example's account code
        best = high_signal[0]
        base_confidence = 0.90 if len(high_signal) >= 2 else 0.82
        # Confidence modulated by similarity
        confidence = round(base_confidence * (0.7 + 0.3 * best.similarity), 3)
        return CategoryProposal(
            account_code=best.transaction.account_code,
            confidence=confidence,
            evidence=f"retrieved {len(high_signal)} high-signal example(s); best match: '{best.transaction.merchant}' → {best.transaction.account_code} (sim={best.similarity:.2f})",
            retrieval_support=True,
        )

    # Low-signal retrieval — reduce confidence, flag as unsupported
    if retrieved:
        best_sim = retrieved[0].similarity
        return CategoryProposal(
            account_code=retrieved[0].transaction.account_code,
            confidence=round(0.55 * best_sim, 3),
            evidence=f"weak retrieval (best sim={best_sim:.2f}, not human-verified) — proposal only",
            retrieval_support=False,
        )

    return CategoryProposal(
        account_code="4990",
        confidence=0.20,
        evidence="no retrieval results — manual categorization required",
        retrieval_support=False,
    )


# ─────────────────────────────────────────
# Stage 4: Evidence gate
# Auto-book requires: confidence ≥ threshold AND retrieval_support = True
# ─────────────────────────────────────────

AUTO_BOOK_THRESHOLD = 0.85

def can_auto_book(proposal: CategoryProposal) -> bool:
    """
    Confidence alone is not enough for auto-book.
    Evidence support is required — unsupported certainty does not earn autonomy.
    """
    return proposal.confidence >= AUTO_BOOK_THRESHOLD and proposal.retrieval_support


# ─────────────────────────────────────────
# Full RAG categorization pipeline
# ─────────────────────────────────────────

def categorize_transaction_rag(
    merchant: str,
    description: str,
    history: list[HistoricalTransaction],
) -> dict:
    """
    Full RAG categorization: query rewrite → retrieve → re-rank → LLM → evidence gate.
    Returns structured result with full provenance.
    """
    query = rewrite_query(merchant, description)
    retrieved = retrieve_similar(query, history)
    proposal = categorize_with_rag(merchant, description, retrieved)
    auto_book = can_auto_book(proposal)

    return {
        "merchant": merchant,
        "query": query,
        "retrieved_count": len(retrieved),
        "high_signal_count": sum(1 for r in retrieved if r.is_high_signal),
        "proposal": proposal,
        "auto_book": auto_book,
        "routing": "AUTO_BOOKED" if auto_book else (
            "PROPOSAL_SENT" if proposal.confidence >= 0.55 else "REJECTED"
        ),
    }


# ─────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────

if __name__ == "__main__":
    test_merchants = [
        ("AWS", "monthly EC2 charges"),          # in history, strong match
        ("Amazon Web Services", "S3 storage"),   # variant, should still match via alias
        ("Lieferando", "team lunch"),            # in history
        ("Unknown Vendor GmbH", "miscellaneous"),  # no history
        ("Deutsche Telekom", "mobile phone"),    # in history but unverified
    ]

    print("\n══ RAG-Augmented Categorization Demo ══\n")
    print("  Transaction history: 6 examples for business biz-001")
    print("  Human-verified: 5/6\n")

    print(f"  {'Merchant':<28} {'Route':<16} {'Conf':<8} {'Support':<10} {'Account'}")
    print(f"  {'─'*28} {'─'*16} {'─'*8} {'─'*10} {'─'*8}")

    for merchant, desc in test_merchants:
        result = categorize_transaction_rag(merchant, desc, TRANSACTION_HISTORY)
        p = result["proposal"]
        support_icon = "✓ cited" if p.retrieval_support else "✗ none"
        print(f"  {merchant:<28} {result['routing']:<16} {p.confidence:.2f}    {support_icon:<10} {p.account_code}")

    print("\n  ── Evidence gate explanation ────────────────────────────")
    print("  AUTO_BOOKED requires: confidence ≥ 0.85 AND retrieval_support = True")
    print("  A confident-but-unsupported proposal stays in PROPOSAL_SENT")
    print("  This prevents: 'the model felt sure' from becoming a booking without evidence")
    print()
    print("  ── Why query rewrite matters ────────────────────────────")
    print("  'AWS' → 'amazon web services [description]'")
    print("  Without rewrite: 'AWS' and 'Amazon Web Services EMEA' would have low similarity")
    print("  With rewrite: the alias table canonicalizes them to the same query vector")
    print()
    print("  ── Production upgrade path ──────────────────────────────")
    print("  1. Replace embed() with text-embedding-3-small API call")
    print("  2. Replace TRANSACTION_HISTORY with vector DB (pgvector, Pinecone, Qdrant)")
    print("  3. Replace categorize_with_rag() with LLM call + retrieved examples in context")
    print("  4. Add learning loop: confirmed bookings → write back to history store")
