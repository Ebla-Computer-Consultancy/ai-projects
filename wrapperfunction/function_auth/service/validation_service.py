from datetime import datetime
import re

def validate_username(username: str, include_num= True):
    
    if not username.strip():
        return False, "Username cannot be empty."
    if len(username) < 3 or len(username) > 50:
        return False, "Username must be between 3 and 50 characters."
    if include_num:
        if not username.isalnum():
            return False, "Username can only contain letters and numbers."
    else:
        if not username.isalpha():
            return False, "Username can only contain letters."
    return True, "Valid username."

def validate_id(employee_ID: int):
    if not isinstance(employee_ID, int):
        return False, "ID must be an integer."
    if employee_ID <= 0:
        return False, "ID must be a positive number."
    return True, "Valid ID."

def validate_password(password: str):
    
    if not password.strip():
        return False, "Password cannot be empty."
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    return True, "Valid password."

def is_valid_yyyy_mm_dd(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True  
    except ValueError:
        return False

def is_valid_iso8601_utc_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False