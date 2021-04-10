Content
-------

* Main page (this page)
* [Hardware description](hardware.html)
* [Auto mode interface](interface.html)
* [Auto mode code description](auto.html)
* [Tools description](tools.html)

Crappy Tribometer V0.1 Documentation
====================================

Welcome to the documentation of the LML braking tribometer.

The goal of this document is to provide user and developer level help for
this Python program, meant to drive the braking tribometer.
It was developed by Victor Couty on Sept/Oct 2017.
The code of this project is hosted on
[GitHub](https://github.com/LaboratoireMecaniqueLille/Tribo.git).

The goal of this project
------------------------
* Allow advanced tests, including any combination of these phases:
    * Breaking with inertia simulation
    * Breaking at a constant force
    * Breaking at a constant torque
    * Waiting for a condition to be reached (for ex Tdisc < 80°C)
    * Customizable acquisition of all the sensors

* Provide scripts for efficient preparation of the tests such as manually
  driving the actuators, measuring and plotting the disc displacement, etc...

The first one is accomplished by all the code in the auto/ folder and
the second by the code in tool/

This project is based on
[CRAPPY](https://github.com/LaboratoireMecaniqueLille/crappy.git),
another project developed by the LML.

Crappy is a Python module meant to run complex tests on a wide variety of
hardware. For more information, please refer to the page of the project or
[the documentation](https://crappy.readthedocs.io/en/latest/).

If you are reading this document to get familiar with this bench,
I strongly suggest reading the [hardware help page](hardware.html) while
analysing the bench in real time, then getting familiar with manual mode
with [tools help page](tools.html) and finally read the
[interface help page](interface.html) to learn how to use the auto program.

If you want to go deeper, you can consult the
[auto mode help page](auto.html) to have an explanation of the global
organization of the code. The next step is to look at the code itself,
it is organized and commented for an easier understanding.

Hardware overview
=================

The bench has 3 IO boards:

* The main Labjack (T7), mostly for command. Connected by USB
* The second Labjack (T7 pro), mostly for thermocouple acquisition,
  connected by Ethernet
* The Spectrum M2i-4711exp PCI card for high frequency acquisition.
  It can read up to 16 channels at 100 kHz

3 actuators:

* The main motor (11.5kW), driving the axle at up to 4000 rpm
* The pad motor, to load the spring in order to apply a chosen
  force on the pad
* The hydraulic bump, to allow a quick lift of the pad and allows to
  preload the spring before actually breaking

And many sensors:

* Torque-meter
* Speed (returned by the main motor converter)
* 3 Axis force on the pad
* Spring force
* 2 Thermocouples in the disc, up to 11 in the pad
* Position sensor for the disc and the pad

For more details on the hardware, please refer to the
[hardware help page](hardware.html)

Software overview
=================
The folder tools/ contains several scripts to perform several operations on
the bench: manually driving the bench, reading sensors independently,
flashing the Labjack, etc...

Each script is described in the [tools help page](tools.html)

The folder auto/ contains a single program, split over multiple files for
simplicity. This program opens a simple GUI to define a test, including
the description of the whole test, configuration of all the sensors and
the real-time graphs to display. It can be started by launching auto/main.py

For user documentation, see [interface help page](interface.html).
For more in depth description of the code, see
[auto mode help page](auto.html)
