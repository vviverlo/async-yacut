import re
import string

ALPHANUMERIC_PATTERN = re.compile(r'^[A-Za-z0-9]+$')
AUTO_SHORT_ID_LENGTH = 6
CUSTOM_SHORT_ID_MAX_LENGTH = 16
ALLOWED_SHORT_CHARS = string.ascii_letters + string.digits
DISALLOWED_SHORT_IDS = {'files'}
