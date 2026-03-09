"""Utility functions for handling report numbers and Rashut formats."""

import re
from typing import Optional


def report_number_to_int(report_number: str) -> Optional[int]:
    """
    Convert a report number string to an integer ID.
    
    Supports:
    - Pure digit strings, with or without leading zeros (e.g. '000000251531')
    - Rashut format with prefix (e.g. '000ACT251531' or '000ACT000251531'),
      where the actual numeric part is the trailing digits.
    """
    if report_number is None:
        return None

    s = str(report_number).strip()
    if not s:
        return None

    # If it contains only digits, parse directly
    if s.isdigit():
        try:
            return int(s)
        except ValueError:
            return None

    # Handle Rashut prefix format like 000ACTxxxxxx (take trailing digits)
    match = re.search(r'(\d+)$', s)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None

    return None


def report_number_normalize(report_number: str) -> str:
    """
    Normalize a report number string to a plain integer string for internal use.
    
    Returns:
        String integer representation (e.g. '251531') or empty string on failure.
    """
    value = report_number_to_int(report_number)
    return str(value) if value is not None else ""


def report_id_to_rashut_display(report_id) -> str:
    """
    Format integer report_id as Rashut display string: 000ACT + 6 zero-padded digits.
    E.g. 251531 -> '000ACT251531', 460 -> '000ACT000460'.
    """
    if report_id is None:
        return ""
    try:
        return "000ACT" + str(int(report_id)).zfill(6)
    except (ValueError, TypeError):
        return ""

