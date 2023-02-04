FROM python:3.10.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install cron nano
WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip install scrapy
RUN pip install scrapy-playwright
RUN playwright install
RUN playwright install-deps
COPY web-scrap/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt 

# COPY owm_scan /app/owm_scan
COPY web-scrap /app/
RUN chmod +x /app/runjob.sh
COPY .env /


COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab

RUN touch /var/log/cron.log
# COPY root /var/spool/cron/crontabs/root
CMD cron && tail -f /var/log/cron.log
