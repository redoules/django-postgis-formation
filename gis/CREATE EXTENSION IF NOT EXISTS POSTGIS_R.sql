CREATE EXTENSION IF NOT EXISTS POSTGIS_RASTER CASCADE;


CREATE TABLE my_table (
    id INTEGER,
    geom GEOMETRY
); 


INSERT INTO my_table (id, geom) VALUES
(1, 'POINT(0 0)'::geometry);
INSERT INTO my_table (id, geom) VALUES
(2, ST_MAKEPOINT(1,1));
INSERT INTO my_table (id, geom) VALUES
(3, 'LINESTRING(0 0, 1 1)'::geometry);

SELECT ST_DISTANCE(geo1.geom, geo2.geom) FROM my_table AS geo1 JOIN my_table AS geo2 ON geo1.id  != geo2.id; 


SELECT "my_gis_app_city"."id",
       "my_gis_app_city"."name",
       "my_gis_app_city"."geom"::bytea,
       (
        SELECT STRING_AGG(U0."name", ', ' ) AS "names"
          FROM "my_gis_app_country" U0
         WHERE ST_Contains(U0."geom", ("my_gis_app_city"."geom"))
         GROUP BY U0."id"
       ) AS "countries_names"
  FROM "my_gis_app_city"
 ORDER BY "my_gis_app_city"."name" ASC,
          "my_gis_app_city"."id" DESC


SELECT "my_gis_app_city"."id",
       "my_gis_app_city"."name",
       "my_gis_app_city"."geom"::bytea,
       (
        SELECT STRING_AGG(U0."name", ', ' )
          FROM "my_gis_app_country" U0
         WHERE ST_Contains(U0."geom", "my_gis_app_city"."geom")
       ) AS "countries_names"
  FROM "my_gis_app_city"
 ORDER BY "my_gis_app_city"."name" ASC,
          "my_gis_app_city"."id" DESC;



SELECT STRING_AGG(U0."name", ', ' )
                  FROM "my_gis_app_country" U0
                 WHERE ST_Contains(U0."geom", "my_gis_app_city"."geom")



SELECT "my_gis_app_city"."id",
       "my_gis_app_city"."name",
       "my_gis_app_city"."geom"::bytea,
       (
        SELECT STRING_AGG(U0."name", ', ')
          FROM "my_gis_app_country" U0
         WHERE ST_INTERSECTS(U0."geom", "my_gis_app_city"."geom")
       ) AS "countries_names"
  FROM "my_gis_app_city"
 ORDER BY "my_gis_app_city"."name" ASC,
          "my_gis_app_city"."id" DESC



SELECT "my_gis_app_city"."id",
       "my_gis_app_city"."name",
       "my_gis_app_city"."geom"::bytea,
       (
        SELECT STRING_AGG(U0."name", ', ')
          FROM 'my_gis_app_country' U0
         WHERE ST_INTERSECTS(U0."geom", 'my_gis_app_city'."geom")
       ) AS "countries_names"
  FROM "my_gis_app_city"
 ORDER BY "my_gis_app_city"."name" ASC,
          "my_gis_app_city"."id" DESC



SELECT * FROM "my_gis_app_city";