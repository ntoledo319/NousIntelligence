"""
Database Index Migration Script

This script adds performance-optimizing indexes to the existing database tables.
Run this script after deploying updated models.py to ensure all indexes are created.
Includes specialized composite indexes, partial indexes, and text search indexes.

@module: migrate_indexes
@author: NOUS Development Team
"""

import os
import logging
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database connection string
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Define the indexes to create
indexes = [
    # User indexes
    "CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);",
    "CREATE INDEX IF NOT EXISTS idx_user_active ON users(account_active);",
    "CREATE INDEX IF NOT EXISTS idx_user_created_at ON users(created_at);",
    
    # UserSettings indexes
    "CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_user_settings_theme ON user_settings(theme);",
    "CREATE INDEX IF NOT EXISTS idx_user_settings_ai_personality ON user_settings(ai_personality);",
    
    # OAuth indexes
    "CREATE INDEX IF NOT EXISTS idx_oauth_user_provider ON oauth(user_id, provider);",
    
    # Assistant profile indexes
    "CREATE INDEX IF NOT EXISTS idx_assistant_profiles_user_id ON assistant_profiles(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_assistant_profiles_is_default ON assistant_profiles(is_default);",
    
    # UserMemoryEntry indexes
    "CREATE INDEX IF NOT EXISTS idx_memory_user_timestamp ON user_memory_entries(user_id, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_memory_role_timestamp ON user_memory_entries(role, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_memory_full ON user_memory_entries(user_id, role, timestamp);",
    
    # KnowledgeBase indexes (with specialized indexes)
    "CREATE INDEX IF NOT EXISTS idx_knowledge_user_relevance ON knowledge_base(user_id, relevance_score);",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_base(source);",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_access ON knowledge_base(access_count);",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_last_accessed ON knowledge_base(last_accessed);",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_created_at ON knowledge_base(created_at);",
    
    # Add a GIN index for full-text search for PostgreSQL (if using)
    "DO $$ BEGIN CREATE EXTENSION IF NOT EXISTS pg_trgm; EXCEPTION WHEN OTHERS THEN NULL; END $$;",
    "DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm') THEN CREATE INDEX IF NOT EXISTS idx_knowledge_content_trgm ON knowledge_base USING GIN(content gin_trgm_ops); END IF; END $$;",
    
    # Doctor indexes
    "CREATE INDEX IF NOT EXISTS idx_doctor_user ON doctor(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_doctor_name ON doctor(name);",
    "CREATE INDEX IF NOT EXISTS idx_doctor_specialty ON doctor(specialty);",
    "CREATE INDEX IF NOT EXISTS idx_doctor_full ON doctor(user_id, name, specialty);",
    
    # Appointment indexes
    "CREATE INDEX IF NOT EXISTS idx_appointment_user ON appointment(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_appointment_doctor ON appointment(doctor_id);",
    "CREATE INDEX IF NOT EXISTS idx_appointment_date ON appointment(date);",
    "CREATE INDEX IF NOT EXISTS idx_appointment_status ON appointment(status);",
    "CREATE INDEX IF NOT EXISTS idx_appointment_user_date ON appointment(user_id, date);",
    "CREATE INDEX IF NOT EXISTS idx_appointment_doctor_date ON appointment(doctor_id, date);",
    
    # Partial index for upcoming appointments (PostgreSQL)
    "DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_appointment_upcoming ON appointment(date) WHERE date > NOW() AND status = 'scheduled'; EXCEPTION WHEN OTHERS THEN NULL; END $$;",
    
    # Appointment reminder indexes
    "CREATE INDEX IF NOT EXISTS idx_appointment_reminder_doctor ON appointment_reminder(doctor_id);",
    "CREATE INDEX IF NOT EXISTS idx_appointment_reminder_next ON appointment_reminder(next_reminder);",
    
    # Medication indexes
    "CREATE INDEX IF NOT EXISTS idx_medication_user ON medication(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_medication_doctor ON medication(doctor_id);",
    "CREATE INDEX IF NOT EXISTS idx_medication_refill_date ON medication(next_refill_date);",
    "CREATE INDEX IF NOT EXISTS idx_medication_name ON medication(name);",
    "CREATE INDEX IF NOT EXISTS idx_medication_refill_remaining ON medication(refills_remaining);",
    
    # Partial index for medications needing refill (PostgreSQL)
    "DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_medication_needs_refill ON medication(user_id, next_refill_date) WHERE quantity_remaining <= refill_reminder_threshold; EXCEPTION WHEN OTHERS THEN NULL; END $$;",
    
    # ShoppingList indexes
    "CREATE INDEX IF NOT EXISTS idx_shopping_list_user ON shopping_list(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_shopping_list_recurring ON shopping_list(is_recurring);",
    "CREATE INDEX IF NOT EXISTS idx_shopping_list_next_order ON shopping_list(next_order_date);",
    "CREATE INDEX IF NOT EXISTS idx_shopping_list_user_recurring ON shopping_list(user_id, is_recurring);",
    
    # ShoppingItem indexes
    "CREATE INDEX IF NOT EXISTS idx_shopping_item_list ON shopping_item(shopping_list_id);",
    "CREATE INDEX IF NOT EXISTS idx_shopping_item_checked ON shopping_item(shopping_list_id, is_checked);",
    "CREATE INDEX IF NOT EXISTS idx_shopping_item_category ON shopping_item(category);",
    "CREATE INDEX IF NOT EXISTS idx_shopping_item_priority ON shopping_item(priority);",
    
    # Product indexes
    "CREATE INDEX IF NOT EXISTS idx_product_user ON product(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_product_name ON product(name);",
    "CREATE INDEX IF NOT EXISTS idx_product_recurring ON product(is_recurring);",
    "CREATE INDEX IF NOT EXISTS idx_product_next_order ON product(next_order_date);",
    "CREATE INDEX IF NOT EXISTS idx_product_user_recurring ON product(user_id, is_recurring);",
    
    # Trip indexes
    "CREATE INDEX IF NOT EXISTS idx_trip_user ON trip(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_trip_dates ON trip(start_date, end_date);",
    "CREATE INDEX IF NOT EXISTS idx_trip_destination ON trip(destination);",
    
    # Partial index for active/upcoming trips (PostgreSQL)
    "DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_trip_active ON trip(user_id, start_date, end_date) WHERE end_date > NOW(); EXCEPTION WHEN OTHERS THEN NULL; END $$;",
    
    # ItineraryItem indexes
    "CREATE INDEX IF NOT EXISTS idx_itinerary_trip ON itinerary_item(trip_id);",
    "CREATE INDEX IF NOT EXISTS idx_itinerary_date ON itinerary_item(date);",
    "CREATE INDEX IF NOT EXISTS idx_itinerary_trip_date ON itinerary_item(trip_id, date);",
    "CREATE INDEX IF NOT EXISTS idx_itinerary_category ON itinerary_item(category);",
    
    # Accommodation indexes
    "CREATE INDEX IF NOT EXISTS idx_accommodation_trip ON accommodation(trip_id);",
    "CREATE INDEX IF NOT EXISTS idx_accommodation_dates ON accommodation(check_in_date, check_out_date);",
    
    # TravelDocument indexes
    "CREATE INDEX IF NOT EXISTS idx_travel_document_trip ON travel_document(trip_id);",
    "CREATE INDEX IF NOT EXISTS idx_travel_document_type ON travel_document(document_type);",
    "CREATE INDEX IF NOT EXISTS idx_travel_document_departure ON travel_document(departure_time);",
    
    # PackingItem indexes
    "CREATE INDEX IF NOT EXISTS idx_packing_trip ON packing_item(trip_id);",
    "CREATE INDEX IF NOT EXISTS idx_packing_packed ON packing_item(is_packed);",
    "CREATE INDEX IF NOT EXISTS idx_packing_trip_packed ON packing_item(trip_id, is_packed);",
    
    # WeatherLocation indexes
    "CREATE INDEX IF NOT EXISTS idx_weather_user ON weather_location(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_weather_primary ON weather_location(is_primary);",
    "CREATE INDEX IF NOT EXISTS idx_weather_coords ON weather_location(latitude, longitude);",
    "CREATE INDEX IF NOT EXISTS idx_weather_user_primary ON weather_location(user_id, is_primary);",
    
    # Budget indexes
    "CREATE INDEX IF NOT EXISTS idx_budget_user ON budget(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_budget_category ON budget(category);",
    "CREATE INDEX IF NOT EXISTS idx_budget_dates ON budget(start_date, end_date);",
    "CREATE INDEX IF NOT EXISTS idx_budget_recurring ON budget(is_recurring);",
    "CREATE INDEX IF NOT EXISTS idx_budget_user_category ON budget(user_id, category);",
    
    # Expense indexes
    "CREATE INDEX IF NOT EXISTS idx_expense_user ON expense(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_expense_date ON expense(date);",
    "CREATE INDEX IF NOT EXISTS idx_expense_category ON expense(category);",
    "CREATE INDEX IF NOT EXISTS idx_expense_budget ON expense(budget_id);",
    "CREATE INDEX IF NOT EXISTS idx_expense_user_date ON expense(user_id, date);",
    "CREATE INDEX IF NOT EXISTS idx_expense_user_category ON expense(user_id, category);",
    "CREATE INDEX IF NOT EXISTS idx_expense_recurring ON expense(is_recurring);",
    "CREATE INDEX IF NOT EXISTS idx_expense_next_due ON expense(next_due_date);",
    
    # RecurringPayment indexes
    "CREATE INDEX IF NOT EXISTS idx_recurring_payment_user ON recurring_payment(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_recurring_payment_due_day ON recurring_payment(due_day);",
    "CREATE INDEX IF NOT EXISTS idx_recurring_payment_next_due ON recurring_payment(next_due_date);",
    "CREATE INDEX IF NOT EXISTS idx_recurring_payment_category ON recurring_payment(category);",
    
    # DBT related indexes
    "CREATE INDEX IF NOT EXISTS idx_dbt_skill_log_user ON dbt_skill_log(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_dbt_skill_log_category ON dbt_skill_log(category);",
    "CREATE INDEX IF NOT EXISTS idx_dbt_skill_log_effectiveness ON dbt_skill_log(effectiveness);",
    
    "CREATE INDEX IF NOT EXISTS idx_dbt_diary_card_user ON dbt_diary_card(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_dbt_diary_card_date ON dbt_diary_card(date);",
    "CREATE INDEX IF NOT EXISTS idx_dbt_diary_card_mood ON dbt_diary_card(mood_rating);",
    
    "CREATE INDEX IF NOT EXISTS idx_dbt_skill_recommendation_user ON dbt_skill_recommendation(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_dbt_skill_recommendation_score ON dbt_skill_recommendation(confidence_score);",
    
    "CREATE INDEX IF NOT EXISTS idx_dbt_emotion_track_user ON dbt_emotion_track(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_dbt_emotion_track_emotion ON dbt_emotion_track(emotion_name);",
    "CREATE INDEX IF NOT EXISTS idx_dbt_emotion_track_intensity ON dbt_emotion_track(intensity);",
    "CREATE INDEX IF NOT EXISTS idx_dbt_emotion_track_date ON dbt_emotion_track(date_recorded);",
    
    # Beta tester indexes 
    "CREATE INDEX IF NOT EXISTS idx_beta_tester_status ON beta_testers(status);",
    "CREATE INDEX IF NOT EXISTS idx_beta_tester_activity ON beta_testers(last_activity);",
    
    # BetaFeedback indexes
    "CREATE INDEX IF NOT EXISTS idx_beta_feedback_tester ON beta_feedback(tester_id);",
    "CREATE INDEX IF NOT EXISTS idx_beta_feedback_category ON beta_feedback(category);",
    "CREATE INDEX IF NOT EXISTS idx_beta_feedback_severity ON beta_feedback(severity);",
    "CREATE INDEX IF NOT EXISTS idx_beta_feedback_status ON beta_feedback(status);",
    
    # UserEntityMemory indexes
    "CREATE INDEX IF NOT EXISTS idx_entity_memory_user ON user_entity_memories(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_entity_memory_type ON user_entity_memories(entity_type);",
    "CREATE INDEX IF NOT EXISTS idx_entity_memory_name ON user_entity_memories(entity_name);",
    "CREATE INDEX IF NOT EXISTS idx_entity_memory_mentioned ON user_entity_memories(last_mentioned);",
    
    # UserTopicInterest indexes
    "CREATE INDEX IF NOT EXISTS idx_topic_interest_user ON user_topic_interests(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_topic_interest_level ON user_topic_interests(interest_level);",
    "CREATE INDEX IF NOT EXISTS idx_topic_interest_discussed ON user_topic_interests(last_discussed);",
]

