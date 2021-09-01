from datetime import datetime
import time

from flask import jsonify

from utils.dynamo_functions import CustomerHandler, MenuHandler


class OrderRegistry:
    def __init__(self):
        self.registered_orders = []
        self.customer_handler = CustomerHandler()
        # self.menu_handler = MenuHandler()
        # self.order_class = Order()
        # self.cart_class = Cart()

    def create_order(self, order_form):

        customer_data = self.customer_handler.query_by_key(
            [int(float(order_form.customer.data))]
        )

        self.current_order = Order(order_form, customer_data)
        self.current_order_status = "UNREGISTERED"

        # order_array = {'order_timestamp_id': self.current_order.order_dict['order_timestamp_id'],
        #                'status': 'UNREGISTERED',
        #                'order_object': self.current_order}

        # self.registered_orders.append(order_array)
        self.last_timestamp_id = self.current_order.order_dict["order_timestamp_id"]



class Order:
    def __init__(self, order_form, customer_data):

        self.cart = Cart()

        nowtime = int(time.mktime(datetime.now().timetuple()))
        nowdate = datetime.now().strftime("%Y-%m-%d")
        order_year = int(datetime.now().strftime('%Y'))

        if order_form.is_custom_address.data == True:
            delivery_address = customer_data["default_address"]
        else:
            delivery_address = "TBD"

        self.order_dict = {
            "order_year": order_year,
            "order_timestamp_id": nowtime,
            "order_date": nowdate,
            "delivery_date": order_form.delivery_date.data.strftime("%Y-%m-%d"),
            "customer_id": order_form.customer.data,
            "customer_name": customer_data["customer_name"],
            "is_custom_address": order_form.is_custom_address.data,
            "address": delivery_address,
            "remark": order_form.remarks.data,
            "delivery_option": order_form.delivery_bool.data,
            "delivery_fee": order_form.delivery_fee.data,
            "cart": self.cart.cart_items,
        }


class Cart:
    def __init__(self):
        self.menu_handler = MenuHandler()
        self.cart_items = {}

    @property
    def all_total_price(self) -> dict:
        all_total_price = 0

        for product, product_info in self.cart_items.items():
            all_total_price = all_total_price + product_info["total_price"]
        return all_total_price

    @property
    def all_total_quantity(self) -> dict:
        all_total_quantity = 0

        for product, product_info in self.cart_items.items():
            all_total_quantity = all_total_quantity + product_info["quantity"]
        return all_total_quantity

    @property
    def cart_dict(self) -> dict:
        return {
            "all_total_price": self.all_total_price,
            "all_total_quantity": self.all_total_quantity,
            "cart_items": self.cart_items,
        }

    def add_item_to_list(self, item_form):
        product_id = item_form.product.data
        quantity = int(float(item_form.quantity.data))

        if isinstance(product_id, str):
            product_id = int(float(product_id))

        item = self.menu_handler.query_by_key([product_id])

        itemArray = {
            str(product_id): {
                "product_name": item["product_name"],
                "quantity": quantity,
                "price": float(item["price"]),
                "total_price": float(quantity) * float(item["price"]),
            }
        }
        self.cart_items.update(itemArray)
        print(self.cart_dict)


# class Order:
#     def __init__(self, table:str, keyname:str, region_name='us-east-1'):
