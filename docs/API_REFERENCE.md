# API Reference - Legacy

**Note**: This file has been superseded by the comprehensive API documentation system.

## Current API Documentation

The complete, up-to-date API reference is now available through:

- **Interactive API Documentation**: `/api/docs/` (when application is running)
- **OpenAPI Specification**: `/api/docs/openapi.json`
- **Comprehensive API Guide**: See `docs/api_reference.rst`

## Migration Notice

This legacy API reference file has been replaced by:
1. **Sphinx-based Documentation**: Complete API reference in reStructuredText format
2. **Interactive Swagger UI**: Live API testing and documentation
3. **Auto-generated Schemas**: Current endpoint definitions and response formats

Please refer to the new documentation system for accurate, current API information.

## Core Endpoints

### Chat & AI

#### `/`

**Handler**: `chat_interface()`  
**File**: `routes/chat_routes.py`

```http
GET /
```

#### `/api/v1/chat`

**Handler**: `api_chat()`  
**File**: `app.py`

```http
GET /api/chat
```

#### `/api/v1/chat`

**Handler**: `api_chat()`  
**File**: `app.py`

```http
GET /api/chat
```

#### `/api/v1/chat`

**Handler**: `api_chat()`  
**File**: `app.py`

```http
GET /api/chat
```

#### `/chat`

**Handler**: `process_chat()`  
**File**: `routes/api.py`

```http
GET /chat
```

#### `/command_help`

**Handler**: `get_command_help()`  
**File**: `routes/chat_routes.py`

```http
GET /command_help
```

#### `/history`

**Handler**: `get_chat_history()`  
**File**: `routes/chat_routes.py`

```http
GET /history
```

#### `/history`

**Handler**: `clear_chat_history()`  
**File**: `routes/chat_routes.py`

```http
GET /history
```

#### `/message`

**Handler**: `chat_message()`  
**File**: `routes/chat_routes.py`

```http
GET /message
```

### Health

#### `/`

**Handler**: `comprehensive_health_check()`  
**File**: `routes/health_api.py`

```http
GET /
```

#### `/ai-services`

**Handler**: `ai_services_health()`  
**File**: `routes/health_api.py`

```http
GET /ai-services
```

#### `/database`

**Handler**: `database_health()`  
**File**: `routes/health_api.py`

```http
GET /database
```

#### `/google-oauth`

**Handler**: `google_oauth_health()`  
**File**: `routes/health_api.py`

```http
GET /google-oauth
```

#### `/health`

**Handler**: `health()`  
**File**: `app.py`

```http
GET /health
```

#### `/health`

**Handler**: `health()`  
**File**: `app.py`

```http
GET /health
```

#### `/health`

**Handler**: `health()`  
**File**: `app.py`

```http
GET /health
```

#### `/health`

**Handler**: `basic_health_check()`  
**File**: `routes/health_check.py`

```http
GET /health
```

#### `/health`

**Handler**: `health()`  
**File**: `routes/main.py`

```http
GET /health
```

#### `/health`

**Handler**: `health_details()`  
**File**: `routes/pulse.py`

```http
GET /health
```

#### `/health`

**Handler**: `health_check()`  
**File**: `cleanup/app.py`

```http
GET /health
```

#### `/health/detailed`

**Handler**: `detailed_health_check()`  
**File**: `routes/health_check.py`

```http
GET /health/detailed
```

#### `/health/metrics`

**Handler**: `application_metrics()`  
**File**: `routes/health_check.py`

```http
GET /health/metrics
```

#### `/health/system`

**Handler**: `system_health()`  
**File**: `routes/health_check.py`

```http
GET /health/system
```

#### `/healthz`

**Handler**: `health()`  
**File**: `app.py`

```http
GET /healthz
```

#### `/healthz`

**Handler**: `health()`  
**File**: `app.py`

```http
GET /healthz
```

### Crisis

#### `/`

**Handler**: `index()`  
**File**: `routes/crisis_routes.py`

```http
GET /
```

#### `/add-resource`

**Handler**: `add_resource()`  
**File**: `routes/crisis_routes.py`

```http
GET /add-resource
```

#### `/crisis/mobile`

**Handler**: `crisis_mobile()`  
**File**: `app.py`

```http
GET /crisis/mobile
```

#### `/de-escalation`

**Handler**: `de_escalation()`  
**File**: `routes/crisis_routes.py`

```http
GET /de-escalation
```

#### `/delete-resource/<int:resource_id>`

**Handler**: `delete_resource()`  
**File**: `routes/crisis_routes.py`

```http
GET /delete-resource/<int:resource_id>
```

#### `/grounding`

**Handler**: `grounding()`  
**File**: `routes/crisis_routes.py`

```http
GET /grounding
```

#### `/mobile`

**Handler**: `mobile_interface()`  
**File**: `routes/crisis_routes.py`

```http
GET /mobile
```

#### `/mobile`

**Handler**: `mobile_crisis()`  
**File**: `routes/crisis_routes.py`

```http
GET /mobile
```

#### `/resources`

**Handler**: `resources()`  
**File**: `routes/crisis_routes.py`

```http
GET /resources
```

#### `/update-resource/<int:resource_id>`

**Handler**: `update_resource()`  
**File**: `routes/crisis_routes.py`

```http
GET /update-resource/<int:resource_id>
```

### Admin

#### `/`

**Handler**: `index()`  
**File**: `routes/admin_routes.py`

```http
GET /
```

#### `/admin`

**Handler**: `admin_dashboard()`  
**File**: `routes/beta_routes.py`

```http
GET /admin
```

#### `/admin`

**Handler**: `admin_route()`  
**File**: `tests/test_api_key_manager.py`

```http
GET /admin
```

#### `/admin/routes`

**Handler**: `admin_routes()`  
**File**: `app.py`

```http
GET /admin/routes
```

#### `/admin/toggle/<user_id>`

**Handler**: `toggle_tester()`  
**File**: `routes/beta_routes.py`

```http
GET /admin/toggle/<user_id>
```

#### `/users`

**Handler**: `users()`  
**File**: `routes/admin_routes.py`

```http
GET /users
```

### Auth

#### `/authorize/google`

**Handler**: `authorize_google()`  
**File**: `cleanup/app.py`

```http
GET /authorize/google
```

#### `/authorize/spotify`

**Handler**: `authorize_spotify()`  
**File**: `cleanup/app.py`

```http
GET /authorize/spotify
```

#### `/check`

**Handler**: `check_auth()`  
**File**: `routes/auth_api.py`

```http
GET /check
```

#### `/direct-google-login`

**Handler**: `direct_google_login()`  
**File**: `routes/view/auth.py`

```http
GET /direct-google-login
```

#### `/email-login`

**Handler**: `email_login()`  
**File**: `routes/view/auth.py`

```http
GET /email-login
```

#### `/login`

**Handler**: `login()`  
**File**: `routes/auth_api.py`

```http
GET /login
```

#### `/login`

**Handler**: `login()`  
**File**: `routes/view/auth.py`

```http
GET /login
```

#### `/login`

**Handler**: `login()`  
**File**: `routes/auth/standardized_routes.py`

