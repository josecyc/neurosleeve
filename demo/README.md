# OpenBCI data prediction stream

We use OSC to stream the data obtaining the sEMG signals from the forearm and translate them to computer input commands.

Uses the python-osc library to communicate with the OpenBCI device.

Setting up the OpenBCI GUI for streaming:

1) Open GUI and connect via bluetooth to OpenBCI Ganglion
2) Start system
3) Select networking widget with timeseries option and start system

<p align="center">
  <img width="800" height="500" src="../images/open_bci_gui.png">
</p>

Communication parameters

* `--ip`
  * The ip to be listened, default = `localhost`
* `--port`
  * The port to be listened, default = `12345`
* `--address`
  * Address to be listened, default = `/openbci`


Model type
* `--model`
  * `spectrogram`: loads spectrogram model weights, preprocesses the data and predicts an action every 10 data points (50 ms)
  * `RD`: loads raw data model weights and predicts an action every 10 data points (50 ms)

##osc_collect_data.py sample usage:
```
$ python3 stream.py
--------------------
 -- OSC LISTENER --
--------------------
IP: localhost
PORT: 12345
ADDRESS: /openbci
--------------------

Action: stop Confidence: 99.0% Key: Key.space
```
Will setup a listener in ip `localhost`, port `12345`, address `/openbci` and will predict actions once the OpenBCI GUI begins streaming data. 
