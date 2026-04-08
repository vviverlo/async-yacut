import asyncio

from flask import flash, redirect, render_template, session, url_for

from yacut import app

from .disk import YandexDiskAPIError, upload_file_and_get_download_link
from .exceptions import ShortLinkAPIError
from .forms import URLMapForm, UploadFilesForm
from .models import URLMap
from .utils import DUPLICATE_SHORT_ID_MSG

FILES_UPLOAD_ROWS_KEY = 'files_upload_rows'


@app.route('/', methods=('GET', 'POST'))
def index_view():
    form = URLMapForm()
    short_link = None
    if form.validate_on_submit():
        try:
            url_map = URLMap.create_from_payload(
                form.original_link.data,
                form.custom_id.data,
            )
        except ShortLinkAPIError as exc:
            if exc.message == DUPLICATE_SHORT_ID_MSG:
                flash(exc.message)
            return render_template('index.html', form=form, short_link=None)
        short_link = url_for(
            'redirect_view', short_id=url_map.short, _external=True
        )
    return render_template('index.html', form=form, short_link=short_link)


async def _upload_files(files):
    tasks = [
        upload_file_and_get_download_link(file_data)
        for file_data in files
    ]
    return await asyncio.gather(*tasks)


@app.route('/files', methods=('GET', 'POST'))
def files_view():
    form = UploadFilesForm()
    uploaded_rows = session.get(FILES_UPLOAD_ROWS_KEY, [])
    if form.validate_on_submit():
        try:
            results = asyncio.run(_upload_files(form.files.data))
        except YandexDiskAPIError as exc:
            flash(str(exc))
            return render_template(
                'files.html', form=form, uploaded=uploaded_rows
            )
        new_rows = []
        for file_name, file_link in results:
            url_map = URLMap.create_from_payload(file_link, None)
            new_rows.append(
                {
                    'name': file_name,
                    'short_link': url_for(
                        'redirect_view',
                        short_id=url_map.short,
                        _external=True,
                    ),
                }
            )
        uploaded_rows = uploaded_rows + new_rows
        session[FILES_UPLOAD_ROWS_KEY] = uploaded_rows
        session.modified = True
    return render_template('files.html', form=form, uploaded=uploaded_rows)


@app.route('/<string:short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
