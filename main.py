import datetime
from tkinter import *
from tkinter import messagebox
from database import FilmDatabase, Film, Producer

NUMBER_OF_FIELDS = 4
SEARCH_BY_NAME = 0
SEARCH_BY_YEAR = 1
SEARCH_BY_RATE = 2
SEARCH_BY_ID = 3
SETTINGS_FILENAME = 'settings.json'
ROOT_GEOMETRY = '900x700+350+70'
TITLE = 'Films and producers database'
ACTIVE_DB_FILENAME = 'active_databases.list'
ROW_FORMAT_FILM = "{:>25}" * 4
ROW_FORMAT_PRODUCER = "{:>20}" * 5


def add_menu(root, film_listbox, producer_listbox, db):
    main_menu = Menu()

    file_menu = Menu()
    file_menu.add_command(label='create database', command=lambda: create_db(db))
    file_menu.add_command(label='delete database', command=lambda: drop_db(db))
    file_menu.add_command(label='open database', command=lambda: open_db(film_listbox, producer_listbox, db))

    clear_menu = Menu()
    clear_menu.add_command(label='Delete everything from current db',
                           command=lambda: clear_all(db, film_listbox, producer_listbox))
    clear_menu.add_command(label='Delete all films from current db',
                           command=lambda: clear_films(db, film_listbox, producer_listbox))
    clear_menu.add_command(label='Delete all producers from current db',
                           command=lambda: clear_producers(db, producer_listbox))

    main_menu.add_cascade(label="File", menu=file_menu)
    main_menu.add_cascade(label="Clear", menu=clear_menu)

    root.config(menu=main_menu)


def clear_all(db, film_listbox, producer_listbox):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    db.delete_all_films(db.current_db)
    db.delete_all_producers(db.current_db)
    db.delete_all_producers(db.current_db)
    show_all_films(db, film_listbox)
    show_all_producers(db, producer_listbox)


def clear_films(db, film_listbox, producer_listbox):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    db.delete_all_films(db.current_db)
    show_all_films(db, film_listbox)
    show_all_producers(db, producer_listbox)


def clear_producers(db, producer_listbox):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    db.delete_all_producers(db.current_db)
    show_all_producers(db, producer_listbox)


def _open(film_listbox, producer_listbox, chosen_db, listbox, choose_window, db):
    chosen = listbox.curselection()
    if chosen:
        chosen_db += [listbox.get(chosen)]
        db_name = chosen_db[0]
        db.make_connection(db_name)
        db.current_db = db_name
        show_all_films(db, film_listbox)
        show_all_producers(db, producer_listbox)
    choose_window.destroy()


def show_all_films(db, film_listbox):
    if db.current_db:
        films = db.select_all_films(db.current_db)
        film_listbox.delete(0, 'end')
        for i, film in enumerate(films):
            film_listbox.insert(i, ROW_FORMAT_FILM.format(*film))


def show_all_producers(db, producer_listbox):
    if db.current_db:
        producers = db.select_all_producers(db.current_db)
        producer_listbox.delete(0, 'end')
        for i, producer in enumerate(producers):
            producer_listbox.insert(i, ROW_FORMAT_PRODUCER.format(*[str(field) for field in producer]))


def open_db(film_listbox, producer_listbox, db):
    active_dbs = []
    with open(ACTIVE_DB_FILENAME, 'r') as file:
        active_dbs += [line.replace('\n', '') for line in file.read().splitlines()]
    if active_dbs:
        choose_window = Toplevel()
        choose_window.geometry('300x150+750+450')
        choose_window.title('Existing databases')

        chosen_db = []
        scrollbar = Scrollbar(choose_window)
        scrollbar.place(relheight=0.9, relwidth=0.02, relx=0.98, rely=0.1)
        listbox = Listbox(choose_window, yscrollcommand=scrollbar.set)
        for i, active_db in enumerate(active_dbs):
            listbox.insert(i, active_db)
        listbox.place(relheight=0.9, relwidth=0.98, rely=0.1)
        btn_open_db = Button(choose_window, text='open',
                             command=lambda: _open(film_listbox, producer_listbox, chosen_db, listbox, choose_window,
                                                   db))
        btn_open_db.place(relheight=0.15, relwidth=0.3, relx=0.35, rely=0.85)
    else:
        messagebox.showinfo("Warning", "No databases created")


