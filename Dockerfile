#FROM python:3.11.1-slim
FROM tadeorubio/pyodbc-msodbcsql17
#WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY /src .
COPY /sql_scripts /sql_scripts