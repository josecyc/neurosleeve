import argparse, time, os, sys
import pandas as pd
import numpy as np
import signal as sg
from pynput.keyboard import Key, Controller
from collections import deque, Counter
from osc_helper import *
if sys.version_info.major == 3:
    from pythonosc import dispatcher
    from pythonosc import osc_server
elif sys.version_info.major == 2:
    import OSC
from tensorflow.keras.models import load_model
from scipy import signal
from time import sleep

# globals
g_iter = 0
TIMES = list(range(0,200,10))
CHANNELS = [
    'ch1', 'ch2',
    'ch3', 'ch4'
    ]
CH_DATA = {ch: deque() for ch in CHANNELS}
NB_CHANNELS = len(CH_DATA.keys())
LABELS = [
    'right', 'go', 'left', 'stop',
    'neutral', 'omega', 'alpha'
    ]
keys = [None, Key.left, None, Key.space, None, Key.right, None]
shape = (6, 21, 4)
flat_dim = shape[0]*shape[1]*shape[2]
nperseg = 10
noverlap = 8
reshape = (-1, shape[0], shape[1], shape[2])
actions = []
prev_action = 4
keyboard = Controller()
ts = 10

def preprocess(x_train):
    '''Creates spectrograms for each channel inside the data stream
    
    Keyword arguments:
    x_train -- raw data from stream
    '''
    sg = np.zeros((1, 6, 21, 4))
    for i in range(4):
        frequencies, times, spec = signal.spectrogram(x=x_train[CHANNELS[i]],
            fs=200, nperseg=nperseg, noverlap=noverlap, window='hann')
        sg[0,:,:,i] = spec
    return sg

def predict(features, threshold):
    '''Makes a prediction based on the model's confidence,
    if the confidence is smaller than confiddence threshold,
    then it pregicts
    
    Keyword arguments:
    features -- preprocessed features
    threshold -- prediction threshold
    '''
    logits = model.predict(features)[0]
    indexes = logits < threshold
    logits[indexes] = 0
    if logits.sum() > 0:
        pred = np.argmax(logits)
        return(LABELS[pred], logits[pred])
    else:
        return(LABELS[4], .42)

def specm_stream_window(*args):
    '''Receives data from server and stores 50 samples inside a 
    global dictionary, preprocesses the data, makes a prediction
    and maps each prediction to a different key in the keyboard
    (Model using spectrograms)
    '''
    
    global g_iter, CH_DATA, prev_action
    
    for x in range(1, NB_CHANNELS + 1):
        ch = 'ch{}'.format(x)
        if g_iter >= 50:
            CH_DATA[ch].popleft()
        CH_DATA[ch].append(round(args[x], 2))

    g_iter += 1
    if g_iter % 200 in times and g_iter >= 50:
        x_data = pd.DataFrame(CH_DATA)
        x_data = preprocess(x_data)
        action, confidence = predict(x_data, .45)
        actions.append(action)
        if len(actions) > ts:
            del actions[0]
        sum_actions = np.concatenate([np.repeat(val,(ind + 1)) for ind, val in enumerate(actions)])
        c = Counter(sum_actions)
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
        
def rdm_stream_window(*args):
        '''Receives data from server and stores 50 samples inside a 
    global dictionary, preprocesses the data, makes a prediction
    and maps each prediction to a different key in the keyboard
    (Model using raw data)
    '''
    
    global g_iter, CH_DATA, prev_action
    
    for x in range(1, NB_CHANNELS + 1):
        ch = 'ch{}'.format(x)
        if g_iter >= 50:
            CH_DATA[ch].popleft()
        CH_DATA[ch].append(round(args[x], 2))

    g_iter += 1
    if g_iter % 200 in times and g_iter >= 50:
        x_data = pd.DataFrame(CH_DATA).transpose().values.flatten().reshape([1, 200])
        action, confidence = predict(x_data, .85)
        actions.append(action)
        if len(actions) > ts:
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
                        help="Address to listen to")
    parser.add_argument("--model",
                        default="spectrogram",
                        help="Type of model to be used (spectrogram, RD)")
    args = parser.parse_args()

    # Local path to trained weights file
    if args.model == "spectrogram":
        model = load_model('../models/model_2.h5')
        stream_window = specm_stream_window
    
    elif args.model == "RD":
        model = load_model('../models/RDM_V3.h5')
        stream_window = rdm_stream_window
    
    else:
        print('Please select a valid model')
        sys.exit()
    
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
    