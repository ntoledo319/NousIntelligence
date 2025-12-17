"""
Mental Health Resources Service

This service provides access to crisis support, affordable therapy, and psychiatry
resources with location-based search capabilities.

@module services.mental_health_resources_service
@ai_prompt Use this for crisis support and mental health provider searches
"""

import logging
import math
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import and_, or_, func
from models.database import db
from models.mental_health_resources import (
    CrisisResource, TherapyProvider, PsychiatryProvider,
    CommunityResource, UserSavedResource
)
from models.health_models import DBTCrisisResource

logger = logging.getLogger(__name__)


class MentalHealthResourcesService:
    """Service for accessing mental health resources and crisis support"""
    
    def __init__(self):
        # Default crisis resources that should always be available
        self.default_crisis_resources = [
            {
                'name': '988 Suicide & Crisis Lifeline',
                'phone_number': '988',
                'text_number': '988',
                'description': '24/7 crisis support for mental health emergencies',
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True
            },
            {
                'name': 'Crisis Text Line',
                'text_number': '741741',
                'description': 'Text HOME to 741741 for 24/7 crisis support',
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True
            },
            {
                'name': 'SAMHSA National Helpline',
                'phone_number': '1-800-662-4357',
                'description': 'Treatment referral and information service for mental health and substance use',
                'is_24_7': True,
                'country_code': 'US',
                'is_national': True
            }
        ]
        logger.info("Mental Health Resources Service initialized")
    
    # === Crisis Resource Methods ===
    
    def get_crisis_resources(self, country_code: str = 'US', 
                           state: Optional[str] = None,
                           specialization: Optional[str] = None) -> List[CrisisResource]:
        """
        Get crisis resources for a location
        
        ## Concept: Crisis Support
        Always provide multiple options for crisis support
        """
        try:
            query = CrisisResource.query.filter_by(is_verified=True)
            
            # Filter by country
            query = query.filter(
                or_(
                    CrisisResource.country_code == country_code,
                    CrisisResource.is_national == True
                )
            )
            
            # Filter by state if provided
            if state:
                query = query.filter(
                    or_(
                        CrisisResource.state_province == state,
                        CrisisResource.is_national == True
                    )
                )
            
            # Filter by specialization if provided
            if specialization:
                query = query.filter(
                    CrisisResource.specializations.contains([specialization])
                )
            
            # Order by priority
            resources = query.order_by(CrisisResource.priority_order).all()
            
            # Always include default resources if none found
            if not resources:
                return self._get_default_crisis_resources()
            
            return resources
            
        except Exception as e:
            logger.error(f"Error getting crisis resources: {e}")
            # In case of error, always return default resources
            return self._get_default_crisis_resources()
    
    def _get_default_crisis_resources(self) -> List[Dict[str, Any]]:
        """Get default crisis resources when database is unavailable"""
        # Also check existing DBT crisis resources
        try:
            dbt_resources = DBTCrisisResource.query.filter_by(is_active=True).all()
            resources = []
            
            # Add DBT resources if available
            for dbt_res in dbt_resources:
                resources.append({
                    'name': dbt_res.name,
                    'phone_number': dbt_res.phone_number,
                    'description': dbt_res.description,
                    'is_24_7': dbt_res.is_24_7,
                    'country_code': 'US',
                    'is_national': True
                })
            
            # Add default resources
            resources.extend(self.default_crisis_resources)
            
            return resources
        except:
            return self.default_crisis_resources
    
    # === Therapy Provider Methods ===
    
    def search_therapy_providers(self, latitude: float, longitude: float,
                               radius_miles: int = 25,
                               filters: Optional[Dict[str, Any]] = None) -> List[TherapyProvider]:
        """
        Search for therapy providers near a location
        
        @ai_prompt Use this to find affordable therapy options near user
        """
        try:
            # Base query
            query = TherapyProvider.query.filter_by(is_verified=True, is_accepting_patients=True)
            
            # Apply filters
            if filters:
                if filters.get('has_sliding_scale'):
                    query = query.filter_by(has_sliding_scale=True)
                
                if filters.get('accepts_insurance'):
                    query = query.filter_by(accepts_insurance=True)
                
                if filters.get('is_online'):
                    query = query.filter_by(is_online=True)
                
                if filters.get('specialization'):
                    query = query.filter(
                        TherapyProvider.specializations.contains([filters['specialization']])
                    )
                
                if filters.get('modality'):
                    query = query.filter(
                        TherapyProvider.modalities.contains([filters['modality']])
                    )
                
                if filters.get('max_fee'):
                    query = query.filter(
                        TherapyProvider.session_fee_min <= filters['max_fee'] * 100  # Convert to cents
                    )
            
            # Get all providers to calculate distance
            providers = query.all()
            
            # Calculate distances and filter by radius
            nearby_providers = []
            for provider in providers:
                if provider.latitude and provider.longitude:
                    distance = self._calculate_distance(
                        latitude, longitude,
                        provider.latitude, provider.longitude
                    )
                    
                    if distance <= radius_miles:
                        provider.distance = round(distance, 1)
                        nearby_providers.append(provider)
            
            # Sort by distance
            nearby_providers.sort(key=lambda p: p.distance)
            
            return nearby_providers[:50]  # Limit to 50 results
            
        except Exception as e:
            logger.error(f"Error searching therapy providers: {e}")
            return []
    
    def get_affordable_therapy_options(self, city: str, state: str) -> List[TherapyProvider]:
        """Get specifically affordable therapy options"""
        try:
            # Query for providers with sliding scale or low fees
            query = TherapyProvider.query.filter_by(
                city=city,
                state_province=state,
                is_verified=True
            ).filter(
                or_(
                    TherapyProvider.has_sliding_scale == True,
                    TherapyProvider.session_fee_min <= 8000  # $80 or less
                )
            )
            
            return query.order_by(TherapyProvider.session_fee_min).limit(20).all()
            
        except Exception as e:
            logger.error(f"Error getting affordable therapy: {e}")
            return []
    
    # === Psychiatry Provider Methods ===
    
    def search_psychiatry_providers(self, latitude: float, longitude: float,
                                  radius_miles: int = 50,
                                  filters: Optional[Dict[str, Any]] = None) -> List[PsychiatryProvider]:
        """Search for psychiatry providers near a location"""
        try:
            query = PsychiatryProvider.query.filter_by(
                is_verified=True,
                accepts_new_patients=True
            )
            
            # Apply filters
            if filters:
                if filters.get('accepts_medicare'):
                    query = query.filter_by(accepts_medicare=True)
                
                if filters.get('accepts_medicaid'):
                    query = query.filter_by(accepts_medicaid=True)
                
                if filters.get('is_telehealth'):
                    query = query.filter_by(is_telehealth=True)
                
                if filters.get('specialization'):
                    query = query.filter(
                        PsychiatryProvider.specializations.contains([filters['specialization']])
                    )
            
            # Get providers and calculate distances
            providers = query.all()
            nearby_providers = []
            
            for provider in providers:
                if provider.latitude and provider.longitude:
                    distance = self._calculate_distance(
                        latitude, longitude,
                        provider.latitude, provider.longitude
                    )
                    
                    if distance <= radius_miles:
                        provider.distance = round(distance, 1)
                        nearby_providers.append(provider)
            
            # Sort by distance
            nearby_providers.sort(key=lambda p: p.distance)
            
            return nearby_providers[:30]
            
        except Exception as e:
            logger.error(f"Error searching psychiatry providers: {e}")
            return []
    
    # === Community Resource Methods ===
    
    def get_community_resources(self, city: str, state: str,
                              resource_type: Optional[str] = None) -> List[CommunityResource]:
        """Get free/low-cost community mental health resources"""
        try:
            query = CommunityResource.query.filter_by(
                city=city,
                state_province=state,
                is_verified=True
            )
            
            if resource_type:
                query = query.filter_by(resource_type=resource_type)
            
            # Prioritize free resources
            query = query.order_by(
                CommunityResource.is_free.desc(),
                CommunityResource.name
            )
            
            return query.limit(20).all()
            
        except Exception as e:
            logger.error(f"Error getting community resources: {e}")
            return []
    
    # === User Saved Resources ===
    
    def save_user_resource(self, user_id: str, resource_type: str,
                         resource_id: int, notes: Optional[str] = None,
                         is_primary: bool = False) -> bool:
        """Save a resource to user's list"""
        try:
            # Check if already saved
            existing = UserSavedResource.query.filter_by(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id
            ).first()
            
            if existing:
                existing.notes = notes
                existing.is_primary = is_primary
            else:
                saved = UserSavedResource(
                    user_id=user_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    notes=notes,
                    is_primary=is_primary
                )
                db.session.add(saved)
            
            # If setting as primary, unset other primaries
            if is_primary:
                UserSavedResource.query.filter_by(
                    user_id=user_id,
                    resource_type=resource_type
                ).filter(UserSavedResource.resource_id != resource_id).update(
                    {'is_primary': False}
                )
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving resource: {e}")
            db.session.rollback()
            return False
    
    def get_user_saved_resources(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all saved resources for a user"""
        try:
            saved = UserSavedResource.query.filter_by(user_id=user_id).all()
            
            resources = {
                'crisis': [],
                'therapy': [],
                'psychiatry': [],
                'community': []
            }
            
            for saved_resource in saved:
                # Get the actual resource based on type
                resource_data = None
                
                if saved_resource.resource_type == 'crisis':
                    resource = CrisisResource.query.get(saved_resource.resource_id)
                    if resource:
                        resource_data = resource.to_dict()
                elif saved_resource.resource_type == 'therapy':
                    resource = TherapyProvider.query.get(saved_resource.resource_id)
                    if resource:
                        resource_data = resource.to_dict()
                elif saved_resource.resource_type == 'psychiatry':
                    resource = PsychiatryProvider.query.get(saved_resource.resource_id)
                    if resource:
                        resource_data = resource.to_dict()
                elif saved_resource.resource_type == 'community':
                    resource = CommunityResource.query.get(saved_resource.resource_id)
                    if resource:
                        resource_data = resource.to_dict()
                
                if resource_data:
                    resource_data['saved_notes'] = saved_resource.notes
                    resource_data['is_primary'] = saved_resource.is_primary
                    resource_data['saved_at'] = saved_resource.saved_at.isoformat()
                    resources[saved_resource.resource_type].append(resource_data)
            
            return resources
            
        except Exception as e:
            logger.error(f"Error getting saved resources: {e}")
            return {'crisis': [], 'therapy': [], 'psychiatry': [], 'community': []}
    
    # === Helper Methods ===
    
    def _calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in miles"""
        # Haversine formula
        R = 3959  # Earth's radius in miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def get_location_from_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get approximate location from IP address for initial search"""
        # This would integrate with a geolocation API
        # For now, return None - frontend should ask for location
        return None
    
    def import_resources_from_api(self, api_name: str, api_key: str) -> int:
        """Import resources from external APIs like Psychology Today, SAMHSA"""
        # This would be implemented to import provider data
        # from various mental health directories
        pass


# AI-GENERATED [2024-12-01]
# @see models.mental_health_resources for database schema
# NON-NEGOTIABLES: Crisis resources must ALWAYS be available, even if database fails 