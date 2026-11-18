from functools import lru_cache

from guardrails import Guard, OnFailAction
from guardrails_ai.detect_pii import DetectPII

from src.access.permissions import can_see_full_numbers
from src.core.config import OUTPUT_PII
from src.guardrails.validators import MaskIndianIDs


@lru_cache
def output_pii():
    return DetectPII(pii_entities=OUTPUT_PII, on_fail=OnFailAction.FIX)


@lru_cache
def output_guard_for(role):
    if can_see_full_numbers(role):
        return None
    return Guard().use(output_pii(),
                       MaskIndianIDs(on_fail=OnFailAction.FIX))
