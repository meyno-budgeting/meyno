# This is the day that the LORD has made. Let us rejoice and be glad in it.
# Psalm 118:24

import os
import sqlite3
from pathlib import Path

# Global Variables
SCRIPT_DIR = Path(__file__).parent

# Makes a database called budget.meyno (if it doesn't exist) and connects to it
con = sqlite3.connect("budget.meyno")

# Make a cursor to actually interact with database
cur = con.cursor()

# For now, just make an "expenses" table (will split out into account creation later)
cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id,
        date,
        payee,
        amount,
        memo
        )
    """)



con.close()