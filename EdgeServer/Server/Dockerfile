FROM python:3.10
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5001 5002 5003
ENV FLASK_PORT=5001

CMD python3 server.py ${FLASK_PORT}