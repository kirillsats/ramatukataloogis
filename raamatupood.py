
import json
from tkinter import *
import tkinter as tk
from tkinter import ttk
from sqlite3 import *
from sqlite3 import Error
from os import *


def create_connection(path: str):
    
    conn = None
    try:
        conn = connect(path)
        print(f"Connected to database")
        return conn
    except Error as e:
        print(e)

def execute_query(connection, query: str, params=None):
    """Execute a single query"""
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"Error executing query: {e}")

def execute_read_query(connection, query: str, params=None):
    """Execute a read query and return the result"""
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error executing query: {e}")

create_table_zanrid = """
CREATE TABLE IF NOT EXISTS zanrid(
    zanr_id INTEGER PRIMARY KEY AUTOINCREMENT,
    zanri_nimi TEXT NOT NULL
)
"""

create_table_autorid = """
CREATE TABLE IF NOT EXISTS autorid(
    autor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    autor_nimi TEXT NOT NULL,
    sunnikuupaev DATE NOT NULL
)
"""

create_table_raamatud = """
CREATE TABLE IF NOT EXISTS raamatud(
    raamat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raamat_nimi TEXT NOT NULL,
    pealkiri TEXT NOT NULL,
    valjaandmise_kuupaev DATE NOT NULL,
    autor_id INTEGER NOT NULL,
    zanr_id INTEGER NOT NULL,
    FOREIGN KEY (autor_id) REFERENCES autorid(autor_id),
    FOREIGN KEY (zanr_id) REFERENCES zanrid(zanr_id)
)
"""

create_zanr = """
INSERT INTO zanrid(zanri_nimi)
VALUES
  ('Draama'),
  ('Horror'),
  ('Komedia'),
  ('Romaan'),
  ('Luuletus')
"""
drop_table_zanrid = """
drop table zanrid
"""

select_from_zanr = """
SELECT * FROM zanrid"""

#SelectAutor = ['HorrorAutor', 'DramaAutor'] списком нельзя
#HorrorAutor = ['Stephen King', 'Bram Stoker', 'Richard Bachman', 'Anne Rice', 'Shirley Jackson' ]
Autor = ['Nimi']
Zanr = ['Horror']
Raamat =['nimi']

def display_results(results):
    text.delete(1.0, tk.END)
    for result in results:
        text.insert(tk.END, f"Raamat: {Raamat}, zanr: {Zanr}, Autor: {Autor}\n")

  

def genre_selected(event):
    selected_genre = genre_combobox.get()
    if selected_genre == "All Genres":
        zanrid = execute_read_query(conn, select_from_zanr)
    else:
        query = f"SELECT * FROM zanrid WHERE zanri_nimi = '{selected_genre}'"
        zanrid = execute_read_query(conn, query)
    display_results(zanrid)

root = tk.Tk()
root.title("Database Query Results")

# выбор жанра
genres = ["All Genres", "Draama", "Horror", "Komedia", "Romaan", "Luuletus"]
genre_combobox = ttk.Combobox(root, values=genres)
genre_combobox.current(0)
genre_combobox.bind("<<ComboboxSelected>>", genre_selected)
genre_combobox.pack()

# отобажение результвта
text = tk.Text(root, wrap="word")
text.pack(fill="both", expand=True)

filename = path.abspath(__file__)
dbdir = filename.rsplit("raamatupood.py")
current_dir = getcwd()
dbpath = path.join(current_dir, "data.db")
conn = create_connection(dbpath)

execute_query(conn, create_table_zanrid)
execute_query(conn, create_table_autorid)
execute_query(conn, create_table_raamatud)
execute_query(conn, create_zanr)
execute_query(conn, select_from_zanr)
zanrid = execute_read_query(conn, select_from_zanr)
display_results(zanrid)

conn.close()

root.mainloop()