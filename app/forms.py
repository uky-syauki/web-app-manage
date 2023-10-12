from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email


class FormLogin(FlaskForm):
    username = StringField("Nama admin", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Ingat saya")
    submit = SubmitField('Masuk')


class FormAddCalgot(FlaskForm):
    username = StringField('Nama Calgot', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Tambahkan')


class FormPertemuan(FlaskForm):
    title = StringField("Title", validators={DataRequired()})
    materi = StringField("Materi", validators=[DataRequired()])
    submit = SubmitField('New Pertemuan')


