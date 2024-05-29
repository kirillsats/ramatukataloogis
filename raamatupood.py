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
create_table_autorid = """
CREATE TABLE IF NOT EXISTS autorid(
    autor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    autor_nimi TEXT NOT NULL,
    sunnikuupaev DATE NOT NULL
)
"""

create_table_zanrid = """
CREATE TABLE IF NOT EXISTS zanrid(
    zanr_id INTEGER PRIMARY KEY AUTOINCREMENT,
    zanri_nimi TEXT NOT NULL
)
"""

create_table_raamatud = """
CREATE TABLE IF NOT EXISTS raamatud(
    raamat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raamat_nimi TEXT NOT NULL,
    autorid INTEGER NOT NULL,
    zanrid INTEGER NOT NULL,
    FOREIGN KEY (autor_id) REFERENCES autorid(autor_id),
    FOREIGN KEY (zanr_id) REFERENCES zanrid(zanr_id)
    insert_book_query = "INSERT INTO raamatud(raamat_nimi, autorid, zanrid) VALUES (?, ?, ?)"
    execute_query(conn, insert_book_query, (book_name, author_id, genre_id))
)
"""


# Определение SQL-запроса для выбора всех уникальных жанров
select_from_zanr = """
SELECT DISTINCT zanri_nimi FROM zanrid
"""
def get_autor_years(connection, autor_id):
    query = "SELECT sunnikuupaev FROM autorid WHERE autor_id = ?"
    result = execute_read_query(connection, query, (autor_id,))
    if result:
        return result[0][0]
    else:
        print(f"Birth date not found for author ID: {autor_id}")
        return None

# Функция для отображения результатов
def display_results(results):
    text.delete(1.0, tk.END)
    for result in results:
        book_id = result[0]
        book_name = result[1]
        autor_id = result[2]
        autor_name = result[3]
        autor_years = get_autor_years(conn, autor_id)
        if autor_years:
            text.insert(tk.END, f"{book_id}: {book_name} by {autor_name} ({autor_years})\n")
        else:
            text.insert(tk.END, f"{book_id}: {book_name} by {autor_name}\n")

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
        print(f"{value} не найдено в таблице {table_name}")
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

def add_book(conn):
    book_name = book_name_entry.get()
    autor_name = author_name_entry.get()
    genre_name = genre_name_entry.get()

    if not book_name or not autor_name or not genre_name:
        print("Пожалуйста, заполните все поля перед добавлением книги.")
        return

    # Проверяем существование автора в базе данных
    autor_id = get_id_from_name(conn, "autorid", "autor_nimi", autor_name)
    if autor_id is None:
        print(f"Author '{autor_name}' не найден в базе данных. Добавьте автора перед добавлением книги.")
        # Здесь можно добавить код для добавления нового автора в базу данных, если это нужно
        return

    # Проверяем существование жанра в базе данных
    genre_id = get_id_from_name(conn, "zanrid", "zanri_nimi", genre_name)
    if genre_id is None:
        print(f"Genre '{genre_name}' не найден в базе данных. Добавьте жанр перед добавлением книги.")
        return

    # Добавляем книгу в базу данных
    insert_book_query = "INSERT INTO raamatud(raamat_nimi, autorid, zanrid) VALUES (?, ?, ?)"
    execute_query(conn, insert_book_query, (book_name, autor_id, genre_id))
    print("Книга успешно добавлена")


def add_genre(connection):
    new_genre = new_genre_entry.get()
    add_genre_to_database(new_genre)
    update_genre_list()  # Обновляем список жанров после добавления нового

def delete_book():
    book_id = delete_book_id_entry.get()
    delete_book_query = "DELETE FROM raamatud WHERE raamat_id = ?"
    execute_query(conn, delete_book_query, (book_id,))
    print("Book deleted successfully")
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
tab1  = ttk.Frame(tab_control)
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

add_book_button = tk.Button(tab2, text="Добавить книгу", command=lambda: add_book(conn))
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

add_genre_button = tk.Button(tab4, text="Добавить жанр", command=lambda: add_genre(conn))
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

# Вызов функций добавления книги и жанра с передачей параметра conn
add_book(conn)
add_genre(conn)

# Запуск главного цикла обработки событий
root.mainloop()

