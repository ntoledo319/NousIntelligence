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
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from utils.knowledge_helper import add_to_knowledge_base
from app import app, db
from models import KnowledgeBase, User

# Base directory for static knowledge files
STATIC_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / 'static'

def _load_static_json(filename: str) -> Dict:
    """Load a static JSON file from the static directory."""
    try:
        filepath = STATIC_DIR / filename
        if not filepath.exists():
            logging.error(f"Static file not found: {filepath}")
            return {}
        
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading static file {filename}: {str(e)}")
        return {}


def _store_knowledge_entries(entries: List[str], category: str) -> int:
    """
    Store multiple knowledge entries in the database.
    
    Args:
        entries: List of knowledge entry texts
        category: Category tag to add to each entry
        
    Returns:
        int: Number of entries successfully added
    """
    count = 0
    for entry in entries:
        if not entry.strip():
            continue
            
        # Add category tag to entry
        tagged_entry = f"{entry.strip()} [Category: {category}]"
        
        try:
            add_to_knowledge_base(tagged_entry, source=f"pre_downloaded/{category}")
            count += 1
            # Small delay to avoid overwhelming the API or database
            time.sleep(0.1)
        except Exception as e:
            logging.error(f"Error storing knowledge entry: {str(e)}")
            
    return count


def _download_basic_facts() -> int:
    """
    Download basic facts that are frequently requested.
    
    Returns:
        int: Number of entries added
    """
    # First check if we have a static file
    basic_facts = _load_static_json('temp_basic_facts.json')
    if basic_facts and isinstance(basic_facts, dict) and 'facts' in basic_facts:
        return _store_knowledge_entries(basic_facts['facts'], "basic_facts")
    
    # Otherwise, use a set of hard-coded basic facts that are commonly requested
    facts = [
        "The Earth is the third planet from the Sun in our solar system.",
        "Water boils at 100 degrees Celsius (212 degrees Fahrenheit) at sea level.",
        "The human body has 206 bones.",
        "The speed of light in a vacuum is approximately 299,792,458 meters per second.",
        "There are 24 hours in a day and 365 days in a standard year.",
        "The United States has 50 states.",
        "The tallest mountain on Earth is Mount Everest, at 8,848.86 meters (29,031.7 feet) above sea level.",
        "The human brain weighs about 3 pounds (1.4 kilograms).",
        "The Moon is approximately 238,855 miles (384,400 kilometers) away from Earth.",
        "DNA stands for deoxyribonucleic acid.",
        "The human body is made up of approximately 60% water.",
        "The Earth's atmosphere is composed of approximately 78% nitrogen, 21% oxygen, and 1% other gases.",
        "The coldest temperature theoretically possible is absolute zero, which is -273.15°C (-459.67°F).",
        "The Great Wall of China is approximately 13,171 miles (21,196 kilometers) long.",
        "The Amazon Rainforest produces about 20% of the Earth's oxygen.",
        "The average adult human body contains about 5 liters of blood.",
        "The Sahara Desert is the largest hot desert in the world, covering about 3.6 million square miles.",
        "The Pacific Ocean is the largest and deepest ocean on Earth.",
        "Sound travels at approximately 343 meters per second (1,125 feet per second) in air at room temperature.",
        "The human heart beats about 100,000 times per day."
    ]
    
    return _store_knowledge_entries(facts, "basic_facts")


