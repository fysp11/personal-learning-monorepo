"""Tests for the deterministic VAT calculation engine.

VAT calculation is the most critical component — wrong VAT = compliance violation.
These tests aim for 100% branch coverage of the VAT rules.
"""

import pytest
from accounting_skills.vat import calculate_vat, VATMechanism


class TestGermanVAT:
    """Test German (DE) VAT calculations — 19% standard, 7% reduced."""

    def test_standard_rate(self):
        result = calculate_vat(amount=119.0, category_code="4930", country="DE")
        assert result.vat_rate == 0.19
        assert result.net == 100.0
        assert result.vat_amount == 19.0
        assert result.mechanism == VATMechanism.STANDARD

    def test_reduced_rate_books(self):
        """Books and magazines use 7% reduced rate in Germany."""
        result = calculate_vat(amount=10.70, category_code="4940", country="DE")
        assert result.vat_rate == 0.07
        assert result.net == 10.0
        assert result.vat_amount == 0.70
        assert result.mechanism == VATMechanism.REDUCED

    def test_reduced_rate_professional_literature(self):
        result = calculate_vat(amount=53.50, category_code="4945", country="DE")
        assert result.vat_rate == 0.07
        assert result.mechanism == VATMechanism.REDUCED

    def test_vat_exempt_insurance(self):
        result = calculate_vat(amount=200.0, category_code="4520", country="DE")
        assert result.vat_rate == 0.0
        assert result.vat_amount == 0.0
        assert result.net == 200.0
        assert result.mechanism == VATMechanism.EXEMPT

    def test_rounding(self):
        """Ensure proper rounding for non-round amounts."""
        result = calculate_vat(amount=45.80, category_code="4650", country="DE")
        assert result.net == 38.49
        assert result.vat_amount == 7.31
        assert abs(result.net + result.vat_amount - result.gross) < 0.01


class TestReverseCharge:
    """Test intra-EU B2B reverse charge mechanism."""

    def test_reverse_charge_with_vat_id(self):
        result = calculate_vat(
            amount=1000.0,
            category_code="4964",
            country="DE",
            is_b2b_intra_eu=True,
            counterparty_vat_id="NL123456789B01",
        )
        assert result.vat_rate == 0.0
        assert result.vat_amount == 0.0
        assert result.net == 1000.0
        assert result.mechanism == VATMechanism.REVERSE_CHARGE
        assert "NL123456789B01" in result.note

    def test_no_reverse_charge_without_vat_id(self):
        """B2B intra-EU without VAT ID should use standard rate."""
        result = calculate_vat(
            amount=1000.0,
            category_code="4964",
            country="DE",
            is_b2b_intra_eu=True,
            counterparty_vat_id=None,
        )
        assert result.mechanism == VATMechanism.STANDARD
        assert result.vat_rate == 0.19


class TestSmallBusiness:
    """Test Kleinunternehmerregelung (small business exemption)."""

    def test_small_business_exempt(self):
        result = calculate_vat(
            amount=500.0,
            category_code="4930",
            country="DE",
            is_small_business=True,
        )
        assert result.vat_rate == 0.0
        assert result.vat_amount == 0.0
        assert result.net == 500.0
        assert result.mechanism == VATMechanism.SMALL_BUSINESS
        assert "§19 UStG" in result.note


class TestMultiCountry:
    """Test VAT rates across supported EU markets."""

    def test_france_standard(self):
        result = calculate_vat(amount=120.0, category_code="4964", country="FR")
        assert result.vat_rate == 0.20
        assert result.mechanism == VATMechanism.STANDARD

    def test_italy_standard(self):
        result = calculate_vat(amount=122.0, category_code="4964", country="IT")
        assert result.vat_rate == 0.22
        assert result.mechanism == VATMechanism.STANDARD

    def test_spain_standard(self):
        result = calculate_vat(amount=121.0, category_code="4964", country="ES")
        assert result.vat_rate == 0.21
        assert result.mechanism == VATMechanism.STANDARD

    def test_netherlands_standard(self):
        result = calculate_vat(amount=121.0, category_code="4964", country="NL")
        assert result.vat_rate == 0.21
        assert result.mechanism == VATMechanism.STANDARD

    def test_unsupported_country(self):
        with pytest.raises(ValueError, match="Unsupported country"):
            calculate_vat(amount=100.0, category_code="4930", country="XX")


class TestBalanceIntegrity:
    """Ensure gross = net + vat for every calculation."""

    @pytest.mark.parametrize(
        "amount,category,country",
        [
            (119.0, "4930", "DE"),
            (45.80, "4650", "DE"),
            (10.70, "4940", "DE"),
            (1234.56, "4964", "FR"),
            (999.99, "4670", "IT"),
            (0.01, "4910", "NL"),
            (99999.99, "4980", "ES"),
        ],
    )
    def test_gross_equals_net_plus_vat(self, amount, category, country):
        result = calculate_vat(amount=amount, category_code=category, country=country)
        assert abs(result.gross - (result.net + result.vat_amount)) < 0.02
