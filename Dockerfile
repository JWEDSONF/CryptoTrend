FROM python:3.8
EXPOSE 8080
WORKDIR /app
COPY . ./
RUN pip install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "1_🫧_CryptoTrend.py", "--server.port=8080", "--server.address=0.0.0.0"]
