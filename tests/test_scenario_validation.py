"""Tests for strengthened scenario validation."""

import unittest

from tools import get_state
from tools.accounting_tools import (
    approve_purchase_order,
    create_customer,
    create_invoice,
    create_project,
    create_purchase_order,
    create_support_ticket,
    create_transaction,
    log_time_entry,
    schedule_meeting,
    update_invoice_status,
    update_support_ticket,
    receive_purchase_order,
)

try:
    from test_scenarios import get_date, validate_scenario_result
except ImportError:
    from tests.test_scenarios import get_date, validate_scenario_result


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

    def test_scenario_9_validates_customer_project_support_workflow(self):
        create_customer(
            "Northwind Labs",
            "ops@northwind.example",
            tier="enterprise",
            payment_terms_days=15,
        )
        customer_id = self.state.customers[0]["id"]
        create_project(customer_id, "Website Revamp", 180, 120)
        project_id = self.state.projects[0]["id"]
        log_time_entry(project_id, "Alice", 6, "Discovery workshop")
        log_time_entry(project_id, "Bob", 4.5, "UI prototype")
        create_support_ticket(customer_id, "SSO login issue", priority="high")
        ticket_id = self.state.support_tickets[0]["id"]
        update_support_ticket(ticket_id, "resolved")
        schedule_meeting(
            "Northwind kickoff",
            ["ops@northwind.example", "pm@agency.example"],
            get_date(1),
            60,
        )

        result = self._validate(9)

        self.assertTrue(result["valid"])
        self.assertEqual(result["failed"], 0)

    def test_scenario_10_validates_procurement_workflow(self):
        create_purchase_order(
            "Acme Hardware",
            [
                {"description": "Monitor", "quantity": 3, "price": 220},
                {"description": "Keyboard", "quantity": 5, "price": 45},
                {"description": "Docking station", "quantity": 2, "price": 180},
            ],
        )
        create_purchase_order(
            "CloudHost LLC",
            [
                {"description": "Annual hosting renewal", "quantity": 1, "price": 1200},
            ],
        )
        approve_purchase_order("PO00001")
        approve_purchase_order("PO00002")
        receive_purchase_order("PO00001")

        result = self._validate(10)

        self.assertTrue(result["valid"])
        self.assertEqual(result["failed"], 0)


if __name__ == "__main__":
    unittest.main()
