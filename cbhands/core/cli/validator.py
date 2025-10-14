"""Input validation for cbhands v3.0.0."""

import os
from typing import Any, Dict, List, Optional, Union
import re


class InputValidator:
    """Input validation utility."""
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 0, max_length: Optional[int] = None, pattern: Optional[str] = None) -> List[str]:
        """Validate string input."""
        errors = []
        
        if not isinstance(value, str):
            errors.append("Value must be a string")
            return errors
        
        if len(value) < min_length:
            errors.append(f"String must be at least {min_length} characters long")
        
        if max_length is not None and len(value) > max_length:
            errors.append(f"String must be no more than {max_length} characters long")
        
        if pattern and not re.match(pattern, value):
            errors.append(f"String does not match required pattern: {pattern}")
        
        return errors
    
    @staticmethod
    def validate_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> List[str]:
        """Validate integer input."""
        errors = []
        
        if not isinstance(value, int):
            errors.append("Value must be an integer")
            return errors
        
        if min_value is not None and value < min_value:
            errors.append(f"Value must be >= {min_value}")
        
        if max_value is not None and value > max_value:
            errors.append(f"Value must be <= {max_value}")
        
        return errors
    
    @staticmethod
    def validate_float(value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None) -> List[str]:
        """Validate float input."""
        errors = []
        
        if not isinstance(value, (int, float)):
            errors.append("Value must be a number")
            return errors
        
        if min_value is not None and value < min_value:
            errors.append(f"Value must be >= {min_value}")
        
        if max_value is not None and value > max_value:
            errors.append(f"Value must be <= {max_value}")
        
        return errors
    
    @staticmethod
    def validate_boolean(value: Any) -> List[str]:
        """Validate boolean input."""
        errors = []
        
        if not isinstance(value, bool):
            errors.append("Value must be a boolean")
        
        return errors
    
    @staticmethod
    def validate_choice(value: Any, choices: List[str]) -> List[str]:
        """Validate choice input."""
        errors = []
        
        if value not in choices:
            errors.append(f"Value must be one of: {', '.join(choices)}")
        
        return errors
    
    @staticmethod
    def validate_email(value: Any) -> List[str]:
        """Validate email input."""
        errors = []
        
        if not isinstance(value, str):
            errors.append("Value must be a string")
            return errors
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            errors.append("Value must be a valid email address")
        
        return errors
    
    @staticmethod
    def validate_url(value: Any) -> List[str]:
        """Validate URL input."""
        errors = []
        
        if not isinstance(value, str):
            errors.append("Value must be a string")
            return errors
        
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, value):
            errors.append("Value must be a valid URL")
        
        return errors
    
    @staticmethod
    def validate_port(value: Any) -> List[str]:
        """Validate port number."""
        errors = []
        
        if not isinstance(value, int):
            errors.append("Value must be an integer")
            return errors
        
        if value < 1 or value > 65535:
            errors.append("Port must be between 1 and 65535")
        
        return errors
    
    @staticmethod
    def validate_file_path(value: Any, must_exist: bool = False) -> List[str]:
        """Validate file path."""
        errors = []
        
        if not isinstance(value, str):
            errors.append("Value must be a string")
            return errors
        
        if must_exist and not os.path.exists(value):
            errors.append(f"File does not exist: {value}")
        
        return errors
    
    @staticmethod
    def validate_directory_path(value: Any, must_exist: bool = False) -> List[str]:
        """Validate directory path."""
        errors = []
        
        if not isinstance(value, str):
            errors.append("Value must be a string")
            return errors
        
        if must_exist and not os.path.isdir(value):
            errors.append(f"Directory does not exist: {value}")
        
        return errors
