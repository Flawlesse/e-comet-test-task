FROM python:3.10
WORKDIR /app
COPY api/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY api /app/api
COPY .env /
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]
