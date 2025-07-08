"""
Migration: Add Default Crisis Resources

This migration adds essential crisis support resources that should always
be available to users in need.

@module migrations.add_crisis_resources
@ai_prompt Run this to populate crisis resources database
"""

import logging
from datetime import datetime
from database import db
from models.mental_health_resources import CrisisResource

logger = logging.getLogger(__name__)


def run_migration():
    """
    Add default crisis resources for immediate help
    
    NON-NEGOTIABLES: These resources must always be available
    """
    try:
        logger.info("Adding default crisis resources...")
        
        # US National Crisis Resources
        us_resources = [
            {
                'name': '988 Suicide & Crisis Lifeline',
                'phone_number': '988',
                'text_number': '988',
                'website': 'https://988lifeline.org',
                'chat_url': 'https://988lifeline.org/chat',
                'description': 'Free, confidential 24/7 crisis support for anyone in suicidal crisis or emotional distress',
                'service_type': 'hotline',
                'specializations': ['suicide_prevention', 'crisis', 'emotional_support'],
                'languages': ['en', 'es'],
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 1
            },
            {
                'name': 'Crisis Text Line',
                'text_number': '741741',
                'website': 'https://www.crisistextline.org',
                'description': 'Text HOME to 741741 - Free 24/7 support for those in crisis',
                'service_type': 'text',
                'specializations': ['crisis', 'anxiety', 'depression', 'self_harm'],
                'languages': ['en', 'es'],
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 2
            },
            {
                'name': 'SAMHSA National Helpline',
                'phone_number': '1-800-662-4357',
                'website': 'https://www.samhsa.gov/find-help/national-helpline',
                'description': 'Treatment referral and information service for mental health and substance use disorders',
                'service_type': 'hotline',
                'specializations': ['substance_abuse', 'mental_health', 'treatment_referral'],
                'languages': ['en', 'es'],
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 3
            },
            {
                'name': 'Veterans Crisis Line',
                'phone_number': '1-800-273-8255',
                'text_number': '838255',
                'website': 'https://www.veteranscrisisline.net',
                'chat_url': 'https://www.veteranscrisisline.net/get-help-now/chat',
                'description': 'Confidential support for Veterans and their loved ones',
                'service_type': 'hotline',
                'specializations': ['veterans', 'military', 'crisis', 'suicide_prevention'],
                'languages': ['en', 'es'],
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 4
            },
            {
                'name': 'LGBT National Hotline',
                'phone_number': '1-888-843-4564',
                'website': 'https://www.lgbthotline.org',
                'description': 'Support for LGBTQ individuals in crisis',
                'service_type': 'hotline',
                'specializations': ['lgbtq', 'crisis', 'coming_out', 'identity'],
                'languages': ['en'],
                'is_24_7': False,
                'hours_of_operation': {
                    'mon': '1pm-9pm ET',
                    'tue': '1pm-9pm ET',
                    'wed': '1pm-9pm ET',
                    'thu': '1pm-9pm ET',
                    'fri': '1pm-9pm ET'
                },
                'country_code': 'US',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 10
            },
            {
                'name': 'National Domestic Violence Hotline',
                'phone_number': '1-800-799-7233',
                'text_number': '88788',
                'website': 'https://www.thehotline.org',
                'chat_url': 'https://www.thehotline.org/get-help',
                'description': '24/7 support for domestic violence victims and survivors',
                'service_type': 'hotline',
                'specializations': ['domestic_violence', 'abuse', 'safety_planning'],
                'languages': ['en', 'es', 'and 200+ languages via interpretation'],
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 5
            },
            {
                'name': 'RAINN National Sexual Assault Hotline',
                'phone_number': '1-800-656-4673',
                'website': 'https://www.rainn.org',
                'chat_url': 'https://hotline.rainn.org/online',
                'description': 'Support for sexual assault survivors',
                'service_type': 'hotline',
                'specializations': ['sexual_assault', 'trauma', 'abuse'],
                'languages': ['en', 'es'],
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 6
            },
            {
                'name': 'Trans Lifeline',
                'phone_number': '877-565-8860',
                'website': 'https://translifeline.org',
                'description': 'Trans peer support & crisis hotline',
                'service_type': 'hotline',
                'specializations': ['transgender', 'crisis', 'peer_support'],
                'languages': ['en', 'es'],
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 11
            }
        ]
        
        # Add Canadian resources
        canada_resources = [
            {
                'name': 'Talk Suicide Canada',
                'phone_number': '1-833-456-4566',
                'text_number': '45645',
                'website': 'https://talksuicide.ca',
                'description': '24/7 suicide prevention support',
                'service_type': 'hotline',
                'specializations': ['suicide_prevention', 'crisis'],
                'languages': ['en', 'fr'],
                'is_24_7': True,
                'country_code': 'CA',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 1
            }
        ]
        
        # Add UK resources
        uk_resources = [
            {
                'name': 'Samaritans',
                'phone_number': '116 123',
                'website': 'https://www.samaritans.org',
                'description': 'Free 24/7 emotional support',
                'service_type': 'hotline',
                'specializations': ['crisis', 'emotional_support', 'suicide_prevention'],
                'languages': ['en'],
                'is_24_7': True,
                'country_code': 'GB',
                'is_national': True,
                'is_free': True,
                'is_verified': True,
                'priority_order': 1
            }
        ]
        
        # Add all resources
        resources_added = 0
        
        for resource_data in us_resources + canada_resources + uk_resources:
            # Check if already exists
            existing = CrisisResource.query.filter_by(
                name=resource_data['name'],
                country_code=resource_data['country_code']
            ).first()
            
            if not existing:
                resource_data['last_verified'] = datetime.utcnow()
                resource = CrisisResource(**resource_data)
                db.session.add(resource)
                resources_added += 1
        
        db.session.commit()
        
        logger.info(f"✅ Added {resources_added} crisis resources")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding crisis resources: {e}")
        db.session.rollback()
        return False


if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        success = run_migration()
        
        if success:
            print("\n✅ Crisis resources added successfully!")
            print("\nResources are now available at:")
            print("  - /resources/crisis - Crisis support page")
            print("  - /api/crisis - API endpoint for crisis resources")
            print("\n⚠️  IMPORTANT: Crisis resources are accessible without login")
        else:
            print("\n❌ Failed to add crisis resources. Check logs for details.")


# AI-GENERATED [2024-12-01]
# CRITICAL: These resources can save lives - verify all phone numbers
# NON-NEGOTIABLES: Crisis resources must be free and accessible to all 