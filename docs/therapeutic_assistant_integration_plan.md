# Therapeutically-Informed Assistant Integration Plan

## Objective
Design and integrate the PDF’s therapeutically-informed AI assistant into the existing NOUS platform, combining evidence-based mental health support (CBT, DBT, ACT/mindfulness, positive psychology/behavioral activation, motivational interviewing) with the current personal assistant stack, while enforcing safety, privacy, bilingual support (EN/ES), and a hybrid retrieval + generative dialogue architecture. Refactors are allowed during implementation to simplify or harden the system so long as no current capabilities are removed; parity is maintained while structure is improved.

## Current System Baseline (what we’re building on)
- **Stack**: Flask backend (`app.py`, `routes/*`), React/Webpack frontend, SQLite/Postgres via SQLAlchemy, SocketIO chat (`core/chat/*`), cron/scheduler scripts, Tailwind/Bootstrap UI. OAuth + sessions via `utils/google_oauth`.
- **AI layer**: `utils/unified_ai_service.py` orchestrates OpenRouter/Gemini/OpenAI/HF with cost optimization; adaptive AI hooks; TTS/STT available when keys exist.
- **Chat orchestration**: `core/chat/dispatcher.py` + `core/chat/handler_registry.py` route chat messages; `services/emotion_aware_therapeutic_assistant.py` provides emotion detection + CBT/DBT skill mapping; `utils/therapeutic_code_framework.py` wraps routes with therapeutic affordances.
- **Therapeutic + wellness features**: CBT/DBT routes (`routes/cbt_routes.py`, `routes/dbt_routes.py`), crisis flows (`routes/crisis_routes.py`, `utils/dbt_crisis_helper.py`), mental health resources, AA/recovery, personal growth, language learning, mood APIs, scheduling/tasks, social/finance integrations, drone/SEED optimization, memory services.
- **Safety & auth**: Crisis helpers, validation wrappers, session/login, API blueprints; security docs + checklists present.
- **Data & analytics**: Numerous models (192+) under `models/*`, health models (CBTThoughtRecord, DBTSkillLog, etc.), analytics routes/services; drone swarm for monitoring/optimization.

## Key Requirements from the PDF (condensed)
- **Therapeutic frameworks**: CBT (distortions, thought records, behavioral activation), DBT (TIP/TIPP, STOP, DEAR MAN, validation, safety plans), ACT + mindfulness (acceptance, values, grounding), positive psychology + behavioral activation, motivational interviewing, psychoeducation library.
- **Persona & UX**: Warm, empathic, validating tone; reflective listening; humor only when safe; bilingual EN/ES with cultural adaptation; persistent memory; explicit “not a therapist” boundary; user-led adaptive dialogue with quick exits.
- **Architecture**: Web chat → mobile app; multimedia (audio, images, timers); NLU for intent/emotion + high-sensitivity crisis classifiers; hybrid retrieval + constrained generative NLG; content repository with metadata; personal assistant integrations (calendar/tasks/info); personalization engine; analytics + feedback loop.
- **Safety & ethics**: Crisis protocol with hotline escalation and resource routing; bias/culture checks; privacy, consent, data deletion; regulatory awareness (wellness positioning, stepped-care, HIPAA-grade handling).

## Integration Blueprint (workstreams)
1) **Therapeutic Content System**
   - Create a structured content repository (YAML/JSON/Markdown) for exercises, scripts, psychoeducation, resources, hotlines, and prompts (EN/ES) with tags (e.g., `panic_attack_skill`, `sleep_hygiene`, `dbt_tipp`).
   - Service layer (`services/therapeutic_content_service.py`) to fetch by intent/emotion/context; versioned entries with clinical approval metadata.
   - Wire into `services/emotion_aware_therapeutic_assistant.py` and chat dispatcher retrieval path; add fallback templates for safety-critical responses.

2) **NLU + Safety Detection**
   - Add `services/nlu_service.py` to run intent + entity + emotion classifiers (fine-tuned transformer for emotion/distress, rules for fast intents; language detection for EN/ES).
   - High-sensitivity crisis classifier (self-harm, abuse, overdose) feeding `routes/crisis_routes.py` and a chat “crisis handler” that overrides normal flows.
   - Integrate NLU middleware into `core/chat/dispatcher.py` so every message is tagged before routing; surface tags to handlers and UnifiedAIService prompts.

3) **Dialogue Manager (Hybrid Retrieval + Guardrailed Generation)**
   - Extend dispatcher with state machine support: modes (task, wellness, crisis), context store, interruption handling.
   - Retrieval-first responses: pull from vetted content repo for psychoeducation, safety, and skills; generative model only used for style/variation with guardrails (forced function calls / templated slots).
   - Safety gate: any generative therapeutic advice is validated against allowed intents; otherwise fall back to retrieval template.

