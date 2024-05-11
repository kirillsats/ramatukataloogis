import tkinter as tk
from tkinter import ttk
from sqlite3 import connect, Error
from os import path, getcwd

# Подключение к базе данных
def create_connection(path: str):
    conn = None
    try:
        conn = connect(path)
        print(f"Connected to database")
        return conn
    except Error as e:
        print(e)

#выполняет запрос к базе данных
def execute_query(connection, query: str, params=None):
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
#читает файлы
def execute_read_query(connection, query: str, params=None):
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error executing read query: {e}")

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
insert_into_autorid = """
INSERT INTO autorid(autor_nimi,sunnikuupaev) 
VALUES ('Stephen King', '1947-09-21'),
('Bram Stoker', '1847-11-08'),
('Richard Bachman', '1936-06-23'),
('William Shakespeare', '1564-04-04'),
('Bernard Shaw', '1856-07-26'), 
("Eugene O'Neill", '1888-10-16'),
#остались эти авторы и их книги
('Evgeny Petrov', '1902-12-13'),
('Denis Fonvizin', '1745-04-14'),
('Vasily Kapnist','1758-02-23'),
('Jojo Moyes', '1969-08-04'), 
('Colin McCullough','1937-06-01'),
('Cecilia Ahern','1981-09-30'),
('Vsevolod Garshin', '1855-02-14'),
('Valentin Kataev', '1897-01-28'),
('Anton Delvig', '1798-08-17')
"""


#SelectAutor = ['HorrorAutor', 'DramaAutor'] списком нельзя
#HorrorAutor = ['Stephen King', 'Bram Stoker', 'Richard Bachman', 'Anne Rice', 'Shirley Jackson' ]



create_table_raamatud = """
CREATE TABLE IF NOT EXISTS raamatud(
    raamat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raamat_nimi TEXT NOT NULL,
    autor_id INTEGER NOT NULL,
    zanr_id INTEGER NOT NULL,
    FOREIGN KEY (autor_id) REFERENCES autorid(autor_id),
    FOREIGN KEY (zanr_id) REFERENCES zanrid(zanr_id)
)
"""
insert_into_raamatud = """
INSERT INTO raamatud(raamat_nimi, autor_id, zanr_id)
VALUES
  ('The Shining', 1, 1),
  ('It', 1, 1),
  ('Carrie', 1, 1),
  ('Misery', 1, 1),
  ('The Long Walk', 1, 1),
  ('Dracula', 2, 1),
  ("Dracula's Guest", 2, 1),
  ('The Mystery of the Sea', 2, 1),
  ('The Running Man', 3, 1),
  ('Thinner', 3, 1),
  ('Blaze', 3, 1),
  ('Hamlet', 4, 2),
  ('Othello', 4, 2),
  ('King Lear', 4, 2),
  ('Pygmalion', 5, 2),
  ('The house where hearts break', 5, 2),
  ('Caesar and Cleopatus', 5, 2),
  ('Fog', 6, 2),
  ('Anna Christie', 6, 2),
  ('Bread and butter', 6, 2),
  ('Twelve chairs', 7, 3),
  ('The Little Golden Calf', 7, 3),
  ('One-story America', 7, 3),
  ('Karion', 8, 3),
  ('The Foreman', 8, 3),
  ('Ignoramus', 8, 3),
  ('A shadow', 9,3),
  ('A sneak', 9,3),
  ('Gasp', 9,3),
  ('After you', 10,4)
  ('One plus one', 10,4)
  ('Dancing with horses', 10,4)
  ('The Thorn Birds', 11,4),
  ("Caesar's Women", 11,4),
  ('Tim', 11,4),
  ('P.S. I love you!', 12,4),
  ('Flawed', 12,4),
  ('Perfect', 12,4),
  #осталось дописать 3 писателя
"""

create_zanr = """
INSERT INTO zanrid(zanri_nimi)
VALUES
   ('Horror'),
  ('Draama'),
  ('Komedia'),
  ('Romaan'),
  ('Luuletus')
"""


select_from_zanr = """
SELECT DISTINCT * FROM zanrid
"""

def display_results(results):
    text.delete(1.0, tk.END)
    for result in results:
        zanr_id = result[0]
        zanri_nimi = result[1]
        text.insert(tk.END, f"Zanr ID: {zanr_id}, Zanr: {zanri_nimi}\n")

def genre_selected(event):
    selected_genre = genre_combobox.get()
    if selected_genre == "All Genres":
        zanrid = execute_read_query(conn, select_from_zanr)
    else:
        query = """
        SELECT raamatud.raamat_nimi, autorid.autor_nimi
        FROM raamatud
        INNER JOIN autorid ON raamatud.autor_id = autorid.autor_id
        INNER JOIN zanrid ON raamatud.zanr_id = zanrid.zanr_id
        WHERE zanrid.zanri_nimi = ?
        """
        zanrid = execute_read_query(conn, query, (selected_genre,))
    display_results(zanrid)

root = tk.Tk()
root.title("Database Query Results")

genres = ["All Genres", "Draama", "Horror", "Komedia", "Romaan", "Luuletus"]
genre_combobox = ttk.Combobox(root, values=genres)
genre_combobox.current(0)
genre_combobox.bind("<<ComboboxSelected>>", genre_selected)
genre_combobox.pack()

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
execute_query(conn,insert_into_autorid)

zanrid = execute_read_query(conn, select_from_zanr)
display_results(zanrid)

conn.close()

root.mainloop()
