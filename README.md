# Neurosleeve
## Deep Learning For Hand Gesture Signal Classification
This is an implementation of a ConvNet to predict the position of the hand using four Double-Differential sEMG signals from the forearm.

<p align="center">
  <img width="800" height="500" src="images/Demo.gif">
</p>

### The repository includes:
* Source code of two ConvNets that work with spectrograms or the raw data from the four channels
* [Script](data/osc_collect_data.py) to collect data using a Ganglion Board from OpenBCI
* Dataset built from [josecyc](https://github.com/josecyc) and [DanielCordovaV](https://github.com/DanielCordovaV)
* Pre-trained weights for this dataset
* [Demo](demo/stream.py) that maps predictions from model to certain keys
* [Resources](resources) on which we based our project


## Training on Your Own Dataset

### Our data acquisition method:

To build our dataset we decided to have six hand positions(labels) as well as a neutral position:

<p align="center">
  <img width="60%" height="60%" src="images/Movements and labels.png">
</p>
<p align="center">
  <img width="30%" height="30%" src="images/Neutral position.png">
</p>

The method we used was placing four pairs of electrodes to measure the Double-Differential sEMG signal from the muscles we tried to target(Flexor Digitorum Profundus, Extensor DigitoriumCommunis , Extensor Capri Radialis Longus and Flexor Carpi Radialis), holding the same position for ten seconds at 200 Hz then splitting that into 40 sub samples.

<p align="center">
  <img width="30%" height="30%" src="images/Electrode position.png">
</p>

### Following our procedure:

* First download the OpenBCI GUI from this [site](https://openbci.com/index.php/downloads)
* Define a position for each label (you can change the quantity of labels and their names by modifying the LABELS variable inside the scrips)
* Run the [osc_collect_data.py](data/osc_collect_data.py) script and hold the position you define for each label ten seconds (You have five seconds after each label appears to adjust the position)
* Run the Jupyter Notebooks inside [models](models) directory
* Test your results using the [demo](demo/stream.py) script


## Requirements

Install required modules:
  * pip install -r requirements.txt
  
<hr>

## Special thanks to:

* [Taylor Yang](https://github.com/rdmcolorz) who provided the code for most of the streaming part of this project with his [openbci_stream](https://github.com/rdmcolorz/openbci_stream) repo
* 42 Silicon Valley, specifically to 42 Robotics for providing the enviroment in which this project was developed
