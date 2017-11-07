Content
-------

* [Main page](help.html)
* [Hardware description](hardware.html)
* [Auto mode interface](interface.html)
* Auto mode code description (this page)
* [Tools description](tools.html)

Architecture of the code
========================

The code for the main interface is divided in several .py files.
It is launched by executing main.py ($ python main.py)

The two major files are main.py, which creates the GUI and launch.py
that creates the Crappy program once the GO button has been clicked.

Here is a step by step decription of what happens when launching the interface:

The code in main.py will create the main window, using all the code in
path_frame.py, spectrum_frame.py, lj_frame.py, graph_frame.py and load_frame.py
to create each frame of the window. When creating its frame, path_frame.py
will read all the available functions in funcs.py. Once the user presses "GO",
the configuration of each frame is read and saved into a list. This list is
given to launch from launch.py and it creates the Crappy program to start
the test. The launch function will not only use the configuration from the
GUI, but it will also use lj1_chan.py to configure the 1st Labjack (since it
cannot be configured from the GUI), pad_config.py, to create a "Drawing" block
if the user chose to display the pad temperatures and spectrum_tools.py,
which defines functions to work with the spectrum. Using all of these,
launch will create the Crappy program, and automatically launch it when ready.
The savers are added automatically and all the data will be saved in a
subfolder of the path specified in the GUI.

Description of each file
========================

This section will describe the role of each file. If this help does not answer
your question, you should probably look for yourself in the code. It is almost
completely commented and it was written to be as clear as possible.

main.py
-------
This is a fairly short file, since the creation of each frame is defined in
other files (xx_frame.py). It creates the root widget for the main window and
all the frames for the configuration of the test. The go button callback is
the go() function that simply reads the config of each frame, places it in
a list and closes the window. Once the window is closed, main.py ultimately
calls launch(), with the previous list as arguments, which performs the test.

xx_frame.py
-----------
These files define the classes that represent each section of the GUI.
(path, spectrum, labjack, graph and load/save). These widgets are children of
the tkinter Frame class. They all have a set_config() and a get_config()
method (except LoadFrame). They are used to get all the configuration made
by the user as a Python object. LoadFrame uses these methods to load and save
the configuration.

### path_frame.py
This frame has a textbox for the user to type the path. This text is
slightly parsed and interpreted as a Python expression. This must be
a list of dicts, but the code provides helper functions that return dicts
for simplicity. These functions are defined in funcs.py. They will be listed
and documented using Python introspection. Refer to the section describing
funcs.py for more info. The config is simply a string: the content of the
textbox. This file also provides a method to turn the text into a list
get_path(). This method adds commas instead of newlines, wraps the text with
brackets and eventually flattens the list (to allow for lists in lists).
This frame does not try to handle exceptions if the eval() fails, this is done
by go(), which prints errors in the help frame if any.

### pectrum_frame.py
This frame allows the user to configure the acquisition by the Spectrum
card. It has several fields to represent a channel: You can name channels
, set the range and eventually add a gain that will be saved as a metadata.
The configuration is a tuple: the first item is the frequency of the
acquisition(a float), the second is a list of dict, each dict
representing a channel. The keys are lbl, chan, range and gain.

### lj_frame.py
Just like the Spectrum frame, it allows the user to configure the second
Labjack. The config is represented the same way, but the channel dicts have
two more keys: offset and make_zero

### graph_frame.py
You can configure the graphs you want to display during the test here.
There is a list of graphs, each graph containing a list of labels. Launch
will automatically detect the parent blocks and link only the required sources.
Its configuration is a tuple: the first item is a bool. If true, the user wants
to open the Drawing block that shows the temperature of the pad. See
pad_config.py for the configuration of this block. The second item is a dict.
Its keys are the names of the graphs (generated automatically), the items are
lists of the labels to plot on this graph.

### load_frame.py
Unlike the previous frames, it does not have a get_config and set_config
methods, but it calls those of all the frames. It takes a list at init: the
list of the frames. Therefore this frame must be instanciated last.
When calling save, it will read the config of each frame with get_config-)
and save them as a list in a Pickle file. Load will read the pickle file
and call set_config on each frame to load the configuration.

