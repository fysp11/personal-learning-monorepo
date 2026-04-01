"""Tests for the transaction categorization engine."""

from accounting_skills.categorizer import categorize_transaction


class TestMerchantRules:
    """Test rule-based merchant matching."""

    def test_github_categorized_as_software(self):
        result = categorize_transaction("GitHub", 4.0)
        assert result.skr03_code == "4964"
        assert result.confidence >= 0.85

    def test_aws_categorized_as_software(self):
        result = categorize_transaction("AWS", 150.0)
        assert result.skr03_code == "4964"

    def test_deutsche_bahn_categorized_as_travel(self):
        result = categorize_transaction("Deutsche Bahn", 89.0)
        assert result.skr03_code == "4670"

    def test_restaurant_categorized_as_meals(self):
        result = categorize_transaction("Restaurant De Keuken", 45.80)
        assert result.skr03_code == "4650"

    def test_postnl_categorized_as_postage(self):
        result = categorize_transaction("PostNL", 8.95)
        assert result.skr03_code == "4910"

    def test_stripe_categorized_as_bank_charges(self):
        result = categorize_transaction("Stripe", 12.50)
        assert result.skr03_code == "4970"


class TestUserHistory:
    """Test that user history takes priority over rules."""

    def test_user_history_overrides_rules(self):
        # Amazon defaults to office supplies, but user has categorized as "advertising" before
        result = categorize_transaction(
            "Amazon",
            50.0,
            user_history={"amazon": "4955"},
        )
        assert result.skr03_code == "4955"
        assert result.confidence >= 0.90

    def test_user_history_case_insensitive(self):
        result = categorize_transaction(
            "GITHUB",
            4.0,
            user_history={"github": "4969"},
        )
        assert result.skr03_code == "4969"


class TestDescriptionFallback:
    """Test description-based heuristic matching."""

    def test_description_software_signal(self):
        result = categorize_transaction(
            "Unknown Merchant",
            99.0,
            description="Monthly SaaS subscription",
        )
        assert result.skr03_code == "4964"
        assert result.confidence < 0.85  # lower confidence for description-based

    def test_description_travel_signal(self):
        result = categorize_transaction(
            "Some Company",
            250.0,
            description="Hotel booking for conference",
        )
        assert result.skr03_code == "4670"


class TestLowConfidence:
    """Test that unknown transactions get low confidence."""

    def test_unknown_merchant_low_confidence(self):
        result = categorize_transaction("Random XYZ Corp", 100.0)
        assert result.confidence < 0.50
        assert result.skr03_code == "4900"  # default: general operating expenses

    def test_low_confidence_flags_review(self):
        result = categorize_transaction("???", 1000.0)
        assert "review" in result.reasoning.lower() or result.confidence < 0.50
