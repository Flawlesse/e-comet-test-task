FROM flawlesse/python-scrapy-playwright-cron:0.1.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY web-scrap/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt 
COPY web-scrap /app/
RUN chmod +x /app/runjob.sh
COPY .env /


COPY web-scrap/crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab

RUN touch /var/log/cron.log
CMD cron && tail -f /var/log/cron.log
