# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
from decouple import Config, RepositoryEnv
from datetime import datetime
env_config = Config(RepositoryEnv("/.env"))

class OwmScanPipeline:
    def __init__(self):
        self._create_connection()

    def _create_connection(self):
        self.connection = psycopg2.connect(
            database=env_config.get("POSTGRES_NAME"), 
            user=env_config.get("POSTGRES_USER"),
            password=env_config.get("POSTGRES_PASSWORD"), 
            host=env_config.get("HOST"), 
            port=env_config.get("PORT")
        )
        self.cursor = self.connection.cursor()

    def _store_in_db(self, item):
        sql = """
            INSERT INTO city_measurement (temperature, windspeed, pressure, 
                city_id, measured_when) VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            float(item['temperature']), 
            float(item['windspeed']), 
            int(item['pressure']), 
            int(item['city_id']),
            datetime.now()
        )
        self.cursor.execute(sql, params)
        self.connection.commit()

    def process_item(self, item, spider):
        self._store_in_db(item)
        return item

    
