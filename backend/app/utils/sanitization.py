"""
Input validation and sanitization utilities for messaging system
Task 15.1: Implement input validation and sanitization
"""
import re
import html
from typing import Optional


# Maximum allowed lengths
MAX_MESSAGE_LENGTH = 2000
MAX_REPORT_DETAILS_LENGTH = 500
MAX_BLOCK_REASON_LENGTH = 500


def sanitize_message_content(content: str) -> str:
    """
    Sanitize message content to prevent XSS and injection attacks.
    
    - Strips HTML tags
    - Escapes HTML entities
    - Trims whitespace
    - Validates length
    
    Args:
        content: Raw message content from user
        
    Returns:
        Sanitized content string
        
    Raises:
        ValueError: If content is empty after sanitization or too long
    """
    if not content:
        raise ValueError("Message content cannot be empty")
    
    # Strip HTML tags using regex (removes <tag> patterns)
    clean = re.sub(r'<[^>]+>', '', content)
    
    # Escape remaining HTML entities
    clean = html.escape(clean, quote=True)
    
    # Normalize whitespace (collapse multiple spaces/newlines but preserve single newlines)
    clean = re.sub(r'\r\n', '\n', clean)       # normalize line endings
    clean = re.sub(r'\r', '\n', clean)          # normalize carriage returns
    clean = re.sub(r'\t', '  ', clean)          # tabs to spaces
    clean = re.sub(r'[ ]{3,}', '  ', clean)    # max 2 consecutive spaces
    clean = re.sub(r'\n{4,}', '\n\n\n', clean) # max 3 consecutive newlines
    
    # Trim leading/trailing whitespace
    clean = clean.strip()
    
    if not clean:
        raise ValueError("Message content cannot be empty after sanitization")
    
    if len(clean) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Message content exceeds maximum length of {MAX_MESSAGE_LENGTH} characters")
    
    return clean


def sanitize_report_details(details: Optional[str]) -> Optional[str]:
    """
    Sanitize report details text.
    
    Args:
        details: Optional report details
        
    Returns:
        Sanitized details or None
    """
    if not details:
        return None
    
    clean = re.sub(r'<[^>]+>', '', details)
    clean = html.escape(clean.strip(), quote=True)
    
    if len(clean) > MAX_REPORT_DETAILS_LENGTH:
        clean = clean[:MAX_REPORT_DETAILS_LENGTH]
    
    return clean if clean else None


def sanitize_block_reason(reason: Optional[str]) -> Optional[str]:
    """
    Sanitize block reason text.
    
    Args:
        reason: Optional reason for blocking
        
    Returns:
        Sanitized reason or None
    """
    if not reason:
        return None
    
    clean = re.sub(r'<[^>]+>', '', reason)
    clean = html.escape(clean.strip(), quote=True)
    
    if len(clean) > MAX_BLOCK_REASON_LENGTH:
        clean = clean[:MAX_BLOCK_REASON_LENGTH]
    
    return clean if clean else None


def validate_uuid(value: str, field_name: str = "ID") -> str:
    """
    Validate that a string is a valid UUID format.
    
    Args:
        value: String to validate
        field_name: Name of the field for error messages
        
    Returns:
        The original value if valid
        
    Raises:
        ValueError: If value is not a valid UUID
    """
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    if not uuid_pattern.match(value):
        raise ValueError(f"{field_name} must be a valid UUID")
    
    return value


def check_for_spam_patterns(content: str) -> bool:
    """
    Basic spam detection patterns.
    Returns True if content appears to be spam.
    
    Args:
        content: Message content to check
        
    Returns:
        True if spam detected, False otherwise
    """
    # Repeated characters (e.g., "aaaaaaa")
    if re.search(r'(.)\1{9,}', content):
        return True
    
    # Excessive caps (more than 70% uppercase for messages > 20 chars)
    if len(content) > 20:
        upper_count = sum(1 for c in content if c.isupper())
        if upper_count / len(content) > 0.7:
            return True
    
    # Suspicious URL patterns (basic check)
    suspicious_urls = re.findall(
        r'https?://[^\s]+',
        content,
        re.IGNORECASE
    )
    if len(suspicious_urls) > 5:
        return True
    
    return False
