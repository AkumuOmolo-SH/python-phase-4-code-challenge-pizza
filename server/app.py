#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify, abort
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def get_endpoint():
    restaurants = [r.to_dict() for r in Restaurant.query.all()]
    return jsonify(restaurants), 200


@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    if request.method == "GET":
        return jsonify(restaurant.to_dict()), 200

    elif request.method == ["DELETE"]:
        db.session.delete(restaurant)
        db.session.commit()

        return '', 204


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = [p.to_dict for p in Pizza.query.all()]

    return jsonify(pizzas), 200


@app.route("/restaurant_pizzas", methods=["POST"])
def add_pizza():
    data = request.get_json()

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if price is None or pizza_id is None or restaurant_id is None:
        return jsonify({"errors": ["price, pizza_id, and restaurant_id are required"]}), 404

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return jsonify({"error": "Pizza or restaurant not found"}), 404

    try:
        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

    response = {
        "id": restaurant_pizza.id,
        "price": restaurant_pizza.price,
        "pizza_id": pizza.id,
        "restaurant_id": restaurant.id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
    }

    return jsonify(response), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