def create_db(db):
    choose_window = Toplevel()
    choose_window.geometry('300x150+750+450')
    choose_window.title('Enter name of the database')

    user_db_name = StringVar()
    label = Label(choose_window, text='Enter filename:', font=14)
    label.place(relheight=0.3, relwidth=0.8, relx=0.1)
    entry = Entry(choose_window, textvariable=user_db_name, font=14)
    entry.place(relheight=0.2, relwidth=0.8, relx=0.1, rely=0.3)
    btn_create_db = Button(choose_window, text='create', command=lambda: _create(db, user_db_name, choose_window))
    btn_create_db.place(relheight=0.15, relwidth=0.3, relx=0.35, rely=0.85)


def _create(db, user_db_name, choose_window):
    db_name = user_db_name.get()
    if db_name:
        db.create_db(db_name)
        active_dbs = set()
        with open(ACTIVE_DB_FILENAME, 'r') as file:
            for line in file:
                active_dbs.add(line.replace('\n', ''))
        active_dbs.add(db_name)
        with open(ACTIVE_DB_FILENAME, 'w') as file:
            file.write('\n'.join(active_dbs))
        choose_window.destroy()
    else:
        messagebox.showerror("Error", "Database name cannot be empty")


def _drop(chosen_db, listbox, choose_window, db):
    chosen = listbox.curselection()
    if chosen:
        chosen_db += [listbox.get(chosen)]
        db_name = chosen_db[0]
        db.drop_db(db_name)
        active_dbs = set()
        with open(ACTIVE_DB_FILENAME, 'r') as file:
            for line in file:
                active_dbs.add(line.replace('\n', ''))
        active_dbs.remove(db_name)
        with open(ACTIVE_DB_FILENAME, 'w') as file:
            file.write('\n'.join(active_dbs))
    choose_window.destroy()


def drop_db(db):
    active_dbs = []
    with open(ACTIVE_DB_FILENAME, 'r') as file:
        active_dbs += [line.replace('\n', '') for line in file.read().splitlines()]
    if active_dbs:
        choose_window = Toplevel()
        choose_window.geometry('300x150+750+450')
        choose_window.title('Existing databases')

        chosen_db = []
        scrollbar = Scrollbar(choose_window)
        scrollbar.place(relheight=0.9, relwidth=0.02, relx=0.98, rely=0.1)
        listbox = Listbox(choose_window, yscrollcommand=scrollbar.set)
        for i, active_db in enumerate(active_dbs):
            listbox.insert(i, active_db)
        listbox.place(relheight=0.9, relwidth=0.98, rely=0.1)
        btn_open_db = Button(choose_window, text='delete', command=lambda: _drop(chosen_db, listbox, choose_window, db))
        btn_open_db.place(relheight=0.15, relwidth=0.3, relx=0.35, rely=0.85)
    else:
        messagebox.showinfo("Warning", "No databases created")


def add_film(db, producer_listbox, film_listbox):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    choose_window = Toplevel()
    choose_window.geometry('800x150+750+450')
    choose_window.title('Film to add')
    user_film_id = StringVar()
    user_film_title = StringVar()
    user_film_year = StringVar()
    user_film_producer_id = StringVar()

    label = Label(choose_window, text='Enter film id:', font=12)
    label.place(relheight=0.25, relwidth=0.15)
    entry = Entry(choose_window, textvariable=user_film_id, font=12)
    entry.place(relheight=0.25, relwidth=0.15, rely=0.3)

    label = Label(choose_window, text='Enter film title:', font=12)
    label.place(relheight=0.25, relwidth=0.45, relx=0.15)
    entry = Entry(choose_window, textvariable=user_film_title, font=12)
    entry.place(relheight=0.25, relwidth=0.45, relx=0.15, rely=0.3)

    label = Label(choose_window, text='Enter film year:', font=12)
    label.place(relheight=0.25, relwidth=0.2, relx=0.6)
    entry = Entry(choose_window, textvariable=user_film_year, font=12)
    entry.place(relheight=0.25, relwidth=0.2, relx=0.6, rely=0.3)

    label = Label(choose_window, text='Enter producer id:', font=12)
    label.place(relheight=0.25, relwidth=0.2, relx=0.8)
    entry = Entry(choose_window, textvariable=user_film_producer_id, font=12)
    entry.place(relheight=0.25, relwidth=0.2, relx=0.8, rely=0.3)

    btn_add = Button(choose_window, text='add',
                     command=lambda: _add_film(db, user_film_id, user_film_title, user_film_year, user_film_producer_id,
                                               choose_window, producer_listbox, film_listbox))
    btn_add.place(relheight=0.2, relwidth=0.15, relx=0.4, rely=0.7)


def _add_film(db, user_film_id, user_film_title, user_film_year,
              user_film_producer_id, choose_window, producer_listbox, film_listbox):
    if db.current_db:
        film_id = user_film_id.get()
        film_title = user_film_title.get()
        film_year = user_film_year.get()
        film_p_id = user_film_producer_id.get()
        film_producer_id = user_film_producer_id.get()
        if film_id and film_title and film_year and film_producer_id:
            errors_in_data = check_film_data(film_id, film_year, film_p_id)
            if errors_in_data:
                messagebox.showerror("Error", errors_in_data)
                return
            db.insert_film(db.current_db, Film(film_id, film_title, film_year, film_p_id))
            show_all_films(db, film_listbox)
            show_all_producers(db, producer_listbox)
        else:
            messagebox.showerror("Error", "Fields cannot be empty")
    else:
        messagebox.showerror("Error", "Open database before inserting")
    choose_window.destroy()


def check_film_data(film_id, film_year, film_p_id):
    error_msg = ''
    try:
        int(film_id)
    except Exception:
        error_msg += 'Incorrect film id\n'
    try:
        f_year = int(film_year)
        if len(film_year) != 4:
            error_msg += 'year should consist of 4 digits\n'
    except Exception:
        error_msg += 'Incorrect film year\n'
    try:
        int(film_p_id)
    except Exception:
        error_msg += 'Incorrect producer id'
    return error_msg


def check_producer_data(p_id, p_birth_date):
    error_msg = ''
    try:
        int(p_id)
    except Exception:
        error_msg += 'Incorrect producer id\n'
    try:
        bd = datetime.datetime.strptime(p_birth_date, "%Y-%m-%d")
    except Exception as e:
        error_msg += 'Birth date must be in format: yyyy-mm-dd'
    return error_msg


def add_producer(db, producer_listbox, film_listbox):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    choose_window = Toplevel()
    choose_window.geometry('800x150+750+450')
    choose_window.title('Producer to add')
    user_producer_id = StringVar()
    user_producer_name = StringVar()
    user_producer_birth_date = StringVar()
    user_producer_address = StringVar()

    label = Label(choose_window, text='Id:', font=12)
    label.place(relheight=0.25, relwidth=0.15)
    entry = Entry(choose_window, textvariable=user_producer_id, font=12)
    entry.place(relheight=0.25, relwidth=0.15, rely=0.3)

    label = Label(choose_window, text='Name:', font=12)
    label.place(relheight=0.25, relwidth=0.45, relx=0.15)
    entry = Entry(choose_window, textvariable=user_producer_name, font=12)
    entry.place(relheight=0.25, relwidth=0.45, relx=0.15, rely=0.3)

    label = Label(choose_window, text='Birth_date:', font=12)
    label.place(relheight=0.25, relwidth=0.2, relx=0.6)
    entry = Entry(choose_window, textvariable=user_producer_birth_date, font=12)
    entry.place(relheight=0.25, relwidth=0.2, relx=0.6, rely=0.3)

    label = Label(choose_window, text='Address:', font=12)
    label.place(relheight=0.25, relwidth=0.2, relx=0.8)
    entry = Entry(choose_window, textvariable=user_producer_address, font=12)
    entry.place(relheight=0.25, relwidth=0.2, relx=0.8, rely=0.3)

    btn_add = Button(choose_window, text='add',
                     command=lambda: _add_producer(db, user_producer_id, user_producer_name,
                                                   user_producer_birth_date, user_producer_address,
                                                   choose_window, producer_listbox, film_listbox))
    btn_add.place(relheight=0.2, relwidth=0.15, relx=0.4, rely=0.7)


def _add_producer(db, user_producer_id, user_producer_name, user_producer_birth_date,
                  user_producer_address, choose_window, producer_listbox, film_listbox):
    if db.current_db:
        producer_id = user_producer_id.get()
        producer_name = user_producer_name.get()
        producer_bd = user_producer_birth_date.get()
        producer_address = user_producer_address.get()
        if producer_id and producer_name and producer_bd and producer_address:
            data_errors = check_producer_data(producer_id, producer_bd)
            if data_errors:
                messagebox.showerror("Error", data_errors)
                return
            db.insert_producer(db.current_db, Producer(producer_id, producer_name, producer_bd, producer_address, 0))
            show_all_producers(db, producer_listbox)
        else:
            messagebox.showerror("Error", "Fields cannot be empty")
    else:
        messagebox.showerror("Error", "Open database before inserting")
    choose_window.destroy()


