"""
Gmail Helper Module

Provides utilities for working with Gmail, including
email categorization, filtering, and smart replies.
"""

import os
import logging
import base64
import email
import re
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from utils.ai_helper import generate_ai_text, analyze_document_content

def get_gmail_service(user_connection):
    """
    Build and return a Gmail service object from user connection data

    Args:
        user_connection: User connection object with OAuth credentials

    Returns:
        Gmail service object or None
    """
    try:
        # Create credentials from stored tokens
        creds = Credentials(
            token=user_connection.token,
            refresh_token=user_connection.refresh_token,
            token_uri=user_connection.token_uri,
            client_id=user_connection.client_id,
            client_secret=user_connection.client_secret,
            scopes=user_connection.scopes.split(",") if user_connection.scopes else []
        )

        # Build the Gmail service
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building Gmail service: {str(e)}")
        return None

def search_gmail(gmail_service, query, max_results=20, include_content=False):
    """
    Search Gmail with a specific query

    Args:
        gmail_service: Authorized Gmail service
        query: Search query in Gmail format (e.g., 'from:example@example.com')
        max_results: Maximum number of results to return
        include_content: Whether to include email content

    Returns:
        List of matching emails
    """
    try:
        # Search for messages matching the query
        results = gmail_service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return []

        email_list = []

        # Get detailed info for each message
        for message in messages:
            message_id = message['id']

            if include_content:
                # Get the full message
                msg = gmail_service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='full'
                ).execute()

                # Extract headers
                headers = {}
                for header in msg['payload']['headers']:
                    headers[header['name'].lower()] = header['value']

                # Get the subject, from, to, and date
                subject = headers.get('subject', '(No Subject)')
                sender = headers.get('from', '')
                recipient = headers.get('to', '')
                date = headers.get('date', '')

                # Get the message body if available
                body = ''
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                    body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

                email_list.append({
                    'id': message_id,
                    'thread_id': msg['threadId'],
                    'subject': subject,
                    'from': sender,
                    'to': recipient,
                    'date': date,
                    'body': body,
                    'labels': msg['labelIds']
                })
            else:
                # Get just the metadata
                msg = gmail_service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'To', 'Date']
                ).execute()

                # Extract headers
                headers = {}
                for header in msg['payload']['headers']:
                    headers[header['name'].lower()] = header['value']

                # Get the subject, from, to, and date
                subject = headers.get('subject', '(No Subject)')
                sender = headers.get('from', '')
                recipient = headers.get('to', '')
                date = headers.get('date', '')

                email_list.append({
                    'id': message_id,
                    'thread_id': msg['threadId'],
                    'subject': subject,
                    'from': sender,
                    'to': recipient,
                    'date': date,
                    'labels': msg['labelIds']
                })

        return email_list

    except Exception as e:
        logging.error(f"Error searching Gmail: {str(e)}")
        return []

def get_gmail_threads(gmail_service, query="", max_results=10, include_content=True):
    """
    Get Gmail threads matching a query

    Args:
        gmail_service: Authorized Gmail service
        query: Search query in Gmail format
        max_results: Maximum number of threads to return
        include_content: Whether to include email content

    Returns:
        List of email threads
    """
    try:
        # Search for threads matching the query
        results = gmail_service.users().threads().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        threads = results.get('threads', [])

        if not threads:
            return []

        thread_list = []

        # Get detailed info for each thread
        for thread in threads:
            thread_id = thread['id']

            # Get the full thread
            thread_data = gmail_service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()

            messages = []

            for message in thread_data['messages']:
                # Extract headers
                headers = {}
                for header in message['payload']['headers']:
                    headers[header['name'].lower()] = header['value']

                # Get the subject, from, to, and date
                subject = headers.get('subject', '(No Subject)')
                sender = headers.get('from', '')
                recipient = headers.get('to', '')
                date = headers.get('date', '')

                # Get the message body if include_content is True
                body = ''
                if include_content:
                    if 'parts' in message['payload']:
                        for part in message['payload']['parts']:
                            if part['mimeType'] == 'text/plain':
                                if 'data' in part['body']:
                                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                break
                    elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                        body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

                messages.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': sender,
                    'to': recipient,
                    'date': date,
                    'body': body if include_content else '',
                    'labels': message.get('labelIds', [])
                })

            thread_list.append({
                'id': thread_id,
                'messages': messages,
                'message_count': len(messages)
            })

        return thread_list

    except Exception as e:
        logging.error(f"Error getting Gmail threads: {str(e)}")
        return []

