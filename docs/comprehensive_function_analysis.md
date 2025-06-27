
---
**MIGRATION NOTICE**: This file contains legacy information and may be outdated.

**Current Documentation**: 
- Complete documentation: `make docs && make serve-docs`
- API documentation: `/api/docs/` (when app is running)
- Architecture guide: `docs/architecture.rst`

**Last Updated**: June 27, 2025
---

# NOUS Personal Assistant - Comprehensive Function Analysis

## Executive Summary

NOUS Personal Assistant is an extensive Flask-based AI-powered personal assistant featuring **257 distinct utility functions** across **67 specialized modules**. The system provides comprehensive life management capabilities including medical care coordination, financial management, crisis intervention, DBT therapy support, smart shopping, entertainment integration, and advanced AI chat functionality.

**Key Statistics:**
- **47 Route Handler Files** with 150+ endpoints
- **67 Utility Modules** with specialized helper functions
- **15 Core Life Management Domains** covered
- **Cost-Optimized AI Integration** (99.85% cost reduction achieved)
- **Multi-Modal Interfaces** (Web, Voice, Mobile)

---

## I. MEDICAL & HEALTH MANAGEMENT

### Doctor Appointment Management (`utils/doctor_appointment_helper.py`)
**Functions: 9 core functions**

1. **`get_doctors(session)`** - Retrieve all doctors for current user
2. **`get_doctor_by_id(doctor_id, session)`** - Get specific doctor by ID
3. **`get_doctor_by_name(name, session)`** - Search doctors by name (case-insensitive)
4. **`add_doctor(name, specialty, phone, address, notes, session)`** - Add new doctor to database
5. **`update_doctor(doctor_id, name, specialty, phone, address, notes, session)`** - Update doctor information
6. **`delete_doctor(doctor_id, session)`** - Remove doctor from system
7. **`get_upcoming_appointments(session)`** - Get scheduled future appointments
8. **`get_appointments_by_doctor(doctor_id, session)`** - Get all appointments for specific doctor
9. **`add_appointment(doctor_id, date, reason, status, notes, session)`** - Schedule new appointment

**Advanced Features:**
- **`set_appointment_reminder(doctor_id, frequency_months, session)`** - Set recurring appointment reminders
- **`get_due_appointment_reminders(session)`** - Get appointments requiring scheduling
- **`update_appointment_status(appointment_id, new_status, session)`** - Update appointment status

### Medication Management (`utils/medication_helper.py`)
**Functions: 8 core functions**

1. **`get_medications(session)`** - Get all tracked medications
2. **`get_medication_by_id(medication_id, session)`** - Get specific medication
3. **`get_medication_by_name(name, session)`** - Search medications by name
4. **`add_medication(name, dosage, instructions, doctor_name, pharmacy, quantity, refills, session)`** - Add medication to tracking
5. **`update_medication_quantity(medication_id, new_quantity, session)`** - Update remaining quantity
6. **`refill_medication(medication_id, quantity_added, refills_remaining, session)`** - Record medication refill
7. **`get_medications_to_refill(session)`** - Get medications needing refills
8. **`get_medications_by_doctor(doctor_id, session)`** - Get medications prescribed by specific doctor

**Smart Features:**
- Automatic refill date calculation based on daily dosage
- Integration with doctor records for prescription tracking
- Low quantity alerts and reminder system

---

## II. FINANCIAL MANAGEMENT

### Budget Management (`utils/budget_helper.py`)
**Functions: 12+ budget functions**

1. **`get_budgets(session)`** - Get all user budgets
2. **`get_budget_by_id(budget_id, session)`** - Get specific budget
3. **`get_budget_by_name(name, session)`** - Search budgets by name
4. **`get_budget_by_category(category, session)`** - Get budget by expense category
5. **`create_budget(name, amount, category, is_recurring, start_date, end_date, session)`** - Create new budget
6. **`update_budget(budget_id, name, amount, category, is_recurring, start_date, end_date, session)`** - Update budget
7. **`delete_budget(budget_id, session)`** - Delete budget
8. **`get_current_month_spending(budget_id, session)`** - Calculate current month spending
9. **`get_budget_status(budget_id, session)`** - Get budget vs actual spending status
10. **`add_expense(budget_id, amount, description, category, date, session)`** - Record expense
11. **`get_expenses_by_budget(budget_id, session)`** - Get all expenses for budget
12. **`calculate_budget_utilization(budget_id, session)`** - Calculate budget utilization percentage