```http
GET /login
```

#### `/logout`

**Handler**: `logout()`  
**File**: `routes/auth_api.py`

```http
GET /logout
```

#### `/logout`

**Handler**: `logout()`  
**File**: `routes/view/auth.py`

```http
GET /logout
```

#### `/logout`

**Handler**: `logout()`  
**File**: `routes/auth/standardized_routes.py`

```http
GET /logout
```

#### `/password/reset`

**Handler**: `password_reset_request()`  
**File**: `routes/auth/standardized_routes.py`

```http
GET /password/reset
```

#### `/password/reset/<token>`

**Handler**: `password_reset()`  
**File**: `routes/auth/standardized_routes.py`

```http
GET /password/reset/<token>
```

#### `/protected`

**Handler**: `protected()`  
**File**: `tests/test_jwt_auth.py`

```http
GET /protected
```

#### `/refresh`

**Handler**: `refresh()`  
**File**: `routes/auth_api.py`

```http
GET /refresh
```

#### `/refresh`

**Handler**: `refresh()`  
**File**: `tests/test_jwt_auth.py`

```http
GET /refresh
```

#### `/register`

**Handler**: `register()`  
**File**: `routes/auth/standardized_routes.py`

```http
GET /register
```

### API

#### ``

**Handler**: `get_settings()`  
**File**: `routes/api/v1/settings.py`

```http
GET 
```

#### ``

**Handler**: `update_settings()`  
**File**: `routes/api/v1/settings.py`

```http
GET 
```

#### `/`

**Handler**: `list_keys()`  
**File**: `routes/api_key_routes.py`

```http
GET /
```

#### `/`

**Handler**: `create_key()`  
**File**: `routes/api_key_routes.py`

```http
GET /
```

#### `/<int:key_id>`

**Handler**: `get_key()`  
**File**: `routes/api_key_routes.py`

```http
GET /<int:key_id>
```

#### `/<int:key_id>`

**Handler**: `revoke_key()`  
**File**: `routes/api_key_routes.py`

```http
GET /<int:key_id>
```

#### `/<int:key_id>/events`

**Handler**: `key_events()`  
**File**: `routes/api_key_routes.py`

```http
GET /<int:key_id>/events
```

#### `/<int:key_id>/rotate`

**Handler**: `rotate_key()`  
**File**: `routes/api_key_routes.py`

```http
GET /<int:key_id>/rotate
```

#### `/ai/analyze`

**Handler**: `ai_analyze()`  
**File**: `routes/api_routes.py`

```http
GET /ai/analyze
```

#### `/ai/ask`

**Handler**: `ai_ask()`  
**File**: `routes/api_routes.py`

```http
GET /ai/ask
```

#### `/ai/stats`

**Handler**: `ai_stats()`  
**File**: `routes/api_routes.py`

```http
GET /ai/stats
```

#### `/api/accommodations/<int:accommodation_id>`

**Handler**: `api_update_accommodation()`  
**File**: `cleanup/app.py`

```http
GET /api/accommodations/<int:accommodation_id>
```

#### `/api/accommodations/<int:accommodation_id>`

**Handler**: `api_delete_accommodation()`  
**File**: `cleanup/app.py`

```http
GET /api/accommodations/<int:accommodation_id>
```

#### `/api/advise`

**Handler**: `api_advise()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/advise
```

#### `/api/analyze/<form_id>`

**Handler**: `api_analyze()`  
**File**: `routes/forms_routes.py`

```http
GET /api/analyze/<form_id>
```

#### `/api/anonymous-sharing`

**Handler**: `api_anonymous_sharing()`  
**File**: `routes/forms_routes.py`

```http
GET /api/anonymous-sharing
```

#### `/api/appointments`

**Handler**: `api_get_appointments()`  
**File**: `cleanup/app.py`

```http
GET /api/appointments
```

#### `/api/appointments`

**Handler**: `api_add_appointment()`  
**File**: `cleanup/app.py`

```http
GET /api/appointments
```

#### `/api/appointments/<int:appointment_id>/status`

**Handler**: `api_update_appointment_status()`  
**File**: `cleanup/app.py`

```http
GET /api/appointments/<int:appointment_id>/status
```

#### `/api/budgets`

**Handler**: `api_get_budgets()`  
**File**: `cleanup/app.py`

```http
GET /api/budgets
```

#### `/api/budgets`

**Handler**: `api_create_budget()`  
**File**: `cleanup/app.py`

```http
GET /api/budgets
```

#### `/api/budgets/<int:budget_id>`

**Handler**: `api_get_budget()`  
**File**: `cleanup/app.py`

```http
GET /api/budgets/<int:budget_id>
```

#### `/api/budgets/<int:budget_id>`

**Handler**: `api_update_budget()`  
**File**: `cleanup/app.py`

```http
GET /api/budgets/<int:budget_id>
```

#### `/api/budgets/<int:budget_id>`

**Handler**: `api_delete_budget()`  
**File**: `cleanup/app.py`

```http
GET /api/budgets/<int:budget_id>
```

#### `/api/budgets/summary`

**Handler**: `api_get_budget_summary()`  
**File**: `cleanup/app.py`

```http
GET /api/budgets/summary
```

#### `/api/chain-analysis`

**Handler**: `api_chain_analysis()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/chain-analysis
```

#### `/api/complete-session`

**Handler**: `complete_session()`  
**File**: `routes/language_learning_routes.py`

```http
GET /api/complete-session
```

#### `/api/confirm`

**Handler**: `api_confirm_2fa()`  
**File**: `routes/two_factor_routes.py`

```http
GET /api/confirm
```

#### `/api/create`

**Handler**: `api_create_form()`  
**File**: `routes/forms_routes.py`

```http
GET /api/create
```

#### `/api/create`

**Handler**: `api_create_meeting()`  
**File**: `routes/meet_routes.py`

```http
GET /api/create
```

#### `/api/daily-check-in`

**Handler**: `api_daily_check_in()`  
**File**: `routes/forms_routes.py`

```http
GET /api/daily-check-in
```

#### `/api/data`

**Handler**: `pulse_api()`  
**File**: `routes/pulse.py`

```http
GET /api/data
```

#### `/api/dialectic`

**Handler**: `api_dialectic()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/dialectic
```

#### `/api/distress`

**Handler**: `api_distress()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/distress
```

#### `/api/docs`

**Handler**: `api_docs_ui()`  
**File**: `api_documentation.py`

```http
GET /api/docs
```

#### `/api/docs/openapi.json`

**Handler**: `get_openapi_spec()`  
**File**: `api_documentation.py`

```http
GET /api/docs/openapi.json
```

#### `/api/doctors`

**Handler**: `api_get_doctors()`  
**File**: `cleanup/app.py`

```http
GET /api/doctors
```

#### `/api/doctors`

**Handler**: `api_add_doctor()`  
**File**: `cleanup/app.py`

```http
GET /api/doctors
```

#### `/api/doctors/<int:doctor_id>`

**Handler**: `api_get_doctor()`  
**File**: `cleanup/app.py`

```http
GET /api/doctors/<int:doctor_id>
```

