# 1. Start from an official, small Python image
FROM python:3.12-slim

# 2. Work inside /app in the container
WORKDIR /app

# 3. Install the Python libraries first (this layer is cached between builds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the application code
COPY app.py .

# 5. Document the port the app listens on
EXPOSE 5000

# 6. Start the app with gunicorn (a production web server), 2 workers
#    Sync workers close the connection after each request, so every browser
#    refresh can be sent to a different replica by Swarm's load balancer.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
