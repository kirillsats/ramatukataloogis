import ison
from tkinter import *
import tkinter as tk
from tkinter import ttk
from sqlite3 import *
from sqlite import Error
import tkinter




create_table_zanrid = """
CREATE TABLE IF NOT EXIST zanrid(
zanr_id INTEGER PRIMARY KEY AUTOINCREMENT,)
zanri_nimi TEXT not null;
"""

create_table_autorid = """
CREATE TABLE IF NOT EXISTS autorid(
autor_id INTEGER PRIMARY KEY AUTOINCREMENT,
autor_nimi TEXT not null,
sunnikuupaev date not null);
"""


create_table_raamatud= """
CREATE TABLE IF NOT EXIST raamatud(
raamat_id INTEGER PRIMARY KEY AUTOINCREMENT,
raamat_nimi TEXT NOT NULL,
pealkiri TEXT not null,
valjaandmise_kuupaev date not null,
autor_id int,
foreign key (autor_id),
zanr_id int,
foreign key (zanr_id));
"""


create_zanr = """
INSERT INTO 
  zanrid(zanri_nimi)
VALUES
  ('Draama'),
  ('Horror'),
  ('Komedia'),
  ('Romaan'),
  ('Luuletus');
"""


zanr = input("Valige zanr:")
add_genre(conn, zanr)
zanrid = execute_read_query(conn, select_zanrid)
print(zanrid)

def execute_query(connection, query: str, params=None):
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else: 
            cursor.execute(query)
        connection.commit()
        print("Õ")
    except Error as e:
        print(f"V")