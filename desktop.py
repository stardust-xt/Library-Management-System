#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import os
from datetime import datetime, timedelta

class Book:
    def __init__(self, title, author, isbn):
        self._title = title
        self._author = author
        self._isbn = isbn
        self._is_borrowed = False
        self._due_date = None

    @property
    def title(self): return self._title

    @property
    def author(self): return self._author

    @property
    def isbn(self): return self._isbn

    @property
    def is_borrowed(self): return self._is_borrowed

    @is_borrowed.setter
    def is_borrowed(self, value):
        if isinstance(value, bool):
            self._is_borrowed = value

    @property
    def due_date(self): return self._due_date

    def borrow(self):
        if not self._is_borrowed:
            self._is_borrowed = True
            self._due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            return True
        return False

    def return_book(self):
        if self._is_borrowed:
            self._is_borrowed = False
            self._due_date = None
            return True
        return False

    def __str__(self):
        status = f"Borrowed (Due: {self._due_date})" if self._is_borrowed else "Available"
        return f"Title: {self._title}, Author: {self._author}, ISBN: {self._isbn}, Status: {status}"

    def to_dict(self):
        return {
            'title': self._title,
            'author': self._author,
            'isbn': self._isbn,
            'is_borrowed': self._is_borrowed,
            'due_date': self._due_date
        }

    @classmethod
    def from_dict(cls, data):
        book = cls(data['title'], data['author'], data['isbn'])
        book._is_borrowed = data['is_borrowed']
        book._due_date = data.get('due_date')
        return book

class User:
    MAX_BORROW_LIMIT = 3

    def __init__(self, name, user_id):
        self._name = name
        self._user_id = user_id
        self._borrowed_books_isbns = []

    @property
    def name(self): return self._name

    @property
    def user_id(self): return self._user_id

    @property
    def borrowed_books_isbns(self): return list(self._borrowed_books_isbns)

    def can_borrow(self):
        return len(self._borrowed_books_isbns) < self.MAX_BORROW_LIMIT

    def add_borrowed_book_isbn(self, isbn):
        if isbn not in self._borrowed_books_isbns and self.can_borrow():
            self._borrowed_books_isbns.append(isbn)

    def remove_borrowed_book_isbn(self, isbn):
        if isbn in self._borrowed_books_isbns:
            self._borrowed_books_isbns.remove(isbn)

    def __str__(self):
        return f"User: {self._name} (ID: {self._user_id}), Borrowed Books: {len(self._borrowed_books_isbns)}"

    def to_dict(self):
        return {
            'name': self._name,
            'user_id': self._user_id,
            'borrowed_books_isbns': self._borrowed_books_isbns
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data['name'], data['user_id'])
        user._borrowed_books_isbns = data.get('borrowed_books_isbns', [])
        return user

