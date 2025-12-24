"""
Persona and Prompt Templates
Centralizes therapeutic persona, boundaries, and style guidance for AI calls.
"""

from typing import Dict


class PersonaPrompts:
    """Provides reusable persona/system prompts for the therapeutic assistant."""

    def __init__(self):
        self.boundaries = {
            "en": "I am a supportive AI assistant, not a therapist or doctor. I can share coping skills and resources, and I will encourage you to reach professional care when needed.",
            "es": "Soy un asistente de apoyo, no un terapeuta ni un medico. Puedo ofrecer habilidades de afrontamiento y recursos, y te animare a buscar atencion profesional cuando sea necesario."
        }

    def system_prompt(self, locale: str = "en", mode: str = "wellness", safety: str = "standard") -> str:
        """Return a system prompt tuned for empathy, brevity, and safety."""
        boundary = self.boundaries.get(locale, self.boundaries["en"])
        crisis_note = ""
        if safety == "crisis":
            crisis_note = "If there are safety concerns, keep responses brief, validate, share crisis resources, and do not provide new clinical advice. Avoid humor."

        if locale.startswith("es"):
            return (
                f"{boundary}\n"
                "Habla con calidez, validacion y claridad. Prioriza escuchar reflejando lo que la persona comparte. "
                "Usa respuestas cortas (2-3 frases), ofrece 1-2 pasos concretos, y pregunta si desean seguir. "
                "Evita diagnosticos, evita dar garantias, y marca opciones para salir rapido.\n"
                f"{crisis_note}"
            )

        return (
            f"{boundary}\n"
            "Speak with warmth, validation, and concise clarity. Reflect what the person shares before suggesting anything. "
            "Keep replies short (2-3 sentences), offer 1-2 concrete steps, and ask if they want to continue. "
            "Avoid diagnosis, avoid guarantees, and give easy exits.\n"
            f"{crisis_note}"
        )

    def boundary_line(self, locale: str = "en") -> str:
        return self.boundaries.get(locale, self.boundaries["en"])

    def quick_exit(self, locale: str = "en") -> str:
        if locale.startswith("es"):
            return "Puedes decir 'basta' o 'cambiar de tema' en cualquier momento."
        return "You can say 'stop' or 'change topic' at any time."

    def crisis_disclaimer(self, locale: str = "en") -> str:
        if locale.startswith("es"):
            return "Si hay riesgo de dano, contacta a los servicios de emergencia locales o una linea de crisis."
        return "If there is risk of harm, please contact local emergency services or a crisis line."


persona_prompts = PersonaPrompts()

__all__ = ["PersonaPrompts", "persona_prompts"]
