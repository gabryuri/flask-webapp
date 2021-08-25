"""Form object declaration."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextField,
    SubmitField,
    SelectField,
    BooleanField,
    FloatField,
)
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import DateField
from utils.dynamo_functions import MenuHandler, CustomerHandler


class AddItemsForm(FlaskForm):
    menus_dh = MenuHandler(initialize=True)
    menu = menus_dh.retrieve_all_items()

    menu_choices = [
        (product.get("product_id"), product.get("product_name")) for product in menu
    ]
    menu_prices = [(product.get("price"), product.get("price")) for product in menu]

    product = SelectField("Sabor de Torta", [DataRequired()], choices=menu_choices)

    quantity = SelectField(
        "Quantidade",
        [DataRequired()],
        coerce=int,
        choices=[(number, number) for number in range(0, 10)],
    )
    submit = SubmitField("Adicionar")


class CreateOrderForm(FlaskForm):
    customers_dh = CustomerHandler(initialize=True)
    customers = customers_dh.retrieve_all_items()

    customer_choices = [
        (customer["customer_id"], customer["customer_name"]) for customer in customers
    ]

    customer = SelectField("Cliente", [DataRequired()], choices=customer_choices)

    is_custom_address = BooleanField("Usar endereço customizado?")
    custom_address = StringField("Endereço alternativo")

    remarks = StringField("Comentário / Observação")

    delivery_date = DateField("Data de entrega", [DataRequired()], format="%Y-%m-%d")

    delivery_bool = BooleanField("Entregar no cliente? ")
    delivery_fee = FloatField("Taxa de entrega")
    create_order = SubmitField("Confirmar pedido")


class AddItemToMenu(FlaskForm):

    product_name = StringField("Sabor de Torta", [DataRequired()])

    product_description = StringField("Descrição")

    price = StringField("Preço", [DataRequired()])

    submit = SubmitField("Adicionar item ao menu")


#
#
# """Form object declaration."""
# from flask_wtf import FlaskForm
# from wtforms import StringField, TextField, SubmitField
# from wtforms.validators import DataRequired, Length
#
#
# class ContactForm(FlaskForm):
#     """Contact form."""
#     name = StringField(
#         'Name',
#         [DataRequired()]
#     )
#     email = StringField(
#         'Email',
#         [
#             Email(message=('Not a valid email address.')),
#             DataRequired()
#         ]
#     )
#     body = TextField(
#         'Message',
#         [
#             DataRequired(),
#             Length(min=4,
#             message=('Your message is too short.'))
#         ]
#     )
#     recaptcha = RecaptchaField()
#     submit = SubmitField('Submit')
