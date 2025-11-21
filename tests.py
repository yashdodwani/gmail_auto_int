import unittest
from datetime import datetime, timedelta, timezone
from process_emails import evaluate_rule

class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        # Mock email data
        self.email = {
            "message_id": "123",
            "sender": "hr@happyfox.com",
            "subject": "Your Interview Schedule",
            "snippet": "Please find attached...",
            "received_date": datetime.now(timezone.utc) - timedelta(days=1) # 1 day old
        }

    def test_string_contains_match(self):
        rule = {
            "predicate": "All",
            "conditions": [
                {"field": "Subject", "predicate": "contains", "value": "Interview"}
            ]
        }
        self.assertTrue(evaluate_rule(self.email, rule))

    def test_string_contains_no_match(self):
        rule = {
            "predicate": "All",
            "conditions": [
                {"field": "Subject", "predicate": "contains", "value": "Reject"}
            ]
        }
        self.assertFalse(evaluate_rule(self.email, rule))

    def test_date_less_than_match(self):
        # Email is 1 day old, Rule expects < 2 days
        rule = {
            "predicate": "All",
            "conditions": [
                {"field": "Received Date/Time", "predicate": "less than", "value": "2", "unit": "days"}
            ]
        }
        self.assertTrue(evaluate_rule(self.email, rule))

    def test_predicate_any_logic(self):
        # One condition fails (Sender), one passes (Subject) -> Should Pass
        rule = {
            "predicate": "Any",
            "conditions": [
                {"field": "From", "predicate": "contains", "value": "google.com"}, # Fails
                {"field": "Subject", "predicate": "contains", "value": "Interview"} # Passes
            ]
        }
        self.assertTrue(evaluate_rule(self.email, rule))

if __name__ == '__main__':
    unittest.main()