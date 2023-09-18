FROM python:3.8

RUN mkdir app
WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
RUN python init.py

ENV PORT=9266
EXPOSE 9266

CMD ["python", "server.py"]