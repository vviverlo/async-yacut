from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import Length, Optional, Regexp, URL, DataRequired

from .constants import CUSTOM_SHORT_ID_MAX_LENGTH


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(), URL()],
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=CUSTOM_SHORT_ID_MAX_LENGTH),
            Regexp(
                r'^[A-Za-z0-9]*$',
                message='Допустимы только латинские буквы и цифры',
            ),
        ],
    )
    submit = SubmitField('Создать')


class UploadFilesForm(FlaskForm):
    files = MultipleFileField('Выберите файлы', validators=[FileRequired()])
    submit = SubmitField('Загрузить')
