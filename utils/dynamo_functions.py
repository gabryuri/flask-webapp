import datetime
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import decimal

class DynamoHandler:
    def __init__(self, initialize: bool, table:str, table_keys:str, region_name='us-east-1'):

        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table_keys = table_keys
        self.table_name = table
        self.region_name = region_name
        self.initialize = initialize

    def create_table(self, key_schema, attr_definitions):
        if self.initialize == True:
            self.client = boto3.client('dynamodb',region_name=self.region_name)
            response = self.client.list_tables()

            if self.table_name in response['TableNames']:
                self.table = self.dynamodb.Table(self.table_name)
                return print(f'Table {self.table_name} Already exists')


            else:
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=key_schema,
                    AttributeDefinitions=attr_definitions,
                    BillingMode='PAY_PER_REQUEST')

                table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)

                return print(f"Table {self.table_name} created with status {table.table_status}")
        self.table = self.dynamodb.Table(self.table_name)


    def delete_table(self):
        self.table.delete()
        print(f'deleted {self.table}')

    def retrieve_all_items(self) -> list:
        items_raw = self.table.scan().get('Items')
        items_to_retrieve = [self.convert_decimal_to_float(item) for item in items_raw]
        return items_to_retrieve

    def put_item(self, item: dict):
        item_to_put = self.convert_float_to_decimal(item)
        self.table.put_item(Item=item_to_put)

    def delete_item(self, value: list):

        key_array = dict(zip(self.table_keys, value))
        print(key_array)
        self.table.delete_item(Key=key_array)

    def query_by_key(self, value) -> dict:
        # print(self.key)
        # print(value)
        # response = self.table.query(
        #     KeyConditionExpression=Key(self.key).eq(value)
        # )


        key_array = dict(zip(self.table_keys, value))
        response = self.table.get_item(Key=key_array)
        item = self.convert_decimal_to_float(response['Item'])
        return item

    def convert_float_to_decimal(self, item: dict) -> dict:
        for key, value in item.items():
            if isinstance(value, dict):
                self.convert_float_to_decimal(value)
            else:
                if type(value) == float:
                    value = Decimal(value)
                item.update({key: value})
        return item

    def convert_decimal_to_float(self, item: dict) -> dict:
        for key, value in item.items():
            if isinstance(value, dict):
                self.convert_decimal_to_float(value)
            else:
                if type(value) == decimal.Decimal:
                    value = float(value)
                item.update({key: value})
        return item


class MenuHandler(DynamoHandler):
    def __init__(self, region_name='us-east-1', initialize=False):

        super().__init__(table='inboxsabores-menu', table_keys=['product_id'], initialize=initialize)
        table = self.create_table(
        key_schema=[
            {
                'AttributeName': 'product_id',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        attr_definitions=[
            {
                'AttributeName': 'product_id',
                'AttributeType': 'N'
            }

        ])



class OrderHandler(DynamoHandler):
    def __init__(self, region_name='us-east-1', initialize=False):
        super().__init__(table='inboxsabores-main-table',
                         table_keys=['order_date','order_timestamp_id'],
                         initialize=initialize)

        table = self.create_table(
        key_schema=[
            {
                'AttributeName': 'order_date',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'order_timestamp_id',
                'KeyType': 'RANGE'  # Sort key
            }
                ],
        attr_definitions=[
            {
                'AttributeName': 'order_date',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'order_timestamp_id',
                'AttributeType': 'N'
            },
                ]
        )

class CustomerHandler(DynamoHandler):
    def __init__(self, region_name='us-east-1', initialize=False):
        super().__init__(table='inboxsabores-customers', table_keys=['customer_id'], initialize=initialize)

        table = self.create_table(
        key_schema=[
            {
                'AttributeName': 'customer_id',
                'KeyType': 'HASH'
            }
        ],
        attr_definitions=[
            {
                'AttributeName': 'customer_id',
                'AttributeType': 'N'
            }

        ]
        )


