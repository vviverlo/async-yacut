import random
from datetime import datetime
from http import HTTPStatus

from yacut import db

from .constants import (
    ALLOWED_SHORT_CHARS,
    AUTO_SHORT_ID_LENGTH,
    CUSTOM_SHORT_ID_MAX_LENGTH,
    DISALLOWED_SHORT_IDS,
)
from .exceptions import ShortLinkError
from .utils import (
    DUPLICATE_SHORT_ID_MSG,
    EMPTY_BODY_MSG,
    INVALID_SHORT_ID_MSG,
    MISSING_URL_MSG,
    NOT_FOUND_ID_MSG,
    validate_custom_short_id,
)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(
        db.String(CUSTOM_SHORT_ID_MAX_LENGTH),
        nullable=False,
        unique=True,
        index=True,
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get_unique_short_id():
        while True:
            short_id = ''.join(
                random.choices(ALLOWED_SHORT_CHARS, k=AUTO_SHORT_ID_LENGTH)
            )
            if (
                short_id.lower() not in DISALLOWED_SHORT_IDS
                and URLMap.query.filter_by(short=short_id).first() is None
            ):
                return short_id

    @staticmethod
    def create_from_payload(original, custom_id=None):
        """
        Проверяет custom_id, при необходимости генерирует short,
        создаёт запись, сохраняет и вернёт объект.
        """
        try:
            validate_custom_short_id(custom_id)
        except KeyError:
            raise ShortLinkError(
                DUPLICATE_SHORT_ID_MSG,
                HTTPStatus.BAD_REQUEST,
            ) from None
        except ValueError:
            raise ShortLinkError(
                INVALID_SHORT_ID_MSG,
                HTTPStatus.BAD_REQUEST,
            ) from None

        short_id = custom_id or URLMap.get_unique_short_id()
        url_map = URLMap(original=original, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def create_from_api_dict(data):
        """Разбор тела POST /api/id/ и создание записи."""
        if data is None:
            raise ShortLinkError(
                EMPTY_BODY_MSG,
                HTTPStatus.BAD_REQUEST,
            )
        if 'url' not in data:
            raise ShortLinkError(
                MISSING_URL_MSG,
                HTTPStatus.BAD_REQUEST,
            )
        custom_id = data.get('custom_id')
        if custom_id == '':
            custom_id = None
        return URLMap.create_from_payload(data['url'], custom_id)

    @staticmethod
    def get_by_short_or_raise(short_id):
        """Возвращает объект по short или бросает ShortLinkError(404)."""
        url_map = URLMap.query.filter_by(short=short_id).first()
        if url_map is None:
            raise ShortLinkError(
                NOT_FOUND_ID_MSG,
                HTTPStatus.NOT_FOUND,
            )
        return url_map
