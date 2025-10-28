# Use the latest Superset image
FROM apache/superset:latest

USER root

# Install packages using uv into the virtual environment
# Superset started using uv after the 4.1 branch
RUN . /app/.venv/bin/activate && \
    uv pip install \
    # install psycopg2 for using PostgreSQL metadata store
    psycopg2-binary \
    # install redis for caching
    redis \
    # install flask-cors for CORS support
    flask-cors

# Copy custom entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Switch back to the superset user
USER superset

# Use custom entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