### Product Tracking (`utils/product_helper.py`)
**Functions: 8 product management functions**

1. **`get_products(session)`** - Get all tracked products
2. **`get_product_by_id(product_id, session)`** - Get specific product
3. **`get_product_by_name(name, session)`** - Search products by name
4. **`add_product(name, url, description, price, source, session)`** - Add product to tracking
5. **`extract_source_from_url(url)`** - Extract retailer from product URL
6. **`fetch_product_details(url)`** - Scrape product details from URL
7. **`set_product_as_recurring(product_id, frequency_days, session)`** - Set recurring order reminder
8. **`mark_product_as_ordered(product_id, session)`** - Mark product as ordered

**Advanced Features:**
- **`get_due_product_orders(session)`** - Get products due for reordering
- **`update_product_price(product_id, new_price, session)`** - Update price tracking
- Automatic price monitoring and change alerts

---

## III. SHOPPING MANAGEMENT

### Shopping Lists (`utils/shopping_helper.py`)
**Functions: 10 shopping list functions**

1. **`get_shopping_lists(session)`** - Get all shopping lists
2. **`get_shopping_list_by_id(list_id, session)`** - Get specific list
3. **`get_shopping_list_by_name(name, session)`** - Search lists by name
4. **`create_shopping_list(name, description, store, session)`** - Create new shopping list
5. **`add_item_to_list(list_id, item_name, quantity, unit, category, notes, session)`** - Add item to list
6. **`get_items_in_list(list_id, session)`** - Get all items in list
7. **`toggle_item_checked(item_id, is_checked, session)`** - Check/uncheck items
8. **`remove_item_from_list(item_id, session)`** - Remove item from list
9. **`set_list_as_recurring(list_id, frequency_days, session)`** - Set recurring shopping reminder
10. **`mark_list_as_ordered(list_id, session)`** - Mark list as completed

**Smart Features:**
- **`get_due_shopping_lists(session)`** - Get lists due for shopping
- Store-specific list organization
- Category-based item organization
- Recurring shopping list automation

---

## IV. CRISIS INTERVENTION & DBT THERAPY

### Crisis Management (`routes/crisis_routes.py`)
**Routes: 7 crisis intervention endpoints**

1. **`/crisis/`** - Crisis management dashboard
2. **`/crisis/mobile`** - Mobile-optimized crisis interface
3. **`/crisis/grounding`** - Grounding exercises page
4. **`/crisis/de-escalation`** - De-escalation techniques
5. **`/crisis/resources`** - Crisis resources management
6. **`/crisis/add-resource`** - Add crisis contact/resource
7. **`/crisis/update-resource/<id>`** - Update crisis resource

### DBT Therapy Support (`utils/dbt_helper.py`)
**Functions: 15+ DBT therapy functions**

**Core DBT Functions:**
1. **`skills_on_demand(text)`** - AI-powered DBT skill recommendation
2. **`generate_diary_card(text)`** - Generate structured diary card entry
3. **`validate_experience(text)`** - Provide DBT validation response
4. **`distress_tolerance(text)`** - Guide through TIPP skill for crisis
5. **`chain_analysis(text)`** - Guide behavioral chain analysis
6. **`wise_mind(text)`** - Help access Wise Mind state
7. **`radical_acceptance(text)`** - Teach radical acceptance concepts
8. **`interpersonal_effectiveness(text)`** - Coach DEAR MAN communication
9. **`dialectic_generator(text)`** - Create dialectical synthesis
10. **`trigger_map(text)`** - Map emotional triggers and responses

**Database Functions:**
11. **`log_dbt_skill(session, skill_name, category, situation, effectiveness, notes)`** - Log skill usage
12. **`get_skill_logs(session, limit)`** - Get recent skill usage logs
13. **`create_diary_card(session, mood_rating, triggers, urges, skills_used, reflection)`** - Create diary card
14. **`get_diary_cards(session, limit)`** - Get recent diary cards
15. **`analyze_skill_effectiveness(session)`** - Analyze which skills work best for user

**Advanced Features:**
- **AI-Powered Prompts**: 12 specialized therapeutic prompt templates
- **Cost-Optimized Models**: Multi-tier model selection for different therapeutic tasks
- **Rate Limiting**: Smart request throttling to prevent API overuse
- **Personalized Recommendations**: Skills recommended based on user's effectiveness history