def _download_health_information() -> int:
    """
    Download health information that is commonly requested.
    
    Returns:
        int: Number of entries added
    """
    health_info = [
        "Adults should aim for 7-9 hours of sleep per night for optimal health.",
        "The recommended daily water intake is about 3.7 liters (125 ounces) for men and 2.7 liters (91 ounces) for women, including water from all foods and beverages.",
        "Regular physical activity can help reduce the risk of chronic diseases like heart disease, type 2 diabetes, and some cancers.",
        "The CDC recommends at least 150 minutes of moderate-intensity aerobic activity or 75 minutes of vigorous activity each week, plus muscle-strengthening activities at least 2 days per week.",
        "A balanced diet includes a variety of fruits, vegetables, whole grains, lean proteins, and healthy fats.",
        "It's recommended to consume at least 5 servings of fruits and vegetables daily.",
        "High blood pressure (hypertension) is generally defined as blood pressure higher than 130/80 mm Hg.",
        "Normal resting heart rate for adults ranges from 60 to 100 beats per minute.",
        "Type 2 diabetes can often be prevented or delayed with healthy lifestyle changes like weight loss, regular physical activity, and a balanced diet.",
        "Mental health is as important as physical health and includes emotional, psychological, and social well-being.",
        "Vaccines help prevent serious illnesses by training your immune system to recognize and fight specific pathogens.",
        "Hand washing with soap and water for at least 20 seconds is one of the most effective ways to prevent the spread of infections.",
        "Sunscreen with at least SPF 30 should be applied daily to exposed skin, even on cloudy days, to help prevent skin cancer.",
        "Smoking is the leading preventable cause of death worldwide.",
        "Stress management techniques include deep breathing, meditation, physical activity, and maintaining social connections.",
        "Annual check-ups with your healthcare provider are important for preventative care and early detection of potential health issues.",
        "Dental health affects overall health, and it's recommended to brush teeth twice daily and floss once daily.",
        "Chronic inflammation in the body is linked to many health conditions including heart disease, diabetes, and arthritis.",
        "The Mediterranean diet, which emphasizes plant foods, fish, olive oil, and limited red meat, is associated with numerous health benefits.",
        "Maintaining a healthy weight reduces the risk of many conditions including heart disease, stroke, diabetes, and certain cancers."
    ]
    
    return _store_knowledge_entries(health_info, "health_information")

def _download_aa_principles() -> int:
    """
    Download AA principles, steps, and common recovery support information.
    
    Returns:
        int: Number of entries added
    """
    # Try to load from static file first
    aa_data = _load_static_json('aa_data/reflections.json')
    stored_count = 0
    
    # If we have reflections data, store them
    if aa_data and 'reflections' in aa_data:
        reflections = []
        for reflection in aa_data['reflections']:
            if 'prompt' in reflection:
                reflections.append(reflection['prompt'])
        if reflections:
            stored_count += _store_knowledge_entries(reflections, "aa_principles")
    
    # Add core AA principles and concepts
    aa_principles = [
        "The 12 Steps of AA provide a framework for recovery from alcoholism and addiction.",
        "Step 1: We admitted we were powerless over alcohol — that our lives had become unmanageable.",
        "Step 2: Came to believe that a Power greater than ourselves could restore us to sanity.",
        "Step 3: Made a decision to turn our will and our lives over to the care of God as we understood Him.",
        "Step 4: Made a searching and fearless moral inventory of ourselves.",
        "Step 5: Admitted to God, to ourselves, and to another human being the exact nature of our wrongs.",
        "Step 6: Were entirely ready to have God remove all these defects of character.",
        "Step 7: Humbly asked Him to remove our shortcomings.",
        "Step 8: Made a list of all persons we had harmed, and became willing to make amends to them all.",
        "Step 9: Made direct amends to such people wherever possible, except when to do so would injure them or others.",
        "Step 10: Continued to take personal inventory and when we were wrong promptly admitted it.",
        "Step 11: Sought through prayer and meditation to improve our conscious contact with God as we understood Him, praying only for knowledge of His will for us and the power to carry that out.",
        "Step 12: Having had a spiritual awakening as the result of these steps, we tried to carry this message to alcoholics, and to practice these principles in all our affairs.",
        "The Big Book of Alcoholics Anonymous serves as the basic text for AA.",
        "One day at a time is a core principle in recovery, focusing on staying sober just for today.",
        "Sponsorship involves a more experienced AA member guiding a newcomer through the recovery process.",
        "Regular meeting attendance is considered essential for maintaining sobriety in AA.",
        "The serenity prayer: 'God, grant me the serenity to accept the things I cannot change, courage to change the things I can, and wisdom to know the difference.'",
        "H.A.L.T. stands for Hungry, Angry, Lonely, Tired - common triggers for relapse that should be addressed.",
        "Making amends is the process of acknowledging harm done to others and taking action to repair relationships."
    ]
    
    # Add the hard-coded principles as well
    stored_count += _store_knowledge_entries(aa_principles, "aa_principles")
    return stored_count


