
------------------- UPDATE PRODUCER -------------------
CREATE OR REPLACE FUNCTION 
	update_producer(p_id integer, new_name text, new_birth_date date, new_address text, new_film_number integer) 
RETURNS void AS $$
BEGIN
	UPDATE producers
	SET name = new_name,
		birth_date = new_birth_date,
		address = new_address,
		film_number = new_film_number
	WHERE id = p_id;
END
$$ LANGUAGE plpgsql;


------------------- UPDATE FILM -------------------
CREATE OR REPLACE FUNCTION 
	update_film(p_id integer, new_title text, new_year integer, new_producer_id integer) 
RETURNS void AS $$
BEGIN
	UPDATE films
	SET title = new_title,
		year = new_year,
		producer_id = new_producer_id
	WHERE id = p_id;
END
$$ LANGUAGE plpgsql;


------------------- DELETE PRODUCERS BY ID -------------------
CREATE OR REPLACE FUNCTION delete_producer(p_id integer) 
RETURNS void AS $$
BEGIN
	DELETE FROM producers
	WHERE id = p_id;
END
$$ LANGUAGE plpgsql;


------------------- DELETE FILMS BY ID -------------------
CREATE OR REPLACE FUNCTION delete_film(f_id integer) 
RETURNS void AS $$
BEGIN
	DELETE FROM films
	WHERE id = f_id;
END
$$ LANGUAGE plpgsql;


------------------- DELETE PRODUCERS BY NAME -------------------
CREATE OR REPLACE FUNCTION delete_producers_by_name(name_to_find text) 
RETURNS void AS $$
BEGIN
	DELETE FROM producers
	WHERE name = name_to_find;
END
$$ LANGUAGE plpgsql;


------------------- DELETE FILMS BY TITLE -------------------
CREATE OR REPLACE FUNCTION delete_films_by_title(title_to_find text) 
RETURNS void AS $$
BEGIN
	DELETE FROM films
	WHERE title = title_to_find;
END
$$ LANGUAGE plpgsql;


------------------- FIND PRODUCERS -------------------
CREATE OR REPLACE FUNCTION find_producers(name_to_find text) 
RETURNS TABLE(id integer, name text, birth_date date, address text, film_number integer) 
AS $func$
BEGIN
	RETURN QUERY
	SELECT * FROM producers p
	WHERE p.name = name_to_find;
END
$func$ LANGUAGE plpgsql;


------------------- FIND FILMS -------------------
CREATE OR REPLACE FUNCTION find_films(title_to_find text) 
RETURNS TABLE(id integer, title text, year integer, producer_id integer) 
AS $func$
BEGIN
	RETURN QUERY
	SELECT * FROM films f
	WHERE f.title = title_to_find;
END
$func$ LANGUAGE plpgsql;


------------------- INSERT PRODUCER -------------------
CREATE OR REPLACE FUNCTION insert_producer(p_id integer, name text, birth_date date, address text, film_number integer)
RETURNS void AS $$
BEGIN
	INSERT INTO producers VALUES
	(p_id, name, birth_date, address, (SELECT COUNT(*) FROM films f WHERE f.producer_id = p_id))
	ON CONFLICT DO NOTHING; 
END
$$ LANGUAGE plpgsql;


------------------- INSERT FILM -------------------
CREATE OR REPLACE FUNCTION insert_film(id integer, title text, year integer, producer_id integer) 
RETURNS void AS $$
BEGIN
	INSERT INTO films VALUES
	(id, title, year, producer_id)
	ON CONFLICT DO NOTHING; 
END
$$ LANGUAGE plpgsql;


------------------- DELETE ALL PRODUCERS -------------------
CREATE OR REPLACE FUNCTION delete_all_producers() 
RETURNS void AS $$
BEGIN
	DELETE FROM producers;
END
$$ LANGUAGE plpgsql;


------------------- DELETE ALL FILMS -------------------
CREATE OR REPLACE FUNCTION delete_all_films() 
RETURNS void AS $$
BEGIN
	DELETE FROM films;
END
$$ LANGUAGE plpgsql;


------------------- SELECT ALL PRODUCERS -------------------
CREATE OR REPLACE FUNCTION get_producers() 
RETURNS TABLE(id integer, name text, birth_date date, address text, film_number integer) 
AS $func$
BEGIN
	RETURN QUERY
	SELECT * FROM producers;
END
$func$ LANGUAGE plpgsql;


------------------- SELECT ALL FILMS -------------------
CREATE OR REPLACE FUNCTION get_films() 
RETURNS TABLE(id integer, title text, year integer, producer_id integer) 
AS $func$
BEGIN
	RETURN QUERY
	SELECT * FROM films;
END
$func$ LANGUAGE plpgsql;


------------------- TRIGGER FUNCTION -------------------
CREATE OR REPLACE FUNCTION update_number() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE producers
			SET film_number = (SELECT COUNT(*) FROM films f WHERE f.producer_id = NEW.producer_id)
			WHERE id = NEW.producer_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
		UPDATE producers
			SET film_number = (SELECT COUNT(*) FROM films f WHERE f.producer_id = OLD.producer_id)
			WHERE id = OLD.producer_id;
		UPDATE producers
			SET film_number = (SELECT COUNT(*) FROM films f WHERE f.producer_id = NEW.producer_id)
			WHERE id = NEW.producer_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
		UPDATE producers
			SET film_number = (SELECT COUNT(*) FROM films f WHERE f.producer_id = OLD.producer_id)
			WHERE id = OLD.producer_id;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;


------------------- CREATE TABLES -----------------
CREATE OR REPLACE FUNCTION create_tables(dbname text, username text, passwd text) RETURNS void AS $$
	BEGIN
			CREATE TABLE producers(
			id integer PRIMARY KEY,
			name text NOT NULL,
			birth_date date NOT NULL,
			address text NOT NULL,
			film_number integer NOT NULL DEFAULT 0
			);

			CREATE TABLE films(
			id integer PRIMARY KEY,
			title text NOT NULL,
			year integer NOT NULL,
			producer_id integer NOT NULL);

			CREATE INDEX on films(title);
			CREATE INDEX on producers(name);

			CREATE TRIGGER film_number_updater
			AFTER INSERT OR UPDATE OR DELETE ON
				films FOR EACH ROW EXECUTE PROCEDURE update_number();
	END
$$ LANGUAGE plpgsql;