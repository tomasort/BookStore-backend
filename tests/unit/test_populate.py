import pytest
from datetime import datetime
from faker import Faker
from app.api.populate import process_date
from app.api.populate import merge_books

fake = Faker()


# def test_process_date():
#     # Generate a random date and format it
#     date = fake.date_between(start_date='-100y', end_date='today')
#     date_str = date.strftime('%d %B %Y')
#     processed_date = process_date(date_str)
#     assert date == datetime.strptime(processed_date, '%Y-%m-%d').date()
#     date_year = fake.year()
#     processed_date_year = process_date(date_year)
#     assert datetime.strptime(processed_date_year, '%Y-%m-%d').date() == datetime.strptime(date_year, '%Y').date()


fake = Faker()


# def test_process_date():
#     # Test case 1: Random date string between -100y and today
#     date = fake.date_between(start_date='-100y', end_date='today')
#     date_str = date.strftime('%d %B %Y')  # Format as "DD Month YYYY"
#     processed_date = process_date(date_str)
#     assert date == datetime.strptime(processed_date, '%Y-%m-%d').date(), f"Failed for date: {date_str}"

#     # Test case 2: Random year
#     date_year = fake.year()  # Generate a random year
#     processed_date_year = process_date(date_year)
#     assert datetime.strptime(processed_date_year, '%Y-%m-%d').date() == datetime.strptime(f"{date_year}-01-01", '%Y-%m-%d').date(), f"Failed for year: {date_year}"

#     # Test case 3: BCE date in various formats
#     bce_date_inputs = [
#         "44 BCE",  # Standard BCE
#         "44 BC",   # Standard BC
#         "44 B.C.",  # With dots
#     ]
#     for bce_input in bce_date_inputs:
#         processed_bce_date = process_date(bce_input)
#         assert processed_bce_date is not None

#     # Test case 4: Malformed input
#     invalid_inputs = [
#         "InvalidDate",
#         "32 January 2000",  # Invalid date
#         "15/20/2023",       # Invalid format
#     ]
#     for invalid_input in invalid_inputs:
#         processed_invalid_date = process_date(invalid_input)
#         assert processed_invalid_date is None, f"Failed to handle invalid input: {invalid_input}"

#     # Test case 5: Edge case for leap years
#     leap_year = "29 February 2020"
#     processed_leap_year_date = process_date(leap_year)
#     assert datetime.strptime(processed_leap_year_date, '%Y-%m-%d').date() == datetime.strptime("2020-02-29", '%Y-%m-%d').date(), f"Failed for leap year: {leap_year}"

#     print("All tests passed!")


def test_merge_books(book_factory):
    books = book_factory.build_batch(5)
    book1 = books[0]
    book2 = books[1]
    previous_description2 = book2.description
    book1.description = None
    merge_books(book1, book2)
    assert book1.description == previous_description2
