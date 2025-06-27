"""
Helper module for Google Docs and Sheets integration
"""
import os
import logging
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json
import re
from utils.ai_helper import generate_ai_text, analyze_document_content

def get_docs_service(user_connection):
    """Build and return a Google Docs service object from user connection data"""
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

        # Build the Docs service
        service = build('docs', 'v1', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building Docs service: {str(e)}")
        return None

def get_sheets_service(user_connection):
    """Build and return a Google Sheets service object from user connection data"""
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

        # Build the Sheets service
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building Sheets service: {str(e)}")
        return None

def get_drive_service(user_connection):
    """Build and return a Google Drive service object from user connection data"""
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

        # Build the Drive service
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building Drive service: {str(e)}")
        return None

# === Document Creation and Management ===

def create_document(docs_service, title, content=None):
    """
    Create a new Google Doc

    Args:
        docs_service: Authorized Google Docs service
        title: Document title
        content: Initial content (optional)

    Returns:
        Document ID and URL
    """
    try:
        # Create empty document
        body = {
            'title': title
        }
        doc = docs_service.documents().create(body=body).execute()
        document_id = doc.get('documentId')

        # Add content if provided
        if content:
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': content
                    }
                }
            ]

            docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}).execute()

        return {
            'document_id': document_id,
            'url': f"https://docs.google.com/document/d/{document_id}/edit"
        }

    except Exception as e:
        logging.error(f"Error creating document: {str(e)}")
        return {'error': str(e)}

def get_document_content(docs_service, document_id):
    """
    Get the content of a Google Doc

    Args:
        docs_service: Authorized Google Docs service
        document_id: Document ID

    Returns:
        Document content as text
    """
    try:
        document = docs_service.documents().get(documentId=document_id).execute()

        # Extract text content
        content = ""
        for content_item in document.get('body').get('content'):
            if 'paragraph' in content_item:
                for element in content_item.get('paragraph').get('elements'):
                    if 'textRun' in element:
                        content += element.get('textRun').get('content')

        return content

    except Exception as e:
        logging.error(f"Error getting document content: {str(e)}")
        return {'error': str(e)}

# === AI-Powered Document Features ===

def ai_edit_document(docs_service, document_id, editing_request):
    """
    Use AI to edit a document based on natural language instructions

    Args:
        docs_service: Authorized Google Docs service
        document_id: Document ID
        editing_request: Natural language editing request

    Returns:
        Status of the edit operation
    """
    try:
        # Get current document content
        document = docs_service.documents().get(documentId=document_id).execute()

        # Extract text content
        current_content = ""
        for content_item in document.get('body').get('content'):
            if 'paragraph' in content_item:
                for element in content_item.get('paragraph').get('elements'):
                    if 'textRun' in element:
                        current_content += element.get('textRun').get('content')

        # Generate edited content using AI
        prompt = f"Original text:\n{current_content}\n\nEditing request: {editing_request}\n\nEdited text:"
        edited_content = generate_ai_text(prompt)

        # Replace entire document content
        # First, delete all content
        end_index = len(current_content)
        requests = [
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': end_index + 1
                    }
                }
            },
            # Then insert new content
            {
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': edited_content
                }
            }
        ]

        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}).execute()

        return {
            'status': 'success',
            'message': 'Document edited successfully'
        }

    except Exception as e:
        logging.error(f"Error editing document: {str(e)}")
        return {'error': str(e)}

def generate_smart_content_suggestions(docs_service, document_id):
    """
    Generate smart content suggestions for a document

    Args:
        docs_service: Authorized Google Docs service
        document_id: Document ID

    Returns:
        List of content suggestions
    """
    try:
        # Get current document content
        content = get_document_content(docs_service, document_id)
        if isinstance(content, dict) and 'error' in content:
            return content

        # Analyze content with AI
        prompt = f"The following is content from a document. Please provide 3-5 suggestions to improve this content or expand on it:\n\n{content}"
        suggestions = generate_ai_text(prompt)

        # Format and return suggestions
        return {
            'document_id': document_id,
            'suggestions': suggestions.split('\n')
        }

    except Exception as e:
        logging.error(f"Error generating content suggestions: {str(e)}")
        return {'error': str(e)}

def summarize_document(docs_service, document_id):
    """
    Automatically summarize a document

    Args:
        docs_service: Authorized Google Docs service
        document_id: Document ID

    Returns:
        Document summary
    """
    try:
        # Get document content
        content = get_document_content(docs_service, document_id)
        if isinstance(content, dict) and 'error' in content:
            return content

        # Generate summary using AI
        prompt = f"Please summarize the following document in a concise way that captures the main points:\n\n{content}"
        summary = generate_ai_text(prompt)

        return {
            'document_id': document_id,
            'summary': summary
        }

    except Exception as e:
        logging.error(f"Error summarizing document: {str(e)}")
        return {'error': str(e)}