#### `/api/doctors/<int:doctor_id>`

**Handler**: `api_update_doctor()`  
**File**: `cleanup/app.py`

```http
GET /api/doctors/<int:doctor_id>
```

#### `/api/doctors/<int:doctor_id>`

**Handler**: `api_delete_doctor()`  
**File**: `cleanup/app.py`

```http
GET /api/doctors/<int:doctor_id>
```

#### `/api/doctors/<int:doctor_id>/appointments`

**Handler**: `api_get_doctor_appointments()`  
**File**: `cleanup/app.py`

```http
GET /api/doctors/<int:doctor_id>/appointments
```

#### `/api/doctors/<int:doctor_id>/medications`

**Handler**: `api_get_doctor_medications()`  
**File**: `cleanup/app.py`

```http
GET /api/doctors/<int:doctor_id>/medications
```

#### `/api/documents/<int:document_id>`

**Handler**: `api_update_travel_document()`  
**File**: `cleanup/app.py`

```http
GET /api/documents/<int:document_id>
```

#### `/api/documents/<int:document_id>`

**Handler**: `api_delete_travel_document()`  
**File**: `cleanup/app.py`

```http
GET /api/documents/<int:document_id>
```

#### `/api/edit-message`

**Handler**: `api_edit_message()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/edit-message
```

#### `/api/expenses`

**Handler**: `api_get_expenses()`  
**File**: `cleanup/app.py`

```http
GET /api/expenses
```

#### `/api/expenses`

**Handler**: `api_add_expense()`  
**File**: `cleanup/app.py`

```http
GET /api/expenses
```

#### `/api/expenses/<int:expense_id>`

**Handler**: `api_get_expense()`  
**File**: `cleanup/app.py`

```http
GET /api/expenses/<int:expense_id>
```

#### `/api/expenses/<int:expense_id>`

**Handler**: `api_update_expense()`  
**File**: `cleanup/app.py`

```http
GET /api/expenses/<int:expense_id>
```

#### `/api/expenses/<int:expense_id>`

**Handler**: `api_delete_expense()`  
**File**: `cleanup/app.py`

```http
GET /api/expenses/<int:expense_id>
```

#### `/api/generate-diary-card`

**Handler**: `api_generate_diary_card()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/generate-diary-card
```

#### `/api/interpersonal`

**Handler**: `api_interpersonal()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/interpersonal
```

#### `/api/itinerary/<int:item_id>`

**Handler**: `api_update_itinerary_item()`  
**File**: `cleanup/app.py`

```http
GET /api/itinerary/<int:item_id>
```

#### `/api/itinerary/<int:item_id>`

**Handler**: `api_delete_itinerary_item()`  
**File**: `cleanup/app.py`

```http
GET /api/itinerary/<int:item_id>
```

#### `/api/medications`

**Handler**: `api_get_medications()`  
**File**: `cleanup/app.py`

```http
GET /api/medications
```

#### `/api/medications`

**Handler**: `api_add_medication()`  
**File**: `cleanup/app.py`

```http
GET /api/medications
```

#### `/api/medications/<int:medication_id>`

**Handler**: `api_get_medication()`  
**File**: `cleanup/app.py`

```http
GET /api/medications/<int:medication_id>
```

#### `/api/medications/<int:medication_id>/quantity`

**Handler**: `api_update_medication_quantity()`  
**File**: `cleanup/app.py`

```http
GET /api/medications/<int:medication_id>/quantity
```

#### `/api/medications/<int:medication_id>/refill`

**Handler**: `api_refill_medication()`  
**File**: `cleanup/app.py`

```http
GET /api/medications/<int:medication_id>/refill
```

#### `/api/medications/refill-needed`

**Handler**: `api_get_medications_to_refill()`  
**File**: `cleanup/app.py`

```http
GET /api/medications/refill-needed
```

#### `/api/notifications`

**Handler**: `get_notifications()`  
**File**: `routes/view/user.py`

```http
GET /api/notifications
```

#### `/api/packing/<int:item_id>`

**Handler**: `api_delete_packing_item()`  
**File**: `cleanup/app.py`

```http
GET /api/packing/<int:item_id>
```

#### `/api/packing/<int:item_id>/toggle`

**Handler**: `api_toggle_packed_status()`  
**File**: `cleanup/app.py`

```http
GET /api/packing/<int:item_id>/toggle
```

#### `/api/products`

**Handler**: `api_get_products()`  
**File**: `cleanup/app.py`

```http
GET /api/products
```

#### `/api/products`

**Handler**: `api_add_product()`  
**File**: `cleanup/app.py`

```http
GET /api/products
```

#### `/api/products/<int:product_id>`

**Handler**: `api_get_product()`  
**File**: `cleanup/app.py`

```http
GET /api/products/<int:product_id>
```

#### `/api/products/<int:product_id>/ordered`

**Handler**: `api_mark_product_ordered()`  
**File**: `cleanup/app.py`

```http
GET /api/products/<int:product_id>/ordered
```

#### `/api/products/<int:product_id>/price`

**Handler**: `api_update_product_price()`  
**File**: `cleanup/app.py`

```http
GET /api/products/<int:product_id>/price
```

#### `/api/products/<int:product_id>/recurring`

**Handler**: `api_set_product_recurring()`  
**File**: `cleanup/app.py`

```http
GET /api/products/<int:product_id>/recurring
```

#### `/api/products/due`

**Handler**: `api_get_due_products()`  
**File**: `cleanup/app.py`

```http
GET /api/products/due
```

#### `/api/pronounce`

**Handler**: `pronounce()`  
**File**: `routes/language_learning_routes.py`

```http
GET /api/pronounce
```

#### `/api/radical-acceptance`

**Handler**: `api_radical_acceptance()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/radical-acceptance
```

#### `/api/recovery-assessment`

**Handler**: `api_recovery_assessment()`  
**File**: `routes/forms_routes.py`

```http
GET /api/recovery-assessment
```

#### `/api/recovery-group`

**Handler**: `api_recovery_group()`  
**File**: `routes/meet_routes.py`

```http
GET /api/recovery-group
```

#### `/api/recurring-payments`

**Handler**: `api_get_recurring_payments()`  
**File**: `cleanup/app.py`

```http
GET /api/recurring-payments
```

#### `/api/recurring-payments/<int:payment_id>/paid`

**Handler**: `api_mark_payment_paid()`  
**File**: `cleanup/app.py`

```http
GET /api/recurring-payments/<int:payment_id>/paid
```

#### `/api/recurring-payments/upcoming`

**Handler**: `api_get_upcoming_payments()`  
**File**: `cleanup/app.py`

```http
GET /api/recurring-payments/upcoming
```

#### `/api/reminders/due`

**Handler**: `api_get_due_reminders()`  
**File**: `cleanup/app.py`

```http
GET /api/reminders/due
```

#### `/api/setup`

**Handler**: `api_setup_2fa()`  
**File**: `routes/two_factor_routes.py`

```http
GET /api/setup
```

#### `/api/shopping-lists`

**Handler**: `api_get_shopping_lists()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists
```

#### `/api/shopping-lists`

**Handler**: `api_create_shopping_list()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists
```

