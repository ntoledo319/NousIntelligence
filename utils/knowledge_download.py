"""
Knowledge download utility to pre-fetch and store frequently accessed information.
This reduces API calls and improves response time for common queries.
"""

import os
import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from utils.knowledge_helper import add_to_knowledge_base
from app import app, db
from models import KnowledgeBase, User

# Categories of knowledge that are worth pre-caching
KNOWLEDGE_CATEGORIES = [
    "basic_facts",
    "health_information",
    "common_procedures",
    "medication_info",
    "emergency_protocols",
    "weather_patterns",
    "travel_guidelines",
    "shopping_tips"
]

def download_and_store_knowledge(category: str, force_refresh: bool = False) -> int:
    """
    Download and store knowledge for a specific category.
    
    Args:
        category: The category of knowledge to download
        force_refresh: Whether to force refresh existing knowledge
        
    Returns:
        int: Number of knowledge entries added
    """
    logging.info(f"Downloading knowledge for category: {category}")
    
    # Check if category already exists in database
    if not force_refresh:
        existing_count = KnowledgeBase.query.filter(
            KnowledgeBase.content.like(f"%[Category: {category}]%")
        ).count()
        
        if existing_count > 0:
            logging.info(f"Category {category} already has {existing_count} entries, skipping")
            return 0
    
    # Different sources for different categories
    entries_added = 0
    
    if category == "basic_facts":
        entries_added = _download_basic_facts()
    elif category == "health_information":
        entries_added = _download_health_information()
    elif category == "common_procedures":
        entries_added = _download_common_procedures()
    elif category == "medication_info":
        entries_added = _download_medication_info()
    elif category == "emergency_protocols":
        entries_added = _download_emergency_protocols()
    elif category == "weather_patterns":
        entries_added = _download_weather_patterns()
    elif category == "travel_guidelines":
        entries_added = _download_travel_guidelines()
    elif category == "shopping_tips":
        entries_added = _download_shopping_tips()
    else:
        logging.warning(f"Unknown category: {category}")
        
    logging.info(f"Added {entries_added} knowledge entries for category {category}")
    return entries_added

def _add_from_json_file(filename: str, category: str) -> int:
    """
    Add knowledge entries from a JSON file.
    
    Args:
        filename: Path to the JSON file
        category: Category to tag entries with
        
    Returns:
        int: Number of entries added
    """
    if not os.path.exists(filename):
        logging.error(f"File not found: {filename}")
        return 0
        
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            
        count = 0
        for item in data:
            # Format the content to include the category
            if 'content' in item:
                content = f"{item['content']}\n[Category: {category}]"
                
                # Add to knowledge base
                entry = add_to_knowledge_base(
                    content=content,
                    user_id=None,  # Global knowledge
                    source="downloaded"
                )
                
                if entry:
                    count += 1
                    
        return count
    except Exception as e:
        logging.error(f"Error adding knowledge from file {filename}: {str(e)}")
        return 0

def _download_basic_facts() -> int:
    """Download and store basic facts."""
    # For demonstration, we'll create some basic facts directly
    facts = [
        {
            "content": "The Earth is the third planet from the Sun and the only astronomical object known to harbor life."
        },
        {
            "content": "Water boils at 100 degrees Celsius (212 degrees Fahrenheit) at sea level."
        },
        {
            "content": "There are 24 hours in a day, divided into AM (ante meridiem) and PM (post meridiem)."
        },
        {
            "content": "The average adult human body contains about 60% water."
        },
        {
            "content": "The four basic tastes are sweet, sour, salty, and bitter. A fifth taste, umami, is also recognized."
        },
        {
            "content": "A year on Earth is approximately 365.25 days, which is why we have leap years."
        },
        {
            "content": "The primary colors of light are red, green, and blue. The primary colors of pigment are cyan, magenta, yellow, and black."
        },
        {
            "content": "The human body has 206 bones."
        },
        {
            "content": "The distance between the Earth and the Sun is approximately 93 million miles (150 million kilometers)."
        },
        {
            "content": "Sound travels at approximately 343 meters per second (1,125 feet per second) in air at room temperature."
        }
    ]
    
    # Write to a temporary JSON file
    temp_file = "static/temp_basic_facts.json"
    with open(temp_file, 'w') as f:
        json.dump(facts, f)
        
    # Add from the file
    count = _add_from_json_file(temp_file, "basic_facts")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return count

