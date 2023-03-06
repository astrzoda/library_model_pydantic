from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ValidationError, validator, constr


class Book(BaseModel):
    title: str
    author: str
    # total_number_of_pieces: int
    # rented_pieces: int
    genre: str
    age_rating: int


class User(BaseModel):
    first_name: str
    second_name: str
    personal_id_nbr: str

    @validator("personal_id_nbr")
    def personal_id_nbr_consists_of_eleven_digits(cls, v):
        if len(v) != 11:
            raise ValueError("personal_id_nbr has to consists of 11 digits")
        return v

    @validator("personal_id_nbr")
    def year_is_between_1900_and_2299(cls, v):
        month_component: str = v[2:4]
        if not (0 <= int(month_component[0]) <= 7):
            raise ValueError("Given personal_id_nbr year is not supported. Supported years: 1900-2299")
        return v

    @property
    def date_of_birth(self) -> date:
        month = int(self.personal_id_nbr[2:4])
        if month < 20:
            year = int("19" + self.personal_id_nbr[:2])
        elif month < 40:
            month -= 20
            year = int("20"+self.personal_id_nbr[:2])
        elif month < 60:
            month -= 40
            year = int("21" + self.personal_id_nbr[:2])
        else:
            month -= 60
            year = int("22" + self.personal_id_nbr[:2])
        day = int(self.personal_id_nbr[4:6])
        return datetime(year, month, day).date()

    @property
    def age(self):
        today_date = datetime.now().date()
        number_of_years: int = today_date.year - self.date_of_birth.year
        if today_date.day >= self.date_of_birth.day and today_date.month >= self.date_of_birth.month:
            return number_of_years
        else:
            return number_of_years - 1


class Rental(BaseModel):
    user: User
    rented_books: list[tuple[Book, int]]
    date: datetime

    @validator("rented_books", each_item=True)
    def the_user_is_allowed_to_rent_a_book_due_to_an_age_restriction(cls, v):
        if v[0].age_rating > user.age: # TODO: is the usage of user.age ok?
            raise ValueError("The legal age of " + v[0].title+" is " +
                             str(v[0].age_rating)+". The user is "+str(user.age)+" years old.")
        return v

    # TODO: i don't know if it's ok
    # @validator("rented_books")
    # def exceeding_the_number_of_books_available_for_rent_by_the_user(cls, v):
    #     rental_limit = 0
    #     total_sum_of_rented_books = 0
    #     for rented_book in v:
    #         book, amount = rented_book
    #         total_sum_of_rented_books += amount
    #     if total_sum_of_rented_books > rental_limit:
    #         raise ValueError("Maximum amount of books for rental per day is "+str(rental_limit)+".")


if __name__ == '__main__':
    user = User(first_name="John", second_name="Doe", personal_id_nbr="05230708202")
    try:
        rental = Rental(user=user,
                        rented_books=[(Book(title="Republic of Samsung",
                                            author="Geoffrey Cain",
                                            genre="non-fiction",
                                            age_rating=18), 1)],
                        date=datetime(2023, 6, 3))
    except ValidationError as e:
        print(e)
    try:
        rental = Rental(user=user,
                        rented_books=[(Book(title="Republic of Samsung",
                                            author="Geoffrey Cain",
                                            genre="non-fiction",
                                            age_rating=10), 1)],
                        date=datetime(2023, 6, 3))
    except ValidationError as e:
        print(e)
