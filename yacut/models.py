from datetime import datetime

from yacut import db

from .constants import CUSTOM_SHORT_ID_MAX_LENGTH


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
    def create_from_payload(original, custom_id=None):
        """
        Проверяет custom_id, при необходимости генерирует short,
        создаёт запись, сохраняет и вернёт объект.
        """
        from http import HTTPStatus

        from .exceptions import ShortLinkAPIError
        from .utils import (
            DUPLICATE_SHORT_ID_MSG,
            get_unique_short_id,
            INVALID_SHORT_ID_MSG,
            validate_custom_short_id,
        )

        try:
            validate_custom_short_id(custom_id)
        except KeyError:
            raise ShortLinkAPIError(
                DUPLICATE_SHORT_ID_MSG,
                HTTPStatus.BAD_REQUEST,
            ) from None
        except ValueError:
            raise ShortLinkAPIError(
                INVALID_SHORT_ID_MSG,
                HTTPStatus.BAD_REQUEST,
            ) from None

        short_id = custom_id or get_unique_short_id()
        url_map = URLMap(original=original, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def create_from_api_dict(data):
        """Разбор тела POST /api/id/ и создание записи."""
        from http import HTTPStatus

        from .exceptions import ShortLinkAPIError
        from .utils import EMPTY_BODY_MSG, MISSING_URL_MSG

        if data is None:
            raise ShortLinkAPIError(
                EMPTY_BODY_MSG,
                HTTPStatus.BAD_REQUEST,
            )
        if 'url' not in data:
            raise ShortLinkAPIError(
                MISSING_URL_MSG,
                HTTPStatus.BAD_REQUEST,
            )
        custom_id = data.get('custom_id')
        if custom_id == '':
            custom_id = None
        return URLMap.create_from_payload(data['url'], custom_id)

    @staticmethod
    def get_by_short_or_raise(short_id):
        """Возвращает объект по short или бросает ShortLinkAPIError(404)."""
        from http import HTTPStatus

        from .exceptions import ShortLinkAPIError
        from .utils import NOT_FOUND_ID_MSG

        url_map = URLMap.query.filter_by(short=short_id).first()
        if url_map is None:
            raise ShortLinkAPIError(
                NOT_FOUND_ID_MSG,
                HTTPStatus.NOT_FOUND,
            )
        return url_map
