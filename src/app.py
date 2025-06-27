from flask import Flask, render_template, request, flash, redirect, url_for
from models import db, User, Movie
from dotenv import load_dotenv
import os
import requests

# .env-Datei laden
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

app = Flask(__name__)
app.secret_key = "dev"

# Datenbankverbindung
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///../data/users.db"
db.init_app(app)

# Nur bei Bedarf aktivieren:
with app.app_context():
    db.create_all()

# Startseite: Nutzer hinzufügen & anzeigen
@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        name = request.form.get('username', '').strip()
        if not name:
            flash("Please enter your name")
        else:
            existing = User.query.filter_by(name=name).first()
            if not existing:
                new_user = User(name=name)
                db.session.add(new_user)
                db.session.commit()
                flash(f"User '{name}' added.")
        return redirect(url_for("hello"))

    users = User.query.all()
    return render_template('index.html', users=users)

# Filmseite eines Nutzers: anzeigen
@app.route("/user/<int:user_id>")
def view_movies(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("user_movies.html", user=user)

# Film hinzufügen (eigenständiger POST-Endpunkt!)
@app.route("/add_movie/<int:user_id>", methods=["POST"])
def add_movie(user_id):
    title = request.form.get("title", "").strip()
    if not title:
        flash("Please enter a movie title.")
        return redirect(url_for("view_movies", user_id=user_id))

    response = requests.get("http://www.omdbapi.com/", params={
        "apikey": OMDB_API_KEY,
        "t": title
    })
    data = response.json()

    if data.get("Response") == "True":
        new_movie = Movie(
            title=data.get("Title"),
            year=data.get("Year"),
            poster=data.get("Poster"),
            user_id=user_id
        )
        db.session.add(new_movie)
        db.session.commit()
        flash(f"{data.get('Title')} was added.")
    else:
        flash("Movie not found.")

    return redirect(url_for("view_movies", user_id=user_id))

# Film löschen
@app.route("/delete_movie/<int:movie_id>/<int:user_id>", methods=["POST"])
def delete_movie(movie_id, user_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash(f"Movie '{movie.title}' deleted.")
    return redirect(url_for("view_movies", user_id=user_id))

if __name__ == "__main__":
    app.run(debug=True)