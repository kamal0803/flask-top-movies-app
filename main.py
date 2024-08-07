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


# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[float] = mapped_column(Float, nullable=False)
    review: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)



with app.app_context():
    db.create_all()

with app.app_context():
    second_movie = Movie(
        title="Avatar The Way of Water",
        year=2022,
        description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
        rating=7.3,
        ranking=9,
        review="I liked the water.",
        img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
    )
    db.session.add(second_movie)
    db.session.commit()


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

        return render_template("index.html")
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

        return render_template("index.html")

    return render_template("add.html", form=form)


if __name__ == '__main__':
    app.run()
