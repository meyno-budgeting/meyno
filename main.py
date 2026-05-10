from core.app import add_user
from database.db import init_db

def main():
    init_db()
    email = input("Enter emaill: ")
    password = input("Enter password: ")
    
    add_user(email_in=email, password_in=password)


if __name__ == "__main__":
    main()
