"""
Helper module for Google Drive integration
"""
import os
import logging
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import io

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

def list_files(service, query=None, max_results=20):
    """List files in Google Drive with optional query"""
    try:
        # Prepare the query
        params = {
            'pageSize': max_results,
            'fields': 'files(id, name, mimeType, modifiedTime, webViewLink, size, thumbnailLink)'
        }

        if query:
            params['q'] = query

        # Execute the request
        results = service.files().list(**params).execute()
        items = results.get('files', [])

        # Format each file with useful information
        formatted_files = []
        for item in items:
            file_info = {
                'id': item.get('id'),
                'name': item.get('name'),
                'type': item.get('mimeType'),
                'modified': item.get('modifiedTime'),
                'link': item.get('webViewLink'),
                'size': item.get('size'),
                'thumbnail': item.get('thumbnailLink')
            }
            formatted_files.append(file_info)

        return formatted_files
    except Exception as e:
        logging.error(f"Error listing Drive files: {str(e)}")
        return []

def search_files(service, query_text, file_type=None, max_results=20):
    """Search for files in Google Drive by name or content"""
    try:
        # Construct the search query
        query_parts = []

        # Add full-text search
        if query_text:
            query_parts.append(f"fullText contains '{query_text}'")

        # Add file type filter if specified
        if file_type:
            if file_type == "document":
                query_parts.append("mimeType='application/vnd.google-apps.document'")
            elif file_type == "spreadsheet":
                query_parts.append("mimeType='application/vnd.google-apps.spreadsheet'")
            elif file_type == "presentation":
                query_parts.append("mimeType='application/vnd.google-apps.presentation'")
            elif file_type == "pdf":
                query_parts.append("mimeType='application/pdf'")
            elif file_type == "image":
                query_parts.append("mimeType contains 'image/'")

        # Add "not trashed" to only show active files
        query_parts.append("trashed=false")

        # Combine all query parts
        query = " and ".join(query_parts)

        return list_files(service, query, max_results)
    except Exception as e:
        logging.error(f"Error searching Drive files: {str(e)}")
        return []

def get_file_metadata(service, file_id):
    """Get detailed metadata for a specific file"""
    try:
        file = service.files().get(
            fileId=file_id,
            fields='id, name, mimeType, description, createdTime, modifiedTime, size, webViewLink, webContentLink, parents, thumbnailLink'
        ).execute()

        return file
    except Exception as e:
        logging.error(f"Error getting Drive file metadata: {str(e)}")
        return None

