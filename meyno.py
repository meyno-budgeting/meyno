# This is the day that the LORD has made. Let us rejoice and be glad in it.
# Psalm 118:24

import os
import sqlite3
from pathlib import Path
import uuid

# Global Variables
SCRIPT_DIR = Path(__file__).parent

def meyno_basic():
    # Makes a database called budget.meyno (if it doesn't exist) and connects to it
    con = sqlite3.connect("budget.meyno")
    # con.row_factory = sqlite3.Row

    # Make a cursor to actually interact with database
    cur = con.cursor()

    # For now, just make an "expenses" table (will split out into account creation later)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id TEXT PRIMARY KEY,
            date TEXT,
            payee TEXT,
            amount REAL,
            memo TEXT
            )
        """)
    
    # cur.execute("""
    #             INSERT INTO expenses VALUES (2, '7/11/2025', 'GameStop', 69.99, 'Metroid Prime 4')
    #             """)
    
    # con.commit()
    
    # # Get most recent id:
    # res = cur.execute("SELECT id FROM expenses")
    # print(res.fetchone()['id'])
    
    actions = {
        "1": "Add a transaction",
        # "2": "Update a transaction"
    }

    for choice, desc in actions.items():
        print(f"{choice}. {desc}")
        
    action = input("What would you like to do? (Select Number): ")

    if action in actions:
        match action:
            case "1": # Adding transaction
                print("Adding transaction...")
                # Generate a UUID for the transaction
                id = str(uuid.uuid4())                
                
                # Get input for remaining fields
                date = ""
                payee = input("Payee: ")
                amount = float(input("Enter Amount: "))
                memo = input("Notes: ")
                
                row_tuple = (id, date, payee, amount, memo)
                # print(row_tuple)
                
                
                
                # Insert row into table:
                cur.execute("INSERT INTO expenses VALUES (?, ?, ?, ?, ?)", row_tuple)
                con.commit()
                
                # Display whole table in console
                for row in cur.execute("SELECT * FROM expenses"):
                    print(row)
            case _:
                print("Not currently supported")
                con.close()
                return
    else:
        print("Invalid choice")
        con.close()
        return

    con.close()
    
if __name__ == "__main__":
    meyno_basic()