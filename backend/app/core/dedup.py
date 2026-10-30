import re
from difflib import SequenceMatcher
from typing import List, Dict, Any

def normalize_name(name: str) -> str:
    """Strip titles, punctuation, and multiple spaces."""
    cleaned = re.sub(r'\b(mr|ms|mrs|shri|smt|master|miss)\b\.?', '', name, flags=re.IGNORECASE)
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned)
    return " ".join(cleaned.lower().split())

def name_similarity(name1: str, name2: str) -> float:
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    return SequenceMatcher(None, n1, n2).ratio()

def find_duplicate_candidates(
    name: str,
    dob_str: str,
    district_id: str,
    existing_athletes: List[Dict[str, Any]],
    threshold: float = 0.75
) -> List[Dict[str, Any]]:
    """
    Evaluates candidate duplicates based on:
    - Fuzzy match on normalized name
    - Exact or close DOB (same year)
    - District match
    NEVER auto-merges records.
    """
    candidates = []
    norm_input = normalize_name(name)
    input_year = dob_str.split("-")[0] if "-" in dob_str else ""

    for ath in existing_athletes:
        sim = name_similarity(norm_input, ath.get("name", ""))
        ath_dob = ath.get("dob", "")
        ath_year = ath_dob.split("-")[0] if "-" in ath_dob else ""
        
        dob_match_type = "none"
        if ath_dob == dob_str:
            dob_match_type = "exact"
        elif ath_year and input_year and abs(int(input_year) - int(ath_year)) <= 1:
            dob_match_type = "within_1_year"

        same_district = ath.get("district_id") == district_id
        
        match_fields = []
        score = sim * 0.5
        if sim >= 0.7:
            match_fields.append("name")

        if dob_match_type == "exact":
            score += 0.35
            match_fields.append("dob_exact")
        elif dob_match_type == "within_1_year":
            score += 0.20
            match_fields.append("dob_close")

        if same_district:
            score += 0.15
            match_fields.append("district")

        if score >= threshold:
            candidates.append({
                "athlete_id": ath.get("id"),
                "kid": ath.get("kid"),
                "name": ath.get("name"),
                "confidence_score": round(score, 2),
                "name_similarity": round(sim, 2),
                "dob_match": dob_match_type,
                "district_match": same_district,
                "match_fields": match_fields
            })

    # Sort descending by confidence
    candidates.sort(key=lambda x: x["confidence_score"], reverse=True)
    return candidates
