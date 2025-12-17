"""
Mental Health Resources Models

This module defines database models for crisis support, therapy, and psychiatry resources.
Provides location-based access to affordable mental health care options.

@module models.mental_health_resources
@context_boundary Crisis Support & Mental Health Resources
"""

from models.database import db
from datetime import datetime
from sqlalchemy import func, Index
from sqlalchemy.dialects.postgresql import JSONB


class CrisisResource(db.Model):
    """Model for crisis hotlines and immediate support resources"""
    
    __tablename__ = 'crisis_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    phone_number = db.Column(db.String(50))
    text_number = db.Column(db.String(50))
    website = db.Column(db.String(500))
    chat_url = db.Column(db.String(500))
    
    # Service details
    service_type = db.Column(db.String(50), nullable=False)  # hotline, text, chat, in-person
    specializations = db.Column(db.JSON)  # ['suicide', 'domestic_violence', 'lgbtq', 'veterans']
    languages = db.Column(db.JSON)  # ['en', 'es', 'zh']
    is_24_7 = db.Column(db.Boolean, default=True)
    hours_of_operation = db.Column(db.JSON)  # {"mon": "9am-5pm", ...}
    
    # Geographic availability
    country_code = db.Column(db.String(2), nullable=False)  # ISO country code
    state_province = db.Column(db.String(100))
    city = db.Column(db.String(100))
    is_national = db.Column(db.Boolean, default=False)
    service_areas = db.Column(db.JSON)  # List of areas served
    
    # Metadata
    is_free = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_verified = db.Column(db.DateTime)
    priority_order = db.Column(db.Integer, default=100)  # Lower number = higher priority
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # VOCAB: Crisis Resource - Immediate help for mental health emergencies
    # NON-NEGOTIABLES: Always show multiple crisis options, never just one
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'phone_number': self.phone_number,
            'text_number': self.text_number,
            'website': self.website,
            'chat_url': self.chat_url,
            'service_type': self.service_type,
            'specializations': self.specializations or [],
            'languages': self.languages or ['en'],
            'is_24_7': self.is_24_7,
            'hours_of_operation': self.hours_of_operation,
            'is_free': self.is_free,
            'country_code': self.country_code,
            'is_national': self.is_national
        }


class TherapyProvider(db.Model):
    """Model for therapy providers and counseling services"""
    
    __tablename__ = 'therapy_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    organization_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # Contact information
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    website = db.Column(db.String(500))
    booking_url = db.Column(db.String(500))
    
    # Location
    address = db.Column(db.String(500))
    city = db.Column(db.String(100), nullable=False)
    state_province = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20))
    country_code = db.Column(db.String(2), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Service details
    therapy_types = db.Column(db.JSON)  # ['individual', 'couples', 'family', 'group']
    specializations = db.Column(db.JSON)  # ['anxiety', 'depression', 'trauma', 'addiction']
    modalities = db.Column(db.JSON)  # ['CBT', 'DBT', 'EMDR', 'psychodynamic']
    age_groups = db.Column(db.JSON)  # ['children', 'adolescents', 'adults', 'seniors']
    languages = db.Column(db.JSON)  # ['en', 'es', 'fr']
    
    # Accessibility
    is_online = db.Column(db.Boolean, default=False)
    is_in_person = db.Column(db.Boolean, default=True)
    has_sliding_scale = db.Column(db.Boolean, default=False)
    accepts_insurance = db.Column(db.Boolean, default=False)
    insurance_accepted = db.Column(db.JSON)  # List of insurance providers
    
    # Pricing
    session_fee_min = db.Column(db.Integer)  # Minimum session fee in cents
    session_fee_max = db.Column(db.Integer)  # Maximum session fee in cents
    currency = db.Column(db.String(3), default='USD')
    offers_free_consultation = db.Column(db.Boolean, default=False)
    
    # Credentials and ratings
    license_number = db.Column(db.String(100))
    license_state = db.Column(db.String(100))
    credentials = db.Column(db.JSON)  # ['PhD', 'LCSW', 'LMFT']
    years_experience = db.Column(db.Integer)
    rating = db.Column(db.Float)
    review_count = db.Column(db.Integer, default=0)
    
    # Metadata
    is_verified = db.Column(db.Boolean, default=False)
    is_accepting_patients = db.Column(db.Boolean, default=True)
    waitlist_available = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # VOCAB: Therapy Provider - Licensed mental health professional
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'organization_name': self.organization_name,
            'description': self.description,
            'phone': self.phone,
            'website': self.website,
            'city': self.city,
            'state_province': self.state_province,
            'therapy_types': self.therapy_types or [],
            'specializations': self.specializations or [],
            'modalities': self.modalities or [],
            'languages': self.languages or ['en'],
            'is_online': self.is_online,
            'is_in_person': self.is_in_person,
            'has_sliding_scale': self.has_sliding_scale,
            'accepts_insurance': self.accepts_insurance,
            'session_fee_range': {
                'min': self.session_fee_min,
                'max': self.session_fee_max,
                'currency': self.currency
            } if self.session_fee_min else None,
            'is_accepting_patients': self.is_accepting_patients,
            'rating': self.rating,
            'distance': getattr(self, 'distance', None)  # Added by location search
        }


