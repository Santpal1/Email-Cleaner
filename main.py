import os
import re
from collections import Counter
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest

SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://mail.google.com/']


def authenticate_and_build_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def extract_email(sender):
    match = re.search(r'<(.+?)>', sender)
    return match.group(1) if match else sender.strip()


def get_top_senders(service, max_messages=3000, top_n=10, progress_callback=None):
    sender_counts = Counter()
    message_ids = []

    # Step 1: Fetch message IDs from inbox
    next_page_token = None
    fetched = 0
    while fetched < max_messages:
        response = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=500,
            pageToken=next_page_token
        ).execute()

        messages = response.get('messages', [])
        message_ids.extend([msg['id'] for msg in messages])
        fetched += len(messages)

        next_page_token = response.get('nextPageToken')
        if not next_page_token or len(messages) == 0:
            break

    # Step 2: Batch fetch metadata (headers)
    def callback(request_id, response, exception):
        if exception is None:
            headers = response['payload'].get('headers', [])
            sender = next((h['value'] for h in headers if h['name'] == 'From'), None)
            if sender:
                sender_counts[sender] += 1

    total_batches = (len(message_ids) // 100) + 1
    for i in range(0, len(message_ids), 100):
        if progress_callback:
            progress_callback(i // 100 + 1, total_batches)

        batch = BatchHttpRequest(
            callback=callback,
            batch_uri='https://gmail.googleapis.com/batch/gmail/v1'  # ✅ Fixed endpoint
        )
        for msg_id in message_ids[i:i + 100]:
            batch.add(service.users().messages().get(
                userId='me',
                id=msg_id,
                format='metadata',
                metadataHeaders=['From']
            ))
        batch.execute()

    return sender_counts.most_common(top_n)



from datetime import datetime
import re

def delete_from_sender(service, sender, log_func=print, progress_callback=None,
                       keyword=None, older_than_days=None, after_date=None, before_date=None):
    email_only = extract_email(sender)
    
    # Build Gmail search query
    query_parts = [f'from:{email_only}']

    if keyword:
        keyword = keyword.strip()
        # Search in subject OR body (basic coverage using OR)
        query_parts.append(f'(subject:{keyword} OR {keyword})')

    if older_than_days:
        query_parts.append(f'older_than:{older_than_days}d')

    if after_date:
        # Gmail expects YYYY/MM/DD
        query_parts.append(f'after:{after_date}')

    if before_date:
        query_parts.append(f'before:{before_date}')

    query = ' '.join(query_parts)
    log_func(f"🔎 Using query: {query}")

    response = service.users().messages().list(userId='me', q=query).execute()
    messages = response.get('messages', [])

    if not messages:
        log_func(f"No messages found for query from {email_only}")
        return

    count = 0
    total = len(messages)
    for i, msg in enumerate(messages):
        try:
            service.users().messages().delete(userId='me', id=msg['id']).execute()
            count += 1
        except Exception as e:
            log_func(f"❌ Failed to delete message {msg['id']}: {e}")

        if progress_callback:
            progress_callback(i + 1, total)

    log_func(f"✅ Deleted {count} messages from {email_only}")


# CLI entry point (optional)
if __name__ == '__main__':
    service = authenticate_and_build_service()

    print("🔍 Scanning inbox for top senders (this is fast now)...")
    top_senders = get_top_senders(service)

    print("\n📧 Top 10 Senders:")
    for i, (sender, count) in enumerate(top_senders, 1):
        print(f"{i}. {sender} — {count} messages")

    print("\nChoose which senders to delete manually.")
    for sender, count in top_senders:
        choice = input(f"Delete {count} messages from '{sender}'? (y/n): ").strip().lower()
        if choice == 'y':
            delete_from_sender(service, sender)
        else:
            print(f"❌ Skipped {sender}")
