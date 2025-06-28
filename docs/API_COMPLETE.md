# NOUS Complete API Documentation

Generated: 2025-06-28T23:51:54.459956

## API Endpoints (48 total)

### GET /api/data

- **File**: routes/pulse.py
- **Type**: general_api
- **Category**: api_endpoints

### POST /api/skills-on-demand

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/generate-diary-card

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/validate

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/distress

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/chain-analysis

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/wise-mind

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/radical-acceptance

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/interpersonal

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/dialectic

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/trigger-map

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### GET /api/skill-of-day

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints

### POST /api/edit-message

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/advise

- **File**: routes/dbt_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/create

- **File**: routes/meet_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/recovery-assessment

- **File**: routes/forms_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/anonymous-sharing

- **File**: routes/forms_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/daily-check-in

- **File**: routes/forms_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### GET /api/analyze/<form_id>

- **File**: routes/forms_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['GET']

### POST /api/complete-session

- **File**: routes/language_learning_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/update-vocabulary

- **File**: routes/language_learning_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/translate

- **File**: routes/language_learning_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/pronounce

- **File**: routes/language_learning_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/therapy-session

- **File**: routes/meet_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/recovery-group

- **File**: routes/meet_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/setup

- **File**: routes/two_factor_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/confirm

- **File**: routes/two_factor_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/verify

- **File**: routes/two_factor_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### GET /api/accounts

- **File**: routes/financial_routes.py
- **Type**: general_api
- **Category**: api_endpoints

### GET /api/transactions

- **File**: routes/financial_routes.py
- **Type**: general_api
- **Category**: api_endpoints

### GET /api/budgets

- **File**: routes/financial_routes.py
- **Type**: general_api
- **Category**: api_endpoints

### PUT /api/budgets/<budget_id>

- **File**: routes/financial_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['PUT']

### GET /api/spending-analysis

- **File**: routes/financial_routes.py
- **Type**: general_api
- **Category**: api_endpoints

### GET /api/investment-summary

- **File**: routes/financial_routes.py
- **Type**: general_api
- **Category**: api_endpoints

### POST /api/financial-goals

- **File**: routes/financial_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/families

- **File**: routes/collaboration_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/families/<family_id>/tasks

- **File**: routes/collaboration_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### PUT /api/tasks/<task_id>/status

- **File**: routes/collaboration_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['PUT']

### GET /api/families/<family_id>/events

- **File**: routes/collaboration_routes.py
- **Type**: general_api
- **Category**: api_endpoints

### GET /api/families/<family_id>/shopping-lists

- **File**: routes/collaboration_routes.py
- **Type**: general_api
- **Category**: api_endpoints

### POST /api/shopping-lists/<list_id>/items

- **File**: routes/collaboration_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### PUT /api/shopping-items/<item_id>/toggle

- **File**: routes/collaboration_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['PUT']

### POST /api/step/<int:step_index>

- **File**: routes/onboarding_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/skip-step/<int:step_index>

- **File**: routes/onboarding_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### GET /api/progress

- **File**: routes/onboarding_routes.py
- **Type**: general_api
- **Category**: api_endpoints

### POST /api/complete

- **File**: routes/onboarding_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### POST /api/restart

- **File**: routes/onboarding_routes.py
- **Type**: general_api
- **Category**: api_endpoints
- **Options**: , methods=['POST']

### GET /api/notifications

- **File**: routes/view/user.py
- **Type**: general_api
- **Category**: api_endpoints

