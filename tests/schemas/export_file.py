ENTITY_SCHEMA = {
    "properties": {
        "created": {"type": "string"},
        "id": {"type": "integer"},
        "size": {"type": "integer"},
        "tag": {"type": "string"},
        "updated": {"type": "string"},
        "used": {"type": ["string", "null"]},
    },
    "required": ["id", "size", "tag", "updated", "used"],
    "type": "object",
}
ENTITIES_ARRAY_SCHEMA = {
    "type": "array",
    "items": {"$ref": "#/definitions/entity"},
    "definitions": {"entity": ENTITY_SCHEMA},
}
