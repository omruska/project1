from bson import ObjectId

class User:
    def __init__(self, user_id, name, email, password):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password

    def register(self, db):
        """Реєстрація користувача без серйозної безпеки та логіки"""
        collection = db.db['Accounts']
        if collection.find_one({"email": self.email}):
            print("Користувач з таким email вже існує.")
            return False
        data = {
            "user_id": str(self.user_id),
            "name": self.name,
            "email": self.email,
            "password": self.password
        }
        collection.insert_one(data)
        return True

    def login(self, password, db):
        """Аутентифікація користувача без серйозної безпеки та логіки"""
        collection = db.db['Accounts']
        user = collection.find_one({"email": self.email})
        return user is not None and user.get("password") == password
