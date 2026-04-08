from http import HTTPStatus

from flask import jsonify, request, url_for

from yacut import app

from .models import URLMap


@app.route('/api/id/', methods=('POST',))
def create_short_link():
    url_map = URLMap.create_from_api_dict(
        request.get_json(silent=True, force=True)
    )
    return jsonify(
        {
            'url': url_map.original,
            'short_link': url_for(
                'redirect_view', short_id=url_map.short, _external=True
            ),
        }
    ), HTTPStatus.CREATED


@app.route(
    '/api/id/<string:short_id>/',
    methods=('GET',),
    strict_slashes=False,
)
def get_original_link(short_id):
    url_map = URLMap.get_by_short_or_raise(short_id)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
