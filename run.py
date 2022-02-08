from eventlet import wsgi, websocket
import eventlet
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer, TopicPartition, KafkaProducer
from flask_cors import CORS, cross_origin
from kafka.errors import KafkaError
import uuid
import logging
import sys
import time

logger = logging.getLogger('kafka')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.ERROR)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app, async_mode='eventlet', logger=True,
                    engineio_logger=True, cors_allowed_origins="*")

BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = "test"
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Access-Control-Allow-Origin'


@app.route('/')
@cross_origin()
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
    # return {}


@socketio.on('connect', namespace='/kafka')
def test_connect(message):
    emit('logs', {'data': 'Connection established'})


@socketio.on("kafkaconsumer", namespace="/kafka")
def kafkaconsumer(message):
    consumer = KafkaConsumer(group_id='consumer-1',
                             bootstrap_servers=BOOTSTRAP_SERVERS,
                             auto_offset_reset="latest")
    tp = TopicPartition(TOPIC_NAME, 0)
    # register to the topic
    consumer.assign([tp])
    # consumer.subscribe([TOPIC_NAME])
    try:

        for message in consumer:
            if not message:
                time.sleep(100)
            print(message)
            print(type(message))
            emit('kafkaconsumer', {'data': message.value.decode('utf-8')})
            break
        # emit('kafkaconsumer', {'data': message.value.decode('utf-8')})
        # obtain the last offset value
        # consumer.seek_to_end(tp)
        # lastOffset = consumer.position(tp)
        # consumer.seek_to_beginning(tp)
        # for message in consumer:
        #     print(message)
        #     emit('kafkaconsumer', {'data': message.value.decode('utf-8')})
        #     if message.offset == lastOffset - 1:
        #         break
    except KafkaError as e:
        print(e)
    finally:
        consumer.close()
        print('finally')


@socketio.on("kafkaproducer", namespace="/kafka")
def kafkaproducer(message):
    print(TOPIC_NAME)
    print(BOOTSTRAP_SERVERS)
    try:
        producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
        producer.send(TOPIC_NAME, value=bytes(
            str(message), encoding='utf-8'), key=bytes(str(uuid.uuid4()), encoding='utf-8'))
        emit('logs', {'data': 'Added ' + message + ' to topic'})
        emit('kafkaproducer', {'data': message})
        producer.close()
        kafkaconsumer(message)
    except KafkaError as e:
        print(e)


if __name__ == '__main__':
    # socketio.run(app, host="127.0.0.1", port=5000, debug=True)
    wsgi.server(eventlet.listen(('0.0.0.0', 8080)), app)
