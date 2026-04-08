from http import HTTPStatus


class ShortLinkAPIError(Exception):
    """Ошибка API или бизнес-логики коротких ссылок (код ответа + текст)."""

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
