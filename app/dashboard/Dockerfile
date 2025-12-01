FROM python:3.9-slim

WORKDIR /app

RUN pip install streamlit mysql-connector-python pandas plotly

COPY app.py .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
