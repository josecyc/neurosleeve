## osc_collect_data.py description:

This script helps you to collect your data and turn it into .csv files, to do this the script outputs a label and waits 5 seconds for you to adjust to the position assigned to that label, then records 10 seconds of data at 200 Hz which is splitted into 40 sub samples

### osc_collect_data.py arguments:

Default values of these arguments are the default values for the OpenBCI GUI running in a local machine
  
* `--ip`
  * The ip to be listened, default = `localhost`
* `--port`
  * The port to be listened, default = `12345`
* `--address`
  * Address to be listened, default = `/openbci`
