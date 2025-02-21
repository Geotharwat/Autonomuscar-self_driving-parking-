from redis import Redis

broker = Redis(host='127.0.0.1', port=6379, db=0, decode_responses='utf-8')
subscriber = broker.pubsub()

__state = {
    'mode' : broker.get('mode'),
    'control_x' : 0,
    'control_y' : 0,
}

def onSetEvent(eventName):
    global mode
    _, key = eventName['channel'].split(':')
    if eventName['data']  == 'set':
        __state[key] = broker.get(key) 

subscriber.subscribe(**{
    '__keyspace@0__:mode': onSetEvent,
    '__keyspace@0__:control_x': onSetEvent,
    '__keyspace@0__:control_y': onSetEvent,
})



subscriber.run_in_thread()

def getControls():
    global __state
    float(__state['control_x'])
    x = __state['control_x']
    y = __state['control_y']
    return [float(x) if x is not None else 0, float(y) if y is not None else 0]

def getMode():
    global __state
    return __state['mode']
