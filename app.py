from flask import Flask, render_template, request
from database import db_session, init_db

app = Flask(__name__)


@app.before_first_request
def init():
    init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/")
def start():
    return "Hello world!"


@app.route("/create-restaurant", methods=["GET", "POST"])
def create_restaurant():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        site_url = request.form.get("site_url")
        return f"{name}, {description}, {site_url}"
    return render_template("create_restaurant.html")


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.run(debug=True)