def send_email(gmail_service, to, subject, body, cc=None, bcc=None):
    """
    Send an email

    Args:
        gmail_service: Authorized Gmail service
        to: Recipient email address or list of addresses
        subject: Email subject
        body: Email body content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)

    Returns:
        Status of the send operation
    """
    try:
        # Format recipient lists
        to_list = to if isinstance(to, list) else [to]
        cc_list = cc if cc and isinstance(cc, list) else [cc] if cc else []
        bcc_list = bcc if bcc and isinstance(bcc, list) else [bcc] if bcc else []

        # Create the email message
        message = email.message.EmailMessage()
        message['To'] = ', '.join(to_list)
        message['Subject'] = subject

        if cc_list:
            message['Cc'] = ', '.join(cc_list)

        if bcc_list:
            message['Bcc'] = ', '.join(bcc_list)

        message.set_content(body)

        # Encode as base64 URL-safe string
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        # Send the message
        sent_message = gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        return {
            'status': 'success',
            'message_id': sent_message['id'],
            'thread_id': sent_message.get('threadId', '')
        }

    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

def reply_to_email(gmail_service, message_id, body):
    """
    Reply to an existing email

    Args:
        gmail_service: Authorized Gmail service
        message_id: ID of the message to reply to
        body: Reply content

    Returns:
        Status of the reply operation
    """
    try:
        # Get the original message
        original_msg = gmail_service.users().messages().get(
            userId='me',
            id=message_id,
            format='metadata',
            metadataHeaders=['Subject', 'From', 'To', 'Message-ID', 'References', 'In-Reply-To']
        ).execute()

        # Extract headers
        headers = {}
        for header in original_msg['payload']['headers']:
            headers[header['name'].lower()] = header['value']

        # Get the thread ID
        thread_id = original_msg['threadId']

        # Extract email addresses
        from_address = headers.get('from', '')
        to_address = headers.get('to', '')
        subject = headers.get('subject', '')

        # Parse the 'From' header to get the email address
        from_match = re.search(r'<([^>]+)>', from_address)
        if from_match:
            reply_to = from_match.group(1)
        else:
            reply_to = from_address

        # Add 'Re:' to subject if it's not already there
        if not subject.lower().startswith('re:'):
            subject = f"Re: {subject}"

        # Create the reply message
        message = email.message.EmailMessage()
        message['To'] = reply_to
        message['Subject'] = subject
        message['In-Reply-To'] = headers.get('message-id', '')
        message['References'] = headers.get('references', '') + ' ' + headers.get('message-id', '')
        message.set_content(body)

        # Encode as base64 URL-safe string
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        # Send the reply
        sent_message = gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw_message, 'threadId': thread_id}
        ).execute()

        return {
            'status': 'success',
            'message_id': sent_message['id'],
            'thread_id': sent_message.get('threadId', '')
        }

    except Exception as e:
        logging.error(f"Error replying to email: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

# === AI-Powered Email Features ===

def categorize_emails(gmail_service, emails):
    """
    Categorize a list of emails into recovery-relevant categories

    Args:
        gmail_service: Authorized Gmail service
        emails: List of email objects with subject and body

    Returns:
        Categorized email list
    """
    try:
        categorized_emails = []

        for email_obj in emails:
            email_text = f"Subject: {email_obj.get('subject', '')}\n\nBody: {email_obj.get('body', '')}"

            # Skip email if it's too short
            if len(email_text) < 10:
                email_obj['category'] = 'uncategorized'
                email_obj['recovery_relevance'] = 'unknown'
                categorized_emails.append(email_obj)
                continue

            # Use AI to categorize
            prompt = f"""Categorize this email into one of the following categories:
1. Support Network (emails from sponsors, recovery groups, etc.)
2. Healthcare (medical/therapy appointments, medication)
3. Recovery Resources (recovery-related information, newsletters)
4. Social (social events, invitations)
5. Work/Professional
6. Shopping/Commerce
7. Personal
8. Other

Also rate its relevance to recovery on a scale from 0-10.

Email: {email_text}

Format response as:
Category: [category]
Recovery Relevance: [0-10]
"""

            response = generate_ai_text(prompt, max_tokens=100)

            # Parse response
            category = "Other"
            relevance = "unknown"

            category_match = re.search(r'Category:\s*(.+)', response)
            if category_match:
                category = category_match.group(1).strip()

            relevance_match = re.search(r'Recovery Relevance:\s*(\d+)', response)
            if relevance_match:
                relevance = int(relevance_match.group(1))

            email_obj['category'] = category
            email_obj['recovery_relevance'] = relevance

            categorized_emails.append(email_obj)

        return categorized_emails

    except Exception as e:
        logging.error(f"Error categorizing emails: {str(e)}")
        for email_obj in emails:
            email_obj['category'] = 'error'
            email_obj['recovery_relevance'] = 'error'
        return emails

def generate_email_reply(gmail_service, email_id, user_context=None):
    """
    Generate an AI-powered reply to an email

    Args:
        gmail_service: Authorized Gmail service
        email_id: ID of the email to reply to
        user_context: Optional user context for personalization

    Returns:
        Generated reply content
    """
    try:
        # Get the email content
        msg = gmail_service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()

        # Extract headers
        headers = {}
        for header in msg['payload']['headers']:
            headers[header['name'].lower()] = header['value']

        # Get the subject and from
        subject = headers.get('subject', '(No Subject)')
        sender = headers.get('from', '')

        # Get the message body
        body = ''
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

        # Create context for the AI
        context = ""
        if user_context:
            context = f"User context: {user_context}\n\n"

        # Generate reply with AI
        prompt = f"""{context}Generate a thoughtful reply to this email. Keep the tone friendly but professional.

From: {sender}
Subject: {subject}
Email content:
{body}

Reply:"""

        reply_content = generate_ai_text(prompt)

        return {
            'status': 'success',
            'email_id': email_id,
            'reply_content': reply_content
        }

    except Exception as e:
        logging.error(f"Error generating email reply: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

def filter_recovery_emails(gmail_service, days=7):
    """
    Filter emails relevant to recovery from the last N days

    Args:
        gmail_service: Authorized Gmail service
        days: Number of days to look back

    Returns:
        List of recovery-relevant emails
    """
    try:
        # Calculate date N days ago
        date_n_days_ago = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')

        # Search for recent emails
        query = f"after:{date_n_days_ago}"
        emails = search_gmail(gmail_service, query, max_results=50, include_content=True)

        # Skip processing if no emails found
        if not emails:
            return []

        # Categorize emails
        categorized_emails = categorize_emails(gmail_service, emails)

        # Filter for recovery relevance
        recovery_emails = []
        for email in categorized_emails:
            relevance = email.get('recovery_relevance', 0)

            # Include emails with relevance score >= 5
            if isinstance(relevance, int) and relevance >= 5:
                recovery_emails.append(email)
            # Also include emails in recovery-specific categories regardless of score
            elif email.get('category') in ['Support Network', 'Healthcare', 'Recovery Resources']:
                recovery_emails.append(email)

        return recovery_emails

    except Exception as e:
        logging.error(f"Error filtering recovery emails: {str(e)}")
        return []

def create_recovery_focused_digest(gmail_service, days=7):
    """
    Create a digest of recovery-focused emails for a given period

    Args:
        gmail_service: Authorized Gmail service
        days: Number of days to include in digest

    Returns:
        Email digest content
    """
    try:
        # Get recovery-relevant emails
        recovery_emails = filter_recovery_emails(gmail_service, days)

        if not recovery_emails:
            return {
                'status': 'info',
                'message': f'No recovery-related emails found in the last {days} days',
                'digest': 'No recovery-related emails to summarize.'
            }

        # Group emails by category
        categories = {}
        for email in recovery_emails:
            category = email.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(email)

        # Create digest content
        digest_content = f"# Recovery Email Digest - Last {days} Days\n\n"

        # Add each category section
        for category, emails in categories.items():
            digest_content += f"## {category} ({len(emails)} emails)\n\n"

            for email in emails:
                sender = email.get('from', 'Unknown Sender')
                subject = email.get('subject', '(No Subject)')
                date = email.get('date', '')
                relevance = email.get('recovery_relevance', '-')

                digest_content += f"- **{subject}** from {sender}\n"
                digest_content += f"  - Date: {date}\n"
                digest_content += f"  - Recovery Relevance: {relevance}/10\n"

        # Add a summary section generated by AI
        email_summaries = []
        for email in recovery_emails:
            summary = f"Subject: {email.get('subject', '')}\n"
            summary += f"From: {email.get('from', '')}\n"
            summary += f"Category: {email.get('category', '')}\n"
            email_summaries.append(summary)

        all_summaries = "\n\n".join(email_summaries)

        prompt = f"""Summarize the key points from these recovery-related emails:

{all_summaries}

Provide 3-5 bullet points highlighting the most important information for someone in recovery."""

        summary = generate_ai_text(prompt)

        digest_content += "\n## Summary\n\n"
        digest_content += summary

        return {
            'status': 'success',
            'email_count': len(recovery_emails),
            'categories': list(categories.keys()),
            'digest': digest_content
        }

    except Exception as e:
        logging.error(f"Error creating recovery email digest: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

def create_support_network_templates(gmail_service):
    """
    Create email templates for communicating with recovery support network

    Args:
        gmail_service: Authorized Gmail service (not used but included for consistency)

    Returns:
        Dictionary of email templates
    """
    try:
        templates = {}

        # Template for reaching out to sponsor
        templates['sponsor_check_in'] = """Subject: Weekly Recovery Check-in

Dear [Sponsor Name],

I hope this email finds you well. I'm sending my weekly check-in to share my progress in recovery.

My recovery status this week:
- Current challenges: [Describe challenges]
- Recent victories: [Describe victories]
- Questions I have: [List questions]
- Goals for the coming week: [List goals]

I [would/would not] like to schedule a call this week to discuss these items further.

Thank you for your continued support.

Sincerely,
[Your Name]"""

        # Template for apologizing/making amends
        templates['making_amends'] = """Subject: Making Amends - A Sincere Apology

Dear [Name],

I hope this message finds you well. As part of my recovery journey, I'm taking steps to make amends with people I may have harmed in the past.

I want to sincerely apologize for [specific behavior or incident]. I understand now that my actions caused you pain and difficulty, and I deeply regret this. My intention is not to disrupt your life or to ask for anything in return, but simply to acknowledge the harm I caused and express my genuine remorse.

I have been working on myself and am committed to behaving differently going forward by [specific changes you've made].

If you would be open to discussing this further, I would welcome the opportunity, but I also completely understand if you prefer not to respond.

Regardless of your response, I wish you well.

Sincerely,
[Your Name]"""

        # Template for requesting time off for recovery activities
        templates['recovery_time_request'] = """Subject: Request for Time Off - Recovery Appointment

Dear [Manager's Name],

I'm writing to request time off on [date] from [start time] to [end time] for a personal healthcare appointment related to my ongoing wellness plan.

I have arranged for [coverage plan if applicable] during my absence, and I will complete [any pending work] before/after my appointment.

Please let me know if you need any additional information. I appreciate your understanding and support.

Thank you,
[Your Name]"""

        # Template for declining event with alcohol
        templates['decline_event'] = """Subject: Regarding [Event Name]

Dear [Name],

Thank you for the invitation to [event]. I appreciate you thinking of me.

Unfortunately, I won't be able to attend this particular event. I'm currently focused on some personal health priorities that require me to be selective about my social commitments.

I would love to connect with you in another setting soon. Perhaps we could [alternative suggestion] instead?

Thank you for your understanding.

Best regards,
[Your Name]"""

        # Template for requesting recovery support
        templates['request_support'] = """Subject: Request for Support

Dear [Name],

I hope you're doing well. I'm reaching out because I'm going through a challenging time in my recovery journey and could use some support.

Specifically, I'm struggling with [brief description of challenge] and would appreciate [specific type of support - call, meeting, advice, etc.].

Please let me know if you would be available for this. If not, I completely understand as I know everyone has their own responsibilities and challenges.

Thank you for being part of my support network.

Warmly,
[Your Name]"""

        return {
            'status': 'success',
            'templates': templates
        }

    except Exception as e:
        logging.error(f"Error creating support network templates: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

def check_email_for_triggers(gmail_service, email_id):
    """
    Check an email for potentially triggering content

    Args:
        gmail_service: Authorized Gmail service
        email_id: ID of the email to check

    Returns:
        Analysis of potential triggers
    """
    try:
        # Get the email content
        msg = gmail_service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()

        # Extract headers
        headers = {}
        for header in msg['payload']['headers']:
            headers[header['name'].lower()] = header['value']

        # Get the subject and body
        subject = headers.get('subject', '(No Subject)')

        # Get the message body
        body = ''
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

        # Combine subject and body for analysis
        email_text = f"Subject: {subject}\n\nBody: {body}"

        # Use AI to analyze for triggers
        prompt = """Analyze this email for content that might be triggering for someone in recovery from addiction.
Consider mentions of substance use, traumatic events, negative social dynamics, or stressful situations.
Provide a trigger assessment that includes:
1. Overall trigger level (0-10 scale)
2. Specific trigger topics identified
3. Brief recommendation for how to approach this email

Email content:
""" + email_text

        analysis = generate_ai_text(prompt)

        # Parse the trigger level if possible
        trigger_level = 0
        match = re.search(r'trigger level.*?(\d+)', analysis, re.IGNORECASE)
        if match:
            try:
                trigger_level = int(match.group(1))
            except:
                trigger_level = 0

        return {
            'status': 'success',
            'email_id': email_id,
            'trigger_analysis': analysis,
            'trigger_level': trigger_level
        }

    except Exception as e:
        logging.error(f"Error checking email for triggers: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }