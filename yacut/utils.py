from .constants import (
    ALPHANUMERIC_PATTERN,
    CUSTOM_SHORT_ID_MAX_LENGTH,
    DISALLOWED_SHORT_IDS,
)

INVALID_SHORT_ID_MSG = 'Указано недопустимое имя для короткой ссылки'
DUPLICATE_SHORT_ID_MSG = 'Предложенный вариант короткой ссылки уже существует.'
NOT_FOUND_ID_MSG = 'Указанный id не найден'
EMPTY_BODY_MSG = 'Отсутствует тело запроса'
MISSING_URL_MSG = '"url" является обязательным полем!'


def is_valid_short_id(short_id):
    return bool(short_id and ALPHANUMERIC_PATTERN.fullmatch(short_id))


def validate_custom_short_id(custom_id):
    from .models import URLMap

    if not custom_id:
        return
    if custom_id.lower() in DISALLOWED_SHORT_IDS:
        raise KeyError(DUPLICATE_SHORT_ID_MSG)
    if (
        len(custom_id) > CUSTOM_SHORT_ID_MAX_LENGTH
        or not is_valid_short_id(custom_id)
    ):
        raise ValueError(INVALID_SHORT_ID_MSG)
    if URLMap.query.filter_by(short=custom_id).first() is not None:
        raise KeyError(DUPLICATE_SHORT_ID_MSG)
