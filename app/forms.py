from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

class CategoryForm(FlaskForm):
    name = StringField('Kategori Adı', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Kategoriyi Ekle')

class DeviceForm(FlaskForm):
    name = StringField('Cihaz Adı', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Açıklama', validators=[Length(max=500)])
    quantity = IntegerField('Adet', validators=[DataRequired(), NumberRange(min=1)], default=1)
    # Kategori seçimi için 'choices' dinamik olarak route içinde doldurulacak
    category = SelectField('Kategori', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Cihazı Ekle')