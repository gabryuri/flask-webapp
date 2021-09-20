import time, datetime
from datetime import datetime
from decimal import Decimal
import json

from flask import Flask, render_template, redirect, request, session, url_for
from forms import AddItemsForm, CreateOrderForm, AddItemToMenu

from utils.dynamo_functions import MenuHandler, OrderHandler, CustomerHandler
from utils.application_objects import Order, Cart, OrderRegistry

# import que esta dando erro, tem que instanciar o banco antes

app = Flask(__name__)
app.config["SECRET_KEY"] = "test"

menus_dh = MenuHandler(initialize=False)
orders_dh = OrderHandler(initialize=True)
customers_dh = CustomerHandler(initialize=False)

order_registry = OrderRegistry()

# Criar um objeto para gerenciar as orders, OrderRegister ou algo assim,
# ele adiciona e tira orders e ao inserir no dynamo muda um status.
# Assim, evito usar o session e crio algo que permanece durante a sessao inteira


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":

        task_content = request.form["content"]
        return redirect("/")
    else:
        return render_template("home.html")


@app.route("/add_items/<mode>/<order_timestamp_id>", methods=["GET", "POST"])
def add_items(mode, order_timestamp_id):

    if mode == 'retrieved':
        order_registry.instantiate_order(order_timestamp_id=order_timestamp_id)

    form = AddItemsForm()
    order_timestamp_id = int(float(order_timestamp_id))
    #print(order_registry.last_timestamp_id)
    print(order_timestamp_id)

    #if order_timestamp_id != order_registry.current_order.order_timestamp_id:


    cart_items = order_registry.current_order.cart.cart_items
    print(cart_items)


    if request.method == "POST" and form.is_submitted():

        order_registry.current_order.cart.add_item_to_list(item_form=form)

    return render_template("edit_items.html", form=form, cart_items=cart_items)


@app.route("/orders", methods=["GET", "POST"])
def orders():
    #print(session)
    form = CreateOrderForm()

    orders = orders_dh.query_by_date_interval('2021-08-01','2022-11-30')
    #print(orders)
    customers = customers_dh.retrieve_all_items()

    customer_choices = [
        (customer["customer_id"], customer["customer_name"]) for customer in customers
    ]
    form.customer.choices = customer_choices

    if request.method == "POST" and form.is_submitted():
        mode='retrieved'
        if form.create_order.data is not None:
            print('creating order')
            mode = 'new'
            order_registry.instantiate_order(order_form=form)

            order_timestamp_id = (
                order_registry.current_order.order_dict['order_timestamp_id']
            )

            print(form.custom_address.data)

        print("Redirect")
        return redirect(url_for("add_items", mode=mode , order_timestamp_id=order_timestamp_id))

    return render_template("orders.html", orders=orders, form=form)

@app.route("/orders/create_order", methods=["GET", "POST"])
def create_order():
    if request.method == "POST":
        print(order_registry.current_order.order_dict)
        orders_dh.put_item(item=order_registry.current_order.order_dict)

    return redirect(url_for("orders"))

@app.route("/orders/delete_order/<order_timestamp_id>", methods=["GET", "POST"])
def delete_order(order_timestamp_id):
    if request.method == "POST":
        order_id = int(float(order_timestamp_id))
        order_year = datetime.utcfromtimestamp(order_id).strftime('%Y')

        #order_to_delete = orders_dh.query_by_key([order_day, order_id])

        orders_dh.delete_item(value=[order_year, order_id])
        #print(order_to_delete)
    return redirect(url_for("orders"))


@app.route('/orders/select_order', methods=['GET', 'POST'])
def select_order():
    if request.method == 'POST':

        order_timestamp_id = int(float(request.form['order_timestamp_id']))
        order_year = int(datetime.utcfromtimestamp(order_timestamp_id).strftime('%Y'))

        item = orders_dh.query_by_key([order_year, order_timestamp_id])
        print(item)

        return json.dumps(item)

@app.route("/menus", defaults={'product_id': None}, methods=["GET", "POST", "PUT"])
@app.route("/menus/<product_id>", methods=["GET", "POST", "PUT"])
def menus(product_id):

    form = AddItemToMenu()
    menu = menus_dh.retrieve_all_items()
    nowtime = int(time.mktime(datetime.now().timetuple()))

    if request.method == "POST":

        if product_id:
            # print('product_id:'+str(product_id))
            product_id = int(float(product_id))
        else:
            # print('nowtime:'+str(nowtime))
            product_id = nowtime

        ProductArray = {
            "product_id": product_id,
            "product_name": form.product_name.data,
            "product_description": form.product_description.data,
            "price": Decimal(form.price.data.replace(",", ".")),
        }

        menus_dh.put_item(item=ProductArray)

        return redirect(url_for("menus"))
    return render_template("menus.html", menu=menu, form=form)


@app.route("/menus/delete_product/<product_id>", methods=["GET", "POST"])
def delete_product_from_menu(product_id):

    if request.method == "POST":
        print(product_id)

        menus_dh.delete_item(value=[int(product_id)])
        return redirect("/menus")

    return render_template("menus.html", menu=menu, form=form)



@app.route('/select_product', methods=['GET', 'POST'])
def select():
    if request.method == 'POST':

        product_id = int(float(request.form['product_id']))
        item = menus_dh.query_by_key([product_id])
        #item['delivery_bool'] = str(item['delivery_bool'])

        return json.dumps(item)






if __name__ == "__main__":
    app.run(debug=True)