def _download_mindfulness_exercises() -> int:
    """
    Download mindfulness exercises and techniques.
    
    Returns:
        int: Number of entries added
    """
    # Try to load from static file first
    mindfulness_data = _load_static_json('aa_data/mindfulness.json')
    if mindfulness_data and 'exercises' in mindfulness_data:
        exercises = []
        for exercise in mindfulness_data['exercises']:
            if 'instructions' in exercise:
                exercises.append(f"{exercise.get('name', 'Mindfulness Exercise')}: {exercise['instructions']}")
        if exercises:
            return _store_knowledge_entries(exercises, "mindfulness_exercises")
    
    # Default mindfulness exercises if file not found
    exercises = [
        "Body Scan: Lie down and focus your attention slowly from your feet to your head, noticing sensations without judgment.",
        "Mindful Breathing: Focus on your breath, noticing the sensation of air moving in and out of your body.",
        "Five Senses Exercise: Notice five things you can see, four things you can touch, three things you can hear, two things you can smell, and one thing you can taste.",
        "Mindful Walking: While walking, pay attention to the sensation of your feet touching the ground, your breath, and your surroundings.",
        "Mindful Eating: Eat slowly, paying attention to the taste, texture, and smell of your food.",
        "Loving-Kindness Meditation: Direct positive wishes and goodwill to yourself and others.",
        "3-Minute Breathing Space: Observe your thoughts and feelings, focus on your breath, and expand awareness to your whole body.",
        "Mindful Observation: Choose a natural object and focus on it for five minutes, observing it as if seeing it for the first time.",
        "Mindful Listening: Close your eyes and notice all the sounds around you without labeling or judging them.",
        "Mindful Movement: Perform gentle stretches or yoga poses while focusing on bodily sensations and breath."
    ]
    
    return _store_knowledge_entries(exercises, "mindfulness_exercises")


def _download_dbt_skills() -> int:
    """
    Download Dialectical Behavior Therapy skills and concepts.
    
    Returns:
        int: Number of entries added
    """
    dbt_skills = [
        "DBT (Dialectical Behavior Therapy) is a type of cognitive-behavioral therapy that helps people manage difficult emotions and improve relationships.",
        "DBT is based on four modules: mindfulness, distress tolerance, emotion regulation, and interpersonal effectiveness.",
        "Mindfulness in DBT involves being fully aware and present in the moment without judgment.",
        "Wise Mind is a DBT concept representing the integration of emotional mind and reasonable mind.",
        "STOP skill: Stop, Take a step back, Observe, Proceed mindfully - used to prevent impulsive reactions in emotional situations.",
        "PLEASE skill: treat PhysicaL illness, Eat healthy, Avoid mood-altering drugs, Sleep well, Exercise - taking care of physical health to improve emotional health.",
        "DEAR MAN: a DBT interpersonal effectiveness skill for making requests assertively (Describe, Express, Assert, Reinforce, stay Mindful, Appear confident, Negotiate).",
        "GIVE skill: (Gentle, Interested, Validate, Easy manner) - for maintaining relationships while addressing problems.",
        "FAST skill: (Fair, no Apologies, Stick to values, Truthful) - for maintaining self-respect in relationships.",
        "Radical acceptance in DBT means completely accepting reality as it is, not as you wish it to be.",
        "The TIPP skill (Temperature, Intense exercise, Paced breathing, Progressive muscle relaxation) helps manage overwhelming emotions.",
        "Emotion regulation in DBT involves identifying, understanding, and changing emotional responses.",
        "Opposite action is a DBT technique where you act opposite to the urge associated with a negative emotion.",
        "Distress tolerance skills help you cope with painful events when you cannot make things better right away.",
        "Interpersonal effectiveness in DBT focuses on maintaining relationships and self-respect while achieving goals.",
        "Self-soothing using the five senses is a distress tolerance skill to comfort yourself during emotional distress.",
        "Checking the facts is a DBT technique to examine if your emotional response matches the situation.",
        "The ABC PLEASE skill adds: Accumulate positive emotions, Build mastery, Cope ahead to the basic PLEASE skill.",
        "Chain analysis is a DBT technique to break down a problem behavior to understand what triggers and maintains it.",
        "Willingness vs. willfulness: willingness means accepting reality and responding effectively; willfulness means refusing to accept reality."
    ]
    
    return _store_knowledge_entries(dbt_skills, "dbt_skills")


