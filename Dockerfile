FROM python:3.12-alpine3.20

WORKDIR /src

RUN pip install --upgrade pip

# Install GStreamer and its plugins (including WebRTC and Python bindings)
RUN apk add --no-cache \ 
    postgresql15 \
    build-base

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask run", "--host=0.0.0.0"]
