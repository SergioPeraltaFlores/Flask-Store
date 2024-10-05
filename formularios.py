from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email, NumberRange

class Register(FlaskForm):
    username=StringField('Username',
                         validators=[
                             DataRequired(),
                             Length(min=5, max=20)])
    email=StringField('Email',
                        validators=[
                            DataRequired(),
                            Email()])
    password=PasswordField('Password',
                           validators=[
                               DataRequired(),
                               ])
    confirm_password=PasswordField('Comfirm Password',
                           validators=[
                               DataRequired(),
                               EqualTo('password')
                               ])
    submit=SubmitField('Register')

class Login(FlaskForm):
    email=StringField('Email',
                        validators=[
                            DataRequired(),
                            Email()])
    password=PasswordField('Password',
                           validators=[
                               DataRequired(),
                               ])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')

class Edit(FlaskForm):
    username=StringField('Nombre de Usuario',
                         validators=[
                             DataRequired(),
                             Length(min=5, max=20)])
    password=PasswordField('Contraseña Actual',
                           validators=[
                               DataRequired(),
                               ])
    confirm_password=PasswordField('Comfirmar Contraseña',
                           validators=[
                               DataRequired(),
                               EqualTo('password')
                               ])
    new_password=PasswordField('Nueva Contraseña',
                           validators=[
                               DataRequired(),
                               ])
    submit=SubmitField('Edit')

class Saldo(FlaskForm):
    tarjeta=IntegerField('Tarjeta',
                validators=[
                DataRequired(),
                NumberRange(min=4000000000000000,max=6999999999999999)
                ])
    saldo=IntegerField('Saldo (Numeros Enteros)',
                validators=[
                DataRequired()])
    submit=SubmitField('Añadir Saldo')

class Mazo(FlaskForm):
    nombre=StringField('Nombre del Mazo',
                        validators=[
                        DataRequired(),
                        Length(min=5, max=20)])

    submit=SubmitField('Crear Nuevo Mazo')