def _download_health_information() -> int:
    """Download and store health information."""
    health_info = [
        {
            "content": "Regular physical activity can reduce the risk of chronic diseases such as heart disease, type 2 diabetes, and some cancers."
        },
        {
            "content": "Adults should aim for at least 150 minutes of moderate-intensity aerobic activity or 75 minutes of vigorous activity each week."
        },
        {
            "content": "A balanced diet should include fruits, vegetables, whole grains, lean proteins, and healthy fats."
        },
        {
            "content": "The normal resting heart rate for adults is between 60 and 100 beats per minute."
        },
        {
            "content": "Normal blood pressure is less than 120/80 mm Hg. Hypertension is defined as blood pressure above 130/80 mm Hg."
        },
        {
            "content": "Common signs of dehydration include thirst, dry mouth, dark urine, fatigue, dizziness, and headache."
        },
        {
            "content": "Adults should sleep 7-9 hours per night for optimal health."
        },
        {
            "content": "Washing hands with soap and water for at least 20 seconds helps prevent the spread of germs and infections."
        },
        {
            "content": "Vaccinations are an important part of preventive healthcare and can protect against serious diseases."
        },
        {
            "content": "Mental health is as important as physical health. Regular self-care and seeking help when needed are essential for wellbeing."
        }
    ]
    
    # Write to a temporary JSON file
    temp_file = "static/temp_health_info.json"
    with open(temp_file, 'w') as f:
        json.dump(health_info, f)
        
    # Add from the file
    count = _add_from_json_file(temp_file, "health_information")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return count

def _download_common_procedures() -> int:
    """Download and store common procedures."""
    procedures = [
        {
            "content": "How to check blood pressure: Sit with back supported and feet flat on the floor. Rest your arm on a table at heart level. Use a properly calibrated and validated blood pressure monitor. Measure at the same time each day."
        },
        {
            "content": "How to administer CPR: Call emergency services first. Place the person on their back on a firm surface. Place your hands one over the other in the center of the chest. Push hard and fast at a rate of 100-120 compressions per minute. Continue until help arrives."
        },
        {
            "content": "How to use an EpiPen: Remove the blue safety cap. Hold with the orange tip pointing downward. Swing and firmly push the orange tip against the outer thigh until it clicks. Hold for 3 seconds. Call emergency services after use."
        },
        {
            "content": "How to check blood sugar levels: Wash and dry hands thoroughly. Insert test strip into meter. Use lancet to prick the side of fingertip. Touch and hold the edge of the test strip to the drop of blood. Read and record results."
        },
        {
            "content": "How to clean and dress a wound: Wash hands thoroughly. Rinse the wound under clean running water. Clean around the wound with mild soap. Apply antibiotic ointment if appropriate. Cover with a sterile bandage or dressing."
        }
    ]
    
    # Write to a temporary JSON file
    temp_file = "static/temp_procedures.json"
    with open(temp_file, 'w') as f:
        json.dump(procedures, f)
        
    # Add from the file
    count = _add_from_json_file(temp_file, "common_procedures")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return count

