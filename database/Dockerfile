FROM postgres:14.1
WORKDIR /sql_scripts
COPY database/db_init.sql /sql_scripts
CMD ["/usr/local/bin/docker-entrypoint.sh","postgres"]