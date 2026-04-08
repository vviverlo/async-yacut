from http import HTTPStatus

from flask import jsonify, render_template, request


def page_not_found(error):
    if request.path.startswith('/api/'):
        return (
            jsonify({'message': 'Указанный id не найден'}),
            HTTPStatus.NOT_FOUND,
        )
    return render_template('404.html'), HTTPStatus.NOT_FOUND


def internal_server_error(error):
    if request.path.startswith('/api/'):
        return (
            jsonify({'message': 'Внутренняя ошибка сервера'}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