class PsychiatryProvider(db.Model):
    """Model for psychiatry providers (medication management)"""
    
    __tablename__ = 'psychiatry_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    practice_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # Contact information
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    website = db.Column(db.String(500))
    booking_url = db.Column(db.String(500))
    
    # Location
    address = db.Column(db.String(500))
    city = db.Column(db.String(100), nullable=False)
    state_province = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20))
    country_code = db.Column(db.String(2), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Service details
    specializations = db.Column(db.JSON)  # ['anxiety', 'bipolar', 'ADHD', 'schizophrenia']
    age_groups = db.Column(db.JSON)  # ['children', 'adolescents', 'adults']
    languages = db.Column(db.JSON)
    provides_therapy = db.Column(db.Boolean, default=False)  # Some psychiatrists also do therapy
    
    # Accessibility
    is_telehealth = db.Column(db.Boolean, default=False)
    is_in_person = db.Column(db.Boolean, default=True)
    accepts_new_patients = db.Column(db.Boolean, default=True)
    has_sliding_scale = db.Column(db.Boolean, default=False)
    accepts_medicare = db.Column(db.Boolean, default=False)
    accepts_medicaid = db.Column(db.Boolean, default=False)
    insurance_accepted = db.Column(db.JSON)
    
    # Pricing
    initial_evaluation_fee = db.Column(db.Integer)  # In cents
    followup_fee = db.Column(db.Integer)  # In cents
    currency = db.Column(db.String(3), default='USD')
    
    # Credentials
    license_number = db.Column(db.String(100))
    license_state = db.Column(db.String(100))
    board_certified = db.Column(db.Boolean, default=False)
    years_experience = db.Column(db.Integer)
    medical_school = db.Column(db.String(200))
    residency_program = db.Column(db.String(200))
    
    # Metadata
    is_verified = db.Column(db.Boolean, default=False)
    last_verified = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'practice_name': self.practice_name,
            'description': self.description,
            'phone': self.phone,
            'website': self.website,
            'city': self.city,
            'state_province': self.state_province,
            'specializations': self.specializations or [],
            'is_telehealth': self.is_telehealth,
            'is_in_person': self.is_in_person,
            'accepts_new_patients': self.accepts_new_patients,
            'accepts_medicare': self.accepts_medicare,
            'accepts_medicaid': self.accepts_medicaid,
            'has_sliding_scale': self.has_sliding_scale,
            'fees': {
                'initial_evaluation': self.initial_evaluation_fee,
                'followup': self.followup_fee,
                'currency': self.currency
            } if self.initial_evaluation_fee else None,
            'board_certified': self.board_certified,
            'distance': getattr(self, 'distance', None)
        }


class CommunityResource(db.Model):
    """Model for community mental health resources and support services"""
    
    __tablename__ = 'community_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # Contact
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    website = db.Column(db.String(500))
    
    # Location
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    state_province = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country_code = db.Column(db.String(2), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Service details
    resource_type = db.Column(db.String(50))  # support_group, clinic, peer_support, rehab
    services_offered = db.Column(db.JSON)  # List of specific services
    populations_served = db.Column(db.JSON)  # ['veterans', 'youth', 'homeless']
    languages = db.Column(db.JSON)
    
    # Accessibility
    is_free = db.Column(db.Boolean, default=True)
    has_sliding_scale = db.Column(db.Boolean, default=False)
    requirements = db.Column(db.Text)  # Eligibility requirements
    
    # Hours
    is_24_7 = db.Column(db.Boolean, default=False)
    hours_of_operation = db.Column(db.JSON)
    
    # Metadata
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'organization': self.organization,
            'description': self.description,
            'phone': self.phone,
            'website': self.website,
            'address': self.address,
            'city': self.city,
            'resource_type': self.resource_type,
            'services_offered': self.services_offered or [],
            'is_free': self.is_free,
            'has_sliding_scale': self.has_sliding_scale,
            'is_24_7': self.is_24_7,
            'distance': getattr(self, 'distance', None)
        }


class UserSavedResource(db.Model):
    """Model for users to save their preferred resources"""
    
    __tablename__ = 'user_saved_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # crisis, therapy, psychiatry, community
    resource_id = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, default=False)  # Primary/preferred provider
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='saved_resources')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'resource_type', 'resource_id', 
                          name='_user_resource_uc'),
    )


# Create indexes for efficient location-based searches
Index('idx_therapy_location', TherapyProvider.latitude, TherapyProvider.longitude)
Index('idx_psychiatry_location', PsychiatryProvider.latitude, PsychiatryProvider.longitude)
Index('idx_community_location', CommunityResource.latitude, CommunityResource.longitude)
Index('idx_crisis_country', CrisisResource.country_code, CrisisResource.is_national)


# AI-GENERATED [2024-12-01]
# HUMAN-VALIDATED [2024-12-01]
# NON-NEGOTIABLES: Crisis resources must always be accessible without authentication 