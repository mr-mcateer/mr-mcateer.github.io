"""
anonymizer.py -- Student Identity Anonymizer

Replaces student names and IDs with deterministic pseudonyms before
data is sent to external APIs (Gemini). Maps back after responses return.

Pseudonyms are deterministic within a session (same name always produces
same pseudonym) but not reversible without the mapping table.

Usage:
    from anonymizer import AnonymizationContext

    ctx = AnonymizationContext()
    pseudonym = ctx.anonymize_name("Jane Doe")       # "Student_7A3F"
    fake_id = ctx.anonymize_id(12345678)              # 82914637
    clean_text = ctx.anonymize_text("Jane Doe scored 85%")  # "Student_7A3F scored 85%"
    real_text = ctx.deanonymize_text("Student_7A3F scored 85%")  # "Jane Doe scored 85%"
"""

import hashlib
import re


class AnonymizationContext:
    """
    Maintains a bidirectional mapping between real student identities
    and pseudonyms for the duration of a grading session.
    """

    def __init__(self, salt: str = ""):
        """
        Args:
            salt: Optional session-specific salt. If empty, pseudonyms are
                  consistent across calls but predictable. Adding a salt
                  (e.g., today's date) makes them session-unique.
        """
        self._salt = salt
        self._name_to_pseudo: dict[str, str] = {}
        self._pseudo_to_name: dict[str, str] = {}
        self._id_to_pseudo: dict[int, int] = {}
        self._pseudo_to_id: dict[int, int] = {}

    def anonymize_name(self, real_name: str) -> str:
        """
        Replace a real student name with a deterministic pseudonym.
        Format: Student_<4-hex-chars> (e.g., Student_7A3F)
        """
        if not real_name or real_name.startswith("Student_"):
            return real_name

        if real_name in self._name_to_pseudo:
            return self._name_to_pseudo[real_name]

        # Deterministic hash
        h = hashlib.sha256(f"{self._salt}:{real_name}".encode()).hexdigest()
        pseudonym = f"Student_{h[:4].upper()}"

        # Handle collisions (rare but possible with 4 hex chars)
        suffix = 4
        while pseudonym in self._pseudo_to_name:
            suffix += 1
            pseudonym = f"Student_{h[:suffix].upper()}"

        self._name_to_pseudo[real_name] = pseudonym
        self._pseudo_to_name[pseudonym] = real_name
        return pseudonym

    def anonymize_id(self, real_id: int) -> int:
        """
        Replace a real Canvas user ID with a deterministic fake ID.
        Preserves digit count for format consistency.
        """
        if real_id in self._id_to_pseudo:
            return self._id_to_pseudo[real_id]

        h = hashlib.sha256(f"{self._salt}:id:{real_id}".encode()).hexdigest()
        # Generate a fake ID with the same number of digits
        digit_count = len(str(real_id))
        fake_id = int(h[:digit_count], 16) % (10 ** digit_count)
        # Ensure it doesn't collide
        while fake_id in self._pseudo_to_id:
            fake_id = (fake_id + 1) % (10 ** digit_count)

        self._id_to_pseudo[real_id] = fake_id
        self._pseudo_to_id[fake_id] = real_id
        return fake_id

    def deanonymize_name(self, pseudonym: str) -> str:
        """Reverse a pseudonym back to the real name."""
        return self._pseudo_to_name.get(pseudonym, pseudonym)

    def deanonymize_id(self, fake_id: int) -> int:
        """Reverse a fake ID back to the real Canvas user ID."""
        return self._pseudo_to_id.get(fake_id, fake_id)

    def anonymize_text(self, text: str) -> str:
        """
        Scan text for all known real names and replace with pseudonyms.
        Processes longer names first to avoid partial replacements.
        """
        if not text or not isinstance(text, str):
            return text or ""

        result = text
        # Sort by length descending to avoid partial matches
        for real_name in sorted(self._name_to_pseudo.keys(), key=len, reverse=True):
            pseudonym = self._name_to_pseudo[real_name]
            result = result.replace(real_name, pseudonym)
        return result

    def deanonymize_text(self, text: str) -> str:
        """
        Scan text for all pseudonyms and replace with real names.
        Processes longer pseudonyms first.
        """
        if not text or not isinstance(text, str):
            return text or ""

        result = text
        for pseudonym in sorted(self._pseudo_to_name.keys(), key=len, reverse=True):
            real_name = self._pseudo_to_name[pseudonym]
            result = result.replace(pseudonym, real_name)
        return result

    def anonymize_parts(self, parts: list) -> list:
        """
        Anonymize a list of submission parts (mixed strings and PIL Images).
        Only processes string elements; images pass through unchanged.
        """
        anonymized = []
        for part in parts:
            if isinstance(part, str):
                anonymized.append(self.anonymize_text(part))
            else:
                anonymized.append(part)
        return anonymized

    @property
    def student_count(self) -> int:
        """Number of students currently registered in this context."""
        return len(self._name_to_pseudo)


if __name__ == "__main__":
    # Quick self-test
    ctx = AnonymizationContext(salt="test-session")

    name = "Jane Doe"
    pseudo = ctx.anonymize_name(name)
    print(f"Anonymize: {name!r} -> {pseudo!r}")
    assert ctx.anonymize_name(name) == pseudo, "Deterministic check failed"
    assert ctx.deanonymize_name(pseudo) == name, "Deanonymize check failed"

    uid = 12345678
    fake = ctx.anonymize_id(uid)
    print(f"Anonymize ID: {uid} -> {fake}")
    assert ctx.deanonymize_id(fake) == uid, "ID deanonymize check failed"

    text = "Jane Doe submitted a great project. Jane Doe scored 95%."
    anon_text = ctx.anonymize_text(text)
    print(f"Anonymize text: {anon_text!r}")
    assert name not in anon_text, "Name leaked in anonymized text"
    assert ctx.deanonymize_text(anon_text) == text, "Text deanonymize failed"

    print("All anonymizer tests passed.")
