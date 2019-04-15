import argparse, time, os, sys, signal, datetime
import pandas as pd
import numpy as np
from osc_helper import *
from collections import deque
from colored import fg, attr
if sys.version_info.major == 3:
    from pythonosc import dispatcher
    from pythonosc import osc_server
elif sys.version_info.major == 2:
    import OSC

#globals
g_iter = 0
label_iter = 0
CHANNELS = [
    'ch1', 'ch2',
    'ch3', 'ch4'
    ]
CH_DATA = {ch: deque() for ch in CHANNELS}
NB_CHANNELS = len(CH_DATA.keys())
LABELS = [
    'alpha', 'go', 'left', 'neutral',
    'omega', 'right', 'stop'
    ]
dir_path = os.path.join(ROOT, 'osc_data')
try:
    os.mkdir(dir_path)
except FileExistsError:
    pass
for label in LABELS:
    try:
        os.mkdir(os.path.join(dir_path, label))
    except FileExistsError:
            pass
LABEL_COUNT = {
    label: len(os.listdir('osc_data/{}'.format(label))) + 1
    for label in LABELS
    }
file_iter = np.sum(list(LABEL_COUNT.values())) - 6
NB_LABELS = len(LABELS)
COLORS = [
    'red', 'green', 'yellow', 'light_blue',
    'magenta', 'cyan', 'white'
    ]
INTERVAL = 15 # seconds to record of each label
SAMPLE_RATE = 200
SAMPLES_PER_INTERVAL = INTERVAL * SAMPLE_RATE
ROOT = os.getcwd()
CHECKPOINTS = list(range(1049,3049,50))

def output_command(s_label, color):
    '''Prints command to be excecuted'''
    color = fg(color)
    reset = attr('reset')
    print(
        color
        + "#" * 42 + "\n"
        + "#" * 42 + "\n"
        + "    {} \n".format(s_label)
        + "#" * 42 + "\n"
        + "#" * 42
        +reset
        )

def dframe2csv(csv_path):
    '''Turns dictionary with data from the four channels into a pd.DataFrame
    and then into a .csv file
    
    Keyword arguments:
    csv_path -- path to the label's directory
    '''
    global LABEL_COUNT, label_iter
    
    label = LABELS[label_iter]
    df = pd.DataFrame(CH_DATA)
    df.to_csv(csv_path + "/{}/".format(label) + str(LABEL_COUNT[label]) + ".csv", index=False)
    
    print(' ' * 42, end='\r')
    print("Produced {}'s csv no.: {}, sample: {}".format(label, LABEL_COUNT[label], file_iter), end='\r')
    
    LABEL_COUNT[label] += 1 
    

def stream_window(*args):
    '''Outputs gestures to be excecuted, receives data from
    server and stores 50 samples inside a global dictionary,
    calls dframe2csv after 5 seconds after the label appears
    on screen (this gives you time to get your arm in the
    right position).
    '''
    global g_iter, file_iter, label_iter, CH_DATA

    if g_iter % SAMPLES_PER_INTERVAL == 0:
        if g_iter != 0:
            print('')
        if label_iter == NB_LABELS - 1:
            label_iter = 0
        else:
            label_iter += 1
        output_command(LABELS[label_iter], COLORS[label_iter])

    for x in range(1, NB_CHANNELS + 1):
        ch = 'ch{}'.format(x)
        if g_iter >= 50:
            CH_DATA[ch].popleft()
        CH_DATA[ch].append(round(args[x + 1], 2))

    g_iter += 1
    if g_iter % SAMPLES_PER_INTERVAL in CHECKPOINTS:
        dframe2csv(args[1][0])
        file_iter += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="localhost", 
                        help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, 
                        default=12345, 
                        help="The port to listen on, default=12345")
    parser.add_argument("--address",
                        default="/openbci", 
                        help="address to listen to, default=/openbci")
    args = parser.parse_args()

    if sys.version_info.major == 3:
        dispatcher = dispatcher.Dispatcher()
        
        dispatcher.map("/openbci", stream_window, dir_path)
        signal.signal(signal.SIGINT, exit_print)

        # Display server attributes
        print('--------------------')
        print(" -- OSC LISTENER -- ")
        print('--------------------')
        print("IP:", args.ip)
        print("PORT:", args.port)
        print("ADDRESS:", args.address)
        print('--------------------')

        # Connect server
        server = osc_server.BlockingOSCUDPServer(
            (args.ip, args.port), dispatcher)
        server.serve_forever()
    else:
        print("Make sure python is version 3 and up")
