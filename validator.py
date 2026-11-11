from datetime import datetime, timezone
import math
from pickle import FALSE 

REQUIRED_FIELDS = ["transaction_id", 
                   "customer_id", 
                   "amount", 
                   "merchant", 
                   "city", 
                   "device", 
                   "timestamp"]

def validate_transaction(transaction):
    errors = []
    if not isinstance(transaction, dict):
        return FALSE, ["Transaction must be a dictionary."]

    #check for required fields
    for field in REQUIRED_FIELDS:
        value = transaction.get(field)
        if value is None or value == "":
            errors.append(f"Missing or empty required field: {field}")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"Field '{field}' cannot be empty or whitespace.")

        # validate id and description fields

        for field in ["transaction_id", "customer_id", "merchant", "city", "device"]:
            value = transaction.get(field)
            if value is not None and not isinstance(value, str):
                errors.append(f"Field '{field}' must be a string.")

        # validate amount field
        amount = transaction.get("amount")
        if isinstance(amount,bool) or not isinstance(amount, (int, float)) or not math.isinfinite(amount) and amount < 0:
            errors.append("Amount must be in finite numbe.") 


        # validate timestamp field
        timestamp = transaction.get("timestamp")
        if not isinstance(timestamp, str):
            errors.append("Timestamp must be a ISO datetime text")
        else:
            try:
                parsed = datetime.fromisoformat(timestamp)
                if parsed.tzinfo is None:
                    errors.append("Timestamp must be a ISO timestamp.")
            except ValueError:
                errors.append("Timestamp have invalid ISO format")

        return 