#### `/api/shopping-lists/<int:list_id>`

**Handler**: `api_get_shopping_list()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists/<int:list_id>
```

#### `/api/shopping-lists/<int:list_id>/items`

**Handler**: `api_get_list_items()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists/<int:list_id>/items
```

#### `/api/shopping-lists/<int:list_id>/items`

**Handler**: `api_add_list_item()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists/<int:list_id>/items
```

#### `/api/shopping-lists/<int:list_id>/ordered`

**Handler**: `api_mark_list_ordered()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists/<int:list_id>/ordered
```

#### `/api/shopping-lists/<int:list_id>/recurring`

**Handler**: `api_set_list_recurring()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists/<int:list_id>/recurring
```

#### `/api/shopping-lists/due`

**Handler**: `api_get_due_lists()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists/due
```

#### `/api/shopping-lists/items/<int:item_id>`

**Handler**: `api_remove_list_item()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists/items/<int:item_id>
```

#### `/api/shopping-lists/items/<int:item_id>/check`

**Handler**: `api_toggle_item_checked()`  
**File**: `cleanup/app.py`

```http
GET /api/shopping-lists/items/<int:item_id>/check
```

#### `/api/skill-of-day`

**Handler**: `api_skill_of_day()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/skill-of-day
```

#### `/api/skills-on-demand`

**Handler**: `api_skills_on_demand()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/skills-on-demand
```

#### `/api/spotify/command/execute`

**Handler**: `execute_spotify_command()`  
**File**: `routes/spotify_commands.py`

```http
GET /api/spotify/command/execute
```

#### `/api/spotify/smart-playlist`

**Handler**: `create_smart_playlist()`  
**File**: `routes/spotify_commands.py`

```http
GET /api/spotify/smart-playlist
```

#### `/api/spotify/track-mood`

**Handler**: `get_track_mood()`  
**File**: `routes/spotify_commands.py`

```http
GET /api/spotify/track-mood
```

#### `/api/spotify/visualization/artists`

**Handler**: `get_top_artists_chart()`  
**File**: `routes/spotify_visualization.py`

```http
GET /api/spotify/visualization/artists
```

#### `/api/spotify/visualization/compare-tracks`

**Handler**: `compare_tracks()`  
**File**: `routes/spotify_visualization.py`

```http
GET /api/spotify/visualization/compare-tracks
```

#### `/api/spotify/visualization/genres`

**Handler**: `get_genre_chart()`  
**File**: `routes/spotify_visualization.py`

```http
GET /api/spotify/visualization/genres
```

#### `/api/spotify/visualization/history`

**Handler**: `get_listening_history_chart()`  
**File**: `routes/spotify_visualization.py`

```http
GET /api/spotify/visualization/history
```

#### `/api/spotify/visualization/playlist-analysis`

**Handler**: `get_playlist_analysis()`  
**File**: `routes/spotify_visualization.py`

```http
GET /api/spotify/visualization/playlist-analysis
```

#### `/api/spotify/visualization/report`

**Handler**: `get_spotify_report()`  
**File**: `routes/spotify_visualization.py`

```http
GET /api/spotify/visualization/report
```

#### `/api/spotify/visualization/track-features`

**Handler**: `get_track_features_chart()`  
**File**: `routes/spotify_visualization.py`

```http
GET /api/spotify/visualization/track-features
```

#### `/api/spotify/visualization/tracks`

**Handler**: `get_top_tracks_chart()`  
**File**: `routes/spotify_visualization.py`

```http
GET /api/spotify/visualization/tracks
```

#### `/api/therapy-session`

**Handler**: `api_therapy_session()`  
**File**: `routes/meet_routes.py`

```http
GET /api/therapy-session
```

#### `/api/translate`

**Handler**: `translate()`  
**File**: `routes/language_learning_routes.py`

```http
GET /api/translate
```

#### `/api/trigger-map`

**Handler**: `api_trigger_map()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/trigger-map
```

#### `/api/trips`

**Handler**: `api_get_trips()`  
**File**: `cleanup/app.py`

```http
GET /api/trips
```

#### `/api/trips`

**Handler**: `api_create_trip()`  
**File**: `cleanup/app.py`

```http
GET /api/trips
```

#### `/api/trips/<int:trip_id>`

**Handler**: `api_get_trip()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>
```

#### `/api/trips/<int:trip_id>`

**Handler**: `api_update_trip()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>
```

#### `/api/trips/<int:trip_id>`

**Handler**: `api_delete_trip()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>
```

#### `/api/trips/<int:trip_id>/accommodations`

**Handler**: `api_get_accommodations()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/accommodations
```

#### `/api/trips/<int:trip_id>/accommodations`

**Handler**: `api_add_accommodation()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/accommodations
```

#### `/api/trips/<int:trip_id>/cost`

**Handler**: `api_get_trip_cost()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/cost
```

#### `/api/trips/<int:trip_id>/documents`

**Handler**: `api_get_travel_documents()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/documents
```

#### `/api/trips/<int:trip_id>/documents`

**Handler**: `api_add_travel_document()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/documents
```

#### `/api/trips/<int:trip_id>/itinerary`

**Handler**: `api_get_itinerary()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/itinerary
```

#### `/api/trips/<int:trip_id>/itinerary`

**Handler**: `api_add_itinerary_item()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/itinerary
```

#### `/api/trips/<int:trip_id>/packing`

**Handler**: `api_get_packing_list()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/packing
```

#### `/api/trips/<int:trip_id>/packing`

**Handler**: `api_add_packing_item()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/packing
```

#### `/api/trips/<int:trip_id>/packing/generate`

**Handler**: `api_generate_packing_list()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/packing/generate
```

#### `/api/trips/<int:trip_id>/packing/progress`

**Handler**: `api_get_packing_progress()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/<int:trip_id>/packing/progress
```

#### `/api/trips/active`

**Handler**: `api_get_active_trip()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/active
```

#### `/api/trips/upcoming`

**Handler**: `api_get_upcoming_trips()`  
**File**: `cleanup/app.py`

```http
GET /api/trips/upcoming
```

#### `/api/update-vocabulary`

**Handler**: `update_vocabulary()`  
**File**: `routes/language_learning_routes.py`

```http
GET /api/update-vocabulary
```

#### `/api/validate`

**Handler**: `api_validate()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/validate
```

#### `/api/verify`

**Handler**: `api_verify_2fa()`  
**File**: `routes/two_factor_routes.py`

```http
GET /api/verify
```

#### `/api/voice`

**Handler**: `api_voice()`  
**File**: `app.py`

```http
GET /api/voice
```

#### `/api/weather/current`

**Handler**: `api_get_current_weather()`  
**File**: `cleanup/app.py`

```http
GET /api/weather/current
```

#### `/api/weather/forecast`

**Handler**: `api_get_weather_forecast()`  
**File**: `cleanup/app.py`

```http
GET /api/weather/forecast
```

#### `/api/weather/locations`

**Handler**: `api_get_weather_locations()`  
**File**: `cleanup/app.py`

```http
GET /api/weather/locations
```

#### `/api/weather/locations`