def _download_grounding_exercises() -> int:
    """
    Download grounding exercises for managing anxiety and crisis situations.
    
    Returns:
        int: Number of entries added
    """
    grounding_exercises = [
        "5-4-3-2-1 Technique: Acknowledge 5 things you see, 4 things you feel, 3 things you hear, 2 things you smell, and 1 thing you taste.",
        "Deep Breathing: Breathe in slowly for 4 counts, hold for 4 counts, exhale for 6 counts. Repeat 5-10 times.",
        "The 3-3-3 Rule: Name 3 things you see, 3 things you hear, and move 3 parts of your body.",
        "Physical Grounding: Feel your feet on the ground, your back against the chair, or hold a piece of ice in your hand.",
        "Category Game: Pick a category (like 'fruits' or 'countries') and name as many items as you can in that category.",
        "Body Awareness: Tense and then relax each muscle group, starting from toes and working upward.",
        "Describe Your Environment: Describe your surroundings in detail, focusing on colors, textures, and shapes.",
        "Mental Math: Count backward from 100 by 7s or solve simple math problems in your head.",
        "Name Game: Work through the alphabet naming animals, cities, or foods that start with each letter.",
        "Object Focus: Hold an object and focus on its weight, texture, temperature, and other physical properties.",
        "Rhythmic Movement: Tap your feet, clap your hands, or rock gently while counting.",
        "Cold Water: Splash cold water on your face or hold a cold pack to your forehead to activate the diving reflex.",
        "Affirmations: Repeat calming statements like 'I am safe', 'This feeling will pass', or 'I am grounded'.",
        "Color Identification: Look around and identify all objects of a specific color, then move to another color.",
        "Orientation: Tell yourself your name, the date, where you are, and why you're there.",
        "Guided Imagery: Imagine a safe, peaceful place in detail, engaging all your senses.",
        "Progressive Muscle Relaxation: Tense and relax each muscle group for 5 seconds, moving from feet to head.",
        "Focus on a Single Task: Engage in a simple activity like counting backward, reciting a poem, or singing a song.",
        "Mindful Walking: Walk slowly, paying attention to each step and the sensation of your feet touching the ground.",
        "Hand Temperature: Focus on warming or cooling your hands by imagining them in warm water or snow."
    ]
    
    return _store_knowledge_entries(grounding_exercises, "grounding_exercises")


# Categories of knowledge that are worth pre-caching
KNOWLEDGE_CATEGORIES = [
    # General Knowledge
    "basic_facts",
    
    # Health & Medical
    "health_information",
    "medication_info",
    "medical_procedures",
    "dbt_skills",             # Dialectical Behavior Therapy
    "crisis_resources",
    "grounding_exercises",
    "emotional_regulation",
    
    # Practical & Daily Life
    "common_procedures",
    "shopping_tips",
    "budgeting_principles",
    "product_information",
    
    # Emergency & Safety
    "emergency_protocols",
    
    # Travel & Location
    "weather_patterns",
    "travel_guidelines",
    "packing_essentials",
    
    # Recovery Support
    "aa_principles",
    "mindfulness_exercises", 
    "reflection_prompts",
    "spot_check_questions",
    
    # Technology & Integration
    "google_api_guides",
    "spotify_features",
    "smart_home_setup",
    
    # Doctor & Medication 
    "appointment_types",
    "medication_reminders",
    
    # Specialized User Interfaces
    "voice_interaction_tips",
    "accessibility_features"
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
    
    # General Knowledge
    if category == "basic_facts":
        entries_added = _download_basic_facts()
    
    # Health & Medical
    elif category == "health_information":
        entries_added = _download_health_information()
    elif category == "dbt_skills":
        entries_added = _download_dbt_skills()
    elif category == "grounding_exercises":
        entries_added = _download_grounding_exercises()
    
    # Recovery Support
    elif category == "aa_principles":
        entries_added = _download_aa_principles()
    elif category == "mindfulness_exercises":
        entries_added = _download_mindfulness_exercises()
    
    # Implementation for other categories would follow the same pattern
    # For now, we're focusing on the essential ones with the highest payoff
    else:
        logging.info(f"Category {category} not implemented yet, skipping")
        
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