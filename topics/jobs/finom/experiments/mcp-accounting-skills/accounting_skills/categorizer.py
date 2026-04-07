"""Transaction categorization engine.

Uses rule-based matching with merchant history as the primary signal,
falling back to heuristic matching. In production, the fallback would
be an LLM with structured output (e.g., GPT-4o with JSON schema).
"""

from pydantic import BaseModel


class CategoryResult(BaseModel):
    skr03_code: str
    category_name: str
    confidence: float
    reasoning: str


# Common SKR03 categories for German SMBs / freelancers
SKR03_CATEGORIES: dict[str, str] = {
    "4650": "Bewirtungskosten (business meals/entertainment)",
    "4654": "Nicht abzugsfähige Bewirtungskosten (non-deductible meals)",
    "4660": "Reisekosten Arbeitnehmer (employee travel)",
    "4670": "Reisekosten Unternehmer (owner travel)",
    "4806": "Reparaturen/Instandhaltung (repairs/maintenance)",
    "4900": "Sonstige betriebliche Aufwendungen (other operating expenses)",
    "4910": "Porto (postage)",
    "4920": "Telefon (telephone/internet)",
    "4921": "Internetkosten (internet costs)",
    "4930": "Bürobedarf (office supplies)",
    "4940": "Zeitschriften/Bücher (magazines/books, 7% VAT)",
    "4945": "Fachliteratur (professional literature, 7% VAT)",
    "4946": "Aus-/Fortbildung (training/education)",
    "4955": "Werbung (advertising)",
    "4957": "Online-Marketing (online marketing/ads)",
    "4960": "Miete/Leasing für Büroeinrichtung (rent/lease office equipment)",
    "4964": "EDV-Kosten/Software (IT/software costs)",
    "4969": "Sonstige EDV-Kosten (other IT costs)",
    "4970": "Nebenkosten des Geldverkehrs (bank charges)",
    "4980": "Rechts-/Beratungskosten (legal/consulting)",
    "4520": "Kfz-Versicherungen (vehicle insurance)",
}

# Merchant keyword → category mapping (rule-based, high confidence)
MERCHANT_RULES: dict[str, tuple[str, str]] = {
    # Software & SaaS
    "github": ("4964", "GitHub subscription — IT/software costs"),
    "aws": ("4964", "AWS cloud services — IT/software costs"),
    "google cloud": ("4964", "Google Cloud — IT/software costs"),
    "azure": ("4964", "Microsoft Azure — IT/software costs"),
    "heroku": ("4964", "Heroku — IT/software costs"),
    "vercel": ("4964", "Vercel — IT/software costs"),
    "netlify": ("4964", "Netlify — IT/software costs"),
    "notion": ("4964", "Notion — IT/software costs"),
    "slack": ("4964", "Slack — IT/software costs"),
    "zoom": ("4964", "Zoom — IT/software costs"),
    "figma": ("4964", "Figma — IT/software costs"),
    "adobe": ("4964", "Adobe — IT/software costs"),
    "jetbrains": ("4964", "JetBrains IDE — IT/software costs"),
    "openai": ("4964", "OpenAI API — IT/software costs"),
    "anthropic": ("4964", "Anthropic API — IT/software costs"),
    # Advertising
    "google ads": ("4957", "Google Ads — online marketing"),
    "meta ads": ("4957", "Meta/Facebook Ads — online marketing"),
    "linkedin ads": ("4957", "LinkedIn Ads — online marketing"),
    # Telecom
    "vodafone": ("4920", "Vodafone — telephone/internet"),
    "t-mobile": ("4920", "T-Mobile — telephone/internet"),
    "kpn": ("4920", "KPN — telephone/internet"),
    # Travel
    "deutsche bahn": ("4670", "Deutsche Bahn — travel costs"),
    "db bahn": ("4670", "Deutsche Bahn — travel costs"),
    "ns.nl": ("4670", "NS (Dutch Railways) — travel costs"),
    "lufthansa": ("4670", "Lufthansa — travel costs"),
    "klm": ("4670", "KLM — travel costs"),
    "booking.com": ("4670", "Booking.com — travel/accommodation"),
    "airbnb": ("4670", "Airbnb — travel/accommodation"),
    "uber": ("4670", "Uber — travel costs"),
    "bolt": ("4670", "Bolt — travel costs"),
    # Office
    "amazon": ("4930", "Amazon — office supplies (review if personal)"),
    "ikea": ("4930", "IKEA — office supplies/furniture"),
    "staples": ("4930", "Staples — office supplies"),
    # Banking
    "bank": ("4970", "Bank charges — financial costs"),
    "stripe": ("4970", "Stripe — payment processing fees"),
    "paypal": ("4970", "PayPal — payment processing fees"),
    # Books & Education
    "udemy": ("4946", "Udemy — professional training"),
    "coursera": ("4946", "Coursera — professional training"),
    "o'reilly": ("4945", "O'Reilly — professional literature"),
    # Meals
    "restaurant": ("4650", "Restaurant — business meals"),
    "deliveroo": ("4650", "Deliveroo — business meals"),
    "uber eats": ("4650", "Uber Eats — business meals"),
    "thuisbezorgd": ("4650", "Thuisbezorgd — business meals"),
    # Postal
    "postnl": ("4910", "PostNL — postage"),
    "dhl": ("4910", "DHL — postage/shipping"),
    "ups": ("4910", "UPS — postage/shipping"),
}


