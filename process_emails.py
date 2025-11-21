import json
import datetime
from dateutil import parser
from fetch_emails import get_gmail_service
from db import get_all_emails


def load_rules():
    """Reads the rules from the JSON file."""
    with open('rules.json', 'r') as f:
        return json.load(f)


def check_string_rule(value, predicate, target):
    """Evaluates string conditions (contains, equals, etc)."""
    value = value.lower() if value else ""
    target = target.lower()

    if predicate == 'contains':
        return target in value
    elif predicate == 'does not contain':
        return target not in value
    elif predicate == 'equals':
        return value == target
    elif predicate == 'does not equal':
        return value != target
    return False


def check_date_rule(email_date, predicate, value, unit):
    """Evaluates date conditions (less than X days/months)."""
    # email_date is already a datetime object from our DB
    now = datetime.datetime.now(datetime.timezone.utc)

    # Calculate the difference
    diff = now - email_date

    days_diff = diff.days

    target_value = int(value)

    if unit == 'days':
        if predicate == 'less than':
            return days_diff < target_value
        elif predicate == 'greater than':
            return days_diff > target_value

    elif unit == 'months':
        # Approximate months as 30 days
        months_diff = days_diff / 30
        if predicate == 'less than':
            return months_diff < target_value
        elif predicate == 'greater than':
            return months_diff > target_value

    return False


def evaluate_rule(email, rule):
    """
    Checks if an email matches a specific rule.
    Returns True if actions should be taken.
    """
    results = []

    for condition in rule['conditions']:
        field = condition['field']
        predicate = condition['predicate']
        value = condition['value']

        # Map fields to our DB column names
        email_value = ""
        if field == 'From':
            email_value = email['sender']
        elif field == 'Subject':
            email_value = email['subject']
        elif field == 'Message':
            email_value = email['snippet']
        elif field == 'Received Date/Time':
            # Special handling for dates
            unit = condition.get('unit', 'days')
            match = check_date_rule(email['received_date'], predicate, value, unit)
            results.append(match)
            continue  # Skip string check for dates

        # Standard string check
        match = check_string_rule(email_value, predicate, value)
        results.append(match)

    # Apply the Overall Predicate (All vs Any)
    if rule['predicate'] == 'All':
        return all(results)
    elif rule['predicate'] == 'Any':
        return any(results)
    return False


def perform_actions(service, message_id, actions):
    """Executes the actions using Gmail API."""
    add_labels = []
    remove_labels = []

    for action in actions:
        if action['type'] == 'mark_as_read':
            remove_labels.append('UNREAD')
            print(f"   -> Action: Mark as Read")

        elif action['type'] == 'mark_as_unread':
            add_labels.append('UNREAD')
            print(f"   -> Action: Mark as Unread")

        elif action['type'] == 'move_message':
            # In Gmail, moving often means adding a Label (like TRASH or IMPORTANT)
            # or removing 'INBOX' to archive it.
            destination = action['value']
            add_labels.append(destination)
            remove_labels.append('INBOX')  # Archive it from Inbox
            print(f"   -> Action: Move to {destination}")

    if add_labels or remove_labels:
        body = {
            'addLabelIds': add_labels,
            'removeLabelIds': remove_labels
        }
        try:
            service.users().messages().modify(userId='me', id=message_id, body=body).execute()
            print("   -> Actions executed successfully on Gmail.")
        except Exception as e:
            print(f"   -> Failed to execute actions: {e}")


def process_emails():
    """Main Logic Loop."""
    # 1. Setup
    service = get_gmail_service()
    rules = load_rules()
    emails = get_all_emails()

    print(f"Processing {len(emails)} emails against {len(rules)} rules...")

    # 2. Loop through emails
    for email in emails:
        print(f"Checking Email: {email['subject'][:50]}...")

        # 3. Loop through rules
        for rule in rules:
            if evaluate_rule(email, rule):
                print(f"  [MATCH] Rule Matched: {rule['description']}")
                perform_actions(service, email['message_id'], rule['actions'])
                # Optional: Break after first match if you don't want multiple rules applying
                # break


if __name__ == "__main__":
    process_emails()