def search_film(db, film_listbox, film_title_to_find):
    if db.current_db:
        title_to_find = film_title_to_find.get()
        if title_to_find:
            films = db.find_films(db.current_db, title_to_find)
            film_listbox.delete(0, 'end')
            for i, film in enumerate(films):
                film_listbox.insert(i, ROW_FORMAT_FILM.format(*film))
        else:
            messagebox.showinfo("Error", "Enter a title before search")
    else:
        messagebox.showerror("Error", "Open database before search")


def search_producer(db, producer_listbox, producer_name_to_find):
    if db.current_db:
        name_to_find = producer_name_to_find.get()
        if name_to_find:
            producers = db.find_producers(db.current_db, name_to_find)
            producer_listbox.delete(0, 'end')
            for i, producer in enumerate(producers):
                producer_listbox.insert(i, ROW_FORMAT_FILM.format(*[str(field) for field in producer]))
        else:
            messagebox.showinfo("Error", "Enter a name before search")
    else:
        messagebox.showerror("Error", "Open database before search")


def _update_film(db, film_listbox, producer_listbox, film_id: int, user_film_title, user_film_year,
                 user_film_producer_id, choose_window):
    film_title = user_film_title.get()
    film_year = user_film_year.get()
    film_producer_id = user_film_producer_id.get()
    if film_id and film_title and film_year and film_producer_id:
        errors_in_data = check_film_data(film_id, film_year, film_producer_id)
        if errors_in_data:
            messagebox.showerror("Error", errors_in_data)
            return
        db.update_film(db.current_db, Film(film_id, film_title, film_year, film_producer_id))
        show_all_films(db, film_listbox)
        show_all_producers(db, producer_listbox)
    else:
        messagebox.showerror("Error", "Fields cannot be empty")
    choose_window.destroy()


def update_film(db, film_listbox, producer_listbox):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    chosen_film = film_listbox.curselection()
    if not chosen_film:
        messagebox.showerror("Error", "No films picked out")
        return
    choose_window = Toplevel()
    choose_window.geometry('800x150+750+450')
    choose_window.title('Film to update')
    user_film_id = StringVar()
    user_film_title = StringVar()
    user_film_year = StringVar()
    user_film_producer_id = StringVar()

    chosen_film = film_listbox.get(chosen_film)
    fields = [field for field in re.split(r'\s{2,}', chosen_film) if field]
    # print(fields)
    # print(chosen_film)
    if len(fields) == 4:
        user_film_id.set(fields[0])
        user_film_title.set(fields[1])
        user_film_year.set(fields[2])
        user_film_producer_id.set(fields[3])
    else:
        return

    label = Label(choose_window, text='Id:', font=12)
    label.place(relheight=0.25, relwidth=0.15)
    label = Label(choose_window, textvariable=user_film_id, font=12)
    label.place(relheight=0.25, relwidth=0.15, rely=0.3)

    label = Label(choose_window, text='Title:', font=12)
    label.place(relheight=0.25, relwidth=0.45, relx=0.15)
    entry = Entry(choose_window, textvariable=user_film_title, font=12)
    entry.place(relheight=0.25, relwidth=0.45, relx=0.15, rely=0.3)

    label = Label(choose_window, text='Year:', font=12)
    label.place(relheight=0.25, relwidth=0.2, relx=0.6)
    entry = Entry(choose_window, textvariable=user_film_year, font=12)
    entry.place(relheight=0.25, relwidth=0.2, relx=0.6, rely=0.3)

    label = Label(choose_window, text='Producer id:', font=12)
    label.place(relheight=0.25, relwidth=0.2, relx=0.8)
    entry = Entry(choose_window, textvariable=user_film_producer_id, font=12)
    entry.place(relheight=0.25, relwidth=0.2, relx=0.8, rely=0.3)

    btn_add = Button(choose_window, text='Update',
                     command=lambda: _update_film(db, film_listbox, producer_listbox, user_film_id.get(),
                                                  user_film_title, user_film_year,
                                                  user_film_producer_id, choose_window))
    btn_add.place(relheight=0.2, relwidth=0.15, relx=0.4, rely=0.7)


