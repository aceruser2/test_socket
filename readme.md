- websocket 
    - https://flask-socketio.readthedocs.io/en/latest/intro.html
- async
    - greenlet
    - gevent-websocket
- confluent-kafka
    - https://kafka-python.readthedocs.io/en/master/

gunicorn -k eventlet -w 5 -b 0.0.0.0:8080 run:app


version: '3'

services:
  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
  kafka:
    image: wurstmeister/kafka
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: localhost
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181