def _download_medication_info() -> int:
    """Download and store medication information."""
    medications = [
        {
            "content": "Acetaminophen (Tylenol): Used for pain relief and fever reduction. Common side effects can include nausea, stomach pain, and rash. Do not exceed recommended doses as it can cause liver damage."
        },
        {
            "content": "Ibuprofen (Advil, Motrin): Non-steroidal anti-inflammatory drug (NSAID) used for pain, fever, and inflammation. Side effects can include stomach upset, heartburn, and dizziness. Take with food to minimize stomach issues."
        },
        {
            "content": "Amoxicillin: Antibiotic used to treat bacterial infections. Common side effects include diarrhea, stomach pain, and rash. Complete the full prescribed course even if symptoms improve."
        },
        {
            "content": "Lisinopril: ACE inhibitor used to treat high blood pressure and heart failure. Side effects can include dry cough, dizziness, and headache. May cause high potassium levels."
        },
        {
            "content": "Metformin: First-line medication for type 2 diabetes. Common side effects include gastrointestinal issues like nausea and diarrhea. Take with meals to reduce these effects."
        }
    ]
    
    # Write to a temporary JSON file
    temp_file = "static/temp_medications.json"
    with open(temp_file, 'w') as f:
        json.dump(medications, f)
        
    # Add from the file
    count = _add_from_json_file(temp_file, "medication_info")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return count

def _download_emergency_protocols() -> int:
    """Download and store emergency protocols."""
    protocols = [
        {
            "content": "Fire Emergency: Alert others by yelling 'Fire!' Pull the fire alarm if available. Call emergency services. If the fire is small and you know how to use an extinguisher, you may attempt to put it out. Otherwise, evacuate immediately using stairs, not elevators. Stay low if there's smoke."
        },
        {
            "content": "Severe Weather: Monitor weather reports. For tornadoes, go to an interior room on the lowest floor without windows. For hurricanes, follow evacuation orders or shelter in place away from windows. For flash floods, move to higher ground immediately."
        },
        {
            "content": "Medical Emergency: Call emergency services immediately. Provide your location and describe the emergency. Follow dispatcher instructions. Send someone to meet emergency responders if possible. If trained, provide appropriate first aid until help arrives."
        },
        {
            "content": "Active Shooter: Run: Evacuate if there is an accessible path. Leave belongings behind. Help others if possible. Hide: If you can't evacuate, find a place to hide out of view, lock/barricade doors, silence phones. Fight: As a last resort, attempt to incapacitate the shooter."
        },
        {
            "content": "Earthquake: Drop, Cover, and Hold On. Drop to the ground, take cover under a sturdy table or desk, and hold on until the shaking stops. Stay away from windows, exterior walls, and anything that could fall. After shaking stops, evacuate to an open area away from buildings."
        }
    ]
    
    # Write to a temporary JSON file
    temp_file = "static/temp_emergency.json"
    with open(temp_file, 'w') as f:
        json.dump(protocols, f)
        
    # Add from the file
    count = _add_from_json_file(temp_file, "emergency_protocols")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return count

def _download_weather_patterns() -> int:
    """Download and store weather patterns information."""
    weather_info = [
        {
            "content": "High pressure systems typically bring fair weather with clear skies and light winds. Barometric pressure above 1013.2 millibars (29.92 inches of mercury) is considered high pressure."
        },
        {
            "content": "Low pressure systems often bring clouds, precipitation, and sometimes stormy conditions. Falling barometric pressure can indicate approaching storms or changing weather."
        },
        {
            "content": "Cumulonimbus clouds (thunderheads) indicate potential for thunderstorms, heavy rain, lightning, and occasionally tornadoes. These tall, anvil-shaped clouds can reach heights of 60,000 feet."
        },
        {
            "content": "A sudden drop in temperature and pressure, along with dark, greenish skies and a wall cloud, may indicate an approaching tornado in severe weather."
        },
        {
            "content": "Weather forecasting combines observations, computer models, and meteorological principles to predict future weather conditions. Modern forecasts are generally accurate for 5-7 days out."
        }
    ]
    
    # Write to a temporary JSON file
    temp_file = "static/temp_weather.json"
    with open(temp_file, 'w') as f:
        json.dump(weather_info, f)
        
    # Add from the file
    count = _add_from_json_file(temp_file, "weather_patterns")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return count