def download_file(service, file_id, destination_path=None):
    """Download a file from Google Drive"""
    try:
        # Get the file metadata to get its name and MIME type
        file_metadata = service.files().get(fileId=file_id, fields='name, mimeType').execute()
        file_name = file_metadata.get('name', 'downloaded_file')
        mime_type = file_metadata.get('mimeType')

        # If it's a Google Docs/Sheets/Slides file, we need to export it
        if mime_type.startswith('application/vnd.google-apps'):
            if 'document' in mime_type:
                # Export as PDF or DOCX
                request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
                file_name += '.pdf'
            elif 'spreadsheet' in mime_type:
                # Export as XLSX
                request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                file_name += '.xlsx'
            elif 'presentation' in mime_type:
                # Export as PPTX
                request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation')
                file_name += '.pptx'
            else:
                # For other Google formats, default to PDF
                request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
                file_name += '.pdf'
        else:
            # For regular files, just download them
            request = service.files().get_media(fileId=file_id)

        # Set the destination path if not provided
        if not destination_path:
            destination_path = os.path.join('/tmp', file_name)

        # Download the file
        with io.BytesIO() as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Save the file
            with open(destination_path, 'wb') as f:
                f.write(fh.getvalue())

        return {
            "success": True,
            "path": destination_path,
            "name": file_name
        }
    except Exception as e:
        logging.error(f"Error downloading Drive file: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def upload_file(service, file_path, parent_folder_id=None, file_name=None):
    """Upload a file to Google Drive"""
    try:
        # Get the file name if not provided
        if not file_name:
            file_name = os.path.basename(file_path)

        # Guess the MIME type based on the file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        mime_type = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }.get(file_ext, 'application/octet-stream')

        # File metadata
        file_metadata = {
            'name': file_name
        }

        # If a parent folder is specified, add it to the metadata
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        # Upload the file
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()

        return {
            "success": True,
            "id": file.get('id'),
            "name": file.get('name'),
            "link": file.get('webViewLink')
        }
    except Exception as e:
        logging.error(f"Error uploading file to Drive: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def create_folder(service, folder_name, parent_folder_id=None):
    """Create a new folder in Google Drive"""
    try:
        # Folder metadata
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # If a parent folder is specified, add it to the metadata
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]

        # Create the folder
        folder = service.files().create(
            body=folder_metadata,
            fields='id, name, webViewLink'
        ).execute()

        return {
            "success": True,
            "id": folder.get('id'),
            "name": folder.get('name'),
            "link": folder.get('webViewLink')
        }
    except Exception as e:
        logging.error(f"Error creating Drive folder: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def share_file(service, file_id, email, role='reader'):
    """Share a file with another user"""
    try:
        # Validate the role
        if role not in ['reader', 'writer', 'commenter']:
            role = 'reader'

        # Create the permission
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }

        # Share the file
        result = service.permissions().create(
            fileId=file_id,
            body=permission,
            sendNotificationEmail=True,
            fields='id'
        ).execute()

        return {
            "success": True,
            "permission_id": result.get('id')
        }
    except Exception as e:
        logging.error(f"Error sharing Drive file: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_recent_files(service, max_results=10):
    """Get recently modified files"""
    try:
        # Query for files ordered by most recently modified
        query = "trashed=false"
        params = {
            'pageSize': max_results,
            'orderBy': 'modifiedTime desc',
            'q': query,
            'fields': 'files(id, name, mimeType, modifiedTime, webViewLink, size)'
        }

        # Execute the request
        results = service.files().list(**params).execute()
        items = results.get('files', [])

        # Format each file with useful information
        formatted_files = []
        for item in items:
            file_info = {
                'id': item.get('id'),
                'name': item.get('name'),
                'type': item.get('mimeType'),
                'modified': item.get('modifiedTime'),
                'link': item.get('webViewLink'),
                'size': item.get('size')
            }
            formatted_files.append(file_info)

        return formatted_files
    except Exception as e:
        logging.error(f"Error getting recent Drive files: {str(e)}")
        return []

def analyze_file_content(service, file_id, openai_client):
    """Analyze the content of a file using AI"""
    try:
        # Get file metadata
        file = service.files().get(fileId=file_id, fields='name, mimeType').execute()
        file_name = file.get('name')
        mime_type = file.get('mimeType')

        # Handle different file types
        file_content = ""

        if mime_type == 'application/vnd.google-apps.document':
            # Get document content as plain text
            result = service.files().export(fileId=file_id, mimeType='text/plain').execute()
            file_content = result.decode('utf-8')
        elif mime_type.startswith('text/'):
            # Get text file content
            result = service.files().get_media(fileId=file_id).execute()
            file_content = result.decode('utf-8')
        else:
            return {
                "success": False,
                "error": f"File type {mime_type} not supported for analysis"
            }

        # Analyze the content using OpenAI
        if not openai_client:
            return {
                "success": False,
                "error": "OpenAI client not available"
            }

        # Truncate content if it's too large
        if len(file_content) > 10000:
            file_content = file_content[:10000] + "...[content truncated]"

        # Prompt for analysis
        system_prompt = """
        You are an expert document analyzer. Analyze the provided document and extract the following:

        1. Key topics and main points
        2. Important entities mentioned (people, organizations, etc.)
        3. Action items or tasks
        4. Summary of the document (100 words max)

        Format your response as JSON with these keys:
        - topics: list of key topics
        - entities: list of important entities
        - action_items: list of action items
        - summary: brief summary text
        """

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Document: {file_name}\n\nContent:\n{file_content}"}
                ],
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content

            import json
            analysis = json.loads(result)
            analysis["success"] = True
            analysis["file_name"] = file_name

            return analysis
        except Exception as e:
            logging.error(f"Error in AI analysis of file: {str(e)}")
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}"
            }

    except Exception as e:
        logging.error(f"Error analyzing Drive file: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }