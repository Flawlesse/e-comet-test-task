from fastapi import FastAPI, Response, HTTPException, status
from api.database import get_db_connection
import psycopg2
from typing import Optional
import requests
from api.config import ENV
from api.validators import get_validated_timestamp_bounds


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
async def city_stats(city: str, response: Response, start_dt: Optional[int] = None, end_dt: Optional[int] = None):
    """
    Please notice that start_dt & end_dt are provided as UTC timestamps, 
    which are raw integers. Time is in SECONDS since Epoch.
    Also, min value for start_dt & end_dt is 2023-01-01 00:00:00
    or 1669766400. Visit https://www.epochconverter.com/ for more help.
    """
    # normalize input
    start_dt, end_dt = get_validated_timestamp_bounds(start_dt=start_dt, end_dt=end_dt)
    city = city.strip()

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # check if city is already present in db
            # and get city.id back for faster search
            sql = """
                SELECT id, name, code FROM city WHERE name ILIKE %s
            """
            params = (city,)
            cursor.execute(sql, params)
            res = cursor.fetchone()
            if res is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"No city \"{city}\" was found. Please provide full name of the city."
                )
            city_id = res[0]
            city_name = res[1]
            city_code = res[2]

            # collect measurements from start_dt to end_dt
            sql = f"""
                SELECT id, temperature, windspeed, pressure, measured_when
                FROM city_measurement
                WHERE city_id = %s
                {"AND measured_when >= %s" if start_dt is not None else ""}
                {"AND measured_when <= %s" if end_dt is not None else ""}
                ORDER BY measured_when DESC;
            """
            params = [city_id]
            if start_dt is not None:
                params.append(start_dt)
            if end_dt is not None:
                params.append(end_dt)
            cursor.execute(sql, params)
            measurements = [
                {
                    'id': entry[0], 
                    'tepmerature': entry[1],
                    'windspeed': entry[2],
                    'pressure': entry[3],
                    'measured_when': entry[4],
                }
                for entry in cursor.fetchall()
            ]

            # form SQL-query & collect statistics
            if len(measurements) != 0:
                sql = f"""
                    SELECT AVG(temperature) as avg_temp, 
                        AVG(windspeed) as avg_wind, 
                        AVG(pressure) as avg_pres
                    FROM city_measurement 
                    WHERE city_id = %s
                    {"AND measured_when >= %s" if start_dt is not None else ""}
                    {"AND measured_when <= %s" if end_dt is not None else ""}
                """
                params = [city_id]
                if start_dt is not None:
                    params.append(start_dt)
                if end_dt is not None:
                    params.append(end_dt)
                cursor.execute(sql, params)
                res = cursor.fetchone()
                avg_stats = {
                    'avg_temperature': round(res[0], 2), 
                    'avg_windspeed': round(res[1], 2),
                    'avg_pressure': round(res[2], 2)
                }
            else:
                avg_stats = {
                    'avg_temperature': None, 
                    'avg_windspeed': None,
                    'avg_pressure': None
                }

            # now form a proper response
            response_body = {
                'id': city_id,
                'name': city_name,
                'code': city_code,
                'stats': avg_stats,
                'count': len(measurements),
                'measurements': measurements,
            }
            response.status_code = status.HTTP_200_OK
            return response_body
    except HTTPException as exc:
        raise exc
    except (Exception, psycopg2.Error):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Bad request."
        )
    finally:
        connection.close()