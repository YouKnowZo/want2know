#!/usr/bin/env python3
import sys
import json
import os

LINE_TYPE_MAP = {
    0:  "Fixed Line", 1:  "Mobile", 2:  "Fixed Line or Mobile",
    3:  "Toll Free", 4:  "Premium Rate", 5:  "Shared Cost",
    6:  "VoIP", 7:  "Personal Number", 8:  "Pager",
    9:  "UAN", 10: "Voicemail", 20: "Unknown", -1: "Not a Number",
}

RISK_BY_TYPE = {
    "Toll Free": ("medium", "Often used by businesses or robocallers"),
    "Premium Rate": ("high", "Premium-rate numbers can incur charges"),
    "VoIP": ("medium", "VoIP numbers are commonly used in scams/spoofing"),
    "Personal Number": ("medium", "Personal-number forwarding can hide true location"),
    "Pager": ("low", "Legacy line"),
    "Voicemail": ("low", "Voicemail-only line"),
    "Unknown": ("medium", "Carrier did not classify this line"),
    "UAN": ("low", "Universal access number"),
    "Mobile": ("low", "Standard mobile line"),
    "Fixed Line": ("low", "Standard landline"),
    "Fixed Line or Mobile": ("low", "Standard line"),
}

def load_area_codes():
    path = os.path.join(os.path.dirname(__file__), "data", "area_codes.json")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}

def lookup(number):
    result = {
        "number": number, "valid": False, "country_code": "", "country_name": "",
        "location": "", "carrier": "", "line_type": "", "timezones": [],
        "international_format": "", "national_format": "", "e164_format": "",
        "rfc3966_format": "", "area_code": "", "area_city": "", "area_state": "",
        "risk_level": "", "risk_note": "", "is_possible": False,
        "region_code": "", "error": ""
    }
    try:
        import phonenumbers
        from phonenumbers import carrier as ph_carrier
        from phonenumbers import geocoder as ph_geocoder
        from phonenumbers import timezone as ph_timezone

        parsed = phonenumbers.parse(number, None)
        result["valid"] = phonenumbers.is_valid_number(parsed)
        result["is_possible"] = phonenumbers.is_possible_number(parsed)

        if result["valid"]:
            fmt = phonenumbers.PhoneNumberFormat
            result["international_format"] = phonenumbers.format_number(parsed, fmt.INTERNATIONAL)
            result["national_format"]      = phonenumbers.format_number(parsed, fmt.NATIONAL)
            result["e164_format"]          = phonenumbers.format_number(parsed, fmt.E164)
            result["rfc3966_format"]       = phonenumbers.format_number(parsed, fmt.RFC3966)
            result["country_code"]         = str(parsed.country_code)
            result["region_code"]          = phonenumbers.region_code_for_number(parsed) or ""
            result["country_name"]         = ph_geocoder.description_for_number(parsed, "en")
            result["location"]             = ph_geocoder.description_for_number(parsed, "en")
            result["carrier"]              = ph_carrier.name_for_number(parsed, "en") or "Unknown"
            num_type                       = phonenumbers.number_type(parsed)
            line_type_str                  = LINE_TYPE_MAP.get(int(num_type), str(num_type))
            result["line_type"]            = line_type_str
            result["timezones"]            = list(ph_timezone.time_zones_for_number(parsed))

            risk_level, risk_note = RISK_BY_TYPE.get(line_type_str, ("low", "Standard line"))
            result["risk_level"] = risk_level
            result["risk_note"] = risk_note

            # US area-code → city/state enrichment
            if result["region_code"] == "US":
                national_digits = "".join(ch for ch in result["national_format"] if ch.isdigit())
                if len(national_digits) >= 3:
                    npa = national_digits[:3]
                    result["area_code"] = npa
                    codes = load_area_codes()
                    if npa in codes:
                        info = codes[npa]
                        result["area_city"] = info.get("city", "")
                        result["area_state"] = info.get("state", "")
                        if not result["location"] or result["location"] == "United States":
                            city_state = ", ".join([x for x in [info.get("city",""), info.get("state","")] if x])
                            if city_state:
                                result["location"] = city_state
        else:
            result["error"] = "Invalid or unrecognized phone number"
    except Exception as e:
        result["error"] = str(e)

    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No phone number provided"}))
    else:
        lookup(sys.argv[1])
