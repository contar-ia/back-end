FROM postgres:17.2-alpine3.20

ENV POSTGRES_DB=contaria
ENV POSTGRES_USER=contaria
ENV POSTGRES_PASSWORD=contaria

COPY setup.sql /docker-entrypoint-initdb.d/

EXPOSE 5432