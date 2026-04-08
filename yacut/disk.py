import os
import ssl
import uuid
from http import HTTPStatus
from urllib.parse import quote

import aiohttp
import certifi
from werkzeug.utils import secure_filename

YANDEX_API_BASE = 'https://cloud-api.yandex.net/v1/disk'


class YandexDiskAPIError(Exception):
    """Ошибка API Диска: нет успеха или есть текст ошибки в ответе."""


def _yandex_ssl_connector():
    """SSL с CA из certifi (на macOS иначе часто падает verify)."""
    ctx = ssl.create_default_context(cafile=certifi.where())
    return aiohttp.TCPConnector(ssl=ctx)


def _yandex_error_message(payload, status):
    if isinstance(payload, dict):
        return (
            payload.get('message')
            or payload.get('description')
            or payload.get('error')
            or str(payload)
        )
    return f'HTTP {status}'


def _unique_app_folder_object_name(original_filename):
    """Уникальное имя на Диске — повтор не затирает предыдущий файл."""
    base = secure_filename(original_filename) or 'file'
    return f'{uuid.uuid4().hex}_{base}'


async def upload_file_and_get_download_link(file_storage):
    token = os.getenv('DISK_TOKEN', '')
    if not token.strip():
        raise YandexDiskAPIError(
            'Не задан токен Яндекс.Диска (переменная DISK_TOKEN).'
        )

    headers = {'Authorization': f'OAuth {token}'}
    file_name = file_storage.filename
    unique_name = _unique_app_folder_object_name(file_name)
    disk_path = 'app:/' + quote(unique_name)

    async with aiohttp.ClientSession(
        connector=_yandex_ssl_connector(),
        headers=headers,
    ) as session:
        async with session.get(
            f'{YANDEX_API_BASE}/resources/upload',
            params={
                'path': disk_path,
                'overwrite': 'true',
                'fields': 'href',
            },
        ) as response:
            upload_data = await response.json(content_type=None)
            if (
                response.status != HTTPStatus.OK
                or not isinstance(upload_data, dict)
            ):
                raise YandexDiskAPIError(
                    _yandex_error_message(upload_data, response.status)
                )
            upload_url = upload_data.get('href')
            if not upload_url:
                raise YandexDiskAPIError(
                    _yandex_error_message(upload_data, response.status)
                )

        file_storage.stream.seek(0)
        async with session.put(
            upload_url, data=file_storage.read()
        ) as put_resp:
            if put_resp.status not in (
                HTTPStatus.OK,
                HTTPStatus.CREATED,
                HTTPStatus.ACCEPTED,
            ):
                text = (await put_resp.text())[:500]
                msg = (
                    f'Не удалось загрузить файл на Диск '
                    f'(HTTP {put_resp.status}): {text}'
                )
                raise YandexDiskAPIError(msg)

        async with session.get(
            f'{YANDEX_API_BASE}/resources/download',
            params={
                'path': disk_path,
                'fields': 'href',
            },
        ) as response:
            download_data = await response.json(content_type=None)
            if (
                response.status != HTTPStatus.OK
                or not isinstance(download_data, dict)
            ):
                raise YandexDiskAPIError(
                    _yandex_error_message(download_data, response.status)
                )
            download_href = download_data.get('href')
            if not download_href:
                raise YandexDiskAPIError(
                    _yandex_error_message(download_data, response.status)
                )

    return file_name, download_href
