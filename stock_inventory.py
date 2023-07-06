from flask import Flask, request
from flask_restful import Resource, Api
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
api = Api(app)

# Create the database connection
conn = sqlite3.connect("inventory.db",check_same_thread=False)
cursor = conn.cursor()

# Create the product table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        name TEXT,
        price REAL,
        quantity INTEGER,
        date_added TEXT
    )
""")

# Function to add a product to the database
def add_product(category, name, price, quantity, date_added):
    """ Null value check 
        Convert price and quantity to numeric values
    """
    # Convert price and quantity to numeric values
    try:
        price = float(price)
        quantity = float(quantity)
    except ValueError:
        return {"error": "Invalid price or quantity."}

    # Insert the product into the database
    cursor.execute("""
        INSERT INTO products (category, name, price, quantity, date_added)
        VALUES (?, ?, ?, ?, ?)
    """, (category, name, price, quantity, date_added))
    conn.commit()
    return {"message": "Product added to the inventory."}

# Validate the value
def validate_date(value):
    """ Validate date
        read time specific format
    """
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Validate float value
def validate_float(value):
    """
        Validate float value
        or except value error
    """
    try:
        float(value)
        return True
    except ValueError:
        return False

# Validate positive float value
def validate_positive_float(value):
    """
        Check float value positive
        and also check greater than or equal
    """
    if validate_float(value) and float(value) >= 1:
        return True
    return False

# Check duplicates Enter or not
def check_duplicate(category, name, price, quantity, date_added):
    """
        All value duplicate will not accept 
        error print existing product
    """
    cursor.execute('SELECT * FROM products WHERE category = ? AND name = ? AND price=? AND quantity=? AND date_added=?', (category, name, price, quantity, date_added))
    return cursor.fetchone() is not None

# Filter category
def filter_by_category(category):
    """
    Function to filter products by category.
    fetch all from memory to print result
    and display the products
    """
    cursor.execute("SELECT * FROM products WHERE category=?", (category,))
    products = cursor.fetchall()
    return {"products": products}

# Filter product_name
def filter_by_product_name(product_name):
    """
    Function to filter products by product name
    fetch all from memory to print result
    and display the products
    """
    cursor.execute("SELECT * FROM products WHERE name=?", (product_name,))
    products = cursor.fetchall()
    return {"products": products}

# Filter by date
def filter_by_date_added(days):
    """
    Function to filter products by date added
    fetch all from memory to print result
    and display the product
    """
    date_limit = datetime.now() - timedelta(days=days)
    cursor.execute(
        "SELECT * FROM products WHERE date_added < ?", (date_limit.strftime("%Y-%m-%d"),))
    products = cursor.fetchall()
    return {"products": products}

# Display inventory
def display_inventory():
    """
        Added products 
        Function to display current inventory
    """
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return {"products": products}

class ProductResource(Resource):
    def post(self):
        category = request.form.get("category")
        name = request.form.get("name")
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        date_added = request.form.get("date_added")

        if not category or not name or not price or not quantity or not date_added:
            return {"error": "Missing required fields."}, 400

        if not validate_positive_float(price) or not validate_positive_float(quantity):
            return {"error": "Invalid price or quantity."}, 400

        if not validate_date(date_added):
            return {"error": "Invalid date format. Please use yyyy-MM-dd"}, 400

        if check_duplicate(category, name, price, quantity, date_added):
            return {"error": "Product already exists."}, 409

        result = add_product(category, name, price, quantity, date_added)
        return result

class CategoryResource(Resource):
    def get(self, category):
        result = filter_by_category(category)
        return result

class ProductNameResource(Resource):
    def get(self, product_name):
        result = filter_by_product_name(product_name)
        return result

class DateAddedResource(Resource):
    def get(self, days):
        result = filter_by_date_added(int(days))
        return result

class InventoryResource(Resource):
    def get(self):
        result = display_inventory()
        return result

api.add_resource(ProductResource, '/product',methods=['POST'])
api.add_resource(CategoryResource, '/category/<string:category>')
api.add_resource(ProductNameResource, '/product_name/<string:product_name>')
api.add_resource(DateAddedResource, '/date_added/<int:days>')
api.add_resource(InventoryResource, '/inventory')

if __name__ == "__main__":
  app.debug=True
  app.run()
