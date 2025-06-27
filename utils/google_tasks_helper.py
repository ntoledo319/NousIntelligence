"""
Google Tasks Helper

This module provides functions for interacting with the Google Tasks API.
"""
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_tasks_service(credentials):
    """Builds and returns a Google Tasks service object."""
    return build('tasks', 'v1', credentials=credentials)

def get_task_lists(service):
    """Gets all of the user's task lists."""
    return service.tasklists().list().execute()

def get_tasks(service, tasklist_id):
    """Gets all tasks from a specific task list."""
    return service.tasks().list(tasklist=tasklist_id).execute()

def create_task(service, tasklist_id, task_body):
    """Creates a new task."""
    return service.tasks().insert(tasklist=tasklist_id, body=task_body).execute()

def update_task(service, tasklist_id, task_id, task_body):
    """Updates an existing task."""
    return service.tasks().update(tasklist=tasklist_id, task=task_id, body=task_body).execute() 