# OpenBCI data prediction stream

We use OSC to stream the data obtaining the sEMG signals from the forearm and translate them to computer input commands.

Uses the python-osc library to communicate with the OpenBCI device.

Device used: OpenBCI Ganglion

Communication parameters

Model type
--option
 # spectrogram: loads spectrogram model weights, preprocesses the data and predicts an action every 10 data points or 50 ms
 # RD: loads raw data model weights and predicts an action every 10 data points or 50 ms