4) **Persona, Style, and Prompting**
   - Centralize persona/system prompts (empathy, validation-first, “not a therapist”, boundary rules, humor policy) and reuse across `UnifiedAIService` calls.
   - Add quick-reply suggestions per context (e.g., “Try a 5-4-3-2-1 grounding”, “Schedule a walk”, “Talk to someone now”) surfaced in chat UI.
   - Memory hooks: persist conversation snippets + user facts in `memory_service` / database for follow-ups (“How did the presentation go?”).

5) **Bilingual + Cultural Adaptation (EN/ES)**
   - Locale layer for content repository; maintain separate EN/ES artifacts reviewed by native clinicians; metadata for formality (`tú`/`usted`), region-specific resources, metaphors.
   - Auto language detection → switch persona + safety resource set; UI locale toggle; ensure crisis numbers per country.

6) **Safety & Crisis Flows**
   - Implement crisis flow in dispatcher: detect → respond with validation + resource offer → block normal intents until resolved; offer to call/text hotline (mobile) or show click-to-call.
   - Abuse/assault-specific scripts (validation + RAINN/local resources); overdose/medical emergency script urging 911/ER.
   - Optional user-provided safety plan + emergency contact; configurable policy for when to surface contacts (consent-driven).

7) **Therapy–Productivity Bridge**
   - Map therapeutic flows to personal assistant modules: after distress support, propose task/calendar organization; behavioral activation creates tasks/reminders via `tasks_routes.py`/`scheduler_service.py`.
   - Health behavior change flows use MI style; integrate with existing reminders, notifications, and wearable hooks (if present).

8) **Personalization & User Profile**
   - Extend profile to store preferences (likes/dislikes for exercises), PHQ-9/GAD-7 history, mood logs, best-response patterns, quiet hours.
   - Recommendation layer: suggest next-best exercise/content based on past helpfulness and current sentiment; respect opt-out (“anonymous mode”).

9) **UI/UX & Mobile Path**
   - Web chat updates: quick replies, chip menus for exercises, timers/animations for breathing, inline multimedia, mood tracker and goals dashboards; ensure Spanish UX parity.
   - Crisis UI always-visible “Get help now” entry; disclaimers visible in therapy contexts.
   - Mobile roadmap: package chat + push notifications for check-ins, JITAI nudges; offline access to saved toolkits/meditations.

10) **Analytics & Continuous Learning**
   - Instrument chat events, NLU tags, feature usage, thumbs-up/down; feed to analytics dashboards (routes/analytics, drones).
   - A/B test scripts/flows; nightly audits for unsafe outputs; feedback loop into content weights and prompt tuning.

11) **Privacy, Compliance, and Boundaries**
   - Enforce “not a therapist” messaging in onboarding, periodic reminders, and therapeutic screens.
   - Data controls: data export/delete, anonymous mode, minimal retention for crisis flows; encrypt at rest/in transit.
   - Claims discipline to stay in wellness/coach lane; document HIPAA-aligned handling for PHI; bias audits across demographics and languages.

## Delivery Roadmap (phased)
- **Phase 0 (foundation)**: Stand up content repository + NLU service + dispatcher hooks; wire crisis detection to crisis routes; add persona/prompt base; EN/ES detection.
- **Phase 1 (therapeutic core)**: Ship CBT/DBT/ACT/MI modules in content repo; retrieval-first responses; safety validation gate; quick replies + UI updates; Spanish parity for core flows.
- **Phase 2 (personalization + bridge)**: Profile enrichment, recommendations, behavioral activation → tasks/scheduler integration, calendar/reminder tie-ins; wellness–productivity blended flows.
- **Phase 3 (mobile + analytics)**: Push notifications/JITAI, offline toolkits, full analytics dashboards, A/B pipeline; broaden multimedia library.
- **Ongoing**: Clinical review cadence, bias/privacy audits, prompt/guardrail tuning, research/efficacy studies planning.

## Traceability (PDF → System)
- Therapeutic frameworks → content repo + `services/emotion_aware_therapeutic_assistant.py` + CBT/DBT routes, powered by hybrid retrieval/generative chat.
- Empathy/persona/bilingual → centralized prompts + locale-aware content + UI affordances.
- NLU/safety → new `services/nlu_service.py` + dispatcher middleware + crisis handlers.
- Personal assistant blend → existing scheduler/tasks/calendar/weather routes with therapeutic triggers.
- Analytics/learning → existing analytics/drone infrastructure plus new event instrumentation.
