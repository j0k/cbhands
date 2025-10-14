"""Configuration schema validation for cbhands v3.0.0."""

from typing import Any, Dict, List, Optional, Union
import json
import yaml
from pathlib import Path


class ConfigSchema:
    """Configuration schema definition."""
    
    def __init__(self, schema: Dict[str, Any]):
        """Initialize with schema definition."""
        self.schema = schema
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        """Validate data against schema."""
        errors = []
        self._validate_object(data, self.schema, "", errors)
        return errors
    
    def _validate_object(self, data: Dict[str, Any], schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        """Validate object against schema."""
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            # Check required fields
            for field in required:
                if field not in data:
                    errors.append(f"{path}.{field} is required")
            
            # Validate each property
            for key, value in data.items():
                if key in properties:
                    self._validate_value(value, properties[key], f"{path}.{key}", errors)
                elif not schema.get("additionalProperties", True):
                    errors.append(f"{path}.{key} is not allowed")
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        """Validate value against schema."""
        if schema.get("type") == "string":
            if not isinstance(value, str):
                errors.append(f"{path} must be a string")
        elif schema.get("type") == "integer":
            if not isinstance(value, int):
                errors.append(f"{path} must be an integer")
            else:
                if "minimum" in schema and value < schema["minimum"]:
                    errors.append(f"{path} must be >= {schema['minimum']}")
                if "maximum" in schema and value > schema["maximum"]:
                    errors.append(f"{path} must be <= {schema['maximum']}")
        elif schema.get("type") == "boolean":
            if not isinstance(value, bool):
                errors.append(f"{path} must be a boolean")
        elif schema.get("type") == "array":
            if not isinstance(value, list):
                errors.append(f"{path} must be an array")
            else:
                items_schema = schema.get("items", {})
                for i, item in enumerate(value):
                    self._validate_value(item, items_schema, f"{path}[{i}]", errors)
        elif schema.get("type") == "object":
            if not isinstance(value, dict):
                errors.append(f"{path} must be an object")
            else:
                self._validate_object(value, schema, path, errors)


class SchemaValidator:
    """Schema validator utility."""
    
    @staticmethod
    def validate_plugin_config(plugin_name: str, config: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Validate plugin configuration."""
        validator = ConfigSchema(schema)
        return validator.validate(config)
    
    @staticmethod
    def load_schema_from_file(schema_file: str) -> Dict[str, Any]:
        """Load schema from file."""
        path = Path(schema_file)
        if not path.exists():
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            elif path.suffix == '.json':
                return json.load(f)
            else:
                return {}
    
    @staticmethod
    def save_schema_to_file(schema: Dict[str, Any], schema_file: str) -> None:
        """Save schema to file."""
        path = Path(schema_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(schema, f, default_flow_style=False, indent=2)
            elif path.suffix == '.json':
                json.dump(schema, f, indent=2)
