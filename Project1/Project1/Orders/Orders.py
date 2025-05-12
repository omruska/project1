class Order:
    def __init__(self, order_id, user):
        self.order_id = order_id
        self.user = user
        self.products = []
        self.total_amount = 0

    def add_product(self, product_name, quantity, db):
        """Додає продукт до замовлення та зменшує запас товару"""
        product = db.get_product_by_name(product_name)
        if product and product.get("stock_quantity", 0) >= quantity:
            self.products.append({"product_name": product_name, "quantity": quantity})
            self.total_amount += product.get("price", 0) * quantity
            if not db.update_product_stock(product_name, quantity):
                print(f"Не вдалося зменшити запас товару для продукту {product_name}.")
            else:
                print(f"Додано {product.get('name')} x{quantity} до замовлення.")
        else:
            print(f"Продукт {product_name} не знайдений або недостатньо товару.")

    def view_order(self, db):
        """Повертає деталі замовлення"""
        order_details = {
            "order_id": str(self.order_id),
            "user": self.user.name,
            "products": [],
            "total_amount": self.total_amount
        }
        for item in self.products:
            product = db.get_product_by_name(item["product_name"])
            if product:
                order_details["products"].append({
                    "name": product.get("name"),
                    "quantity": item["quantity"]
                })
        return order_details

    def save_order(self, db):
        """Зберігає замовлення в базі даних"""
        order_data = {
            "order_id": str(self.order_id),
            "user": {
                "user_id": str(self.user.user_id),
                "name": self.user.name,
                "email": self.user.email
            },
            "products": self.products,
            "total_amount": self.total_amount
        }
        return db.insert_order(order_data)
