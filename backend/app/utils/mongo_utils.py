from typing import Any
from datetime import datetime

try:
    from bson import ObjectId
except Exception:
    class ObjectId:  # type: ignore
        pass


def _convert_value(v: Any) -> Any:
    """Convert single value to JSON-serializable form."""
    if v is None:
        return None
        
    # Handle MongoDB Extended JSON format
    if isinstance(v, dict):
        # Handle $oid (ObjectId)
        if "$oid" in v:
            return v["$oid"]
        # Handle $date (ISODate)
        if "$date" in v:
            return v["$date"]
        # Regular dict - recurse
        return bson_to_json(v)
        
    # ObjectId -> str
    if isinstance(v, ObjectId):
        return str(v)
    # datetime -> ISO string
    if isinstance(v, datetime):
        return v.isoformat()
    # bytes -> decode if possible
    if isinstance(v, (bytes, bytearray)):
        try:
            return v.decode()
        except Exception:
            return str(v)
    # list/tuple -> recurse
    if isinstance(v, (list, tuple)):
        return [_convert_value(x) for x in v]
    # default: return as-is (JSON serializable types)
    return v


def bson_to_json(doc: Any) -> Any:
    """Convert a MongoDB/BSON document (or nested structure) to a JSON-safe dict.

    - Renames `_id` to `id` and converts it to string
    - Converts ObjectId and datetime values to strings
    - Recursively converts nested dicts and lists
    """
    if doc is None:
        return None

    if isinstance(doc, dict):
        out = {}
        for k, v in doc.items():
            # Special handling for _id field
            if k == "_id":
                if isinstance(v, dict) and "$oid" in v:
                    out["id"] = v["$oid"]
                else:
                    out["id"] = str(v)  # Convert ObjectId to string directly
                continue
            
            # Convert the value
            converted = _convert_value(v)
            # Don't add None values to output
            if converted is not None:
                out[k] = converted
        return out

    # If it's a list/tuple
    if isinstance(doc, (list, tuple)):
        return [_convert_value(x) for x in doc]

    # Otherwise, single value
    return _convert_value(doc)
