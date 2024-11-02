FROM python:3.9-alpine3.19

WORKDIR /src

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /src/start.sh

CMD ["/src/start.sh"]
