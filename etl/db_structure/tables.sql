Create TABLE vehicles (vehicle_id        SERIAL,
                       vehicle_id_string TEXT    NOT NULL,
                       vehicle_type_id   SMALLINT);

CREATE UNIQUE INDEX unique_veh_id ON vehicles (vehicle_id_string);
CREATE UNIQUE INDEX unique_veh_idx ON vehicles (vehicle_id);


CREATE TABLE vehicle_types (id               SERIAL,
                            type_vn          TEXT,
                            type_en          TEXT,
                            group_name       TEXT,
                            vehicle_type     TEXT);



Create TABLE vehicle_days  (vehicle_id  INTEGER   NOT NULL,
                            day         DATE      NOT NULL,
                            pings       INTEGER   NOT NULL,
                            min_time    TIMESTAMP NOT NULL,
                            max_time    TIMESTAMP NOT NULL,
                            geom        geometry(Polygon, 4326));

CREATE INDEX veh_days_gist ON vehicle_days USING GIST(geom);
CREATE INDEX vehicle_days_id_idx ON vehicle_days (vehicle_id);
CREATE INDEX vehicle_days_day_idx ON vehicle_days (day);
CREATE INDEX vehicle_days_pings_idx ON vehicle_days (pings);
CREATE INDEX vehicle_days_min_time_idx ON vehicle_days (min_time);
CREATE INDEX vehicle_days_max_time_idx ON vehicle_days (max_time);


Create TABLE days_ingested  (day            TEXT      NOT NULL,
                             ingestion_date TIMESTAMP NOT NULL);