def categorize_transaction(
    merchant_name: str,
    amount: float,
    description: str = "",
    user_history: dict[str, str] | None = None,
) -> CategoryResult:
    """Categorize a bank transaction to SKR03 account code.

    Priority:
    1. User history (strongest signal — how did this user categorize this merchant before?)
    2. Merchant keyword rules (high confidence, deterministic)
    3. Description analysis (medium confidence, heuristic)
    4. Default fallback (low confidence, needs review)

    In production, step 3-4 would be an LLM with structured output.
    """
    merchant_lower = merchant_name.lower()
    description_lower = description.lower()

    # Priority 1: User history for this merchant
    if user_history and merchant_lower in user_history:
        code = user_history[merchant_lower]
        return CategoryResult(
            skr03_code=code,
            category_name=SKR03_CATEGORIES.get(code, "Unknown"),
            confidence=0.95,
            reasoning=f"User previously categorized '{merchant_name}' as {code}",
        )

    # Priority 2: Merchant keyword rules
    for keyword, (code, reason) in MERCHANT_RULES.items():
        if keyword in merchant_lower:
            return CategoryResult(
                skr03_code=code,
                category_name=SKR03_CATEGORIES.get(code, "Unknown"),
                confidence=0.90,
                reasoning=reason,
            )

    # Priority 3: Description keyword analysis (simplified heuristic)
    combined = f"{merchant_lower} {description_lower}"
    description_signals = [
        (["software", "saas", "subscription", "api", "cloud", "hosting"], "4964", "Software/SaaS pattern in description"),
        (["hotel", "flight", "travel", "train", "taxi"], "4670", "Travel pattern in description"),
        (["restaurant", "cafe", "lunch", "dinner", "catering"], "4650", "Meal/dining pattern in description"),
        (["office", "stationery", "supplies", "desk", "chair"], "4930", "Office supply pattern in description"),
        (["phone", "internet", "mobile", "telecom"], "4920", "Telecom pattern in description"),
        (["ad", "marketing", "campaign", "promotion"], "4955", "Advertising pattern in description"),
        (["legal", "lawyer", "attorney", "consulting"], "4980", "Legal/consulting pattern in description"),
        (["insurance", "versicherung"], "4900", "Insurance pattern in description"),
        (["book", "course", "training", "seminar", "workshop"], "4946", "Education/training pattern in description"),
    ]

    for keywords, code, reason in description_signals:
        if any(kw in combined for kw in keywords):
            return CategoryResult(
                skr03_code=code,
                category_name=SKR03_CATEGORIES.get(code, "Unknown"),
                confidence=0.65,
                reasoning=f"{reason} — medium confidence, review recommended",
            )

    # Priority 4: Default fallback — needs human review
    return CategoryResult(
        skr03_code="4900",
        category_name=SKR03_CATEGORIES["4900"],
        confidence=0.30,
        reasoning=f"No pattern match for '{merchant_name}' — defaulting to general operating expenses. Human review required.",
    )
