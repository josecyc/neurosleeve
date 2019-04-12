import time, sys

def print_message(*args):
    try:
        current = time.time()
        if sys.version_info.major == 2: #check if python2 
            print("(%f) RECEIVED MESSAGE: %s %s" % (current, args[0], ",".join(str(x) for x in args[2:])))
        elif sys.version_info.major == 3: #check if python3
            print("(%f) RECEIVED MESSAGE: %s %s" % (current, args[0], ",".join(str(x) for x in args[1:])))
    except ValueError: pass

# Clean exit from print mode
def exit_print(signal, frame):
    print("Closing listener")
    sys.exit(0)