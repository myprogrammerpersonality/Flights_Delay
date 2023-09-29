from datetime import datetime
import re
from logger import Logger

logger = Logger(__name__).get_logger()

def calc_delay(formal_time, real_time):
    if not formal_time or not real_time:
        return None

    # Regular expression to extract time in HH:MM or HH:MM:SS format
    pattern = re.compile(r'(\d{2}:\d{2}(:\d{2})?)')

    # Extract times
    formal_match = pattern.search(formal_time)
    real_match = pattern.search(real_time)

    if not formal_match or not real_match:
        logger.warning(f"Couldn't find a valid time in either '{formal_time}' or '{real_time}'")
        return None  # Couldn't find a valid time

    formal_time_str = formal_match.group(1)
    real_time_str = real_match.group(1)

    # If the extracted time is in HH:MM format
    if len(real_time_str) == 5:
        real_datetime = datetime.strptime(real_time_str, '%H:%M')
    # If the extracted time is in HH:MM:SS format
    else:
        real_datetime = datetime.strptime(real_time_str, '%H:%M:%S')

    formal_datetime = datetime.strptime(formal_time_str, '%H:%M')

    return (real_datetime - formal_datetime).total_seconds() // 60
