from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ValidationError, validator, constr, root_validator
from fastapi import FastAPI


class NewBook(BaseModel):
    title: str
    author: str
    genre: str
    age_rating: int


class Book(BaseModel):
    book_id: int
    title: str
    author: str
    genre: str
    age_rating: int


class NewUser(BaseModel):
    first_name: str
    second_name: str
    personal_id_nbr: str

    @validator("personal_id_nbr")
    def all_of_characters_are_digits(cls, v):
        if not v.isdigit():
            raise ValueError("Invalid value. Each character must be a digit.")
        return v

    @validator("personal_id_nbr")
    def personal_id_nbr_consists_of_eleven_digits(cls, v):
        if len(v) != 11:
            raise ValueError("personal_id_nbr has to consists of 11 digits")
        return v


class User(BaseModel):
    user_id: int
    first_name: str
    second_name: str
    personal_id_nbr: str

    @property
    def date_of_birth(self) -> date:
        day = int(self.personal_id_nbr[4:6])
        month = int(self.personal_id_nbr[2:4])
        year = int(self.personal_id_nbr[:2])
        year += {0: 1900, 1: 2000, 2: 2100, 3: 2200, 4: 1800}[month // 20]
        month %= 20
        return datetime(year, month, day).date()

    @property
    def age(self) -> int:
        today_date = datetime.now().date()
        number_of_years: int = today_date.year - self.date_of_birth.year
        if today_date.day >= self.date_of_birth.day and today_date.month >= self.date_of_birth.month:
            return number_of_years
        else:
            return number_of_years - 1


class Rental(BaseModel):
    rental_id: int
    user: User
    rented_books: list[Book]
    date: datetime


class NewRental(BaseModel):
    user_id: int
    rented_books_ids: list[int]
    date: datetime

    @root_validator
    def the_user_is_allowed_to_rent_a_book_due_to_an_age_restriction(cls, values):
        user_id, rented_books_ids = values.get("user_id"), values.get("rented_books_ids")
        user = [u for u in user_db if user_id == u.user_id][0]
        for book_id in rented_books_ids:
            book = [b for b in book_db if book_id == b.book_id][0]
            if book.age_rating > user.age:
                raise ValueError("User is under age ("+str(user.age)+") to rent the " + book.title + " ("+
                                 str(book.age_rating) + "+).")
        return values


##########################################################################################################
# FastAPI


app = FastAPI()
rental_db = []
user_db = [User(user_id=0, first_name="John",
                second_name="Doe",
                personal_id_nbr="05320708202")]
book_db = [Book(book_id=0, title="Republic of Samsung", author="Geoffrey Cain", genre="non-fiction", age_rating=16),
           Book(book_id=1, title="Good Economics", author="Esther Duflo, Abhijit V. Banerjee", genre="non-fiction", age_rating=0),
           Book(book_id=2, title="Republic of Samsung", author="Geoffrey Cain", genre="non-fiction", age_rating=22)]


@app.get("/rentals/")
def retrieve_rentals():
    return rental_db


@app.post("/rentals/")
def create_rental(rental: NewRental):
    new_id = max(i.rental_id for i in rental_db) + 1 if rental_db else 1
    new_rental = Rental(rental_id=new_id,
                        user=[u for u in user_db if u.user_id == rental.user_id][0],
                        rented_books=[b for i in rental.rented_books_ids for b in book_db if b.book_id == i],
                        date=rental.date
    )
    rental_db.append(new_rental)
    return new_rental


@app.get("/rentals/{rental_id}")
def retrieve_rental(rental_id: int):
    return [i for i in rental_db if i.rental_id == rental_id][0]


@app.get("/users/")
def retrieve_users():
    return user_db


@app.get("/users/{user_id}")
def retrieve_user(user_id: int):
    return [i for i in user_db if i.user_id == user_id][0]


@app.post("/users/")
def create_user(user: NewUser):
    new_id = max(i.user_id for i in user_db) + 1 if user_db else 1
    new_user = User(user_id=new_id,
                    first_name=user.first_name,
                    second_name=user.second_name,
                    personal_id_nbr=user.personal_id_nbr)
    user_db.append(new_user)
    return new_user


@app.get("/books/")
def retrieve_books():
    return book_db


@app.get("/books/{book_id}")
def retrieve_book(book_id: int):
    return [i for i in book_db if i.book_id == book_id][0]


@app.post("/books/")
def create_book(book: NewBook):
    new_id = max(i.book_id for i in book_db) + 1 if book_db else 1
    new_book = Book(book_id=new_id, title=book.title, author=book.author, genre=book.genre, age_rating=book.age_rating)
    book_db.append(new_book)
    return new_book

