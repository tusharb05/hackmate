FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/local/app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy the entrypoint script and make it executable
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT [ "entrypoint.sh" ]
# Set the default command to run the server
CMD ["python", "-u", "./team_service/manage.py", "runserver", "0.0.0.0:8000"]


# FROM python:3.11-slim

# ENV PYTHONUNBUFFERED=1

# WORKDIR /usr/local/app

# COPY ./requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# RUN chmod +x entrypoint.sh

# ENTRYPOINT [ "./entrypoint.sh" ]