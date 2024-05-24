import tkinter as tk
from tkinter import ttk
from sqlite3 import connect, Error

# Подключение к базе данных
def create_connection(path: str):
    conn = None
    try:
        conn = connect(path)
        print("Connected to database")
        return conn
    except Error as e:
        print(e)

# Функция для выполнения запроса к базе данных
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

# Функция для выполнения запроса на чтение данных из базы данных
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

# Определение SQL-запросов для создания таблиц
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
    autor_id INTEGER NOT NULL,
    zanr_id INTEGER NOT NULL,
    FOREIGN KEY (autor_id) REFERENCES autorid(autor_id),
    FOREIGN KEY (zanr_id) REFERENCES zanrid(zanr_id)
)
"""

# Определение SQL-запроса для выбора всех уникальных жанров
select_from_zanr = """
SELECT DISTINCT zanri_nimi FROM zanrid
"""

# Функция для отображения результатов
def display_results(results):
    text.delete(1.0, tk.END)
    for result in results:
        book_id = result[0]
        book_name = result[1]
        author_id = result[2]
        author_name = result[3]
        author_years = get_author_years(conn, author_id)
        if author_years:
            text.insert(tk.END, f"{book_id}: {book_name} by {author_name} ({author_years})\n")
        else:
            text.insert(tk.END, f"{book_id}: {book_name} by {author_name}\n")

# Функция для обработки выбора жанра
def genre_selected(event=None):
    selected_genre = genre_combobox.get()
    if selected_genre == "All Genres":
        query = """
        SELECT raamatud.raamat_id, raamatud.raamat_nimi, autorid.autor_id, autorid.autor_nimi 
        FROM raamatud 
        JOIN autorid ON raamatud.autor_id = autorid.autor_id
        """
        results = execute_read_query(conn, query)
        display_results(results)
    else:
        query = """
        SELECT raamatud.raamat_id, raamatud.raamat_nimi, autorid.autor_id, autorid.autor_nimi
        FROM raamatud
        INNER JOIN autorid ON raamatud.autor_id = autorid.autor_id
        INNER JOIN zanrid ON raamatud.zanr_id = zanrid.zanr_id
        WHERE zanrid.zanri_nimi = ?
        """
        results = execute_read_query(conn, query, (selected_genre,))
        display_results(results)

def get_id_from_name(connection, table_name, column_name, value):
    query = f"SELECT {table_name}_id FROM {table_name} WHERE {column_name} = ?"
    result = execute_read_query(connection, query, (value,))
    if result:
        return result[0][0]
    else:
        print(f"{value} not found in {table_name}")
        return None

def add_genre_to_database(genre_name):
    if genre_name:
        add_genre_query = "INSERT INTO zanrid(zanri_nimi) VALUES (?)"
        execute_query(conn, add_genre_query, (genre_name,))
        print("Genre added successfully")
    else:
        print("Please enter a genre name")

def update_genre_list():
    genres = ["All Genres"] + [genre[0] for genre in execute_read_query(conn, "SELECT zanri_nimi FROM zanrid")]
    genre_combobox['values'] = genres
    delete_genre_combobox['values'] = genres

def add_book():
    book_name = book_name_entry.get()
    author_name = author_name_entry.get()
    genre_name = genre_name_entry.get()
    # Проверка существования и добавление нового автора
    author_id = get_id_from_name(conn, "autorid", "autor_nimi", author_name)
    if author_id is None:
        add_author_query = "INSERT INTO autorid(autor_nimi, sunnikuupaev) VALUES (?, ?)"
        execute_query(conn, add_author_query, (author_name, '1970-01-01'))  # Используем дату по умолчанию
        author_id = get_id_from_name(conn, "autorid", "autor_nimi", author_name)

    # Проверка существования и добавление нового жанра
    genre_id = get_id_from_name(conn, "zanrid", "zanri_nimi", genre_name)
    if genre_id is None:
        add_genre_query = "INSERT INTO zanrid(zanri_nimi) VALUES (?)"
        execute_query(conn, add_genre_query, (genre_name,))
        genre_id = get_id_from_name(conn, "zanrid", "zanri_nimi", genre_name)

    # Добавление книги в базу данных
    insert_book_query = "INSERT INTO raamatud(raamat_nimi, autor_id, zanr_id) VALUES (?, ?, ?)"
    execute_query(conn, insert_book_query, (book_name, author_id, genre_id))
    print("Book added successfully")

    # После добавления книги обновим отображение списка книг
    genre_selected()

def add_genre():
    new_genre = new_genre_entry.get()
    add_genre_to_database(new_genre)
    update_genre_list()  # Обновляем список жанров после добавления нового

def delete_book():
    book_id = delete_book_id_entry.get()
    delete_book_query = "DELETE FROM raamatud WHERE raamat_id = ?"
    execute_query(conn, delete_book_query, (book_id,))
    print("Book deleted successfully")
    genre_selected()

def delete_genre():
    genre_name = delete_genre_combobox.get()
    if genre_name != "All Genres":
        delete_genre_query = "DELETE FROM zanrid WHERE zanri_nimi = ?"
        execute_query(conn, delete_genre_query, (genre_name,))
        print("Genre deleted successfully")
        update_genre_list()  # Обновляем список жанров после удаления
        genre_selected()  # Обновляем отображение после удаления жанра
    else:
        print("Cannot delete 'All Genres'")

# Создание главного окна приложения
root = tk.Tk()
root.title("Database Query Results")

# Создание вкладок
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)  # Новая вкладка для добавления жанра
tab5 = ttk.Frame(tab_control)  # Новая вкладка для удаления жанра
tab_control.add(tab1, text="Просмотр книг")
tab_control.add(tab2, text="Добавить книгу")
tab_control.add(tab3, text="Удалить книгу")
tab_control.add(tab4, text="Добавить жанр")  # Добавляем вкладку для добавления жанра
tab_control.add(tab5, text="Удалить жанр")  # Добавляем вкладку для удаления жанра
tab_control.pack(expand=1, fill="both")

# Вкладка "Просмотр книг"
genres = ["All Genres"] + [genre[0] for genre in execute_read_query(create_connection("books.db"), "SELECT zanri_nimi FROM zanrid")]
genre_combobox = ttk.Combobox(tab1, values=genres)
genre_combobox.current(0)
genre_combobox.bind("<<ComboboxSelected>>", genre_selected)
genre_combobox.pack()

text = tk.Text(tab1, wrap="word")
text.pack(fill="both", expand=True)

# Вкладка "Добавить книгу"
tk.Label(tab2, text="Название книги").pack()
book_name_entry = tk.Entry(tab2)
book_name_entry.pack()

tk.Label(tab2, text="Имя автора").pack()
author_name_entry = tk.Entry(tab2)
author_name_entry.pack()

tk.Label(tab2, text="Жанр").pack()
genre_name_entry = tk.Entry(tab2)
genre_name_entry.pack()

add_book_button = tk.Button(tab2, text="Добавить книгу", command=add_book)
add_book_button.pack()

# Вкладка "Удалить книгу"
tk.Label(tab3, text="ID книги").pack()
delete_book_id_entry = tk.Entry(tab3)
delete_book_id_entry.pack()

delete_book_button = tk.Button(tab3, text="Удалить книгу", command=delete_book)
delete_book_button.pack()

# Вкладка "Добавить жанр"
tk.Label(tab4, text="Новый жанр").pack()
new_genre_entry = tk.Entry(tab4)
new_genre_entry.pack()

add_genre_button = tk.Button(tab4, text="Добавить жанр", command=add_genre)
add_genre_button.pack()

# Вкладка "Удалить жанр"
tk.Label(tab5, text="Выберите жанр для удаления").pack()
delete_genre_combobox = ttk.Combobox(tab5, values=genres)
delete_genre_combobox.current(0)
delete_genre_combobox.pack()

delete_genre_button = tk.Button(tab5, text="Удалить жанр", command=delete_genre)
delete_genre_button.pack()

# Подключение к базе данных
conn = create_connection("books.db")

# Создание таблиц
execute_query(conn, create_table_zanrid)
execute_query(conn, create_table_autorid)
execute_query(conn, create_table_raamatud)

# Вставка данных (если требуется)
if not execute_read_query(conn, "SELECT 1 FROM zanrid LIMIT 1"):
    insert_into_zanrid = """
    INSERT INTO zanrid(zanri_nimi)
    VALUES
       ('Horror'),
       ('Draama'),
       ('Komedia'),
       ('Romaan'),
       ('Luuletus')
    """
    execute_query(conn, insert_into_zanrid)

if not execute_read_query(conn, "SELECT 1 FROM autorid LIMIT 1"):
    insert_into_autorid = """
    INSERT INTO autorid(autor_nimi, sunnikuupaev) 
    VALUES 
    ('Stephen King', '1947-09-21'),
    ('Bram Stoker', '1847-11-08'),
    ('Richard Bachman', '1936-06-23'),
    ('William Shakespeare', '1564-04-04'),
    ('Bernard Shaw', '1856-07-26'), 
    ("Eugene O'Neill", '1888-10-16'),
    ('Evgeny Petrov', '1902-12-13'),
    ('Denis Fonvizin', '1745-04-14'),
    ('Vasily Kapnist', '1758-02-23'),
    ('Jojo Moyes', '1969-08-04'), 
    ('Colin McCullough', '1937-06-01'),
    ('Cecilia Ahern', '1981-09-30'),
    ('Vsevolod Garshin', '1855-02-14'),
    ('Valentin Kataev', '1897-01-28'),
    ('Anton Delvig', '1798-08-17')
    """
    execute_query(conn, insert_into_autorid)

if not execute_read_query(conn, "SELECT 1 FROM raamatud LIMIT 1"):
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
      ('A shadow', 9, 3),
      ('A sneak',9, 3),
      ('Gasp', 9, 3),
      ('After you', 10, 4),
      ('One plus one', 10, 4),
      ('Dancing with horses', 10, 4),
      ('The Thorn Birds', 11, 4),
      ("Caesar's Women", 11, 4),
      ('Tim', 11, 4),
      ('P.S. I love you!', 12, 4),
      ('Flawed', 12, 4),
      ('Perfect', 12, 4),
      ('Four days', 13, 5),
      ('The incident', 13, 5),
      ('Coward', 13, 5),
      ('Horseshoe', 14, 5),
      ('A scene on a train', 14, 5),
      ('A dark personality', 14, 5)
    """
    execute_query(conn, insert_into_raamatud)

def get_author_years(connection, author_id):
    query = "SELECT sunnikuupaev FROM autorid WHERE autor_id = ?"
    result = execute_read_query(connection, query, (author_id,))
    if result:
        return result[0][0]
    else:
        print(f"Birth date not found for author ID: {author_id}")
        return None

def display_results(results):
    text.delete(1.0, tk.END)
    for result in results:
        book_id = result[0]
        book_name = result[1]
        author_id = result[2]
        author_name = result[3]
        author_years = get_author_years(conn, author_id)
        if author_years:
            text.insert(tk.END, f"{book_id}: {book_name} by {author_name} ({author_years})\n")
        else:
            text.insert(tk.END, f"{book_id}: {book_name} by {author_name}\n")

# Запуск главного цикла обработки событий
root.mainloop()
