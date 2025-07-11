# This is the day that the LORD has made. Let us rejoice and be glad in it.
# Psalm 118:24

import os
import sqlite3
from pathlib import Path

# Global Variables
SCRIPT_DIR = Path(__file__).parent

def meyno_basic():
    # Makes a database called budget.meyno (if it doesn't exist) and connects to it
    con = sqlite3.connect("budget.meyno")

    # Make a cursor to actually interact with database
    cur = con.cursor()

    # For now, just make an "expenses" table (will split out into account creation later)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY,
            date TEXT,
            payee TEXT,
            amount REAL,
            memo REAL
            )
        """)
    
    # cur.execute("""
    #             INSERT INTO expenses VALUES (1, '7/11/2025', 'GameStop', 69.99, 'Metroid Prime 4')
    #             """)
    # Get most recent id:
    res = cur.execute("SELECT id FROM expenses")
    
    
    
    
    
    
    actions = {
        "1": "Add a transaction",
        "2": "Update a transaction"
    }

    for choice, desc in actions.items():
        print(f"{choice}. {desc}")
        
    action = input("What would you like to do? (Select Number): ")

    if action in actions:
        match action:
            case "1": # Adding transaction
                print(7)    
            case _:
                print("Not currently supported")
                con.close()
                return
    else:
        con.close()
        return
        

# match hello:
#     case "yes":
#         x = 7
#     case _:
#         x = 8
        
# print(x)

    con.close()
    
if __name__ == "__main__":
    meyno_basic()