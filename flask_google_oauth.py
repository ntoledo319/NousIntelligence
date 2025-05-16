"""
OAuth login for Google using Flask-Dance
"""
import os
from flask import Flask, redirect, url_for, flash, render_template, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_login import login_user, logout_user, current_user
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.exc import NoResultFound
import json

# Load client configuration from client_secret.json
with open('client_secret.json', 'r') as f:
    client_config = json.load(f)['web']

def create_google_blueprint(db, User, OAuth):
    """Create and configure the Google blueprint"""
    # Create the blueprint
    blueprint = make_google_blueprint(
        client_id=client_config['client_id'],
        client_secret=client_config['client_secret'],
        scope=["profile", "email"],
        redirect_url=client_config['redirect_uris'][0],
        # Use SQLAlchemyStorage to store OAuth tokens
        storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
    )
    
    # Define what happens after successful OAuth login
    @oauth_authorized.connect_via(blueprint)
    def google_logged_in(blueprint, token):
        """Execute when user logs in via Google OAuth"""
        if not token:
            flash("Failed to log in with Google.", "error")
            return False

        # Get user info from Google
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google.", "error")
            return False
        
        # Get user info from response
        google_info = resp.json()
        google_user_id = google_info["id"]
        google_email = google_info.get("email")
        google_name = google_info.get("given_name", "User")
        
        # Find or create user
        query = User.query.filter_by(id=google_user_id)
        try:
            user = query.one()
        except NoResultFound:
            # Create a new user
            user = User()
            user.id = google_user_id
            user.email = google_email
            user.first_name = google_name
            user.is_admin = (google_email == "toledonick98@gmail.com")
            db.session.add(user)
            db.session.commit()
        
        # Login the user
        login_user(user)
        flash("Successfully logged in with Google.", "success")
        return False  # Flask-Dance should not save the OAuth token itself
    
    return blueprint