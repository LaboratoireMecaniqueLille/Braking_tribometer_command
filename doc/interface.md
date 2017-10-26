Content
-------

* [Main page](help.html)
* [Hardware description](hardware.html)
* Auto mode interface (this page)
* [Auto mode code description](auto.html)
* [Tools description](tools.html)

Using the interface
===================
It is divided in 4 sections: Path, Labjack, Spectrum and Graph. There is a help
section on the bottom-left hand corner, and load/save buttons to manage
configurations.

When the user clicks "GO", this window disappears, only leaving a popup that
allows to interrupt the test and states the current step, and the graphs
asked in the "Graph" frame. It will create a folder named like so
"Day_Month_dd_hh:mm:ss" in the chosen folder (default is "Bureau/essais").
This folder will contain 4 files:

* config.p: The configuration of the test, to reload the program if necessary
* lj1.csv: The data read by the first Labjack
* lj2.csv: The data read by the second Labjack (if at least one channel is
  given)
* spectrum.hdf: The data read from the Spectrum (if at least one channel is
  given)

Path
----
This frame is to define the steps of the test. Each substep can be defined
by a function. They are shown on the list on the right of the frame. Clicking
a function will print the associated help on the help frame, double-clicking it
will automatically add it at the end of the list.

The text in this textbox will be parsed as so:

* Leading and trailing newline/spaces are removed
* Newlines are replaced by commas
* The text is surrounded by brackets [...]
* It is evaluated as Python expression and assigned to a variable
  * If the syntax was correct, this variable is a list
* The inner lists are "flattened" ie. each elements of a sublist are inserted
  as individual elements of the list.

The last step is meant to simplify looping over multiple steps. For exemple
you can write:

    [goto(1000),slow(800)]*2

It will be expanded as goto(500), slow(200), goto(500), slow(200)

Note that since newlines are replaced by commas, you can also write

    [goto(1000)
    slow(800)]*2

Here is an example of a correct code:

    goto(500)
    slow_p(-2000,10,200)
    goto(1000)
    cst_f(500,10)
    wait(10)
    [slow(800,inertia=8)
    wait_cd('T12<80']*3
    slow(1000)

Some args are facultative: For example slow(force,inertia=5,speed=0)
can be used with only the force slow(800). Inertia and final speed will
be the default values (5 and 0). You can also explicitly name the arguments:
slow(force=1000,speed=300). In that case, the order does not matter. You
must make sure to give all the arguments that do not have a default value.
When inserting a function by double-clicking, make sure to remove all
the chevron as they will raise a syntax error. They are just here to
illustrate the place of the arguments.

At the end of the path, will automatically be added an "end" step, which
pushes the hydraulic actuator out, stops the main motor and sets the pad
to its initial position.

The acquisition on specified channels (see Labjack and Spectrum section)
will automitaclly start at the beginning of the test, when clicking "GO" and
stop when the end of the path is reached. If you want to continue the
acquisition after the test, you can use wait(<delay>) or wait_cd("condition").

Spectrum
--------
This frame is meant to configure the channels to be acquired by the Spectrum
PCI card. To add a channel, simply type its label (or name), the index of
the channel (0-15) and click the right arrow. It will add an entry to the list.

You can delete a channel by selecting it (by clicking on it) and pressing
"Delete". To edit a channel, click the left arrow to remove it from the list
and fill the fields with the previous values. You can edit them and click
the right arrow to add it again.

The order of the channel has no impact, therefore there is no convenient
way to modify it once the chanels were created.

You can specify the range of the acquisition to configure the Spectrum channels.
This card supports (+/-50mV, 100mV, 250mV, 500mV, 1V, 2V, 5V and 10V).
The range is always symmetrical and must be given in mV. Not providing
the range or giving an invalid value will result in the default value: 10000.

You can also specify a gain to convert the channel readings in V to the
physical unit. This will NOT have any impact on the saved data itself, as
it is stored as int16. They will only be applied to real-time plots and
saved as a metadata in the hdf file. If it is not specified, it will be
set to 1. See below for more info on the hdf file and how to process it.

The Spectrum can only open 0,1,2,4 or 8 channels per module
(channels 0-7 and 8-15) and if both modules are used, they must have the same
number of open channels. The program takes care of opening "useless" channels
if necessary if the selected channels do not comply with these conditions.
This may make your HDF files heavier than expected.

Labjack
-------
This frame is used to configure the SECOND Labjack (the one linked by Ethernet)
and used for acquisition only. The main Labjack cannot be configured with the
GUI but by editing a file, see below for more information.

Just like the Spectrum frame, it is used to configure the channels of the
Labjack. The label is a name to identify the channel. You cannot use the same
name as a channel from the spectrum: each label must be unique.

The channel must be specified according to Labjack naming convention (Ex: AIN0)

Labjack ranges must be either 10 (default), 1, .1 or .01. It is the range in
Volt (Ex: 1 => +/- 1V)

Note that unlike the Spectrum channels, the gain WILL be applied to the
data. Additionally you can add an offset and/or substract the value read
when starting the test by ticking "make zero".

The data will be saved as lj2.csv and it will try to run at the specified
frequency. However, note that the frequency may vary as the acquisition
is run in "single" mode.



Graph
-----
TODO

Saving/Loading
--------------
TODO

The output data
---------------
* Structure of the HDF file