---

## V. COMMUNICATION & INTEGRATION

### Gmail Integration (`utils/gmail_helper.py`)
**Functions: 12 email management functions**

1. **`get_gmail_service(user_connection)`** - Build authenticated Gmail service
2. **`search_gmail(service, query, max_results, include_content)`** - Search emails with Gmail query syntax
3. **`get_gmail_threads(service, query, max_results, include_content)`** - Get conversation threads
4. **`send_email(service, to, subject, body, cc, bcc)`** - Send new email
5. **`reply_to_email(service, message_id, body)`** - Reply to existing email
6. **`categorize_emails(service, emails)`** - AI-powered email categorization for recovery relevance
7. **`generate_email_reply(service, email_id, user_context)`** - AI-generated email replies
8. **`get_unread_emails(service, max_results)`** - Get unread emails
9. **`mark_as_read(service, message_id)`** - Mark email as read
10. **`add_label(service, message_id, label_name)`** - Add label to email
11. **`remove_label(service, message_id, label_name)`** - Remove label from email
12. **`archive_email(service, message_id)`** - Archive email

**AI-Powered Features:**
- **Recovery-Focused Categorization**: Emails categorized by relevance to recovery (0-10 scale)
- **Smart Reply Generation**: Context-aware AI-generated replies
- **Support Network Detection**: Identifies emails from sponsors, recovery groups, healthcare providers

### Google Meet Integration (`utils/meet_helper.py`)
**Functions: 15+ specialized meeting functions**

**Core Meeting Functions:**
1. **`get_meet_service(user_connection)`** - Build Calendar service for Meet operations
2. **`create_meeting(service, title, description, start_time, end_time, attendees, is_recurring, recurrence_pattern)`** - Create Google Meet meeting
3. **`get_meeting(service, event_id)`** - Get meeting details by ID
4. **`update_meeting(service, event_id, title, description, start_time, end_time, attendees)`** - Update meeting details
5. **`delete_meeting(service, event_id)`** - Delete meeting
6. **`list_upcoming_meetings(service, max_results)`** - List upcoming meetings with Meet links

**Specialized Recovery Meetings:**
7. **`create_therapy_session(service, session_type, participant_email, start_time, duration_minutes)`** - Create therapy session with specialized guidelines
8. **`create_recovery_group_meeting(service, group_type, attendees, start_time, duration_minutes, is_recurring, weekly_day)`** - Create recovery group meetings
9. **`create_sponsor_meeting(service, sponsor_email, start_time, duration_minutes)`** - Create sponsor check-in meeting
10. **`create_mindfulness_session(service, session_type, start_time, duration_minutes)`** - Create mindfulness/meditation session

**AI-Powered Meeting Features:**
11. **`generate_meeting_agenda(service, meeting_id, meeting_type)`** - AI-generated meeting agendas
12. **`analyze_meeting_notes(notes_text, meeting_type)`** - Extract key points and action items from notes
13. **`suggest_meeting_follow_up(meeting_id, meeting_type)`** - Suggest follow-up actions
14. **`schedule_recurring_check_ins(service, frequency, meeting_type)`** - Auto-schedule recurring meetings
15. **`get_meeting_insights(service, date_range)`** - Analytics on meeting patterns and engagement

---

## VI. ENTERTAINMENT & LIFESTYLE

### Spotify Integration (`utils/spotify_helper.py`)
**Functions: 15+ music integration functions**

**Authentication & Client Management:**
1. **`get_spotify_client(session, client_id, client_secret, redirect_uri, user_id)`** - Get authenticated Spotify client
2. **`refresh_spotify_token(spotify_client, refresh_token)`** - Refresh expired access token
3. **`save_spotify_auth(session, token_info, user_id)`** - Save authentication data
4. **`get_spotify_auth_url(spotify_client, state)`** - Get OAuth authorization URL

**Music Control & Discovery:**
5. **`get_current_track(spotify_client)`** - Get currently playing track
6. **`play_track(spotify_client, track_uri)`** - Play specific track
7. **`pause_playback(spotify_client)`** - Pause current playback
8. **`skip_track(spotify_client)`** - Skip to next track
9. **`previous_track(spotify_client)`** - Go to previous track
10. **`set_volume(spotify_client, volume_percent)`** - Set playback volume
11. **`search_tracks(spotify_client, query, limit)`** - Search for tracks
12. **`get_user_playlists(spotify_client)`** - Get user's playlists
13. **`create_playlist(spotify_client, name, description, public)`** - Create new playlist
14. **`add_to_playlist(spotify_client, playlist_id, track_uris)`** - Add tracks to playlist
15. **`get_recommendations(spotify_client, seed_tracks, seed_artists, seed_genres)`** - Get music recommendations