def _update_producer(db, producer_listbox, producer_id: int, user_producer_name,
                     user_producer_birth_date, user_producer_address, choose_window):
    producer_name = user_producer_name.get()
    producer_db = user_producer_birth_date.get()
    producer_address = user_producer_address.get()
    if producer_id and producer_name and producer_db and producer_address:
        db.update_producer(db.current_db, Producer(producer_id, producer_name, producer_db, producer_address))
        show_all_producers(db, producer_listbox)
    else:
        messagebox.showerror("Error", "Fields cannot be empty")
    choose_window.destroy()


def update_producer(db, producer_listbox):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    chosen_producer = producer_listbox.curselection()
    if not chosen_producer:
        messagebox.showerror("Error", "No producers picked out")
        return
    choose_window = Toplevel()
    choose_window.geometry('800x150+750+450')
    choose_window.title('Film to update')
    choose_window.title('Producer to add')

    user_producer_id = StringVar()
    user_producer_name = StringVar()
    user_producer_birth_date = StringVar()
    user_producer_address = StringVar()

    chosen_producer = producer_listbox.get(chosen_producer)
    fields = [field for field in re.split(r'\s{2,}', chosen_producer) if field]

    if len(fields) != 5:
        return

    user_producer_id.set(fields[0])
    user_producer_name.set(fields[1])
    user_producer_birth_date.set(fields[2])
    user_producer_address.set(fields[3])

    label = Label(choose_window, text='Id:', font=12)
    label.place(relheight=0.25, relwidth=0.15)
    label = Label(choose_window, textvariable=user_producer_id, font=12)
    label.place(relheight=0.25, relwidth=0.15, rely=0.3)

    label = Label(choose_window, text='Name:', font=12)
    label.place(relheight=0.25, relwidth=0.45, relx=0.15)
    entry = Entry(choose_window, textvariable=user_producer_name, font=12)
    entry.place(relheight=0.25, relwidth=0.45, relx=0.15, rely=0.3)

    label = Label(choose_window, text='Birth_date:', font=12)
    label.place(relheight=0.25, relwidth=0.2, relx=0.6)
    entry = Entry(choose_window, textvariable=user_producer_birth_date, font=12)
    entry.place(relheight=0.25, relwidth=0.2, relx=0.6, rely=0.3)

    label = Label(choose_window, text='Address:', font=12)
    label.place(relheight=0.25, relwidth=0.2, relx=0.8)
    entry = Entry(choose_window, textvariable=user_producer_address, font=12)
    entry.place(relheight=0.25, relwidth=0.2, relx=0.8, rely=0.3)

    btn_add = Button(choose_window, text='Update',
                     command=lambda: _update_producer(db, producer_listbox, user_producer_id.get(), user_producer_name,
                                                      user_producer_birth_date, user_producer_address, choose_window))
    btn_add.place(relheight=0.2, relwidth=0.15, relx=0.4, rely=0.7)


def drop_film(db, film_listbox, producer_listbox):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    chosen_film = film_listbox.curselection()
    if not chosen_film:
        messagebox.showerror("Error", "No films picked out")
        return
    chosen_film = film_listbox.get(chosen_film)
    fields = [field for field in re.split(r'\s{2,}', chosen_film) if field]
    if len(fields) == 4:
        film_id = fields[0]
        db.delete_film_by_id(db.current_db, film_id)
        show_all_films(db, film_listbox)
        show_all_producers(db, producer_listbox)
    else:
        return


def drop_producer(db, producer_listbox):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    chosen_producer = producer_listbox.curselection()
    if not chosen_producer:
        messagebox.showerror("Error", "No producers picked out")
        return
    chosen_producer = producer_listbox.get(chosen_producer)
    fields = [field for field in re.split(r'\s{2,}', chosen_producer) if field]
    if len(fields) == 5:
        producer_id = fields[0]
        db.delete_producer_by_id(db.current_db, producer_id)
        show_all_producers(db, producer_listbox)
    else:
        return


def delete_films_by_name(db, film_listbox, producer_listbox, film_title_to_find):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    title_to_find = film_title_to_find.get()
    if not title_to_find:
        return
    db.delete_films_by_title(db.current_db, title_to_find)
    show_all_films(db, film_listbox)
    show_all_producers(db, producer_listbox)


def delete_producers_by_name(db, producer_listbox, producer_name_to_find):
    if not db.current_db:
        messagebox.showerror("Error", "No database opened")
        return
    name_to_find = producer_name_to_find.get()
    if not name_to_find:
        return
    db.delete_producers_by_name(db.current_db, name_to_find)
    show_all_producers(db, producer_listbox)


