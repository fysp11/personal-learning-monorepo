"""Deterministic VAT calculation engine.

This is intentionally NOT LLM-powered. Tax calculation must be deterministic
and testable with 100% branch coverage. Wrong VAT = compliance violation.
"""

from pydantic import BaseModel
from enum import Enum


class VATMechanism(str, Enum):
    STANDARD = "standard"
    REDUCED = "reduced"
    EXEMPT = "exempt"
    REVERSE_CHARGE = "reverse_charge"
    SMALL_BUSINESS = "small_business_exempt"  # Kleinunternehmerregelung


class VATResult(BaseModel):
    gross: float
    net: float
    vat_amount: float
    vat_rate: float
    mechanism: VATMechanism
    country: str
    note: str | None = None


# EU VAT rates by country (standard and reduced)
EU_VAT_RATES: dict[str, dict[str, float]] = {
    "DE": {"standard": 0.19, "reduced": 0.07},
    "FR": {"standard": 0.20, "reduced": 0.055, "intermediate": 0.10, "super_reduced": 0.021},
    "IT": {"standard": 0.22, "reduced": 0.10, "reduced_2": 0.05, "super_reduced": 0.04},
    "ES": {"standard": 0.21, "reduced": 0.10, "super_reduced": 0.04},
    "NL": {"standard": 0.21, "reduced": 0.09},
}

# SKR03 categories that use reduced VAT rate in Germany
REDUCED_VAT_CATEGORIES_DE = {
    "4940",  # Zeitschriften/Bücher (magazines/books)
    "4945",  # Fachliteratur (professional literature)
}

# SKR03 categories that are VAT-exempt
EXEMPT_CATEGORIES = {
    "4520",  # Kfz-Versicherungen (vehicle insurance)
    "4360",  # Versicherungen (insurance general)
    "4390",  # Sonstige Abgaben (certain government fees)
}


def calculate_vat(
    amount: float,
    category_code: str,
    country: str = "DE",
    is_b2b_intra_eu: bool = False,
    counterparty_vat_id: str | None = None,
    is_small_business: bool = False,
) -> VATResult:
    """Calculate VAT for a transaction using deterministic rules.

    Args:
        amount: Gross transaction amount in EUR
        category_code: SKR03 account code (for DE) or equivalent
        country: ISO 2-letter country code
        is_b2b_intra_eu: Whether this is an intra-EU B2B transaction
        counterparty_vat_id: EU VAT ID of counterparty (for reverse charge)
        is_small_business: Whether the business uses Kleinunternehmerregelung
    """
    # Kleinunternehmerregelung: exempt from VAT if revenue < €22,000
    if is_small_business:
        return VATResult(
            gross=amount,
            net=amount,
            vat_amount=0.0,
            vat_rate=0.0,
            mechanism=VATMechanism.SMALL_BUSINESS,
            country=country,
            note="Kleinunternehmerregelung §19 UStG — no VAT charged or deducted",
        )

    # Reverse charge for intra-EU B2B with valid VAT ID
    if is_b2b_intra_eu and counterparty_vat_id:
        return VATResult(
            gross=amount,
            net=amount,
            vat_amount=0.0,
            vat_rate=0.0,
            mechanism=VATMechanism.REVERSE_CHARGE,
            country=country,
            note=f"Reverse charge §13b UStG. Counterparty VAT: {counterparty_vat_id}",
        )

    # VAT-exempt categories
    if category_code in EXEMPT_CATEGORIES:
        return VATResult(
            gross=amount,
            net=amount,
            vat_amount=0.0,
            vat_rate=0.0,
            mechanism=VATMechanism.EXEMPT,
            country=country,
            note=f"VAT-exempt category {category_code}",
        )

    # Get country rates
    rates = EU_VAT_RATES.get(country)
    if not rates:
        raise ValueError(f"Unsupported country: {country}. Supported: {list(EU_VAT_RATES.keys())}")

    # Determine rate: reduced or standard
    if country == "DE" and category_code in REDUCED_VAT_CATEGORIES_DE:
        rate = rates["reduced"]
        mechanism = VATMechanism.REDUCED
    else:
        rate = rates["standard"]
        mechanism = VATMechanism.STANDARD

    # Calculate: amount is gross (includes VAT)
    net = round(amount / (1 + rate), 2)
    vat_amount = round(amount - net, 2)

    return VATResult(
        gross=amount,
        net=net,
        vat_amount=vat_amount,
        vat_rate=rate,
        mechanism=mechanism,
        country=country,
    )
