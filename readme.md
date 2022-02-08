- websocket 
    - https://flask-socketio.readthedocs.io/en/latest/intro.html
- async
    - greenlet
    - gevent-websocket
- confluent-kafka
    - https://kafka-python.readthedocs.io/en/master/

gunicorn -k eventlet -w 5 -b 0.0.0.0:8080 run:app