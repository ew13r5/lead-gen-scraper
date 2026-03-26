from __future__ import annotations

import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import phonenumbers
from email_validator import EmailNotValidError, validate_email

from pipeline.base import PipelineStage

LEGAL_SUFFIXES = re.compile(
    r"\b(LLC|L\.L\.C\.|Inc\.?|Incorporated|Corp\.?|Corporation|Ltd\.?|Limited|Co\.?|Company|LP|LLP)\s*[,.]?\s*$",
    re.IGNORECASE,
)

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "mkt_tok", "mc_cid", "mc_eid",
}

ADDRESS_ABBREVS = {
    r"\bSt\b": "Street", r"\bAve\b": "Avenue", r"\bBlvd\b": "Boulevard",
    r"\bDr\b": "Drive", r"\bLn\b": "Lane", r"\bCt\b": "Court",
    r"\bRd\b": "Road", r"\bSte\b": "Suite", r"\bApt\b": "Apartment",
}


class FieldValidator(PipelineStage):
    def __init__(self, check_email_dns: bool = False) -> None:
        self._check_dns = check_email_dns
        self._stats = {}

    @property
    def name(self) -> str:
        return "field_validator"

    def process(self, data: list[dict]) -> list[dict]:
        stats = {"emails_validated": 0, "emails_invalid": 0, "phones_normalized": 0,
                 "phones_invalid": 0, "urls_cleaned": 0, "urls_invalid": 0}

        for record in data:
            self._validate_email(record, stats)
            self._normalize_phone(record, stats)
            self._clean_website(record, stats)
            self._normalize_company_name(record)
            self._standardize_address(record)

        self._stats = stats
        return data

    def run(self, data, **kw):
        result_data, stage_result = super().run(data)
        stage_result.details = self._stats
        return result_data, stage_result

    def _validate_email(self, record: dict, stats: dict) -> None:
        email = record.get("email")
        if not email:
            return
        try:
            result = validate_email(email, check_deliverability=self._check_dns)
            record["email"] = result.normalized
            record["email_validated"] = True
            stats["emails_validated"] += 1
        except EmailNotValidError:
            record["email"] = None
            record["email_validated"] = False
            stats["emails_invalid"] += 1

    def _normalize_phone(self, record: dict, stats: dict) -> None:
        phone = record.get("phone")
        if not phone:
            return
        try:
            parsed = phonenumbers.parse(phone, "US")
            if phonenumbers.is_valid_number(parsed):
                record["phone_normalized"] = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
                record["phone_display"] = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
                stats["phones_normalized"] += 1
            else:
                record["phone_normalized"] = None
                stats["phones_invalid"] += 1
        except phonenumbers.NumberParseException:
            record["phone_normalized"] = None
            stats["phones_invalid"] += 1

    def _clean_website(self, record: dict, stats: dict) -> None:
        url = record.get("website")
        if not url:
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        parsed = urlparse(url)
        if not parsed.netloc:
            record["website"] = None
            stats["urls_invalid"] += 1
            return
        if parsed.query:
            params = parse_qs(parsed.query, keep_blank_values=False)
            clean_params = {k: v for k, v in params.items() if k.lower() not in TRACKING_PARAMS}
            clean_query = urlencode(clean_params, doseq=True)
        else:
            clean_query = ""
        path = parsed.path.rstrip("/") if parsed.path != "/" else "/"
        cleaned = urlunparse((parsed.scheme, parsed.netloc.lower(), path, parsed.params, clean_query, ""))
        record["website"] = cleaned
        stats["urls_cleaned"] += 1

    def _normalize_company_name(self, record: dict) -> None:
        name = record.get("company_name")
        if not name:
            return
        normalized = name.lower().strip()
        normalized = LEGAL_SUFFIXES.sub("", normalized).strip()
        record["company_name_normalized"] = normalized

    def _standardize_address(self, record: dict) -> None:
        address = record.get("address")
        if not address:
            return
        normalized = address
        for pattern, replacement in ADDRESS_ABBREVS.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        record["address_normalized"] = normalized
