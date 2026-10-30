import datetime
from typing import Optional

def calculate_age(dob: datetime.date, as_of: Optional[datetime.date] = None) -> int:
    """Calculate exact age handling birthday boundaries and leap years."""
    if as_of is None:
        as_of = datetime.date.today()
    age = as_of.year - dob.year
    if (as_of.month, as_of.day) < (dob.month, dob.day):
        age -= 1
    return age

def get_age_band(dob: datetime.date, as_of: Optional[datetime.date] = None) -> str:
    """
    Derives age band from DOB:
    - U-10: age < 10
    - U-14: 10 <= age < 14
    - U-17: 14 <= age < 17
    - U-19: 17 <= age < 19
    - Senior: 19 <= age < 35
    - Post-Career: age >= 35
    """
    age = calculate_age(dob, as_of)
    if age < 10:
        return "U-10"
    elif age < 14:
        return "U-14"
    elif age < 17:
        return "U-17"
    elif age < 19:
        return "U-19"
    elif age < 35:
        return "Senior"
    else:
        return "Post-Career"