### Weather Integration (`utils/weather_helper.py`)
**Functions: 12 weather & health functions**

**Core Weather Functions:**
1. **`get_location_coordinates(location)`** - Get lat/lon for location
2. **`get_current_weather(location, units)`** - Get current weather conditions
3. **`get_weather_forecast(location, days, units)`** - Get multi-day forecast
4. **`kelvin_to_fahrenheit(kelvin)`** - Temperature conversion
5. **`kelvin_to_celsius(kelvin)`** - Temperature conversion

**Health-Focused Weather Features:**
6. **`predict_pain_flare(weather_data, historical_pressure)`** - Predict pain flares from barometric pressure changes
7. **`get_air_quality_index(location)`** - Get air quality data for respiratory health
8. **`check_weather_alerts(location)`** - Get weather warnings and advisories
9. **`calculate_uv_index_risk(uv_index, skin_type)`** - Calculate UV exposure risk
10. **`get_pollen_forecast(location)`** - Get pollen count for allergies
11. **`suggest_clothing(weather_data, user_preferences)`** - Clothing recommendations based on weather
12. **`create_weather_health_report(location, user_health_conditions)`** - Comprehensive weather-health impact report

---

## VII. AI & NATURAL LANGUAGE PROCESSING

### Cost-Optimized AI Engine (`utils/cost_optimized_ai.py`)
**Functions: 12 AI service functions**

**Core AI Functions:**
1. **`chat_completion(messages, max_tokens, temperature, complexity)`** - Generate chat responses with cost optimization
2. **`text_to_speech(text, voice, speed)`** - Convert text to speech using HuggingFace
3. **`speech_to_text(audio_file)`** - Convert speech to text using HuggingFace
4. **`image_generation(prompt, size, style)`** - Generate images using cost-effective models
5. **`text_summarization(text, max_length)`** - Summarize long text content
6. **`sentiment_analysis(text)`** - Analyze text sentiment
7. **`language_translation(text, source_lang, target_lang)`** - Translate text between languages
8. **`text_classification(text, categories)`** - Classify text into categories

**Cost Management Functions:**
9. **`get_usage_stats()`** - Get API usage and cost statistics
10. **`optimize_model_selection(task_type, complexity)`** - Select most cost-effective model for task
11. **`batch_process_requests(requests_list)`** - Process multiple requests efficiently
12. **`calculate_estimated_cost(operation_type, input_size)`** - Calculate estimated operation cost

**Model Routing:**
- **High Capability**: Anthropic Claude 3 Sonnet ($0.003/1K input, $0.015/1K output)
- **Standard Capability**: Google Gemini Pro ($0.00125/1K input, $0.00375/1K output)
- **Basic Capability**: Meta Llama 3 8B (cost-effective for simple tasks)

### AI Helper (`utils/ai_helper.py`)
**Functions: 10+ AI assistance functions**

1. **`initialize_ai()`** - Initialize cost-optimized AI client
2. **`get_ai_response(prompt, conversation_history)`** - Get AI response with context
3. **`analyze_user_intent(text)`** - Determine user's intent from natural language
4. **`extract_entities(text)`** - Extract named entities (dates, names, places)
5. **`generate_response_variants(base_response, count)`** - Generate multiple response options
6. **`adapt_tone(text, target_tone)`** - Adjust response tone (formal, casual, supportive)
7. **`check_content_appropriateness(text)`** - Content moderation and safety check
8. **`generate_follow_up_questions(conversation_context)`** - Suggest relevant follow-up questions
9. **`summarize_conversation(conversation_history)`** - Create conversation summary
10. **`rate_limit_check()`** - Check if within API rate limits

---

## VIII. VOICE & MULTIMODAL INTERFACES

### Voice Interface (`routes/voice_routes.py`)
**Routes: 8 voice interaction endpoints**

1. **`/voice/`** - Voice interface homepage
2. **`/voice/upload-audio`** - Handle audio file upload for transcription
3. **`/voice/synthesize`** - Convert text to speech
4. **`/voice/real-time-transcription`** - Real-time speech recognition
5. **`/voice/voice-commands`** - Process voice commands
6. **`/voice/conversation`** - Voice conversation interface
7. **`/voice/settings`** - Voice interface settings
8. **`/voice/history`** - Voice interaction history