def analyze_document_sentiment(docs_service, document_id):
    """
    Analyze the sentiment and emotional content of a document

    Args:
        docs_service: Authorized Google Docs service
        document_id: Document ID

    Returns:
        Sentiment analysis results
    """
    try:
        # Get document content
        content = get_document_content(docs_service, document_id)
        if isinstance(content, dict) and 'error' in content:
            return content

        # Analyze sentiment using AI
        analysis = analyze_document_content(content, analysis_type="sentiment")

        return {
            'document_id': document_id,
            'sentiment_analysis': analysis
        }

    except Exception as e:
        logging.error(f"Error analyzing document sentiment: {str(e)}")
        return {'error': str(e)}

# === Recovery-Focused Document Templates ===

def create_recovery_journal_document(docs_service, user_info=None):
    """
    Create a recovery journal document with structured templates

    Args:
        docs_service: Authorized Google Docs service
        user_info: Optional user information for personalization

    Returns:
        Document ID and URL
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        title = f"Recovery Journal - {today}"

        # Create structured journal template
        template = f"""# Recovery Journal - {today}

## Morning Reflection
- How am I feeling today (1-10):
- Physical sensations:
- Emotional state:
- Things I'm grateful for:
  1.
  2.
  3.
- Intentions for today:
  -
  -
  -

## Evening Reflection
- Overall mood today (1-10):
- Challenges faced:
- Victories (big or small):
- Skills I used today:
  -
  -
- What I learned:
- Plan for tomorrow:

## Recovery Progress
- Days in recovery:
- Recent insights:
- Patterns I've noticed:
- Areas for growth:

Remember: Progress, not perfection.
"""

        # Create the document
        document = create_document(docs_service, title, template)

        return document

    except Exception as e:
        logging.error(f"Error creating recovery journal: {str(e)}")
        return {'error': str(e)}

def create_therapy_worksheet(docs_service, worksheet_type, user_info=None):
    """
    Create a therapy worksheet based on the specified type

    Args:
        docs_service: Authorized Google Docs service
        worksheet_type: Type of therapy worksheet (e.g., "dbt_diary_card", "chain_analysis", "thought_record")
        user_info: Optional user information for personalization

    Returns:
        Document ID and URL
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        # Select template based on worksheet type
        if worksheet_type == "dbt_diary_card":
            title = f"DBT Diary Card - {today}"
            template = """# DBT Diary Card

## Daily Tracking
Date:

### Emotions (Rate 0-5)
- Sadness:
- Fear/Anxiety:
- Anger:
- Shame/Guilt:
- Joy:
- Peace:

### Urges/Behaviors (Rate 0-5)
- Self-harm:
- Suicidal thoughts:
- Substance use:
- Therapy-interfering behaviors:
- Other target behaviors:

## Skills Used Today
- Mindfulness:
- Distress Tolerance:
- Emotion Regulation:
- Interpersonal Effectiveness:

## Reflection
- What situations were most challenging today?

- What skills worked best?

- What skills will I try tomorrow?

"""
        elif worksheet_type == "chain_analysis":
            title = f"DBT Chain Analysis - {today}"
            template = """# DBT Chain Analysis Worksheet

## Target Behavior to Analyze
Describe the behavior you want to understand:


## Vulnerability Factors
What factors made me more vulnerable?
- Physical (sleep, illness, etc.):
- Emotional:
- Cognitive:
- Environmental:

## Prompting Event
What triggered the chain of events?


## Chain of Events
What happened next? (include thoughts, feelings, actions)
1.
2.
3.
4.
5.

## Consequences
What were the short-term consequences?


What were the long-term consequences?


## Alternative Behaviors
What skills could I use next time?
1.
2.
3.

## Prevention Plan
How can I prevent vulnerability factors?


What specific skills will I practice?

"""
        elif worksheet_type == "thought_record":
            title = f"CBT Thought Record - {today}"
            template = """# Cognitive Behavioral Therapy Thought Record

## Situation
What happened? When? Where? Who with?


## Emotions
What emotions did you feel? (Rate intensity 0-100%)


## Automatic Thoughts
What went through your mind? What disturbed you? What did these thoughts mean about you or the situation?


## Evidence That Supports The Thought
Facts that support this thought being true:


## Evidence That Does Not Support The Thought
Facts that suggest this thought might not be completely true:


## Alternative/Balanced Perspective
More balanced view of the situation:


## Emotion After Reappraisal
How do you feel now? (Rate intensity 0-100%)

"""
        else:
            title = f"Therapy Worksheet - {today}"
            template = """# Therapy Worksheet

## Current Situation
Describe what's happening right now:


## Thoughts and Feelings
What are you thinking:

What are you feeling:


## Actions and Behaviors
What actions did this lead to:


## Alternative Approaches
What else could you try:


## Next Steps
What will you do next time:

"""

        # Create the document
        document = create_document(docs_service, title, template)

        return document

    except Exception as e:
        logging.error(f"Error creating therapy worksheet: {str(e)}")
        return {'error': str(e)}

