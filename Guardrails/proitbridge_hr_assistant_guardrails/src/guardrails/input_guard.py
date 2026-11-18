from functools import lru_cache

from guardrails import Guard, OnFailAction
from guardrails_ai.ban_list import BanList
from guardrails_ai.detect_pii import DetectPII
from guardrails_ai.valid_length import ValidLength

from src.access.permissions import can_see_all_records
from src.core.config import BANNED_PHRASES, INPUT_PII, MAX_QUESTION_CHARS
from src.guardrails.validators import MaskIndianIDs, OtherEmployeeCheck


@lru_cache
def input_pii():
    return DetectPII(pii_entities=INPUT_PII, on_fail=OnFailAction.FIX)


@lru_cache
def input_guard_for(role):
    validators = [ValidLength(min=3, max=MAX_QUESTION_CHARS, on_fail=OnFailAction.EXCEPTION),
                  BanList(banned_words=BANNED_PHRASES, on_fail=OnFailAction.EXCEPTION)]
    if not can_see_all_records(role):
        validators.append(OtherEmployeeCheck(on_fail=OnFailAction.EXCEPTION))
    validators += [input_pii(),
                   MaskIndianIDs(on_fail=OnFailAction.FIX)]
    return Guard().use(*validators)


@lru_cache
def mask_only_guard():
    return Guard().use(input_pii(),
                       MaskIndianIDs(on_fail=OnFailAction.FIX))
