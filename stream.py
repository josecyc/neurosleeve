import argparse, time, os, sys
import pandas as pd
import numpy as np
import signal as sg
from pynput.keyboard import Key, Controller
from collections import deque, Counter
from osc_helper import *
from pythonosc import dispatcher
from pythonosc import osc_server
from tensorflow.keras.models import load_model
from scipy import signal

# globals ########################
g_iter = 0
s = time.time()
times = list(range(0,200,10))
CHANNELS = ['ch1', 'ch2', 'ch3', 'ch4']
CH_DATA = {ch: deque() for ch in CHANNELS}
NB_CHANNELS = len(CH_DATA.keys())
LABELS = ['right', 'go', 'left', 'stop', 'neutral', 'omega', 'alpha']
keys = [Key.right, Key.down, Key.left, None, None, Key.up, 'c']
shape = (6, 21, 4)
flat_dim = shape[0]*shape[1]*shape[2]
nperseg = 10
noverlap = 8
reshape = (-1, shape[0], shape[1], shape[2])
actions = []
prev_action = 4
keyboard = Controller()


# Local path to trained weights file
model = load_model('./model_2.h5')

def preprocess(x_train):
    sg = np.zeros((1, 6, 21, 4))
    for i in range(4):
        frequencies, times, spec = signal.spectrogram(x=x_train[CHANNELS[i]],
            fs=200, nperseg=nperseg, noverlap=noverlap, window='hann')
        sg[0,:,:,i] = spec
    return sg

def predict(features):
    logits = model.predict(features)[0]
    threshold = logits < .45
    logits[threshold] = 0
    if logits.sum() > 0:
        pred = np.argmax(logits)
        return(LABELS[pred], logits[pred])
    else:
        return(LABELS[4], .42)

def stream_window(*args):
    global g_iter, CH_DATA, prev_action 
    #print(g_iter, 'W_time:', time.time()-s)
    for x in range(1, NB_CHANNELS + 1):
        ch = 'ch{}'.format(x)
        if g_iter >= 50:
            CH_DATA[ch].popleft()
        CH_DATA[ch].append(round(args[x], 2))

    g_iter += 1
    if g_iter % 200 in times and g_iter >= 50: # number of signal samples to be packed into prediction.
        x_data = pd.DataFrame(CH_DATA)
        x_data_x = preprocess(x_data)
        label, confidence = predict(x_data_x)
        action, confidence = predict(x_data_x)
        actions.append(action)
        if len(actions) == 11:
            del actions[0]
        c = Counter(actions)
        value, count = c.most_common()[0]
        action_index = LABELS.index(value)
        print(' '*80, end="\r")
        print('Action:', value, 'Confidence: {:.1f}%'.format(confidence*100), 'Key:', keys[action_index], end="\r")
        if prev_action != action_index:
            if keys[prev_action] != None:
                keyboard.release(keys[prev_action])
            if keys[action_index]!= None:
                keyboard.press(keys[action_index])
        prev_action = action_index
    #s = time.time()
        

if __name__ == "__main__":
# Collect command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="localhost",
                        help="The ip to listen on")
    parser.add_argument("--port",
                        type=int,
                        default=12345,
                        help="The port to listen on")
    parser.add_argument("--address",
                        default="/openbci",
                        help="address to listen to")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/openbci", stream_window)
    sg.signal(sg.SIGINT, exit_print)

    # Display server attributes
    print('--------------------')
    print(" -- OSC LISTENER -- ")
    print('--------------------')
    print("IP:", args.ip)
    print("PORT:", args.port)
    print("ADDRESS:", args.address)
    print('--------------------')

    # connect server
    server = osc_server.BlockingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    server.serve_forever()
    