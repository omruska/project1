from dotenv import load_dotenv
import os

load_dotenv()

connection_string_mongo = os.getenv('CONNECTION_STRING_MONGO')