def create_progress_tracking_document(docs_service, user_info=None):
    """
    Create a recovery progress tracking document

    Args:
        docs_service: Authorized Google Docs service
        user_info: Optional user information for personalization

    Returns:
        Document ID and URL
    """
    try:
        title = "Recovery Progress Tracker"

        template = """# Recovery Progress Tracker

## Recovery Milestones
| Date | Days | Milestone | Notes |
|------|------|-----------|-------|
|      |      |           |       |
|      |      |           |       |
|      |      |           |       |

## Monthly Progress Review
### Month:

#### Achievements:
-
-
-

#### Challenges:
-
-
-

#### Skills Developed:
-
-
-

#### Goals for Next Month:
-
-
-

## Recovery Insights

### Patterns I've Noticed:

### Effective Coping Strategies:

### Areas for Growth:

### Support System:

## Long-Term Goals
1.
2.
3.

Remember: Recovery is not linear. Every step counts, even the difficult ones.
"""

        # Create the document
        document = create_document(docs_service, title, template)

        return document

    except Exception as e:
        logging.error(f"Error creating progress tracking document: {str(e)}")
        return {'error': str(e)}

def create_meeting_notes_template(docs_service, meeting_type="support_group"):
    """
    Create a meeting notes template with intelligent fields

    Args:
        docs_service: Authorized Google Docs service
        meeting_type: Type of meeting (support_group, therapy, sponsor)

    Returns:
        Document ID and URL
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        if meeting_type == "support_group":
            title = f"Support Group Meeting Notes - {today}"
            template = """# Support Group Meeting Notes

## Meeting Details
- Date:
- Location:
- Type of Meeting:
- Number of Attendees:

## Topics Discussed
1.
2.
3.

## Key Insights
-

## Personal Reflections
- How I felt during the meeting:
- What resonated with me:
- What challenged me:

## Action Items
- [ ]
- [ ]
- [ ]

## Follow-up for Next Meeting
-

Remember: What is shared in the meeting, stays in the meeting.
"""
        elif meeting_type == "therapy":
            title = f"Therapy Session Notes - {today}"
            template = """# Therapy Session Notes

## Session Details
- Date:
- Therapist:
- Session #:

## Topics Discussed
1.
2.
3.

## Insights and Realizations
-

## Skills Practiced
-

## Homework Assigned
- [ ]
- [ ]

## Questions for Next Session
-

## Goals for Coming Week
1.
2.
3.

Notes to self:

"""
        elif meeting_type == "sponsor":
            title = f"Sponsor Meeting Notes - {today}"
            template = """# Sponsor Meeting Notes

## Meeting Details
- Date:
- Duration:

## Recovery Check-in
- Days in recovery:
- Current challenges:
- Recent victories:

## Step Work Discussed
- Current step:
- Progress:
- Insights:

## Action Items
- [ ]
- [ ]
- [ ]

## Topics for Next Meeting
-

## Personal Reflections
-

"""
        else:
            title = f"Meeting Notes - {today}"
            template = """# Meeting Notes

## Meeting Details
- Date:
- Attendees:
- Purpose:

## Agenda
1.
2.
3.

## Discussion Points
-

## Decisions Made
-

## Action Items
- [ ]
- [ ]

## Next Meeting
- Date:
- Topics:

"""

        # Create the document
        document = create_document(docs_service, title, template)

        return document

    except Exception as e:
        logging.error(f"Error creating meeting notes template: {str(e)}")
        return {'error': str(e)}

# === Sheets Specific Functions ===

def create_spreadsheet(sheets_service, title, sheets=None):
    """
    Create a new Google Sheet

    Args:
        sheets_service: Authorized Google Sheets service
        title: Spreadsheet title
        sheets: List of sheet names to create (optional)

    Returns:
        Spreadsheet ID and URL
    """
    try:
        spreadsheet = {
            'properties': {
                'title': title
            }
        }

        # Add specific sheets if provided
        if sheets:
            spreadsheet['sheets'] = [{'properties': {'title': sheet}} for sheet in sheets]

        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')

        return {
            'spreadsheet_id': spreadsheet_id,
            'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
        }

    except Exception as e:
        logging.error(f"Error creating spreadsheet: {str(e)}")
        return {'error': str(e)}

def update_sheet_values(sheets_service, spreadsheet_id, range_name, values):
    """
    Update values in a spreadsheet

    Args:
        sheets_service: Authorized Google Sheets service
        spreadsheet_id: Spreadsheet ID
        range_name: Range to update (e.g., 'Sheet1!A1:B5')
        values: 2D array of values to update

    Returns:
        Update result
    """
    try:
        body = {
            'values': values
        }
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body).execute()

        return result

    except Exception as e:
        logging.error(f"Error updating sheet values: {str(e)}")
        return {'error': str(e)}

def create_medication_tracker_spreadsheet(sheets_service):
    """
    Create a medication tracking spreadsheet

    Args:
        sheets_service: Authorized Google Sheets service

    Returns:
        Spreadsheet ID and URL
    """
    try:
        title = "Medication Tracker"
        sheets = ["Daily Tracking", "Medication List", "Side Effects", "Notes"]

        # Create the spreadsheet with sheets
        spreadsheet = create_spreadsheet(sheets_service, title, sheets)

        if 'error' in spreadsheet:
            return spreadsheet

        spreadsheet_id = spreadsheet['spreadsheet_id']

        # Set up Medication List sheet
        medication_headers = [
            ["Medication Name", "Dosage", "Frequency", "With Food?", "Start Date", "End Date", "Prescriber", "Pharmacy", "Notes"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Medication List!A1:I1", medication_headers)

        # Set up Daily Tracking sheet - headers with dates
        today = datetime.now()
        date_headers = [["Medication"]]
        dates_row = []

        # Generate 31 days of dates
        for i in range(31):
            date = today.replace(day=1) + datetime.timedelta(days=i)
            if date.month == today.month:
                dates_row.append(date.strftime("%m/%d"))

        date_headers.append([""] + dates_row)
        update_sheet_values(sheets_service, spreadsheet_id, "Daily Tracking!A1:AJ2", date_headers)

        # Set up Side Effects sheet
        side_effect_headers = [
            ["Date", "Medication", "Side Effect", "Severity (1-10)", "Duration", "Actions Taken", "Reported to Doctor?"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Side Effects!A1:G1", side_effect_headers)

        return spreadsheet

    except Exception as e:
        logging.error(f"Error creating medication tracker: {str(e)}")
        return {'error': str(e)}

def create_recovery_metrics_dashboard(sheets_service, recovery_type="aa"):
    """
    Create a recovery metrics dashboard spreadsheet

    Args:
        sheets_service: Authorized Google Sheets service
        recovery_type: Type of recovery program (aa, dbt, etc.)

    Returns:
        Spreadsheet ID and URL
    """
    try:
        title = "Recovery Metrics Dashboard"
        sheets = ["Dashboard", "Daily Tracking", "Triggers", "Coping Skills", "Support Network"]

        # Create the spreadsheet with sheets
        spreadsheet = create_spreadsheet(sheets_service, title, sheets)

        if 'error' in spreadsheet:
            return spreadsheet

        spreadsheet_id = spreadsheet['spreadsheet_id']

        # Set up Dashboard sheet
        dashboard_headers = [
            ["Recovery Metrics Dashboard"],
            [""],
            ["Days in Recovery:", "=COUNTA(Daily Tracking!A:A)-1"],
            ["Average Daily Rating:", "=AVERAGE(Daily Tracking!C:C)"],
            ["Triggers This Month:", "=COUNTA(Triggers!A:A)-1"],
            ["Coping Skills Used:", "=COUNTA(Coping Skills!A:A)-1"],
            ["Most Effective Skill:", "=INDEX(Coping Skills!A:A, MATCH(MAX(Coping Skills!C:C), Coping Skills!C:C, 0))"],
            ["Support Network Size:", "=COUNTA(Support Network!A:A)-1"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Dashboard!A1:B8", dashboard_headers)

        # Set up Daily Tracking sheet
        daily_headers = [
            ["Date", "Check-in Complete", "Overall Rating (1-10)", "Morning Mood", "Evening Mood", "Challenges", "Victories", "Notes"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Daily Tracking!A1:H1", daily_headers)

        # Set up Triggers sheet
        trigger_headers = [
            ["Date", "Trigger", "Intensity (1-10)", "Environment", "People Present", "Thoughts", "Emotions", "Response", "Coping Skill Used", "Effectiveness (1-10)"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Triggers!A1:J1", trigger_headers)

        # Set up Coping Skills sheet
        coping_headers = [
            ["Skill Name", "Category", "Average Effectiveness", "Times Used", "Notes"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Coping Skills!A1:E1", coping_headers)

        # Set up Support Network sheet
        support_headers = [
            ["Name", "Relationship", "Contact Info", "Role in Recovery", "Last Contact", "Notes"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Support Network!A1:F1", support_headers)

        return spreadsheet

    except Exception as e:
        logging.error(f"Error creating recovery metrics dashboard: {str(e)}")
        return {'error': str(e)}

def create_budget_spreadsheet(sheets_service):
    """
    Create a budget management spreadsheet

    Args:
        sheets_service: Authorized Google Sheets service

    Returns:
        Spreadsheet ID and URL
    """
    try:
        title = "Recovery Budget Management"
        sheets = ["Monthly Budget", "Expenses", "Income", "Recovery Expenses", "Summary"]

        # Create the spreadsheet with sheets
        spreadsheet = create_spreadsheet(sheets_service, title, sheets)

        if 'error' in spreadsheet:
            return spreadsheet

        spreadsheet_id = spreadsheet['spreadsheet_id']

        # Set up Monthly Budget sheet
        budget_headers = [
            ["Monthly Budget"],
            [""],
            ["Category", "Budgeted Amount", "Actual Amount", "Difference", "Notes"],
            ["Housing", "", "=SUMIF(Expenses!B:B,\"Housing\",Expenses!C:C)", "=C5-B5", ""],
            ["Utilities", "", "=SUMIF(Expenses!B:B,\"Utilities\",Expenses!C:C)", "=C6-B6", ""],
            ["Food", "", "=SUMIF(Expenses!B:B,\"Food\",Expenses!C:C)", "=C7-B7", ""],
            ["Transportation", "", "=SUMIF(Expenses!B:B,\"Transportation\",Expenses!C:C)", "=C8-B8", ""],
            ["Healthcare", "", "=SUMIF(Expenses!B:B,\"Healthcare\",Expenses!C:C)", "=C9-B9", ""],
            ["Recovery", "", "=SUMIF(Expenses!B:B,\"Recovery\",Expenses!C:C)", "=C10-B10", ""],
            ["Entertainment", "", "=SUMIF(Expenses!B:B,\"Entertainment\",Expenses!C:C)", "=C11-B11", ""],
            ["Other", "", "=SUMIF(Expenses!B:B,\"Other\",Expenses!C:C)", "=C12-B12", ""],
            ["TOTAL", "=SUM(B5:B12)", "=SUM(C5:C12)", "=C13-B13", ""]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Monthly Budget!A1:E13", budget_headers)

        # Set up Expenses sheet
        expenses_headers = [
            ["Date", "Category", "Amount", "Description", "Recovery-Related?", "Necessary?", "Notes"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Expenses!A1:G1", expenses_headers)

        # Set up Income sheet
        income_headers = [
            ["Date", "Source", "Amount", "Recurring?", "Notes"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Income!A1:E1", income_headers)

        # Set up Recovery Expenses sheet
        recovery_headers = [
            ["Date", "Category", "Amount", "Description", "Priority (1-5)", "Notes"],
            ["", "Therapy", "", "", "", ""],
            ["", "Medication", "", "", "", ""],
            ["", "Support Groups", "", "", "", ""],
            ["", "Recovery Literature", "", "", "", ""],
            ["", "Self-Care", "", "", "", ""],
            ["", "Recovery Activities", "", "", "", ""],
            ["", "Other", "", "", "", ""]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Recovery Expenses!A1:F8", recovery_headers)

        # Set up Summary sheet
        summary_headers = [
            ["Financial Summary"],
            [""],
            ["Total Income:", "=SUM(Income!C:C)"],
            ["Total Expenses:", "=SUM(Expenses!C:C)"],
            ["Net Balance:", "=C3-C4"],
            ["Recovery Expenses:", "=SUMIF(Expenses!E:E,\"Yes\",Expenses!C:C)"],
            ["Recovery % of Total:", "=C6/C4"],
            [""],
            ["Notes for Improvement:"]
        ]
        update_sheet_values(sheets_service, spreadsheet_id, "Summary!A1:C9", summary_headers)

        return spreadsheet

    except Exception as e:
        logging.error(f"Error creating budget spreadsheet: {str(e)}")
        return {'error': str(e)}