funcs.py
--------
This file defines all the functions that will be available in path frame.
Each function actually needs two functions to be defined: as simple helper,
which will be exposed to the user. It must return a dict with at least a
'type' key.  Then there is a parser function that, given this dict will
actually extend the lists of the Generators to perform the said action.
They are associated through the 'avail' dict. All the functions in the list
named 'funcs' are the helpers and will be listed in the function list.
Their docstring will be displayed when clicked, the name will be the name of
the function and the prototype will be generated automatically so the name
of the arguments matters.
To add a function, add its helper in funcs.py, with a good help docstring,
an axplicit name and arguments. Add it to "__all__" at the top of the file
and "funcs" in the last section.
Create the actual function (make_xx), that extends all the generators with
the chosen commands. Finally, add them both to the 'avail' dict.

launch.py
---------
![diagram](../img/diagram_low.png)

This is the core of the program: this file defines a function 'launch' that
does all the work: it takes the configuration as arguments and then creates
a Crappy program based on these settings and the settings in lj1.chan.py and
pad_config.py.

This crappy program has a total of eight generators to drive the bench, but
two of them are not directly used, they automatically drive the
hydraulic actuator based on the command of a third generator (see the diagram
above). These generators command the first labjack (see lj1_chan.py), except
for padpos_gen, which talks to the servostar converter through a serial
connection. If at least one channel is specified on the spectrum,
it creates a spectrum block and a hdf_saver to save data from the spectrum.
It uses functions from spectrum_tools.py to open the correct number of channels
and plot data in real time (see spectrum_tools.py).
If a lj2 channel is open, it will create an other IOBlock for the second
Labjack and a saver to save the data as csv. It will then create all the
graphs, and link them to the correct parent blocks. Finally, if the user
asked for it, it will create a 'Drawing' block based on pad_config.py and
start the program.

lj1_chan.py
-----------
This file holds the cnofiguration for the main Labjack, which drives the
actuators. This file is extremely short and simple: identifier is a string
to identify the Labjack (here we used the serial number). in_chan and out_chan
are dicts that hold the input and output channels. Note that the inputs
channels are necessary as they are used to take decisions. Editing/removing
channels from this file will require to edit launch.py because the Crappy
program relies on these channels, but you can simply add other channels
by adding lines to this file.

The main Labjack runs an internal PI script written in LUA (see flash_lj.py in
[Tools description](tools.html)). It has 3 modes: disabled (0), force mode (1)
and torque mode (2). The mode can be changed by writing the 46002 register.
It must be kept to 0 when the PI is not running, to avoid diverging.
This script reads the setpoint from register 46000.
In mode 1 (force), the setpoint is in N. The actual value is read from AIN0,
taken from the force sensor inline with the spring. It is corrected with
a gain and offset to correspond to the actual value in N.
The output is TDAC0, which sets the speed of the motor of the pad (if
set in analog mode by a serial command).
In mode 2 (torque), the setpoint is in Nm and the actual value is
read from AIN2. The PI values differ between the
two modes, they can be set by editing the script.

spectrum_tools.py
-----------------
This file defines two objects for the spectrum:

The first is a condition that allows the data to be displayed in a Grapher
block. Because this card can read at up to 100kHz, the data is returned as
numpy arrays of int16. This condition takes the first value of each array
and applies the gain, so it can be plotted.

The second is a function that checks the user configuration. Due to hardware
restriction, the spectrum can only open 1,2,4 or 8 channels per module and
0 or the same number of channel on each modules.  This functions makes
sure these conditions are met and if not, it opens useless channels
to meet them. Also, the intervealing is alternating on each module
so it returns the channels in the order they will
be read so they correspond the the right column in the hdf file.

pad_config.py
-------------
This file sets the labels and their coordinates for the block that displays
the temperatures on the pad during the test. These labels must be read from
the second Labjack. If a label does not exist, it will be omitted.
