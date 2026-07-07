from flask import Flask
from database.db import get_db, init_db, seed_db

app = Flask(__name__)

with app.app_context():
    init_db()
    seed_db()


@app.route("/")
def index():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
