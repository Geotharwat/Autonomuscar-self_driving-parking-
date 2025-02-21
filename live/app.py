from flask import Flask, Response
from redis import Redis
from os import environ
import time

app = Flask(__name__)

broker = Redis(host=environ['REDIS_HOST'], port=environ['REDIS_PORT'], db=0)
subscriber = broker.pubsub()

feed = None

def onFeed(message):
    global feed
    feed = message['data']

subscriber.subscribe(**{
    'video_feed_original': onFeed,
})

subscriber.run_in_thread()

app.debug = False

def gen_frames():
    global feed
    prev = None
    while True:
        if feed is None or prev is feed:
            time.sleep(1/24)
            print('waiting for frame...')
            continue
        prev = feed;
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + feed + b"\r\n"
        )  # concat frame one by one and show result


@app.route("/api/live")
def live():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")