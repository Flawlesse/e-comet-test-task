from fastapi import FastAPI, Response, HTTPException, status
from api.database import get_db_connection
import psycopg2
from typing import Optional
import requests
from api.config import ENV


app = FastAPI()


@app.post('/weather/{city}')
async def add_new_city(city: str, response: Response):
    city = city.strip()
    r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?appid={ENV.get('OWM_API_KEY')}&q={city}")
    r_json = r.json()
    # be careful as OWM API returns STRING status code in response body for NOT FOUND 
    if int(r_json['cod']) >= 400 or r_json['name'].lower() != city.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"No city \"{city}\" was found. Please provide full name of the city."
        )
    res = dict(
        id=r_json['id'],
        name=r_json['name'],
        code=r_json['sys']['country']
    )
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # check if city is already present in db
            sql = """
                SELECT id FROM city WHERE name = %s
            """
            params = (res['name'],)
            cursor.execute(sql, params)
            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"City \"{res['name']}\" is already present in the system."
                )
            # now insert new city
            sql = f"""
                INSERT INTO city (id, name, code)
                VALUES (%s, %s, %s)
            """
            params = (res['id'], res['name'], res['code'])
            cursor.execute(sql, params)
            connection.commit()
            response.status_code = status.HTTP_201_CREATED
            return f"City \"{res['name']}\" was successfully added."
    except HTTPException as exc:
        raise exc
    except (Exception, psycopg2.Error):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Bad request."
        )
    finally:
        connection.close()



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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Bad request."
        )
    finally:
        connection.close()


@app.get('/city_stats')
async def city_stats(city: str, start_dt: int, end_dt: int, response: Response):
    pass