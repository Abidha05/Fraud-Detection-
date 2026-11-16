from datetime import datetime
import math

REQUIRED_FIELDS = ["transaction_id",
                    "customer_id", 
                    "amount", 
                    "merchant", 
                    "city", 
                    "device", 
                    "timestamp"]
def validate_transaction(transaction):
    if not isinstance(transaction, dict):
        return False, ["Transaction must be a dictionary"]

    errors = []

    for field in REQUIRED_FIELDS:
        value = transaction.get(field)
        if value is None or value == "":
            errors.append(f"{field} is required")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"{field} cannot be empty or whitespace")

    for field in ("transaction_id", "customer_id", "merchant", "city", "device"):
        value = transaction.get(field)
        if value is not None and not isinstance(value, str):
            errors.append(f"{field} must be a string")

    amount = transaction.get("amount")
    if (
        isinstance(amount, bool)
        or not isinstance(amount, (int, float))
        or not math.isfinite(amount)
        or amount < 0
    ):
        errors.append("amount must be a finite, non-negative number")

    timestamp = transaction.get("timestamp")
    if not isinstance(timestamp, str):
        errors.append("timestamp must be ISO datetime text")
    else:
        try:
            parsed = datetime.fromisoformat(timestamp)
            if parsed.tzinfo is None:
                errors.append("timestamp must include a timezone")
        except ValueError:
            errors.append("timestamp has invalid format")

    return len(errors) == 0, errors