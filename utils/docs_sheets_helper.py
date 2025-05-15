"""
Helper module for Google Docs and Sheets integration
"""
import os
import logging
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json

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

# Google Docs Functions

def create_document(docs_service, drive_service, title, content=None):
    """Create a new Google Doc"""
    try:
        # Create an empty document
        document = docs_service.documents().create(body={'title': title}).execute()
        document_id = document.get('documentId')
        
        # If content is provided, add it to the document
        if content:
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                }
            ]
            
            docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
        # Get the document link
        file = drive_service.files().get(
            fileId=document_id,
            fields='webViewLink'
        ).execute()
        
        return {
            "success": True,
            "document_id": document_id,
            "title": title,
            "link": file.get('webViewLink')
        }
    except Exception as e:
        logging.error(f"Error creating document: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_document(docs_service, document_id):
    """Get a Google Doc by ID"""
    try:
        document = docs_service.documents().get(documentId=document_id).execute()
        return {
            "success": True,
            "document": document
        }
    except Exception as e:
        logging.error(f"Error getting document: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def update_document(docs_service, document_id, requests):
    """Update a Google Doc with a list of requests"""
    try:
        result = docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logging.error(f"Error updating document: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_document_content(docs_service, document_id):
    """Extract text content from a Google Doc"""
    try:
        document = docs_service.documents().get(documentId=document_id).execute()
        
        # Extract text from the document
        content = ''
        for content_item in document.get('body', {}).get('content', []):
            if 'paragraph' in content_item:
                for element in content_item['paragraph']['elements']:
                    if 'textRun' in element:
                        content += element['textRun']['content']
                        
        return {
            "success": True,
            "content": content,
            "title": document.get('title', '')
        }
    except Exception as e:
        logging.error(f"Error getting document content: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Google Sheets Functions

def create_spreadsheet(sheets_service, drive_service, title, sheets=None):
    """Create a new Google Sheet"""
    try:
        # Prepare sheet data
        spreadsheet_body = {
            'properties': {
                'title': title
            }
        }
        
        # Add custom sheets if provided
        if sheets and isinstance(sheets, list):
            spreadsheet_body['sheets'] = []
            
            for sheet in sheets:
                sheet_object = {
                    'properties': {
                        'title': sheet['title'] if 'title' in sheet else 'Sheet1'
                    }
                }
                
                # Add grid properties if provided
                if 'rows' in sheet or 'columns' in sheet:
                    sheet_object['properties']['gridProperties'] = {}
                    
                    if 'rows' in sheet:
                        sheet_object['properties']['gridProperties']['rowCount'] = sheet['rows']
                        
                    if 'columns' in sheet:
                        sheet_object['properties']['gridProperties']['columnCount'] = sheet['columns']
                        
                spreadsheet_body['sheets'].append(sheet_object)
                
        # Create the spreadsheet
        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        
        # Get the spreadsheet link
        file = drive_service.files().get(
            fileId=spreadsheet_id,
            fields='webViewLink'
        ).execute()
        
        return {
            "success": True,
            "spreadsheet_id": spreadsheet_id,
            "title": title,
            "link": file.get('webViewLink')
        }
    except Exception as e:
        logging.error(f"Error creating spreadsheet: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_spreadsheet(sheets_service, spreadsheet_id):
    """Get a Google Sheet by ID"""
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return {
            "success": True,
            "spreadsheet": spreadsheet
        }
    except Exception as e:
        logging.error(f"Error getting spreadsheet: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_sheet_values(sheets_service, spreadsheet_id, range_name):
    """Get values from a range in a Google Sheet"""
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, 
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        return {
            "success": True,
            "values": values,
            "range": result.get('range')
        }
    except Exception as e:
        logging.error(f"Error getting sheet values: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def update_sheet_values(sheets_service, spreadsheet_id, range_name, values, value_input_option='USER_ENTERED'):
    """Update values in a Google Sheet"""
    try:
        body = {
            'values': values
        }
        
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()
        
        return {
            "success": True,
            "updated_rows": result.get('updatedRows'),
            "updated_columns": result.get('updatedColumns'),
            "updated_cells": result.get('updatedCells')
        }
    except Exception as e:
        logging.error(f"Error updating sheet values: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def append_sheet_values(sheets_service, spreadsheet_id, range_name, values, value_input_option='USER_ENTERED'):
    """Append values to a Google Sheet"""
    try:
        body = {
            'values': values
        }
        
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()
        
        return {
            "success": True,
            "updated_rows": result.get('updates', {}).get('updatedRows'),
            "updated_columns": result.get('updates', {}).get('updatedColumns'),
            "updated_cells": result.get('updates', {}).get('updatedCells')
        }
    except Exception as e:
        logging.error(f"Error appending sheet values: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def clear_sheet_values(sheets_service, spreadsheet_id, range_name):
    """Clear values in a Google Sheet"""
    try:
        result = sheets_service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        return {
            "success": True,
            "cleared_range": result.get('clearedRange')
        }
    except Exception as e:
        logging.error(f"Error clearing sheet values: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Template Functions

def create_medication_tracker_spreadsheet(sheets_service, drive_service, title="Medication Tracker"):
    """Create a medication tracker spreadsheet"""
    try:
        # Create the spreadsheet
        spreadsheet_result = create_spreadsheet(
            sheets_service, 
            drive_service, 
            title, 
            sheets=[
                {
                    'title': 'Medications',
                    'rows': 100,
                    'columns': 10
                },
                {
                    'title': 'Refill History',
                    'rows': 100,
                    'columns': 8
                }
            ]
        )
        
        if not spreadsheet_result["success"]:
            return spreadsheet_result
            
        spreadsheet_id = spreadsheet_result["spreadsheet_id"]
        
        # Set up the Medications sheet
        medications_headers = [
            ['Medication Name', 'Dosage', 'Frequency', 'Quantity Remaining', 
             'Refill Date', 'Notes', 'Prescribing Doctor', 'Pharmacy', 'Reminder (days)', 'Last Updated']
        ]
        
        update_sheet_values(
            sheets_service,
            spreadsheet_id,
            'Medications!A1:J1',
            medications_headers
        )
        
        # Set up the Refill History sheet
        refill_headers = [
            ['Medication Name', 'Refill Date', 'Quantity', 
             'Pharmacy', 'Prescribing Doctor', 'Notes', 'Cost', 'Insurance Coverage']
        ]
        
        update_sheet_values(
            sheets_service,
            spreadsheet_id,
            'Refill History!A1:H1',
            refill_headers
        )
        
        # Format the spreadsheet
        # Add formatting requests here if needed
        
        return {
            "success": True,
            "spreadsheet_id": spreadsheet_id,
            "title": title,
            "link": spreadsheet_result["link"]
        }
    except Exception as e:
        logging.error(f"Error creating medication tracker: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def create_recovery_journal_document(docs_service, drive_service, title="Recovery Journal"):
    """Create a recovery journal document template"""
    try:
        # Create the document
        journal_content = """# Recovery Journal

## Daily Check-In Template

Date: 

Mood (1-10): 

Gratitude List:
1. 
2. 
3. 

Challenges Faced Today:
- 
- 

Victories Today:
- 
- 

Triggers Encountered:
- 
- 

Skills Used:
- 
- 

Tomorrow's Goals:
1. 
2. 
3. 

Self-Care Activities:
- 
- 

Notes:

---

## Weekly Reflection Template

Week of: 

Overall Progress (1-10): 

What Went Well:
- 
- 

What I Struggled With:
- 
- 

Lessons Learned:
- 
- 

Goals for Next Week:
1. 
2. 
3. 

Support Needed:
- 
- 

Notes:

---

## Monthly Recovery Milestone

Month: 

Sobriety Days: 

Key Achievements:
1. 
2. 
3. 

Most Valuable Skills Learned:
- 
- 

Changes Noticed:
- 
- 

Areas for Growth:
- 
- 

Gratitude Reflections:
- 
- 

Notes:

"""
        
        document_result = create_document(docs_service, drive_service, title, journal_content)
        
        return document_result
    except Exception as e:
        logging.error(f"Error creating recovery journal: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def create_budget_spreadsheet(sheets_service, drive_service, title="Budget Tracker"):
    """Create a budget and expense tracking spreadsheet"""
    try:
        # Create the spreadsheet
        spreadsheet_result = create_spreadsheet(
            sheets_service, 
            drive_service, 
            title, 
            sheets=[
                {
                    'title': 'Monthly Budget',
                    'rows': 50,
                    'columns': 10
                },
                {
                    'title': 'Expenses',
                    'rows': 500,
                    'columns': 8
                },
                {
                    'title': 'Summary',
                    'rows': 25,
                    'columns': 6
                }
            ]
        )
        
        if not spreadsheet_result["success"]:
            return spreadsheet_result
            
        spreadsheet_id = spreadsheet_result["spreadsheet_id"]
        
        # Set up the Monthly Budget sheet
        budget_headers = [
            ['Category', 'Subcategory', 'Budgeted Amount', 'Actual Amount', 
             'Difference', 'Notes', 'Month', 'Year', 'Status', 'Priority']
        ]
        
        update_sheet_values(
            sheets_service,
            spreadsheet_id,
            'Monthly Budget!A1:J1',
            budget_headers
        )
        
        # Add default budget categories
        budget_categories = [
            ['Housing', 'Rent/Mortgage', '', '', '', '', '', '', '', ''],
            ['Housing', 'Utilities', '', '', '', '', '', '', '', ''],
            ['Transportation', 'Gas', '', '', '', '', '', '', '', ''],
            ['Transportation', 'Public Transit', '', '', '', '', '', '', '', ''],
            ['Food', 'Groceries', '', '', '', '', '', '', '', ''],
            ['Food', 'Dining Out', '', '', '', '', '', '', '', ''],
            ['Healthcare', 'Insurance', '', '', '', '', '', '', '', ''],
            ['Healthcare', 'Medications', '', '', '', '', '', '', '', ''],
            ['Entertainment', 'Subscriptions', '', '', '', '', '', '', '', ''],
            ['Entertainment', 'Hobbies', '', '', '', '', '', '', '', ''],
            ['Personal', 'Clothing', '', '', '', '', '', '', '', ''],
            ['Personal', 'Self-care', '', '', '', '', '', '', '', ''],
            ['Savings', 'Emergency Fund', '', '', '', '', '', '', '', ''],
            ['Savings', 'Goals', '', '', '', '', '', '', '', ''],
            ['Recovery', 'Meetings', '', '', '', '', '', '', '', ''],
            ['Recovery', 'Support', '', '', '', '', '', '', '', '']
        ]
        
        update_sheet_values(
            sheets_service,
            spreadsheet_id,
            'Monthly Budget!A2:J17',
            budget_categories
        )
        
        # Set up the Expenses sheet
        expense_headers = [
            ['Date', 'Category', 'Subcategory', 'Amount', 
             'Method', 'Description', 'Receipt', 'Status']
        ]
        
        update_sheet_values(
            sheets_service,
            spreadsheet_id,
            'Expenses!A1:H1',
            expense_headers
        )
        
        # Set up the Summary sheet
        summary_headers = [
            ['Month', 'Year', 'Total Budget', 'Total Expenses', 
             'Difference', 'Savings']
        ]
        
        update_sheet_values(
            sheets_service,
            spreadsheet_id,
            'Summary!A1:F1',
            summary_headers
        )
        
        return {
            "success": True,
            "spreadsheet_id": spreadsheet_id,
            "title": title,
            "link": spreadsheet_result["link"]
        }
    except Exception as e:
        logging.error(f"Error creating budget spreadsheet: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def create_travel_planning_document(docs_service, drive_service, title="Travel Planning"):
    """Create a travel planning document template"""
    try:
        # Create the document
        travel_content = """# Travel Planning Document

## Trip Overview

Destination: 
Dates: 
Purpose: 

## Pre-Trip Checklist

### Documents
- [ ] Passport/ID
- [ ] Travel insurance
- [ ] Tickets/confirmations
- [ ] Visa (if required)
- [ ] Driver's license (if driving)
- [ ] Health insurance card
- [ ] COVID-19 requirements (if applicable)
- [ ] Copies of important documents

### Accommodations
- 
- 

### Transportation
- 
- 

### Financial
- [ ] Notify bank/credit card companies
- [ ] Exchange currency (if needed)
- [ ] Set aside emergency cash
- [ ] Budget for trip

### Health
- [ ] Medications (sufficient supply)
- [ ] First aid kit
- [ ] Check travel health advisories
- [ ] Refill prescriptions
- [ ] Medical contact info
- [ ] Health insurance coverage confirmed

### Recovery Support
- [ ] Find local meetings
- [ ] Contact person plan
- [ ] Recovery materials
- [ ] Self-care items
- [ ] Trigger management plan

## Itinerary

### Day 1
Date: 
Schedule:
- 
- 

### Day 2
Date: 
Schedule:
- 
- 

## Packing List

### Clothing
- 
- 

### Toiletries
- 
- 

### Electronics
- 
- 

### Recovery Items
- 
- 

## Contacts & Emergency Information

### Emergency Contacts
- 
- 

### Local Resources
- 
- 

### Recovery Resources
- 
- 

## Notes & Reminders
- 
- 

"""
        
        document_result = create_document(docs_service, drive_service, title, travel_content)
        
        return document_result
    except Exception as e:
        logging.error(f"Error creating travel planning document: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def analyze_document_content(docs_service, document_id, openai_client=None):
    """Analyze the content of a document using AI"""
    try:
        # Get the document content
        content_result = get_document_content(docs_service, document_id)
        
        if not content_result["success"]:
            return content_result
            
        content = content_result["content"]
        title = content_result["title"]
        
        # If OpenAI client is not available, just return the content
        if not openai_client:
            return {
                "success": True,
                "document_id": document_id,
                "title": title,
                "content": content
            }
            
        # Trim if too long
        if len(content) > 10000:
            content = content[:10000] + "...[content truncated]"
            
        try:
            # Analyze using OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {
                        "role": "system",
                        "content": "You are a document analysis assistant. Analyze the provided document and extract key information."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this document titled '{title}'. Provide a summary, key topics, any action items, and overall theme. Format your response as JSON."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "document_id": document_id,
                "title": title,
                "analysis": analysis
            }
        except Exception as e:
            logging.error(f"Error in AI analysis of document: {str(e)}")
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}"
            }
            
    except Exception as e:
        logging.error(f"Error analyzing document: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def analyze_spreadsheet_data(sheets_service, spreadsheet_id, range_name, openai_client=None):
    """Analyze data in a spreadsheet using AI"""
    try:
        # Get the spreadsheet data
        data_result = get_sheet_values(sheets_service, spreadsheet_id, range_name)
        
        if not data_result["success"]:
            return data_result
            
        values = data_result["values"]
        
        # If no values or OpenAI client is not available, just return the data
        if not values or not openai_client:
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "range": range_name,
                "values": values
            }
            
        # Convert the data to a more readable format
        if len(values) > 0:
            headers = values[0]
            rows = values[1:]
            
            formatted_data = []
            for row in rows:
                row_dict = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        row_dict[header] = row[i]
                    else:
                        row_dict[header] = ""
                formatted_data.append(row_dict)
                
            data_str = json.dumps(formatted_data, indent=2)
        else:
            data_str = "No data found in this range."
            
        # Trim if too long
        if len(data_str) > 10000:
            data_str = data_str[:10000] + "...[data truncated]"
            
        try:
            # Analyze using OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analysis assistant. Analyze the provided spreadsheet data and extract insights."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this spreadsheet data from range '{range_name}'. Provide a summary, key trends, notable patterns, and any insights or recommendations. Format your response as JSON."
                    },
                    {
                        "role": "user",
                        "content": data_str
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "range": range_name,
                "analysis": analysis
            }
        except Exception as e:
            logging.error(f"Error in AI analysis of spreadsheet: {str(e)}")
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}"
            }
            
    except Exception as e:
        logging.error(f"Error analyzing spreadsheet: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }