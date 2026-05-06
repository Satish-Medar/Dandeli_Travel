"""
Data validation module for resort data integrity.
"""
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError, field_validator

logger = logging.getLogger(__name__)

class ResortModel(BaseModel):
    """Pydantic model for resort data validation."""
    id: int = Field(..., gt=0, description="Unique resort identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Resort name")
    category: str = Field(..., min_length=1, max_length=100, description="Resort category")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    location: str = Field(..., min_length=1, max_length=500, description="Detailed location")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    phone: str = Field(..., min_length=1, max_length=20, description="Contact phone number")
    email: str = Field(..., min_length=1, max_length=200, description="Contact email")
    website: Optional[str] = Field(None, description="Website URL")
    rating: float = Field(..., ge=0, le=5, description="Rating out of 5")
    review_count: int = Field(..., ge=0, description="Number of reviews")
    rooms: List[str] = Field(..., min_length=1, description="Available room types")
    amenities: List[str] = Field(..., min_length=1, description="Available amenities")
    activities_onsite: List[str] = Field(default_factory=list, description="On-site activities")
    activities_nearby: List[str] = Field(default_factory=list, description="Nearby activities")
    water_activities: List[str] = Field(default_factory=list, description="Water activities")
    food_options: List[str] = Field(default_factory=list, description="Food options")
    family_friendly: bool = Field(..., description="Suitable for families")
    romantic_couples: bool = Field(..., description="Suitable for couples")
    check_in: str = Field(..., min_length=1, max_length=20, description="Check-in time")
    check_out: str = Field(..., min_length=1, max_length=20, description="Check-out time")
    description: str = Field(..., min_length=1, max_length=2000, description="Resort description")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Basic email validation."""
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Basic phone validation."""
        # Remove spaces, dashes, parentheses for validation
        clean_phone = ''.join(c for c in v if c.isdigit() or c in ['+', ' '])
        if len(clean_phone.replace(' ', '')) < 10:
            raise ValueError('Phone number too short')
        return v

    @field_validator('website')
    @classmethod
    def validate_website(cls, v):
        """Basic website URL validation."""
        if v is None:
            return v
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Website must start with http:// or https://')
        return v


def validate_resort_data(data: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
    """
    Validate resort data against the schema.

    Args:
        data: List of resort dictionaries

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    valid_count = 0

    # Check for duplicate IDs
    ids = [resort.get('id') for resort in data if isinstance(resort.get('id'), int)]
    duplicate_ids = [id for id in ids if ids.count(id) > 1]
    if duplicate_ids:
        errors.append(f"Duplicate resort IDs found: {set(duplicate_ids)}")

    # Check for duplicate names
    names = [resort.get('name', '').strip() for resort in data if resort.get('name')]
    duplicate_names = [name for name in names if names.count(name) > 1]
    if duplicate_names:
        errors.append(f"Duplicate resort names found: {set(duplicate_names)}")

    # Validate each resort
    for i, resort_data in enumerate(data):
        try:
            resort = ResortModel(**resort_data)
            valid_count += 1
        except ValidationError as e:
            resort_name = resort_data.get('name', f'Resort {i+1}')
            errors.append(f"Validation error for '{resort_name}': {e}")
        except Exception as e:
            resort_name = resort_data.get('name', f'Resort {i+1}')
            errors.append(f"Unexpected error for '{resort_name}': {e}")

    # Additional business logic validations
    for i, resort in enumerate(data):
        resort_name = resort.get('name', f'Resort {i+1}')

        # Check for empty required string fields
        required_fields = ['name', 'category', 'city', 'location', 'phone', 'email', 'description']
        for field in required_fields:
            value = resort.get(field, '')
            if isinstance(value, str) and value.strip() == '':
                errors.append(f"'{resort_name}' has empty {field}")

        # Check rating is reasonable
        rating = resort.get('rating', 0)
        if not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
            errors.append(f"'{resort_name}' has invalid rating: {rating}")

        # Check coordinates are in India (rough bounds)
        lat = resort.get('latitude', 0)
        lon = resort.get('longitude', 0)
        if not (8 <= lat <= 37) or not (68 <= lon <= 97):
            errors.append(f"'{resort_name}' coordinates may be outside India: {lat}, {lon}")

    is_valid = len(errors) == 0
    logger.info(f"Validated {len(data)} resorts: {valid_count} valid, {len(errors)} errors")

    return is_valid, errors


def load_and_validate_resorts(file_path: Path) -> tuple[List[Dict[str, Any]], bool, List[str]]:
    """
    Load resort data from file and validate it.

    Args:
        file_path: Path to the resorts JSON file

    Returns:
        Tuple of (resort_data, is_valid, error_messages)
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        if not isinstance(data, list):
            return [], False, ["Resort data must be a list of objects"]

        is_valid, errors = validate_resort_data(data)
        return data, is_valid, errors

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in {file_path}: {e}"
        logger.error(error_msg)
        return [], False, [error_msg]
    except FileNotFoundError:
        error_msg = f"Resort data file not found: {file_path}"
        logger.error(error_msg)
        return [], False, [error_msg]
    except Exception as e:
        error_msg = f"Error loading resort data: {e}"
        logger.error(error_msg)
        return [], False, [error_msg]


def validate_resorts_on_startup():
    """
    Validate resorts data on application startup.
    This should be called during app initialization.
    """
    base_dir = Path(__file__).resolve().parent.parent
    resorts_file = base_dir / "data" / "json_files" / "resorts.json"

    logger.info("Validating resort data on startup...")
    data, is_valid, errors = load_and_validate_resorts(resorts_file)

    if not is_valid:
        logger.error("Resort data validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        raise ValueError("Resort data validation failed. Please fix the issues above.")

    logger.info(f"Successfully validated {len(data)} resorts")
    return data


if __name__ == "__main__":
    # Test validation
    base_dir = Path(__file__).resolve().parent.parent
    resorts_file = base_dir / "data" / "json_files" / "resorts.json"

    logger.info(f"Validating resorts from: {resorts_file}")
    data, is_valid, errors = load_and_validate_resorts(resorts_file)

    if is_valid:
        logger.info(f"✅ Validation successful! {len(data)} resorts validated.")
    else:
        logger.error(f"❌ Validation failed with {len(errors)} errors:")
        for error in errors[:10]:  # Show first 10 errors
            logger.error(f"  - {error}")
        if len(errors) > 10:
            logger.error(f"  ... and {len(errors) - 10} more errors")