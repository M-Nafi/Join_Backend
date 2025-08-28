import re
from django.core.exceptions import ValidationError

def validate_username_format(value):
    """
    Validates a username format.

    Checks that the username only contains letters, numbers, spaces, hyphens, and underscores.

    Args:
        value (str): The username to validate.

    Raises:
        ValidationError: If the username contains any invalid characters.
    """
    if not all(c.isalnum() or c in " ._- " for c in value):
        raise ValidationError(
            'Use only letters, numbers, spaces, "-", and "_".',
            code='invalid'
        )

def validate_phone_format(value):
    """
    Validates a phone number format.

    Checks that the phone number matches the regular expression
    ``^\+?[0-9\s\-]+$`` and has a length of at least 6 characters.

    Args:
        value (str): The phone number to validate.

    Raises:
        ValidationError: If the phone number does not match the regular expression
                         or is too short.
    """
    phone_regex = r'^\+?[0-9\s\-]+$'
    if not re.match(phone_regex, value):
        raise ValidationError("Invalid phone number format.")
    
    if len(value) < 6:
        raise ValidationError("Phone number too short.")