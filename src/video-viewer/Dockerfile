FROM python:3.10-slim

EXPOSE 8080
WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "app_viewer.py", "--server.port=8080", "--server.address=0.0.0.0"]
