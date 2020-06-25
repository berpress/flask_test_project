import datetime
from random import choice

from flask import Flask, render_template, request, redirect
from sqlalchemy import desc, text

from database import db_session, init_db
from models.histories import Histories
from models.restaurants import Restaurants

app = Flask(__name__)


@app.before_first_request
def init():
    init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/")
def start():
    now = datetime.datetime.now()
    return render_template("start.html", now=now)


@app.route("/draw")
def draw():
    restaurants = Restaurants.query.all()
    if not restaurants:
        return redirect("/create-restaurant")
    random_restaurant = choice(restaurants)

    try:
        restaurant = Restaurants.query.get(random_restaurant.id)
        restaurant.draw += 1
        history = Histories(restaurant_id=restaurant.id)
        db_session.add(history)
        db_session.commit()
    except Exception:
        db_session.rollback()
        return redirect("/")

    now = datetime.datetime.now()

    return render_template("draw.html", restaurant=restaurant, now=now)


@app.route("/create-restaurant", methods=["GET", "POST"])
def create_restaurant():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        site_url = request.form.get("site_url")
        restaurant = Restaurants(name, description, site_url)
        db_session.add(restaurant)
        db_session.commit()
        return redirect("/restaurants")
    return render_template("create_restaurant.html")


@app.route("/restaurants")
def restaurants_list():
    restaurants = Restaurants.query.all()
    return render_template("restaurants.html", restaurants=restaurants)


@app.route("/edit-restaurant", methods=["GET", "POST"])
def edit_restaurant():
    id = request.args.get("id")

    restaurant = Restaurants.query.filter(Restaurants.id == id).first()
    print(restaurant)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        site_url = request.form.get("site_url")

        restaurant.name = name
        restaurant.description = description
        restaurant.site_url = site_url
        restaurant.modified_time = datetime.datetime.now()
        db_session.commit()
        return redirect("/restaurants")
    return render_template("edit_restaurant.html", restaurant=restaurant)


@app.route("/delete-restaurant")
def delete_restaurant():
    id = request.args.get("id")
    restaurant = Restaurants.query.filter(Restaurants.id == id).first()

    if restaurant:
        db_session.delete(restaurant)
        db_session.commit()
    return redirect("/restaurants")


@app.route("/top")
def top():
    restaurants = Restaurants.query.order_by(text("-draw")).limit(5)
    return render_template("top.html", restaurants=restaurants)


@app.route("/history")
def history():
    histories = Histories.query.order_by(desc(Histories.created_time)).limit(20)
    return render_template("history.html", histories=histories)


def meal_format(value):
    if 3 < value.hour < 10:
        return "Breakfast"
    elif 9 < value.hour < 16:
        return "Lunch"
    return "Diner"


def datetime_format(value):
    return value.strftime("%d-%m-%Y %H:%M:%S")


app.jinja_env.filters["meal"] = meal_format
app.jinja_env.filters["datetime"] = datetime_format

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.run(debug=True)
