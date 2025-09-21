#!/usr/bin/env python3
import os
from flask import Flask, request
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.compact = False

    db.init_app(app)
    Migrate(app, db)

    @app.route("/")
    def index():
        return "<h1>Code challenge</h1>"

    @app.route("/restaurants", methods=["GET"])
    def get_restaurants():
        restaurants = Restaurant.query.all()
        out = []
        for r in restaurants:
            d = r.to_dict()
            if "restaurant_pizzas" in d:
                d.pop("restaurant_pizzas")
            out.append(d)
        return out, 200

    @app.route("/restaurants/<int:id>", methods=["GET"])
    def get_restaurant(id):
        r = Restaurant.query.get(id)
        if not r:
            return {"error": "Restaurant not found"}, 404
        d = r.to_dict()
        return d, 200

    @app.route("/restaurants/<int:id>", methods=["DELETE"])
    def delete_restaurant(id):
        r = Restaurant.query.get(id)
        if not r:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(r)
        db.session.commit()
        return "", 204

    @app.route("/pizzas", methods=["GET"])
    def get_pizzas():
        pizzas = Pizza.query.all()
        out = [p.to_dict() for p in pizzas]
        for d in out:
            d.pop("restaurant_pizzas", None)
        return out, 200

    @app.route("/restaurant_pizzas", methods=["POST"])
    def create_restaurant_pizza():
        data = request.get_json() or {}
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)
        if not pizza or not restaurant:
            return {"errors": ["validation errors"]}, 400

        try:
            rp = RestaurantPizza(
                price=price, pizza_id=pizza_id, restaurant_id=restaurant_id
            )
            db.session.add(rp)
            db.session.commit()
        except ValueError:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400

        rp_dict = rp.to_dict()
        return rp_dict, 201

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
