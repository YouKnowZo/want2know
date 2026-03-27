#!/usr/bin/env python3
import sys
import json

def lookup(number):
    result = {
        "number": number,
        "valid": False,
        "country_code": "",
        "country_name": "",
        "location": "",
        "carrier": "",
        "line_type": "",
        "timezones": [],
        "international_format": "",
        "national_format": "",
        "error": ""
    }
    try:
        import phonenumbers
        from phonenumbers import carrier as ph_carrier
        from phonenumbers import geocoder as ph_geocoder
        from phonenumbers import timezone as ph_timezone

        parsed = phonenumbers.parse(number, None)
        result["valid"] = phonenumbers.is_valid_number(parsed)

        if result["valid"]:
            result["international_format"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            result["national_format"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
            result["country_code"] = str(parsed.country_code)
            result["country_name"] = ph_geocoder.description_for_number(parsed, "en")
            result["location"] = ph_geocoder.description_for_number(parsed, "en")
            result["carrier"] = ph_carrier.name_for_number(parsed, "en")
            result["line_type"] = str(phonenumbers.number_type(parsed)).replace("PhoneNumberType.", "")
            result["timezones"] = list(ph_timezone.time_zones_for_number(parsed))
        else:
            result["error"] = "Invalid phone number"
    except Exception as e:
        result["error"] = str(e)

    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No phone number provided"}))
    else:
        lookup(sys.argv[1])