class Library:
    def __init__(self, book_file='books.json', user_file='users.json'):
        self._books = {}
        self._users = {}
        self._data_file_books = book_file
        self._data_file_users = user_file
        self._load_data()

    def _load_data(self):
        if os.path.exists(self._data_file_books):
            with open(self._data_file_books, 'r') as f:
                books_data = json.load(f)
                for isbn, b in books_data.items():
                    self._books[isbn] = Book.from_dict(b)
        if os.path.exists(self._data_file_users):
            with open(self._data_file_users, 'r') as f:
                users_data = json.load(f)
                for uid, u in users_data.items():
                    self._users[uid] = User.from_dict(u)

    def _save_data(self):
        with open(self._data_file_books, 'w') as f:
            json.dump({isbn: book.to_dict() for isbn, book in self._books.items()}, f, indent=4)
        with open(self._data_file_users, 'w') as f:
            json.dump({uid: user.to_dict() for uid, user in self._users.items()}, f, indent=4)

    def add_book(self, book):
        if book.isbn in self._books:
            return False
        self._books[book.isbn] = book
        self._save_data()
        return True

    def remove_book(self, isbn):
        if isbn in self._books and not self._books[isbn].is_borrowed:
            del self._books[isbn]
            self._save_data()
            return True
        return False

    def register_user(self, user):
        if user.user_id in self._users:
            return False
        self._users[user.user_id] = user
        self._save_data()
        return True

    def remove_user(self, user_id):
        if user_id in self._users and not self._users[user_id].borrowed_books_isbns:
            del self._users[user_id]
            self._save_data()
            return True
        return False

    def borrow_book(self, isbn, user_id):
        if isbn in self._books and user_id in self._users:
            book = self._books[isbn]
            user = self._users[user_id]
            if not book.is_borrowed and user.can_borrow():
                if book.borrow():
                    user.add_borrowed_book_isbn(isbn)
                    self._save_data()
                    return True
        return False

    def return_book(self, isbn, user_id):
        if isbn in self._books and user_id in self._users:
            book = self._books[isbn]
            user = self._users[user_id]
            if isbn in user.borrowed_books_isbns:
                if book.return_book():
                    user.remove_borrowed_book_isbn(isbn)
                    self._save_data()
                    return True
        return False

    def search_book(self, query):
        result = []
        for book in self._books.values():
            if query.lower() in book.title.lower() or query.lower() in book.author.lower() or query == book.isbn:
                result.append(book)
        return result

    def display_all_books(self, show_available_only=False):
        for book in self._books.values():
            if show_available_only and book.is_borrowed:
                continue
            print(book)

    def display_all_users(self):
        for user in self._users.values():
            print(user)

    def display_user_borrowed_books(self, user_id):
        if user_id in self._users:
            user = self._users[user_id]
            for isbn in user.borrowed_books_isbns:
                print(self._books[isbn])
        else:
            print("User not found.")

    def report_overdue_books(self):
        today = datetime.now()
        for book in self._books.values():
            if book.is_borrowed and book.due_date:
                due = datetime.strptime(book.due_date, '%Y-%m-%d')
                if today > due:
                    days_late = (today - due).days
                    fee = days_late * 5  # ₹5 per day late
                    print(f"Overdue: {book} (Due {book.due_date}) - Late by {days_late} day(s), Fee: ₹{fee}")

def main():
    lib = Library()

    while True:
        print("\nLibrary Menu")
        print("1. Add Book\n2. Register User\n3. Borrow Book\n4. Return Book\n5. Search Book\n6. Show All Books\n7. Show Available Books\n8. Show Users\n9. Show User's Borrowed Books\n10. Show Overdue Books\n11. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            title = input("Title: ")
            author = input("Author: ")
            isbn = input("ISBN: ")
            if lib.add_book(Book(title, author, isbn)):
                print("Book added.")
            else:
                print("Book already exists.")

        elif choice == '2':
            name = input("Name: ")
            uid = input("User ID: ")
            if lib.register_user(User(name, uid)):
                print("User registered.")
            else:
                print("User ID already exists.")

        elif choice == '3':
            isbn = input("Book ISBN: ")
            uid = input("User ID: ")
            if lib.borrow_book(isbn, uid):
                print("Book borrowed.")
            else:
                print("Borrow failed. Either the book is not available or user has reached borrowing limit.")

        elif choice == '4':
            isbn = input("Book ISBN: ")
            uid = input("User ID: ")
            if lib.return_book(isbn, uid):
                print("Book returned.")
            else:
                print("Return failed.")

        elif choice == '5':
            q = input("Enter title, author, or ISBN: ")
            results = lib.search_book(q)
            for b in results:
                print(b)

        elif choice == '6':
            lib.display_all_books()

        elif choice == '7':
            lib.display_all_books(show_available_only=True)

        elif choice == '8':
            lib.display_all_users()

        elif choice == '9':
            uid = input("User ID: ")
            lib.display_user_borrowed_books(uid)

        elif choice == '10':
            lib.report_overdue_books()

        elif choice == '11':
            break

        else:
            print("Invalid choice.")


if __name__ == '__main__':
    main()

