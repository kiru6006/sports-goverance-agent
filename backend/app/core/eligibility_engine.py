import json
import datetime
from typing import Dict, Any, List, Optional

SCHEME_RULE_SCHEMA = {
    "type": "object",
    "required": ["criteria", "required_fields", "schema_version"],
    "properties": {
        "schema_version": {"type": "string"},
        "valid_for": {
            "type": "object",
            "properties": {
                "states": {"type": "array", "items": {"type": "string"}},
                "districts": {"type": "array", "items": {"type": "string"}},
                "sports": {"type": "array", "items": {"type": "string"}},
                "age_bands": {"type": "array", "items": {"type": "string"}},
                "gender": {"type": "array", "items": {"type": "string"}}
            }
        },
        "required_fields": {"type": "array", "items": {"type": "string"}},
        "criteria": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["field", "operator", "value", "reason_text"],
                "properties": {
                    "field": {"type": "string"},
                    "operator": {"type": "string", "enum": ["eq", "in", "gte", "lte", "between", "exists"]},
                    "value": {},
                    "reason_text": {"type": "string"}
                }
            }
        }
    }
}

def validate_rule_json(rule_dict: Dict[str, Any]) -> List[str]:
    """Validate rule dictionary structure against closed schema."""
    errors = []
    if "criteria" not in rule_dict or not isinstance(rule_dict["criteria"], list):
        errors.append("criteria must be a list of rule conditions")
    if "required_fields" not in rule_dict or not isinstance(rule_dict["required_fields"], list):
        errors.append("required_fields list is mandatory")
    
    valid_ops = {"eq", "in", "gte", "lte", "between", "exists"}
    for idx, c in enumerate(rule_dict.get("criteria", [])):
        if "field" not in c:
            errors.append(f"criterion[{idx}] missing field")
        if c.get("operator") not in valid_ops:
            errors.append(f"criterion[{idx}] invalid operator: {c.get('operator')}")
        if "reason_text" not in c:
            errors.append(f"criterion[{idx}] missing reason_text")
    return errors

def evaluate_scheme_eligibility(
    athlete_profile: Dict[str, Any],
    rule_dict: Dict[str, Any],
    source_ref: Dict[str, str],
    rule_version: str
) -> Dict[str, Any]:
    """
    Deterministic rule evaluator:
    - Only evaluates approved rules.
    - If any required field is missing/None: returns eligible = None with missing_fields. Never returns False.
    - Deterministic across runs for identical inputs.
    """
    required_fields = rule_dict.get("required_fields", [])
    missing_fields = []
    for f in required_fields:
        if f not in athlete_profile or athlete_profile[f] is None:
            missing_fields.append(f)

    if missing_fields:
        return {
            "eligible": None,
            "missing_fields": missing_fields,
            "reasons": [{"code": "MISSING_REQUIRED_DATA", "reason_text": f"Required fields missing: {missing_fields}"}],
            "rule_version": rule_version,
            "source_refs": [source_ref],
            "evaluated_at": datetime.datetime.utcnow().isoformat()
        }

    # Evaluate criteria
    reasons = []
    all_passed = True

    for c in rule_dict.get("criteria", []):
        field = c["field"]
        op = c["operator"]
        target_val = c["value"]
        actual_val = athlete_profile.get(field)
        reason_text = c["reason_text"]

        passed = False
        if op == "eq":
            passed = actual_val == target_val
        elif op == "in":
            passed = actual_val in target_val if isinstance(target_val, list) else False
        elif op == "gte":
            passed = actual_val >= target_val
        elif op == "lte":
            passed = actual_val <= target_val
        elif op == "between":
            passed = target_val[0] <= actual_val <= target_val[1]
        elif op == "exists":
            passed = actual_val is not None

        if not passed:
            all_passed = False
            reasons.append({"field": field, "passed": False, "reason_text": f"Did not meet requirement: {reason_text}"})
        else:
            reasons.append({"field": field, "passed": True, "reason_text": f"Met requirement: {reason_text}"})

    return {
        "eligible": all_passed,
        "missing_fields": [],
        "reasons": reasons,
        "rule_version": rule_version,
        "source_refs": [source_ref],
        "evaluated_at": datetime.datetime.utcnow().isoformat()
    }
