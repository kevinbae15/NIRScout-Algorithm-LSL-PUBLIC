# NIRScout-Algorithm-LSL-

This algorithm utilizes the NIRX Lab Streaming Layer (LSL), particularly pylsl, provided publicly by Christian Kothe in his github repository [pylsl](https://github.com/chkothe/pylsl).

More information can be found in [DESCRIPTION.rst](https://github.com/kevinbae15/NIRScout-Algorithm-LSL-/blob/master/DESCRIPTION.rst).

## Background Information

We were planning on conducting a study that involved simulating driving and reading text on a tablet at the same time.
After a couple of dummy tests and configuration sessions, the participant would be put into a difficult situation that requires driving and reading text at the same time.
When this algorithm detects that the user is having difficulty, the text on the tablet would automatically space out, enlarge the font, etc. 
Basically, it would do its best to make the text easier to read and make the whole experience a little bit more manageable for the participant. 

## The Purpose of This Algorithm

This algorithm was written for a research study.
It is designed to recognize an increase in oxygenated hemoglobin in real time with a participant during a driving simulation without the use of machine learning.
The study relies on a NIRScout, a functional Near Infrared Spectroscopy machine (fNIRS) made by NIRX, and concentrates on only one part of brain: Bowman's Area 46. 
With the help of the LSL, this algorithm will detect a rise in oxygenated blood in the area of the brain and halt the program after posting to a server that will handle making the text easier to read.

## The Concept Behind the Algorithm

First of all, there needs to be bandpass filter in order to retrieve good data from the NIRScout. Unfortunately, NIRStar (the software used in conjunction with the NIRScout) only has low-pass filter.
Therefore, there is a makeshift filter in the algorithm that utilizes a mean summation concept.
After a couple of readings, it will take the highest and lowest number in the array of readings and then create a single slope value out of it.
During the configuration process, it will take the highest slope value and use it as the threshold slope value.
In the experimental process, it will compare the current slope to the threshold slope value. 

## How to Use

* Before attempting to run this program, make sure that pylsl has been properly downloaded with its dependencies installed.
* Next, make sure that your NIRStar software is at least version 15.0 and LSL capabilities are turned on.
* When ready to begin, make sure you configure the hardware properly so that it only reads through one detector and probe pair.
* Calibrate the sensor and detectors.
* Make sure to start recording.
* Open up a LINUX terminal; now you have three options:

```
python ReceiveData.py [-p] 
python ReceiveData.py [-c config_files] 
python ReceiveData.py [-e config_files]
```
* -p option is for testing purposes and prints out current hbO values
* -c option is for configuration. It will run the algorithm and write the max slope value in the file provided
* -e option is for the actual experimental testing. The file provided should be a text file with the max slope values

## Important Notes

* Make sure there are "dummy runs" so that when it is actually time to run the configuration and experiment, the participant is not as nervous, which can affect affect the data.
* It is also recommended that you do not run anything until a couple of seconds after recording for two reasons:
  * It takes a while for signals to show up because of the lowpass filter,
  * Wait for the signals to stabilize a little bit first;
  * At least 1 minute of running the FNIRS is recommended.
* Make sure that lowpass filter provided by NIRStar is at value 0.1.
* It is recommended that you do a couple of calibration sessions before experimenting to minimize the possibility of any special cases:
  * We usually do around 4 to 6 calibration sessions.
* This algorithm is specifically meant for Bowman's Area 46.

 