**Handler**: `api_add_weather_location()`  
**File**: `cleanup/app.py`

```http
GET /api/weather/locations
```

#### `/api/weather/locations/<int:location_id>`

**Handler**: `api_delete_weather_location()`  
**File**: `cleanup/app.py`

```http
GET /api/weather/locations/<int:location_id>
```

#### `/api/weather/locations/<int:location_id>/primary`

**Handler**: `api_set_primary_weather_location()`  
**File**: `cleanup/app.py`

```http
GET /api/weather/locations/<int:location_id>/primary
```

#### `/api/weather/pain-forecast`

**Handler**: `api_pain_flare_forecast()`  
**File**: `cleanup/app.py`

```http
GET /api/weather/pain-forecast
```

#### `/api/wise-mind`

**Handler**: `api_wise_mind()`  
**File**: `routes/dbt_routes.py`

```http
GET /api/wise-mind
```

#### `/current`

**Handler**: `api_get_current_weather()`  
**File**: `routes/api/v1/weather.py`

```http
GET /current
```

#### `/forecast`

**Handler**: `api_get_weather_forecast()`  
**File**: `routes/api/v1/weather.py`

```http
GET /forecast
```

#### `/items/<int:item_id>`

**Handler**: `remove_list_item()`  
**File**: `routes/api/shopping.py`

```http
GET /items/<int:item_id>
```

#### `/items/<int:item_id>/check`

**Handler**: `toggle_item_checked()`  
**File**: `routes/api/shopping.py`

```http
GET /items/<int:item_id>/check
```

#### `/lists`

**Handler**: `get_shopping_lists()`  
**File**: `routes/api/shopping.py`

```http
GET /lists
```

#### `/lists`

**Handler**: `create_shopping_list()`  
**File**: `routes/api/shopping.py`

```http
GET /lists
```

#### `/lists/<int:list_id>`

**Handler**: `get_shopping_list()`  
**File**: `routes/api/shopping.py`

```http
GET /lists/<int:list_id>
```

#### `/lists/<int:list_id>/items`

**Handler**: `get_list_items()`  
**File**: `routes/api/shopping.py`

```http
GET /lists/<int:list_id>/items
```

#### `/lists/<int:list_id>/items`

**Handler**: `add_list_item()`  
**File**: `routes/api/shopping.py`

```http
GET /lists/<int:list_id>/items
```

#### `/locations`

**Handler**: `api_get_weather_locations()`  
**File**: `routes/api/v1/weather.py`

```http
GET /locations
```

#### `/locations`

**Handler**: `api_add_weather_location()`  
**File**: `routes/api/v1/weather.py`

```http
GET /locations
```

#### `/locations/<int:location_id>`

**Handler**: `api_delete_weather_location()`  
**File**: `routes/api/v1/weather.py`

```http
GET /locations/<int:location_id>
```

#### `/locations/<int:location_id>/primary`

**Handler**: `api_set_primary_weather_location()`  
**File**: `routes/api/v1/weather.py`

```http
GET /locations/<int:location_id>/primary
```

#### `/pain-forecast`

**Handler**: `api_pain_flare_forecast()`  
**File**: `routes/api/v1/weather.py`

```http
GET /pain-forecast
```

#### `/products`

**Handler**: `get_products()`  
**File**: `routes/api/shopping.py`

```http
GET /products
```

#### `/products`

**Handler**: `add_product()`  
**File**: `routes/api/shopping.py`

```http
GET /products
```

#### `/products/<int:product_id>`

**Handler**: `get_product()`  
**File**: `routes/api/shopping.py`

```http
GET /products/<int:product_id>
```

#### `/reset`

**Handler**: `reset_settings()`  
**File**: `routes/api/v1/settings.py`

```http
GET /reset
```

#### `/scopes`

**Handler**: `list_scopes()`  
**File**: `routes/api_key_routes.py`

```http
GET /scopes
```

#### `/settings`

**Handler**: `get_settings()`  
**File**: `routes/api.py`

```http
GET /settings
```

#### `/settings`

**Handler**: `update_settings()`  
**File**: `routes/api.py`

```http
GET /settings
```

#### `/status`

**Handler**: `api_status()`  
**File**: `routes/api.py`

```http
GET /status
```

#### `/tasks`

**Handler**: `get_tasks()`  
**File**: `routes/api.py`

```http
GET /tasks
```

#### `/tasks`

**Handler**: `create_task()`  
**File**: `routes/api.py`

```http
GET /tasks
```

#### `/tasks/<int:task_id>`

**Handler**: `get_task()`  
**File**: `routes/api.py`

```http
GET /tasks/<int:task_id>
```

#### `/tasks/<int:task_id>`

**Handler**: `update_task()`  
**File**: `routes/api.py`

```http
GET /tasks/<int:task_id>
```

#### `/tasks/<int:task_id>`

**Handler**: `delete_task()`  
**File**: `routes/api.py`

```http
GET /tasks/<int:task_id>
```

#### `/tasks/<task_id>`

**Handler**: `get_task_result()`  
**File**: `routes/async_api.py`

```http
GET /tasks/<task_id>
```

#### `/tasks/api_simulation`

**Handler**: `start_api_simulation()`  
**File**: `routes/async_api.py`

```http
GET /tasks/api_simulation
```

#### `/tasks/fibonacci`

**Handler**: `start_fibonacci_task()`  
**File**: `routes/async_api.py`

```http
GET /tasks/fibonacci
```

#### `/tasks/process_data`

**Handler**: `start_data_processing()`  
**File**: `routes/async_api.py`

```http
GET /tasks/process_data
```

#### `/test`

**Handler**: `test_route()`  
**File**: `tests/test_api_key_manager.py`

```http
GET /test
```

#### `/user`

**Handler**: `get_user_info()`  
**File**: `routes/api.py`

```http
GET /user
```

#### `/user/profile`

**Handler**: `get_user_profile()`  
**File**: `routes/api.py`

```http
GET /user/profile
```

#### `/user/settings`

**Handler**: `user_settings()`  
**File**: `routes/api.py`

```http
GET /user/settings
```

#### `/verify`

**Handler**: `verify_key()`  
**File**: `routes/api_key_routes.py`

```http
GET /verify
```

### Other

#### ``

**Handler**: `settings_page()`  
**File**: `routes/view/settings.py`

```http
GET 
```

#### ``

**Handler**: `save_settings()`  
**File**: `routes/view/settings.py`

```http
GET 
```

#### ``

**Handler**: `dashboard()`  
**File**: `routes/view/dashboard.py`

```http
GET 
```

#### `/`

**Handler**: `index()`  
**File**: `app.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `app.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `app.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/voice_mindfulness_routes.py`

```http
GET /
```

#### `/`

**Handler**: `wizard()`  
**File**: `routes/setup_routes.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/beta_routes.py`

```http
GET /
```

#### `/`

**Handler**: `dashboard()`  
**File**: `routes/dbt_routes.py`

```http
GET /
```

#### `/`

**Handler**: `dashboard()`  
**File**: `routes/forms_routes.py`

```http
GET /
```

#### `/`

