import re

from guardrails.validators import Validator, register_validator, PassResult, FailResult

ID_PATTERNS = {"<PAN>"         : r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
               "<AADHAAR>"     : r"\b\d{4}\s?\d{4}\s?\d{4}\b",
               "<BANK_ACCOUNT>": r"\b\d{9,18}\b"}


@register_validator(name="proitbridge/mask_indian_ids", data_type="string")
class MaskIndianIDs(Validator):
    def _validate(self, value, metadata):
        masked = value
        for tag, pattern in ID_PATTERNS.items():
            masked = re.sub(pattern, tag, masked)
        if masked == value:
            return PassResult()
        return FailResult(error_message="Indian ID numbers found.",
                          fix_value=masked)


@register_validator(name="proitbridge/other_employee_check", data_type="string")
class OtherEmployeeCheck(Validator):
    def _validate(self, value, metadata):
        for name in metadata.get("other_employees", []):
            if re.search(rf"\b{re.escape(name)}\b", value, flags=re.IGNORECASE):
                return FailResult(error_message="The question is about another employee.")
        return PassResult()
