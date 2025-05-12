from bson import ObjectId
from Users.Users import User
from Orders.Orders import Order
from Database.Databases import Database

# Ініціалізація бази даних
db = Database()

# Оновлення кількості товару за назвою
db.update_product_quantity_by_name("PS5", 5)
db.update_product_quantity_by_name("Laptop", 15)
db.update_product_quantity_by_name("Smartphone", 3)
db.update_product_quantity_by_name("Headphones", 3)

# Створення користувача
user1 = User(user_id=ObjectId(), name="John Doe", email="john@example.com", password="1306986")
if user1.register(db):
    print("Користувач успішно зареєстрований.")
else:
    print("Реєстрація не вдалася.")

# Логін користувача
if user1.login("1306986", db):
    print("Користувач успішно увійшов.")
else:
    print("Невірні облікові дані.")

# Створення замовлення та додавання продуктів
order = Order(order_id=ObjectId(), user=user1)
order.add_product("Laptop", 2, db)
order.add_product("PS5", 3, db)
order.add_product("Smartphone", 5, db)

# Перегляд замовлення
order_details = order.view_order(db)
print("Деталі замовлення:", order_details)

# Збереження замовлення в базі даних
if order.save_order(db):
    print("Замовлення збережено.")
else:
    print("Помилка збереження замовлення.")
