from fastapi import FastAPI, Response, HTTPException, status
from api.database import get_db_connection
import psycopg2
from typing import Optional
import requests
import json


app = FastAPI()


@app.post('/weather/{city}')
async def add_new_city(city: str, response: Response):
    
    pass


@app.get('/last_weather')
async def cities_last_weather(response: Response, search: Optional[str] = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = f"""
                SELECT found_max_measurements.city_name, city_measurement.temperature 
                FROM (
                    SELECT city.name as city_name, 
                        MAX(city_measurement.id) as measure_id
                    FROM city 
                    JOIN city_measurement ON city.id=city_measurement.city_id 
                    {f"WHERE city.name ILIKE '%{search.strip()}%'" if search is not None else ""}
                    GROUP BY city.name
                ) AS found_max_measurements
                JOIN city_measurement 
                ON found_max_measurements.measure_id = city_measurement.id;
            """
            cursor.execute(sql)
            res = [
                {'city': entry[0], 'temperature': entry[1]} 
                for entry in cursor.fetchall()
            ]
            response.status_code = status.HTTP_200_OK
            return res
    except (Exception, psycopg2.Error):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Bad request."
        )
    finally:
        connection.close()

@app.get('/city_stats')
async def city_stats(city: str, start_dt: int, end_dt: int, response: Response):
    pass