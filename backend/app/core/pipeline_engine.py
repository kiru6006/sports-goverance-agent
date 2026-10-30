import statistics
import datetime
from typing import List, Dict, Any, Optional

def compute_peer_median(rates: List[float]) -> float:
    """Computes median rate across peer districts."""
    if not rates:
        return 0.0
    return float(statistics.median(rates))

def evaluate_district_gap(
    district_rate: float,
    peer_rates: List[float],
    threshold_multiplier: float = 0.50
) -> Dict[str, Any]:
    """
    Evaluates whether a district has a talent identification gap:
    Flags cell if district rate < threshold_multiplier * peer_median.
    Returns transparent reasons array.
    """
    peer_med = compute_peer_median(peer_rates)
    threshold = round(peer_med * threshold_multiplier, 2)
    is_gap = district_rate < threshold

    reasons = []
    if is_gap:
        reasons.append({
            "code": "BELOW_PEER_MEDIAN_THRESHOLD",
            "threshold_used": threshold_multiplier,
            "peer_median_rate_per_100k": round(peer_med, 2),
            "district_rate_per_100k": round(district_rate, 2),
            "gap_deficit_per_100k": round(threshold - district_rate, 2),
            "advisory_label": "Advisory indicator only. Not a district performance ranking."
        })

    return {
        "is_gap": is_gap,
        "district_rate": round(district_rate, 2),
        "peer_median": round(peer_med, 2),
        "threshold": threshold,
        "reasons": reasons
    }

def calculate_funnel_stages(
    athletes: List[Dict[str, Any]],
    support_records: List[Dict[str, Any]],
    achievements: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Cumulative conversion funnel:
    - Identified: total in sport/district/age_band
    - Verified: status == VERIFIED
    - Supported: has active/completed SupportRecord
    - Progressed: has achievement with date >= support start date
    Invariant: Identified >= Verified >= Supported >= Progressed
    """
    identified_ids = {a["id"] for a in athletes}
    verified_ids = {a["id"] for a in athletes if a.get("verification_status") == "VERIFIED"}
    
    # Supported: athlete must be verified and have support record
    supported_athlete_ids = set()
    support_start_dates = {}
    for sr in support_records:
        if sr.get("athlete_id") in verified_ids and sr.get("status") in ("ACTIVE", "COMPLETED"):
            supported_athlete_ids.add(sr["athlete_id"])
            if sr["athlete_id"] not in support_start_dates or sr.get("start_date") < support_start_dates[sr["athlete_id"]]:
                support_start_dates[sr["athlete_id"]] = sr.get("start_date")

    # Progressed: athlete must be supported and have achievement after support start
    progressed_athlete_ids = set()
    for ach in achievements:
        ath_id = ach.get("athlete_id")
        if ath_id in supported_athlete_ids:
            start_d = support_start_dates.get(ath_id)
            if start_d and ach.get("event_date") >= start_d:
                progressed_athlete_ids.add(ath_id)

    return {
        "identified": len(identified_ids),
        "verified": len(verified_ids),
        "supported": len(supported_athlete_ids),
        "progressed": len(progressed_athlete_ids)
    }
