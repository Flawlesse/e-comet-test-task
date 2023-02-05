CREATE TABLE IF NOT EXISTS city (
    id bigint UNIQUE NOT NULL,
    name varchar(300) NOT NULL,
    code varchar(5) NOT NULL,

    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS city_measurement (
    id bigint GENERATED ALWAYS AS IDENTITY,
    measured_when timestamp NOT NULL,
    temperature float8 NOT NULL,
    windspeed float8 NOT NULL,
    pressure int NOT NULL,
    city_id bigint NOT NULL,

    PRIMARY KEY (id),
    CONSTRAINT measurement_fk_city 
        FOREIGN KEY(city_id)
        REFERENCES city(id)
        ON DELETE CASCADE
);

INSERT INTO city (id, name, code) VALUES (625144, 'Minsk', 'BY');
INSERT INTO city (id, name, code) VALUES (524901, 'Moscow', 'RU');
INSERT INTO city (id, name, code) VALUES (6094817, 'Ottawa', 'CA');
INSERT INTO city (id, name, code) VALUES (264371, 'Athens', 'GR');


-- COMMENT THIS OUT!
-- SELECT found_max_measurements.city_name, city_measurement.temperature FROM (
--     SELECT city.name as city_name, MAX(city_measurement.id) as measure_id
--     FROM city 
--     JOIN city_measurement ON city.id=city_measurement.city_id 
--     -- WHERE city.name ILIKE 'M%'
--     GROUP BY city.name
-- ) AS found_max_measurements
-- JOIN city_measurement ON found_max_measurements.measure_id = city_measurement.id;