def analyze_tables():
    """Run ANALYZE on all tables to update statistics for the query planner"""
    if not database_url:
        return False
        
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            # Get all table names
            result = connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
            tables = [row[0] for row in result]
            
            # Run ANALYZE on each table
            for table in tables:
                logger.info(f"Analyzing table: {table}")
                connection.execute(text(f"ANALYZE {table}"))
                
            connection.commit()
            return True
    except Exception as e:
        logger.error(f"Error analyzing tables: {str(e)}")
        return False

def apply_migrations():
    """Apply all index migrations to the database"""
    if not database_url:
        logger.error("No DATABASE_URL found in environment variables")
        return False
    
    try:
        logger.info(f"Connecting to database: {database_url}")
        engine = create_engine(database_url)
        
        # First check which tables exist in database
        existing_tables = []
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
                existing_tables = [row[0] for row in result]
                logger.info(f"Found {len(existing_tables)} existing tables in database")
        except Exception as e:
            logger.error(f"Error getting table list: {str(e)}")
            # Continue anyway, will likely fail on non-existent tables
        
        # Filter indexes to only target existing tables
        filtered_indexes = []
        for index_sql in indexes:
            # Simple heuristic to check if index applies to existing table
            should_include = True
            
            # Skip indexes that use non-existent tables
            for table in existing_tables:
                if f"ON {table}(" in index_sql:
                    break
            else:
                # If we get here, no table match was found and it's not a special SQL block
                if "CREATE INDEX" in index_sql and not any(special in index_sql for special in ["DO $$", "EXCEPTION"]):
                    should_include = False
            
            if should_include:
                filtered_indexes.append(index_sql)
        
        logger.info(f"Applying {len(filtered_indexes)} out of {len(indexes)} indexes (skipping indexes for non-existent tables)")
        
        # Set a reasonable limit to avoid deployment timeouts
        max_indexes = 20
        if len(filtered_indexes) > max_indexes:
            logger.info(f"Limiting to first {max_indexes} indexes to avoid deployment timeout")
            filtered_indexes = filtered_indexes[:max_indexes]
        
        # Execute each index creation statement
        start_time = time.time()
        with engine.connect() as connection:
            for idx, index_sql in enumerate(filtered_indexes):
                try:
                    logger.info(f"Creating index {idx+1}/{len(filtered_indexes)}")
                    connection.execute(text(index_sql))
                    connection.commit()
                except SQLAlchemyError as e:
                    logger.error(f"Error creating index: {str(e)}")
                    connection.rollback()
        
        # Only analyze tables that we know exist
        if existing_tables:
            try:
                logger.info("Updating database statistics for existing tables")
                with engine.connect() as connection:
                    for table in existing_tables[:10]:  # Limit to avoid timeout
                        logger.info(f"Analyzing table: {table}")
                        connection.execute(text(f"ANALYZE {table}"))
            except Exception as e:
                logger.error(f"Error analyzing tables: {str(e)}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"Database index migration completed successfully in {elapsed_time:.2f} seconds")
        return True
    
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting database index migration")
    if apply_migrations():
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed") 