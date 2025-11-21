import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from db import save_emails_to_db

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def get_gmail_service():
    """Load creds and return service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        print("No token.json found. Run auth.py first.")
        return None

    return build('gmail', 'v1', credentials=creds)


def fetch_recent_emails(max_results=10):
    """Fetch a list of emails from the Inbox and print details."""
    service = get_gmail_service()
    if not service:
        return []

    print("Authentication valid. Fetching emails...")

    # Call the Gmail API to list messages
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No emails found in Inbox.')
        return []

    print(f"Found {len(messages)} emails. Retrieving details...\n")

    final_emails = []

    for msg in messages:
        # Get full message details (payload, snippet, headers)
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()

        payload = msg_detail.get('payload', {})
        headers = payload.get('headers', [])

        subject = "No Subject"
        sender = "Unknown Sender"
        date_received = "Unknown Date"

        # Extract specific headers we need for the rules
        for h in headers:
            if h['name'] == 'Subject':
                subject = h['value']
            if h['name'] == 'From':
                sender = h['value']
            if h['name'] == 'Date':
                date_received = h['value']

        print(f"--- Email ID: {msg['id']} ---")
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Date: {date_received}")
        print("-" * 30)

        final_emails.append({
            "message_id": msg['id'],
            "sender": sender,
            "subject": subject,
            "received_date": date_received,
            "snippet": msg_detail.get('snippet', '')
        })

    return final_emails


if __name__ == '__main__':
    # 1. Fetch the emails
    emails = fetch_recent_emails(max_results=15)

    # 2. Save them to DB
    if emails:
        save_emails_to_db(emails)