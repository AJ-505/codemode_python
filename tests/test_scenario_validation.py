"""Tests for strengthened scenario validation."""

import unittest

from tools import get_state
from tools.accounting_tools import create_invoice, create_transaction, update_invoice_status

try:
    from test_scenarios import validate_scenario_result
except ImportError:
    from tests.test_scenarios import validate_scenario_result


class ScenarioValidationTests(unittest.TestCase):
    def setUp(self):
        self.state = get_state()
        self.state.reset()

    def _validate(self, scenario_id: int):
        return validate_scenario_result(
            scenario_id,
            self.state.get_summary(),
            full_state=self.state.snapshot(),
        )

    def test_scenario_1_uses_exact_state_checks(self):
        create_transaction("expense", "Rent", 2500, "Monthly rent")
        create_transaction("expense", "Utilities (electricity)", 150, "Utilities")
        create_transaction("expense", "Internet/Phone", 100, "Internet and phone")
        create_transaction("expense", "Office supplies", 75, "Office supplies")

        result = self._validate(1)

        self.assertTrue(result["valid"])
        self.assertEqual(result["failed"], 0)

    def test_scenario_2_catches_wrong_invoice_total(self):
        create_invoice(
            "TechStart Inc",
            [
                {"description": "Software Development", "quantity": 80, "price": 150},
                {"description": "Code Review", "quantity": 10, "price": 100},
            ],
            due_days=30,
        )
        create_invoice(
            "Design Studio",
            [
                {"description": "UI/UX Design", "quantity": 40, "price": 125},
                {"description": "Prototyping", "quantity": 10, "price": 100},
            ],
            due_days=15,
        )
        update_invoice_status("INV00001", "sent")

        result = self._validate(2)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any(check["check"] == "Exact total invoice amount" and not check["passed"] for check in result["checks"])
        )

    def test_scenario_8_validates_major_category_totals(self):
        expenses = [
            ("rent", 2500, "Rent"),
            ("utilities", 180, "Utilities"),
            ("internet", 100, "Internet"),
            ("office_supplies", 250, "Office supplies"),
            ("cleaning_service", 200, "Cleaning service"),
            ("social_media_ads", 600, "Social media ads"),
            ("content_creation", 800, "Content creation"),
            ("seo_tools", 150, "SEO tools"),
            ("software_licenses", 450, "Software licenses"),
            ("cloud_hosting", 300, "Cloud hosting"),
            ("domain_renewals", 50, "Domain renewals"),
            ("online_courses", 200, "Online courses"),
            ("conference_ticket", 500, "Conference ticket"),
            ("books", 75, "Books"),
        ]
        for category, amount, description in expenses:
            create_transaction("expense", category, amount, description)

        result = self._validate(8)

        self.assertTrue(result["valid"])
        self.assertTrue(
            all(
                check["passed"]
                for check in result["checks"]
                if str(check["check"]).startswith("Major category total for ")
            )
        )


if __name__ == "__main__":
    unittest.main()