**Handler**: `dashboard()`  
**File**: `routes/meet_routes.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/spotify_routes.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/smart_shopping_routes.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/price_routes.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/voice_routes.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/aa_content.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/aa_routes.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/language_learning_routes.py`

```http
GET /
```

#### `/`

**Handler**: `memory_dashboard()`  
**File**: `routes/memory_dashboard_routes.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/index.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/main.py`

```http
GET /
```

#### `/`

**Handler**: `pulse_dashboard()`  
**File**: `routes/pulse.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `routes/view/index.py`

```http
GET /
```

#### `/`

**Handler**: `dashboard()`  
**File**: `routes/view/dashboard.py`

```http
GET /
```

#### `/`

**Handler**: `index()`  
**File**: `cleanup/app.py`

```http
GET /
```

#### `/<path:path>`

**Handler**: `catch_all()`  
**File**: `routes/main.py`

```http
GET /<path:path>
```

#### `/about`

**Handler**: `about()`  
**File**: `app.py`

```http
GET /about
```

#### `/activity`

**Handler**: `activity()`  
**File**: `routes/user_routes.py`

```http
GET /activity
```

#### `/add`

**Handler**: `add_item()`  
**File**: `routes/price_routes.py`

```http
GET /add
```

#### `/add-to-list`

**Handler**: `add_to_shopping_list()`  
**File**: `routes/amazon_routes.py`

```http
GET /add-to-list
```

#### `/analyze-notes`

**Handler**: `analyze_notes()`  
**File**: `routes/meet_routes.py`

```http
GET /analyze-notes
```

#### `/analyze/<form_id>`

**Handler**: `analyze()`  
**File**: `routes/forms_routes.py`

```http
GET /analyze/<form_id>
```

#### `/anonymous-sharing`

**Handler**: `anonymous_sharing()`  
**File**: `routes/forms_routes.py`

```http
GET /anonymous-sharing
```

#### `/apply`

**Handler**: `apply()`  
**File**: `routes/beta_routes.py`

```http
GET /apply
```

#### `/big-book`

**Handler**: `big_book()`  
**File**: `routes/aa_content.py`

```http
GET /big-book
```

#### `/big-book/<int:chapter_id>`

**Handler**: `big_book_chapter()`  
**File**: `routes/aa_content.py`

```http
GET /big-book/<int:chapter_id>
```

#### `/big-book/audio/<int:audio_id>`

**Handler**: `big_book_audio()`  
**File**: `routes/aa_content.py`

```http
GET /big-book/audio/<int:audio_id>
```

#### `/callback`

**Handler**: `callback()`  
**File**: `routes/spotify_routes.py`

```http
GET /callback
```

#### `/callback/google`

**Handler**: `callback_google()`  
**File**: `cleanup/app.py`

```http
GET /callback/google
```

#### `/callback/spotify`

**Handler**: `callback_spotify()`  
**File**: `cleanup/app.py`

```http
GET /callback/spotify
```

#### `/challenges`

**Handler**: `challenges()`  
**File**: `routes/dbt_routes.py`

```http
GET /challenges
```

#### `/challenges/complete/<challenge_id>`

**Handler**: `complete_challenge()`  
**File**: `routes/dbt_routes.py`

```http
GET /challenges/complete/<challenge_id>
```

#### `/challenges/create`

**Handler**: `create_new_challenge()`  
**File**: `routes/dbt_routes.py`

```http
GET /challenges/create
```

#### `/challenges/generate`

**Handler**: `generate_challenge()`  
**File**: `routes/dbt_routes.py`

```http
GET /challenges/generate
```

#### `/challenges/reset/<challenge_id>`

**Handler**: `reset_challenge_progress()`  
**File**: `routes/dbt_routes.py`

```http
GET /challenges/reset/<challenge_id>
```

#### `/challenges/update/<challenge_id>`

**Handler**: `update_challenge()`  
**File**: `routes/dbt_routes.py`

```http
GET /challenges/update/<challenge_id>
```

#### `/clear`

**Handler**: `clear_log()`  
**File**: `routes/view/index.py`

```http
GET /clear
```

#### `/clear`

**Handler**: `clear_log()`  
**File**: `cleanup/app.py`

```http
GET /clear
```

#### `/complete`

**Handler**: `complete()`  
**File**: `routes/setup_routes.py`

```http
GET /complete
```

#### `/connect`

**Handler**: `connect()`  
**File**: `routes/spotify_routes.py`

```http
GET /connect
```

#### `/continuous-listening`

**Handler**: `continuous_listening()`  
**File**: `routes/voice_routes.py`

```http
GET /continuous-listening
```

#### `/create`

**Handler**: `create()`  
**File**: `routes/forms_routes.py`

```http
GET /create
```

#### `/create`

**Handler**: `create()`  
**File**: `routes/meet_routes.py`

```http
GET /create
```

#### `/create-notes/<meeting_id>`

**Handler**: `create_notes()`  
**File**: `routes/meet_routes.py`

```http
GET /create-notes/<meeting_id>
```

#### `/daily-check-in`

**Handler**: `daily_check_in()`  
**File**: `routes/forms_routes.py`

```http
GET /daily-check-in
```

#### `/dashboard`

**Handler**: `dashboard()`  
**File**: `app.py`

```http
GET /dashboard
```

#### `/dashboard`

**Handler**: `dashboard()`  
**File**: `app.py`

```http
GET /dashboard
```

#### `/dashboard`

**Handler**: `dashboard()`  
**File**: `routes/beta_routes.py`

```http
GET /dashboard
```

#### `/dashboard`

**Handler**: `dashboard()`  
**File**: `routes/dashboard.py`

```http
GET /dashboard
```

#### `/dashboard`

**Handler**: `dashboard()`  
**File**: `routes/main.py`

```http
GET /dashboard
```

#### `/dashboard`

**Handler**: `dashboard()`  
**File**: `cleanup/app.py`

```http
GET /dashboard
```

#### `/deals`

**Handler**: `deals()`  
**File**: `routes/smart_shopping_routes.py`

```http
GET /deals
```

#### `/debug/db-stats`

**Handler**: `view_db_stats()`  
**File**: `utils/db_optimizations.py`

```http
GET /debug/db-stats
```

#### `/debug/db-stats/clear`

**Handler**: `clear_db_stats_route()`  
**File**: `utils/db_optimizations.py`

```http
GET /debug/db-stats/clear
```

#### `/delete/<meeting_id>`

**Handler**: `delete()`  
**File**: `routes/meet_routes.py`

```http
GET /delete/<meeting_id>
```

#### `/diary`

**Handler**: `diary()`  
**File**: `routes/dbt_routes.py`

```http
GET /diary
```

#### `/disable`

**Handler**: `disable_2fa()`  
**File**: `routes/two_factor_routes.py`

```http
GET /disable
```

#### `/edit/<meeting_id>`

**Handler**: `edit()`  
**File**: `routes/meet_routes.py`

```http
GET /edit/<meeting_id>
```

#### `/email-participants/<meeting_id>`

**Handler**: `email_participants()`  
**File**: `routes/meet_routes.py`

```http
GET /email-participants/<meeting_id>
```

#### `/entities`

**Handler**: `get_entities()`  
**File**: `routes/memory_routes.py`

```http
GET /entities
```

#### `/entities`

**Handler**: `add_entity()`  
**File**: `routes/memory_routes.py`

```http
GET /entities
```

#### `/exercise/<exercise_name>`

**Handler**: `exercise_detail()`  
**File**: `routes/voice_mindfulness_routes.py`

```http
GET /exercise/<exercise_name>
```

#### `/favorites`

**Handler**: `favorites()`  
**File**: `routes/aa_content.py`

```http
GET /favorites
```

#### `/favorites/add`

**Handler**: `add_favorite()`  
**File**: `routes/aa_content.py`

```http
GET /favorites/add
```

#### `/favorites/remove/<int:favorite_id>`

**Handler**: `remove_favorite()`  
**File**: `routes/aa_content.py`

```http
GET /favorites/remove/<int:favorite_id>
```

#### `/features`

**Handler**: `features()`  
**File**: `routes/setup_routes.py`

```http
GET /features
```

#### `/features/save`

**Handler**: `features_save()`  
**File**: `routes/setup_routes.py`

```http
GET /features/save
```

#### `/finalize`

**Handler**: `finalize()`  
**File**: `routes/setup_routes.py`

```http
GET /finalize
```

#### `/finance`

**Handler**: `finance_details()`  
**File**: `routes/pulse.py`

```http
GET /finance
```

#### `/generate-agenda`

**Handler**: `generate_agenda()`  
**File**: `routes/meet_routes.py`

```http
GET /generate-agenda
```

#### `/guide`

**Handler**: `user_guide()`  
**File**: `routes/view/user.py`

```http
GET /guide
```

#### `/help`

**Handler**: `help_page()`  
**File**: `routes/index.py`

```http
GET /help
```

#### `/help`

**Handler**: `help()`  
**File**: `routes/main.py`

```http
GET /help
```

#### `/help`

**Handler**: `help_page()`  
**File**: `routes/view/index.py`

```http
GET /help
```

#### `/help`

**Handler**: `help_page()`  
**File**: `cleanup/app.py`

```http
GET /help
```

#### `/image/analyze`

**Handler**: `analyze_image()`  
**File**: `routes/image_routes.py`

```http
GET /image/analyze
```

#### `/image/organize`

**Handler**: `organize_images()`  
**File**: `routes/image_routes.py`

```http
GET /image/organize
```

#### `/index`

**Handler**: `index()`  
**File**: `routes/index.py`

```http
GET /index
```

#### `/initialize`

**Handler**: `initialize_memory()`  
**File**: `routes/memory_routes.py`

```http
GET /initialize
```

#### `/leave`

**Handler**: `leave_beta()`  
**File**: `routes/beta_routes.py`

```http
GET /leave
```

#### `/log-completion`

**Handler**: `log_completion()`  
**File**: `routes/voice_mindfulness_routes.py`

```http
GET /log-completion
```

#### `/logout`

**Handler**: `logout()`  
**File**: `cleanup/app.py`

```http
GET /logout
```

#### `/mark-ordered/<int:product_id>`

**Handler**: `mark_ordered()`  
**File**: `routes/amazon_routes.py`

```http
GET /mark-ordered/<int:product_id>
```

#### `/mindfulness-session`

**Handler**: `mindfulness_session()`  
**File**: `routes/meet_routes.py`

```http
GET /mindfulness-session
```

#### `/nonexistent`

**Handler**: `nonexistent_route()`  
**File**: `tests/test_schema_validation.py`

```http
GET /nonexistent
```

#### `/personalize`

**Handler**: `personalize()`  
**File**: `routes/setup_routes.py`

```http
GET /personalize
```

#### `/personalize/save`

**Handler**: `personalize_save()`  
**File**: `routes/setup_routes.py`

```http
GET /personalize/save
```

#### `/personalized`

**Handler**: `personalized_exercise()`  
**File**: `routes/voice_mindfulness_routes.py`

```http
GET /personalized
```

#### `/practice/<int:profile_id>`

**Handler**: `practice_dashboard()`  
**File**: `routes/language_learning_routes.py`

```http
GET /practice/<int:profile_id>
```

#### `/practice/conversation/<int:profile_id>/<int:template_id>`

**Handler**: `practice_conversation()`  
**File**: `routes/language_learning_routes.py`

```http
GET /practice/conversation/<int:profile_id>/<int:template_id>
```

#### `/practice/vocabulary/<int:profile_id>`

**Handler**: `practice_vocabulary()`  
**File**: `routes/language_learning_routes.py`

```http
GET /practice/vocabulary/<int:profile_id>
```

#### `/preferences`

**Handler**: `preferences()`  
**File**: `routes/setup_routes.py`

```http
GET /preferences
```

#### `/preferences`

**Handler**: `preferences()`  
**File**: `routes/user_routes.py`

```http
GET /preferences
```

#### `/preferences/save`

**Handler**: `preferences_save()`  
**File**: `routes/setup_routes.py`

```http
GET /preferences/save
```

#### `/process-voice-command`

**Handler**: `process_voice_command()`  
**File**: `routes/voice_routes.py`

```http
GET /process-voice-command
```

#### `/product/<path:asin_or_url>`

**Handler**: `product_details()`  
**File**: `routes/amazon_routes.py`

```http
GET /product/<path:asin_or_url>
```

#### `/profile`

**Handler**: `profile()`  
**File**: `routes/user_routes.py`

```http
GET /profile
```

#### `/profile`

**Handler**: `profile()`  
**File**: `routes/view/user.py`

```http
GET /profile
```

#### `/profile`

**Handler**: `update_profile()`  
**File**: `routes/view/user.py`

```http
GET /profile
```

#### `/profile/<int:profile_id>`

**Handler**: `profile()`  
**File**: `routes/language_learning_routes.py`

```http
GET /profile/<int:profile_id>
```

#### `/profile/new`

**Handler**: `new_profile()`  
**File**: `routes/language_learning_routes.py`

```http
GET /profile/new
```

#### `/pulse`

**Handler**: `pulse()`  
**File**: `app.py`

```http
GET /pulse
```

#### `/random`

**Handler**: `random_exercise()`  
**File**: `routes/voice_mindfulness_routes.py`

```http
GET /random
```

#### `/recent`

**Handler**: `get_recent_memories()`  
**File**: `routes/memory_routes.py`

```http
GET /recent
```

#### `/recommendations`

**Handler**: `recommendations()`  
**File**: `routes/smart_shopping_routes.py`

```http
GET /recommendations
```

#### `/recovery-assessment`

**Handler**: `recovery_assessment()`  
**File**: `routes/forms_routes.py`

```http
GET /recovery-assessment
```

#### `/recovery-group`

**Handler**: `recovery_group()`  
**File**: `routes/meet_routes.py`

```http
GET /recovery-group
```

#### `/regenerate-backup-codes`

**Handler**: `regenerate_backup_codes()`  
**File**: `routes/two_factor_routes.py`

```http
GET /regenerate-backup-codes
```

#### `/reset`

**Handler**: `reset()`  
**File**: `routes/setup_routes.py`

```http
GET /reset
```

#### `/reset`

**Handler**: `reset_settings()`  
**File**: `routes/view/settings.py`

```http
GET /reset
```

#### `/search`

**Handler**: `search()`  
**File**: `routes/amazon_routes.py`

```http
GET /search
```

#### `/search`

**Handler**: `search()`  
**File**: `routes/aa_content.py`

```http
GET /search
```

#### `/settings`

**Handler**: `settings_page()`  
**File**: `routes/settings.py`

```http
GET /settings
```

#### `/settings`

**Handler**: `settings_page()`  
**File**: `cleanup/app.py`

```http
GET /settings
```

#### `/settings`

**Handler**: `save_settings()`  
**File**: `cleanup/app.py`

```http
GET /settings
```

#### `/settings/appearance`

**Handler**: `update_appearance()`  
**File**: `routes/settings.py`

```http
GET /settings/appearance
```

#### `/settings/assistant`

**Handler**: `update_assistant()`  
**File**: `routes/settings.py`

```http
GET /settings/assistant
```

#### `/settings/audit`

**Handler**: `settings_audit()`  
**File**: `app.py`

```http
GET /settings/audit
```

#### `/settings/audit`

**Handler**: `settings_audit()`  
**File**: `app.py`

```http
GET /settings/audit
```

#### `/settings/delete-account`

**Handler**: `delete_account()`  
**File**: `routes/settings.py`

```http
GET /settings/delete-account
```

#### `/settings/password`

**Handler**: `update_password()`  
**File**: `routes/settings.py`

```http
GET /settings/password
```

#### `/settings/profile`

**Handler**: `update_profile()`  
**File**: `routes/settings.py`

```http
GET /settings/profile
```

#### `/setup`

**Handler**: `setup_wizard()`  
**File**: `app.py`

```http
GET /setup
```

#### `/setup`

**Handler**: `setup_2fa()`  
**File**: `routes/two_factor_routes.py`

```http
GET /setup
```

#### `/skills`

**Handler**: `skills()`  
**File**: `routes/dbt_routes.py`

```http
GET /skills
```

#### `/skills/log`

**Handler**: `log_skill()`  
**File**: `routes/dbt_routes.py`

```http
GET /skills/log
```

#### `/skills/recommend`

**Handler**: `recommend_skills()`  
**File**: `routes/dbt_routes.py`

```http
GET /skills/recommend
```

#### `/speakers`

**Handler**: `speakers()`  
**File**: `routes/aa_content.py`

```http
GET /speakers
```

#### `/speakers/<int:recording_id>`

**Handler**: `speaker_detail()`  
**File**: `routes/aa_content.py`

```http
GET /speakers/<int:recording_id>
```

#### `/speakers/audio/<int:recording_id>`

**Handler**: `speaker_audio()`  
**File**: `routes/aa_content.py`

```http
GET /speakers/audio/<int:recording_id>
```

#### `/sponsor-meeting`

**Handler**: `sponsor_meeting()`  
**File**: `routes/meet_routes.py`

```http
GET /sponsor-meeting
```

#### `/static/<path:path>`

**Handler**: `serve_static()`  
**File**: `routes/main.py`

```http
GET /static/<path:path>
```

#### `/static/test.css`

**Handler**: `static_route()`  
**File**: `tests/test_security_headers.py`

```http
GET /static/test.css
```

#### `/summary`

**Handler**: `get_memory_summary()`  
**File**: `routes/memory_routes.py`

```http
GET /summary
```

#### `/synthesize`

**Handler**: `synthesize_speech()`  
**File**: `routes/voice_routes.py`

```http
GET /synthesize
```

#### `/test`

**Handler**: `test_route()`  
**File**: `tests/test_schema_validation.py`

```http
GET /test
```

#### `/test`

**Handler**: `test_route()`  
**File**: `tests/test_security_headers.py`

```http
GET /test
```

#### `/test-piper`

**Handler**: `test_piper()`  
**File**: `routes/voice_routes.py`

```http
GET /test-piper
```

#### `/test-whisper`

**Handler**: `test_whisper()`  
**File**: `routes/voice_routes.py`

```http
GET /test-whisper
```

#### `/therapy-session`

**Handler**: `therapy_session()`  
**File**: `routes/meet_routes.py`

```http
GET /therapy-session
```

#### `/topics`

**Handler**: `get_topics()`  
**File**: `routes/memory_routes.py`

```http
GET /topics
```

#### `/topics`

**Handler**: `update_topic()`  
**File**: `routes/memory_routes.py`

```http
GET /topics
```

#### `/track`

**Handler**: `track_product()`  
**File**: `routes/amazon_routes.py`

```http
GET /track
```

#### `/tracked`

**Handler**: `tracked_products()`  
**File**: `routes/amazon_routes.py`

```http
GET /tracked
```

#### `/tracked-items`

**Handler**: `tracked_items()`  
**File**: `routes/price_routes.py`

```http
GET /tracked-items
```

#### `/untrack/<int:product_id>`

**Handler**: `untrack_product()`  
**File**: `routes/amazon_routes.py`

```http
GET /untrack/<int:product_id>
```

#### `/upload-audio`

**Handler**: `upload_audio()`  
**File**: `routes/voice_routes.py`

```http
GET /upload-audio
```

#### `/verify`

**Handler**: `verify_2fa()`  
**File**: `routes/two_factor_routes.py`

```http
GET /verify
```

#### `/view/<form_id>`

**Handler**: `view()`  
**File**: `routes/forms_routes.py`

```http
GET /view/<form_id>
```

#### `/view/<meeting_id>`

**Handler**: `view()`  
**File**: `routes/meet_routes.py`

```http
GET /view/<meeting_id>
```

#### `/viz/spotify/report`

**Handler**: `spotify_report_page()`  
**File**: `routes/spotify_visualization.py`

```http
GET /viz/spotify/report
```

#### `/vocabulary/<int:profile_id>`

**Handler**: `vocabulary()`  
**File**: `routes/language_learning_routes.py`

```http
GET /vocabulary/<int:profile_id>
```

#### `/vocabulary/add/<int:profile_id>`

**Handler**: `add_vocabulary()`  
**File**: `routes/language_learning_routes.py`

```http
GET /vocabulary/add/<int:profile_id>
```

#### `/voice/analyze_emotion`

**Handler**: `analyze_voice_emotion()`  
**File**: `routes/voice_emotion_routes.py`

```http
GET /voice/analyze_emotion
```

#### `/voice/emotion`

**Handler**: `voice_emotion_analysis()`  
**File**: `routes/voice_emotion_routes.py`

```http
GET /voice/emotion
```

#### `/welcome`

**Handler**: `welcome()`  
**File**: `routes/setup_routes.py`

```http
GET /welcome
```

#### `/welcome/complete`

**Handler**: `welcome_complete()`  
**File**: `routes/setup_routes.py`

```http
GET /welcome/complete
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Endpoint not found
- `500 Internal Server Error`: Server error

Error responses include a JSON body with error details:

```json
{
  "success": false,
  "error": "Error description",
  "message": "User-friendly error message"
}
```