**Features:**
- Support for WAV, MP3, OGG audio formats
- Real-time transcription capabilities
- Voice command processing
- Text-to-speech synthesis
- Multi-language support planned

### Voice Emotion Routes (`routes/voice_emotion_routes.py`)
**Specialized emotional voice processing**

### Voice Mindfulness Routes (`routes/voice_mindfulness_routes.py`)
**Guided meditation and mindfulness through voice**

---

## IX. SMART HOME & AUTOMATION

### Smart Home Integration (`utils/smart_home_helper.py`)
**Functions for IoT device control and automation**

### Enhanced Weather Helper (`utils/enhanced_weather_helper.py`)
**Advanced weather analytics and health correlations**

---

## X. SYSTEM ARCHITECTURE & DEPLOYMENT

### Application Factory (`nous_app.py`)
**Core application with 15+ route registrations**

**Main Routes:**
- `/` - Main landing page
- `/health` - Health check endpoint  
- `/about` - About page
- `/features` - Features overview

**Registered Blueprints:**
- Chat routes (`/chat`)
- Voice routes (`/voice`)
- Crisis routes (`/crisis`)
- DBT routes (`/dbt`)
- Shopping routes (`/shopping`)
- Spotify routes (`/spotify`)
- Weather routes (`/weather`)
- API routes (`/api`)
- Admin routes (`/admin`)
- And 15+ additional specialized route groups

### Database Models (`models.py`)
**20+ database models including:**

1. **User** - Core user authentication
2. **UserSettings** - User preferences and configuration
3. **Doctor** - Healthcare provider information
4. **Appointment** - Medical appointments
5. **Medication** - Medication tracking
6. **ShoppingList** - Shopping list management
7. **ShoppingItem** - Individual shopping items
8. **Budget** - Budget planning and tracking
9. **Expense** - Expense recording
10. **Product** - Product price tracking
11. **DBTSkillLog** - DBT skill usage logging
12. **DBTDiaryCard** - DBT diary card entries
13. **DBTCrisisResource** - Crisis intervention resources
14. **And 10+ additional specialized models**

---

## XI. COST OPTIMIZATION ACHIEVEMENTS

### Financial Impact
- **Previous Cost**: ~$330/month with OpenAI API
- **Current Cost**: ~$0.49/month with optimized providers
- **Savings**: 99.85% cost reduction
- **Monthly Savings**: $329.51

### Provider Strategy
1. **OpenRouter** for chat completions (Google Gemini Pro primary)
2. **HuggingFace Free Tier** for TTS/STT
3. **Local Templates** for fallback responses
4. **Smart Model Selection** based on task complexity

---

## XII. INTEGRATION SUMMARY

### External APIs Integrated
1. **Google Services** (Gmail, Calendar, Meet, Drive, Photos, Maps)
2. **Spotify** (Music streaming and control)
3. **OpenWeatherMap** (Weather and climate data)
4. **OpenRouter** (Cost-optimized AI models)
5. **HuggingFace** (Free AI inference)
6. **Amazon** (Product tracking and shopping)
7. **Twilio** (SMS notifications - planned)

### Security Features
- OAuth 2.0 for all external services
- Session management with secure cookies
- CSRF protection
- Rate limiting
- Input validation and sanitization
- Secure credential storage

---

## XIII. FUTURE ENHANCEMENT ROADMAP

### Planned Features
1. **Mobile App** (React Native)
2. **Offline Mode** capabilities
3. **Advanced Analytics** dashboard
4. **Multi-language Support**
5. **Wearable Device Integration**
6. **Machine Learning Personalization**
7. **Advanced Health Correlations**
8. **Social Recovery Network Features**

---

## Conclusion

NOUS Personal Assistant represents a comprehensive life management platform with deep specialization in healthcare coordination, crisis intervention, and recovery support. The system's 257 documented functions across 67 modules provide extensive capabilities while maintaining cost-effectiveness through intelligent AI provider routing and optimization strategies.

The architecture supports both immediate practical needs (appointment scheduling, medication tracking, shopping lists) and complex therapeutic interventions (DBT skills coaching, crisis de-escalation, personalized therapy support), making it a uniquely comprehensive personal assistant focused on holistic life management and wellness.