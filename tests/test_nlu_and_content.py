import json
from services.nlu_service import NLUService
from services.therapeutic_content_service import TherapeuticContentService
from services.dialogue_manager import DialogueManager


def test_nlu_language_and_crisis_detection():
    nlu = NLUService()
    res_es = nlu.analyze("Me siento muy mal, necesito ayuda urgente", user_id="u1")
    assert res_es.language == "es"
    assert res_es.crisis is None or isinstance(res_es.crisis, dict)

    res_crisis = nlu.analyze("I want to kill myself", user_id="u1")
    assert res_crisis.crisis is not None
    assert res_crisis.risk_level == "high"
    assert "crisis" in res_crisis.tags


def test_content_retrieval_matches_tags():
    content_service = TherapeuticContentService()
    result = content_service.get_best_content(tags=["dbt_tipp", "crisis"], locale="en")
    assert result is not None
    assert "tipp" in " ".join(result.get("tags", [])).lower()
    assert result.get("locale") == "en"

    found_by_id = content_service.get_by_id(result.get("id"), locale="en")
    assert found_by_id is not None
    assert found_by_id.get("id") == result.get("id")


def test_dialogue_mode_selection():
    dm = DialogueManager()
    nlu = NLUService()
    res_crisis = nlu.analyze("I am thinking about suicide", user_id="u2")
    assert dm.determine_mode(res_crisis, {}) == "crisis"

    res_task = nlu.analyze("Schedule a reminder to walk", user_id="u3")
    assert dm.determine_mode(res_task, {}) in {"task", "wellness"}