def _download_travel_guidelines() -> int:
    """Download and store travel guidelines information."""
    travel_info = [
        {
            "content": "Passport validity: Many countries require that your passport be valid for at least 6 months beyond your planned stay. Check specific country requirements before traveling."
        },
        {
            "content": "Travel insurance can cover medical emergencies, trip cancellations, lost luggage, and other unexpected issues. Consider purchasing comprehensive coverage for international trips."
        },
        {
            "content": "When traveling internationally, check visa requirements well in advance. Processing times can range from a few days to several months depending on the country."
        },
        {
            "content": "Keep digital and physical copies of important documents such as passports, visas, insurance policies, and emergency contacts. Store them separately from the originals."
        },
        {
            "content": "Register with your country's embassy or consulate when traveling to high-risk or remote areas. This helps them contact you in case of emergency or natural disaster."
        }
    ]
    
    # Write to a temporary JSON file
    temp_file = "static/temp_travel.json"
    with open(temp_file, 'w') as f:
        json.dump(travel_info, f)
        
    # Add from the file
    count = _add_from_json_file(temp_file, "travel_guidelines")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return count

def _download_shopping_tips() -> int:
    """Download and store shopping tips information."""
    shopping_info = [
        {
            "content": "Create a shopping list before going to the store to avoid impulse purchases and ensure you get everything you need."
        },
        {
            "content": "Compare prices per unit (price per ounce, pound, etc.) rather than package price to determine the best value."
        },
        {
            "content": "Seasonal produce is often less expensive and better quality than out-of-season items."
        },
        {
            "content": "Many stores mark down prices on perishable items like meat and bread in the evening as they approach their sell-by dates."
        },
        {
            "content": "Store loyalty programs, cashback apps, and digital coupons can provide significant savings over time."
        }
    ]
    
    # Write to a temporary JSON file
    temp_file = "static/temp_shopping.json"
    with open(temp_file, 'w') as f:
        json.dump(shopping_info, f)
        
    # Add from the file
    count = _add_from_json_file(temp_file, "shopping_tips")
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return count

def download_all_knowledge(force_refresh: bool = False) -> Dict[str, int]:
    """
    Download and store all categories of knowledge.
    
    Args:
        force_refresh: Whether to force refresh existing knowledge
        
    Returns:
        Dict[str, int]: Number of entries added per category
    """
    results = {}
    
    for category in KNOWLEDGE_CATEGORIES:
        entries_added = download_and_store_knowledge(category, force_refresh)
        results[category] = entries_added
        # Add a small delay to avoid database contention
        time.sleep(0.5)
        
    total_added = sum(results.values())
    logging.info(f"Added a total of {total_added} knowledge entries across all categories")
    
    return results

def search_knowledge_by_category(category: str, query: str = None, limit: int = 10) -> List[Dict]:
    """
    Search for knowledge entries in a specific category.
    
    Args:
        category: The category to search in
        query: Optional search terms
        limit: Maximum number of results
        
    Returns:
        List of knowledge entries as dictionaries
    """
    with app.app_context():
        base_query = KnowledgeBase.query.filter(
            KnowledgeBase.content.like(f"%[Category: {category}]%")
        )
        
        if query:
            search_terms = [f"%{term}%" for term in query.split()]
            for term in search_terms:
                base_query = base_query.filter(KnowledgeBase.content.like(term))
                
        entries = base_query.limit(limit).all()
        
        return [
            {
                'id': entry.id,
                'content': entry.content.replace(f"[Category: {category}]", "").strip(),
                'created_at': entry.created_at.isoformat() if entry.created_at else None
            }
            for entry in entries
        ]

if __name__ == "__main__":
    # When run directly, download all knowledge
    with app.app_context():
        download_all_knowledge()