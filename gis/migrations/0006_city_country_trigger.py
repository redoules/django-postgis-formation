from django.db import migrations, connection, models

TRIGGER_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION assign_country_to_city() RETURNS trigger AS $$
DECLARE
    country_id INTEGER;
BEGIN
    SELECT id INTO country_id
    FROM {country_table}
    WHERE ST_Contains(geom, NEW.geom)
    LIMIT 1;
    NEW.country_id := country_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS city_country_trigger ON {city_table};
CREATE TRIGGER city_country_trigger
BEFORE INSERT OR UPDATE ON {city_table}
FOR EACH ROW EXECUTE FUNCTION assign_country_to_city();
"""

class Migration(migrations.Migration):
    dependencies = [
        ('my_gis_app', '0005_rename_area_country_area_generated'),
    ]

    operations = [
        migrations.RunSQL(
            sql=TRIGGER_FUNCTION_SQL.format(country_table='my_gis_app_country', city_table='my_gis_app_city'),
            reverse_sql="""
                    DROP TRIGGER IF EXISTS city_country_trigger ON my_gis_app_city;
                    DROP FUNCTION IF EXISTS assign_country_to_city();
                """
        ),
    ]

