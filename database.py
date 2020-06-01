import json

import psycopg2


class SettingNotFoundException(Exception):
    pass


class Film:
    def __init__(self, film_id: int, title: str, year: int, producer_id: int):
        self.id = film_id
        self.title = title
        self.year = year
        self.producer_id = producer_id


class Producer:
    def __init__(self, producer_id: int, name: str, birth_date: str, address: str, film_number: int = 0):
        self.id = producer_id
        self.name = name
        self.birth_date = birth_date
        self.address = address
        self.film_number = film_number


class FilmDatabase:
    def __init__(self, settings_filename: str):
        with open(settings_filename, 'r') as file:
            settings = json.load(file)
            if not settings.get('postgres', ''):
                raise SettingNotFoundException('Posgres section not found in settings')
            postgres_settings = settings['postgres']
            if not postgres_settings.get('user', ''):
                raise SettingNotFoundException('User name not found in postgres settings')
            if not postgres_settings.get('password', ''):
                raise SettingNotFoundException('Password not found in postgres settings')
            if not postgres_settings.get('host', ''):
                raise SettingNotFoundException('Host not found in postgres settings')
            if not postgres_settings.get('port', ''):
                raise SettingNotFoundException('Port not found in postgres settings')
            if not postgres_settings.get('db_name', ''):
                raise SettingNotFoundException('db_name not found in postgres settings')
            self.postgres_settings = postgres_settings
            self.user = postgres_settings['user']
            self.password = postgres_settings['password']
            self.host = postgres_settings['host']
            self.port = postgres_settings['port']
            self.db_name = postgres_settings['db_name']
            self.open_connections = {}
            self.make_connection('postgres')
            self.current_db = ''

    def make_connection(self, db_name):
        con = psycopg2.connect(
            database=db_name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port)
        self.open_connections[db_name] = con

    def create_db(self, db_name):
        with self.open_connections['postgres'] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT create_db('{db_name}', '{self.user}', '{self.password}');")
        self.make_connection(db_name)
        self.read_functions(db_name)
        self._create_tables(db_name)
        con.commit()

    def read_functions(self, db_name):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(open("functions.sql", "r").read())
            con.commit()

    def drop_db(self, db_name):
        with self.open_connections['postgres'] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT drop_db('{db_name}', '{self.user}', '{self.password}');")
            con.commit()

    def _create_tables(self, db_name):
        with self.open_connections[db_name] as con:
            with self.open_connections[db_name].cursor() as cur:
                cur.execute(f"SELECT create_tables('{db_name}', '{self.user}', '{self.password}');")
            con.commit()

    def select_all_films(self, db_name):
        with self.open_connections[db_name].cursor() as cur:
            cur.execute(f"SELECT * FROM get_films();")
            records = cur.fetchall()
            return records

    def select_all_producers(self, db_name):
        with self.open_connections[db_name].cursor() as cur:
            cur.execute(f"SELECT * FROM get_producers();")
            records = cur.fetchall()
            return records

    def find_films(self, db_name, title):
        with self.open_connections[db_name].cursor() as cur:
            cur.execute(f"SELECT * FROM find_films('{title}');")
            records = cur.fetchall()
            return records

    def find_producers(self, db_name, name):
        with self.open_connections[db_name].cursor() as cur:
            cur.execute(f"SELECT * FROM find_producers('{name}');")
            records = cur.fetchall()
            return records

    def insert_film(self, db_name: str, film: Film):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT insert_film('{film.id}', '{film.title}', '{film.year}', '{film.producer_id}');")
            con.commit()

    def insert_producer(self, db_name: str, producer: Producer):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT insert_producer(CAST('{producer.id}' AS INTEGER), CAST('{producer.name}' AS TEXT), "
                            f"CAST('{producer.birth_date}' AS date), CAST('{producer.address}' AS TEXT), CAST('{producer.film_number}' AS INTEGER));")
            con.commit()

    def delete_all_films(self, db_name: str):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT delete_all_films();")
            con.commit()

    def delete_all_producers(self, db_name: str):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT delete_all_producers();")
            con.commit()

    def delete_producers_by_name(self, db_name: str, name: str):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT delete_producers_by_name('{name}');")
            con.commit()

    def delete_films_by_title(self, db_name: str, title: str):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT delete_films_by_title('{title}');")
            con.commit()

    def delete_producer_by_id(self, db_name: str, producer_id: int):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT delete_producer('{producer_id}');")
            con.commit()

    def delete_film_by_id(self, db_name: str, film_id: int):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT delete_film('{film_id}');")
            con.commit()

    def update_film(self, db_name: str, film: Film):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT update_film('{film.id}', '{film.title}', '{film.year}', '{film.producer_id}');")
            con.commit()

    def update_producer(self, db_name: str, producer: Producer):
        with self.open_connections[db_name] as con:
            with con.cursor() as cur:
                cur.execute(f"SELECT update_producer('{producer.id}', '{producer.name}', '{producer.birth_date}', "
                            f"'{producer.address}', '{producer.film_number}');")
            con.commit()
