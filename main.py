from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

class RateMovieForm(FlaskForm):
    rating = StringField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])

    submit = SubmitField('Done')

class NewMovieForm(FlaskForm):
    movie_title = StringField('Movie Title', validators=[DataRequired()])

    submit = SubmitField('Add Movie')

# CREATE DB

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-movies-collection.db"
db.init_app(app)

search_movie_url = "https://api.themoviedb.org/3/search/movie"
movie_details_url = "https://api.themoviedb.org/3/movie/"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjMGNiMjg4MjMyYWM4NWI3MTllN2E2NzY4MzE4MGIwMCIsIm5iZiI6MTcyMzAyMjc1OC42MzU2LCJzdWIiOiI2NmIzMzg1MmNjOWNkYjNhOWU3YjkxZTIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.H0zyhikFIxSAM2w6z4BXHpHBuNg_P8a3iiJnZIAYoPc",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
}

# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[float] = mapped_column(Float, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)



with app.app_context():
    db.create_all()

# with app.app_context():
#     second_movie = Movie(
#         title="Avatar The Way of Water",
#         year=2022,
#         description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#         rating=7.3,
#         ranking=9,
#         review="I liked the water.",
#         img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
#     )
#     db.session.add(second_movie)
#     db.session.commit()


@app.route("/")
def home():

    result = db.session.execute(db.select(Movie).order_by(Movie.title))
    all_movies = result.scalars().all()

    return render_template("index.html", all_movies=all_movies)

@app.route("/edit", methods=["GET", "POST"])
def edit():

    form = RateMovieForm()
    movie_id = request.args.get('id')

    if form.validate_on_submit():
        rating = form.rating.data
        review = form.review.data

        with app.app_context():

            movie_to_update = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
            movie_to_update.rating = rating
            movie_to_update.review = review
            db.session.commit()

            result = db.session.execute(db.select(Movie).order_by(Movie.title))
            all_movies = result.scalars().all()

        return render_template("index.html", all_movies=all_movies)
    return render_template("edit.html", form=form)

@app.route("/delete")
def delete():

    movie_id = request.args.get('id')
    with app.app_context():
        book_to_delete = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
        db.session.delete(book_to_delete)
        db.session.commit()

        result = db.session.execute(db.select(Movie).order_by(Movie.title))
        all_movies = result.scalars().all()

    return render_template("index.html", all_movies=all_movies)

@app.route("/add", methods=["GET", "POST"])
def add():

    form = NewMovieForm()

    if form.validate_on_submit():
        movie_title = form.movie_title.data

        params = {
            "query": movie_title
        }

        all_movies_response = requests.get(search_movie_url, headers=headers, params=params).json()['results']

        return render_template("select.html", all_movies_response=all_movies_response)

    return render_template("add.html", form=form)

@app.route("/search", methods=["GET", "POST"])
def search_new_movie():

    id = request.args.get('id')
    response = requests.get(movie_details_url + id, headers=headers).json()

    title = response['title']
    img_url = "https://image.tmdb.org/t/p/w500" + response['poster_path']
    year = int(response['release_date'].split("-")[0])
    description = response['overview']

    new_movie = Movie(title=title, img_url=img_url, year=year, description=description)
    db.session.add(new_movie)
    db.session.commit()


    return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run()
