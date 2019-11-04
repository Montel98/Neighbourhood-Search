CREATE TABLE IF NOT EXISTS vicinity (
	id integer PRIMARY KEY,
	name text NOT NULL,
	local_authority text NOT NULL,
	county text NOT NULL
	);

CREATE TABLE IF NOT EXISTS area_code (
    code text PRIMARY KEY
    );

CREATE TABLE IF NOT EXISTS has_area_code (
    vicinity_id integer NOT NULL,
    area_code_id text NOT NULL,
    proportion real NOT NULL,
    PRIMARY KEY (vicinity_id, area_code_id),
    FOREIGN KEY (vicinity_id) REFERENCES vicinity(id),
    FOREIGN KEY (area_code_id) REFERENCES area_code(code)
    );

CREATE TABLE IF NOT EXISTS rent_price (
	id integer PRIMARY KEY,
	area_code_id integer NOT NULL,
	room_type text NOT NULL,
	mean real NOT NULL,
	variance real NOT NULL,
	FOREIGN KEY (area_code_id) REFERENCES area_code(id)
	);