from http import HTTPStatus

from flask import jsonify, request, url_for

from yacut import app, db

from .models import URLMap
from .utils import (
    DUPLICATE_SHORT_ID_MSG,
    EMPTY_BODY_MSG,
    INVALID_SHORT_ID_MSG,
    MISSING_URL_MSG,
    NOT_FOUND_ID_MSG,
    get_unique_short_id,
    validate_custom_short_id,
)


def _message_response(message, status):
    return jsonify({'message': message}), status


@app.route('/api/id/', methods=('POST',))
def create_short_link():
    data = request.get_json(silent=True, force=True)
    if data is None:
        return _message_response(EMPTY_BODY_MSG, HTTPStatus.BAD_REQUEST)
    if 'url' not in data:
        return _message_response(MISSING_URL_MSG, HTTPStatus.BAD_REQUEST)

    custom_id = data.get('custom_id')
    if custom_id == '':
        custom_id = None
    try:
        validate_custom_short_id(custom_id)
    except KeyError:
        return _message_response(
            DUPLICATE_SHORT_ID_MSG, HTTPStatus.BAD_REQUEST
        )
    except ValueError:
        return _message_response(INVALID_SHORT_ID_MSG, HTTPStatus.BAD_REQUEST)

    short_id = custom_id or get_unique_short_id()
    url_map = URLMap(original=data['url'], short=short_id)
    db.session.add(url_map)
    db.session.commit()
    return jsonify(
        {
            'url': url_map.original,
            'short_link': url_for(
                'redirect_view', short_id=short_id, _external=True
            ),
        }
    ), HTTPStatus.CREATED


@app.route(
    '/api/id/<string:short_id>/',
    methods=('GET',),
    strict_slashes=False,
)
def get_original_link(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        return _message_response(NOT_FOUND_ID_MSG, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