def main():
    root = Tk()
    root.title(TITLE)
    root.geometry(ROOT_GEOMETRY)
    db = FilmDatabase(SETTINGS_FILENAME)

    # TODO close all connections
    film_scrollbar = Scrollbar(root)
    film_scrollbar.place(relheight=0.9, relwidth=0.02, relx=0.48, rely=0.2)

    producer_scrollbar = Scrollbar(root)
    producer_scrollbar.place(relheight=0.9, relwidth=0.02, relx=0.98, rely=0.2)

    film_listbox = Listbox(root, yscrollcommand=film_scrollbar.set)
    producer_listbox = Listbox(root, yscrollcommand=producer_scrollbar.set)

    film_listbox.place(relheight=0.7, relwidth=0.48, rely=0.2)

    producer_listbox.place(relheight=0.7, relwidth=0.48, rely=0.2, relx=0.5)

    add_menu(root, film_listbox, producer_listbox, db)

    add_film_button = Button(root, text='Add film', command=lambda: add_film(db, producer_listbox, film_listbox))
    add_film_button.place(relheight=0.05, relwidth=0.1, relx=0.65, rely=0.9)

    add_producer_button = Button(root, text='Add producer',
                                 command=lambda: add_producer(db, producer_listbox, film_listbox))
    add_producer_button.place(relheight=0.05, relwidth=0.1, relx=0.85, rely=0.9)

    update_film_button = Button(root, text='Update film',
                                command=lambda: update_film(db, film_listbox, producer_listbox))
    update_film_button.place(relheight=0.05, relwidth=0.1, rely=0.9)

    update_producer_button = Button(root, text='Update producer', command=lambda: update_producer(db, producer_listbox))
    update_producer_button.place(relheight=0.05, relwidth=0.1, relx=0.15, rely=0.9)

    delete_film_button = Button(root, text='Delete film', command=lambda: drop_film(db, film_listbox, producer_listbox))
    delete_film_button.place(relheight=0.05, relwidth=0.1, relx=0.3, rely=0.9)

    delete_producer_button = Button(root, text='Delete producer', command=lambda: drop_producer(db, producer_listbox))
    delete_producer_button.place(relheight=0.05, relwidth=0.1, relx=0.45, rely=0.9)

    film_title_to_find = StringVar()
    label = Label(root, text='Title:', font=10)
    label.place(relheight=0.05, relwidth=0.4)
    entry = Entry(root, textvariable=film_title_to_find, font=10)
    entry.place(relheight=0.05, relwidth=0.4, rely=0.05)
    search_film_button = Button(root, text='Search', command=lambda: search_film(db, film_listbox, film_title_to_find))
    search_film_button.place(relheight=0.05, relwidth=0.07, relx=0.4, rely=0.05)
    delete_film_by_name_button = Button(root, text='Delete',
                                        command=lambda: delete_films_by_name(db, film_listbox, producer_listbox,
                                                                             film_title_to_find))
    delete_film_by_name_button.place(relheight=0.05, relwidth=0.07, relx=0.4, rely=0.1)

    producer_name_to_find = StringVar()
    label = Label(root, text='Name:', font=10)
    label.place(relheight=0.05, relwidth=0.4, relx=0.5)
    entry = Entry(root, textvariable=producer_name_to_find, font=10)
    entry.place(relheight=0.05, relwidth=0.4, relx=0.5, rely=0.05)
    search_film_button = Button(root, text='Search',
                                command=lambda: search_producer(db, producer_listbox, producer_name_to_find))
    search_film_button.place(relheight=0.05, relwidth=0.07, relx=0.9, rely=0.05)
    delete_producer_by_name_button = Button(root, text='Delete',
                                            command=lambda: delete_producers_by_name(db, producer_listbox,
                                                                                     producer_name_to_find))
    delete_producer_by_name_button.place(relheight=0.05, relwidth=0.07, relx=0.9, rely=0.1)

    show_all_film_button = Button(root, text='Show all films', command=lambda: show_all_films(db, film_listbox))
    show_all_film_button.place(relheight=0.05, relwidth=0.4, relx=0.0, rely=0.1)
    show_all_producers_button = Button(root, text='Show all producers',
                                       command=lambda: show_all_producers(db, producer_listbox))
    show_all_producers_button.place(relheight=0.05, relwidth=0.4, relx=0.5, rely=0.1)

    root.mainloop()


if __name__ == '__main__':
    main()
