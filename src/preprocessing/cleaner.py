"""
src/preprocessing/cleaner.py

Purpose:
    Normalizes transcript text by stripping control characters and harmonizing whitespace.

Working & Flow:
    - `clean_text(raw_text)` removes redundant blank lines and trailing spaces.
    - Preserves line breaks for transcript structure retention.

Links to:
    - src/ingestion/parser.py
    - src/preprocessing/chunker.py
"""

import re


class TranscriptCleaner:
    """Cleans and standardizes raw transcript strings."""

    @staticmethod
    def clean_text(raw_text: str) -> str:
        if not raw_text:
            return ""
        # Remove null/control bytes
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", raw_text)
        # Normalize non-breaking spaces
        text = text.replace("\xa0", " ")
        # Normalize multiple spaces per line
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
        # Strip consecutive blank lines
        cleaned_lines = []
        prev_blank = False
        for line in lines:
            if not line:
                if not prev_blank:
                    cleaned_lines.append("")
                prev_blank = True
            else:
                cleaned_lines.append(line)
                prev_blank = False
        return "\n".join(cleaned_lines)
