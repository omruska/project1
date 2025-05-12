import unittest
from pymongo import MongoClient
from bson import ObjectId
from Database.Databases import Database
from Orders.Orders import Order
from Users.Users import User
from Project1.Config.Config import connection_string_mongo

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_instance = Database()
        self.client = MongoClient(connection_string_mongo)
        self.db = self.client['My']

        self.db['Products'].delete_many({})
        self.db['Orders'].delete_many({})
        self.db['Accounts'].delete_many({})
        # Ініціалізуємо дефолтні продукти
        self.db_instance.initialize_products()

    def tearDown(self):
        self.db['Products'].delete_many({})
        self.db['Orders'].delete_many({})
        self.db['Accounts'].delete_many({})
        self.db['Account'].delete_many({})

    def test_initialize_products(self):
        # Маємо мати як мінімум 4 дефолтних продукти
        products = list(self.db['Products'].find({}))
        self.assertGreaterEqual(len(products), 4)

    def test_update_product_quantity_by_name_success(self):
        # Отримуємо початкове значення для "Laptop"
        product_before = self.db_instance.get_product_by_name("Laptop")
        initial_qty = product_before["stock_quantity"]
        result = self.db_instance.update_product_quantity_by_name("Laptop", 5)
        product_after = self.db_instance.get_product_by_name("Laptop")
        self.assertTrue(result)
        self.assertEqual(product_after["stock_quantity"], initial_qty + 5)

    def test_update_product_quantity_by_name_fail(self):
        # Спроба оновити неіснуючий продукт
        result = self.db_instance.update_product_quantity_by_name("Nonexistent", 5)
        self.assertFalse(result)

    def test_get_product_by_name(self):
        product = self.db_instance.get_product_by_name("PS5")
        self.assertIsNotNone(product)
        self.assertEqual(product["name"], "PS5")

    def test_get_product_by_name_nonexistent(self):
        product = self.db_instance.get_product_by_name("Tablet")
        self.assertIsNone(product)

    def test_update_product_stock_success(self):
        # Перш за все – збільшимо запас, щоб точно зменшити на певну кількість
        self.db_instance.update_product_quantity_by_name("Smartphone", 10)
        product = self.db_instance.get_product_by_name("Smartphone")
        initial_qty = product["stock_quantity"]
        result = self.db_instance.update_product_stock("Smartphone", 5)
        self.assertTrue(result)
        updated_product = self.db_instance.get_product_by_name("Smartphone")
        self.assertEqual(updated_product["stock_quantity"], initial_qty - 5)

    def test_update_product_stock_insufficient(self):
        product = self.db_instance.get_product_by_name("Headphones")
        initial_qty = product["stock_quantity"]
        # Запитуємо зменшення більше, ніж є в наявності
        result = self.db_instance.update_product_stock("Headphones", initial_qty + 1)
        self.assertFalse(result)

    def test_update_product_stock_value(self):
        product = self.db_instance.get_product_by_name("Laptop")
        initial_qty = product["stock_quantity"]
        self.db_instance.update_product_stock("Laptop", 3)
        updated_product = self.db_instance.get_product_by_name("Laptop")
        self.assertEqual(updated_product["stock_quantity"], initial_qty - 3)

    def test_insert_order(self):
        order_data = {
            "order_id": "test_order",
            "user": {"name": "Test"},
            "products": [],
            "total_amount": 0
        }
        result = self.db_instance.insert_order(order_data)
        self.assertTrue(result)


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.db_instance = Database()
        self.client = MongoClient(connection_string_mongo)
        self.db = self.client['My']
        self.db['Products'].delete_many({})
        self.db['Orders'].delete_many({})
        self.db_instance.initialize_products()
        # Створюємо тестового користувача
        self.user = User(user_id=ObjectId(), name="Test User", email="test@example.com", password="pwd")

    def tearDown(self):
        self.db['Products'].delete_many({})
        self.db['Orders'].delete_many({})

    def test_add_product_success(self):
        order = Order(order_id=ObjectId(), user=self.user)
        order.add_product("Laptop", 2, self.db_instance)
        self.assertEqual(len(order.products), 1)

    def test_add_product_insufficient_stock(self):
        order = Order(order_id=ObjectId(), user=self.user)
        # Зменшуємо запас для "Smartphone" до маленького значення
        self.db_instance.update_product_quantity_by_name("Smartphone", -15)  # початково 20 -> 5
        order.add_product("Smartphone", 10, self.db_instance)
        self.assertEqual(len(order.products), 0)

    def test_total_amount_calculation(self):
        order = Order(order_id=ObjectId(), user=self.user)
        product = self.db_instance.get_product_by_name("Laptop")
        order.add_product("Laptop", 2, self.db_instance)
        expected_total = product["price"] * 2
        self.assertEqual(order.total_amount, expected_total)

    def test_view_order(self):
        order = Order(order_id=ObjectId(), user=self.user)
        order.add_product("PS5", 1, self.db_instance)
        details = order.view_order(self.db_instance)
        self.assertEqual(details["user"], self.user.name)
        self.assertEqual(len(details["products"]), 1)

    def test_save_order(self):
        order = Order(order_id=ObjectId(), user=self.user)
        order.add_product("Headphones", 2, self.db_instance)
        result = order.save_order(self.db_instance)
        self.assertTrue(result)

    def test_add_multiple_products(self):
        order = Order(order_id=ObjectId(), user=self.user)
        order.add_product("Laptop", 1, self.db_instance)
        order.add_product("Smartphone", 2, self.db_instance)
        self.assertEqual(len(order.products), 2)
        expected_total = (self.db_instance.get_product_by_name("Laptop")["price"] * 1 +
                          self.db_instance.get_product_by_name("Smartphone")["price"] * 2)
        self.assertEqual(order.total_amount, expected_total)

    def test_order_total_amount_accumulation(self):
        order = Order(order_id=ObjectId(), user=self.user)
        order.add_product("Laptop", 1, self.db_instance)
        order.add_product("Headphones", 3, self.db_instance)
        product1 = self.db_instance.get_product_by_name("Laptop")
        product2 = self.db_instance.get_product_by_name("Headphones")
        expected_total = product1["price"] * 1 + product2["price"] * 3
        self.assertEqual(order.total_amount, expected_total)


class TestUser(unittest.TestCase):
    def setUp(self):
        self.db_instance = Database()
        self.client = MongoClient(connection_string_mongo)
        self.db = self.client['My']
        self.db['Accounts'].delete_many({})
        self.db['Account'].delete_many({})
        self.user = User(user_id=ObjectId(), name="Test User", email="user@example.com", password="secret")

    def tearDown(self):
        self.db['Accounts'].delete_many({})
        self.db['Account'].delete_many({})

    def test_register_success(self):
        result = self.user.register(self.db_instance)
        self.assertTrue(result)

    def test_register_duplicate(self):
        self.user.register(self.db_instance)
        user2 = User(user_id=ObjectId(), name="Test User", email="user@example.com", password="secret")
        result = user2.register(self.db_instance)
        self.assertFalse(result)

    def test_login_success(self):
        self.user.register(self.db_instance)
        result = self.user.login("secret", self.db_instance)
        self.assertTrue(result)

    def test_login_failure(self):
        self.user.register(self.db_instance)
        result = self.user.login("wrong", self.db_instance)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
