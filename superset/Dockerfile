FROM apache/superset:3.0.0

USER root

# Install PostgreSQL client
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

USER superset

# Install additional Python packages
RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.9 \
    redis==5.0.1

EXPOSE 8088
