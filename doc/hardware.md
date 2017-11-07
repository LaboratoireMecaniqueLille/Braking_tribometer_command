Content
-------

* [Main page](help.html)
* Hardware description (this page)
* [Auto mode interface](interface.html)
* [Auto mode code description](auto.html)
* [Tools description](tools.html)

This page presents all the information about the hardware currently in use
for the bench.

TODO
====
* Add pictures !

![diagram](../img/diagram_low.png)

The main Labjack
================
Currently connected by USB, right under the desk.
It is mostly used for command (but can be used for acquisition)
It runs an internal LUA script for the PID of the pad (see the PID section)

Input channels:

|Channel    |Name       |Gain       |
|-----------|-----------|-----------|
|AIN0       |Force (N)  |2061.3     |
|AIN1       |speed (rpm)|413        |
|AIN2       |torque (Nm)|-50        |

Output channels:

|Channel    |Name            |Gain                   |
|-----------|----------------|-----------------------|
|DAC0       |Begin pulse     |5V                     |
|TDAC0      |speed (rpm)     |413                    |
|TDAC1      |pad bump speed  |- (driven by PID)      |
|FIO2       |Hydraulic valve1|3.3V (Digital output)  |
|FIO3       |Hydraulic valve2|3.3V (Digital output)  |

This Labjack cannot be configured through the GUI: its configuration is
in auto/lj1_chan.py (see Code doc below).
It is possible to add inputs by simply adding a few lines to this file.
Also, these channels can be saved and plotted.


The secondary Labjack
=====================
It is a Labjack T7-PRO, deported on the bench and read through an Ethernet link.
It is meant to read all the thermocouples, but can read any analog voltage
at max ~200Hz (input only).
All the inputs can be configured in the GUI, with custom channel, gain and
offset.

The program connects via the local network, ljm module can detect automatically
Labjack devices on the network. They are filtered by serial number, to make
sure we open the correct device. Note that to connect through Ethernet you must
make sure that the Labjack is on the same local network: enable DHCP if a DHCP
server is present, else configure its IP and subnet to match the one of the
host computer.

The spectrum PCI card
=====================
For high frequency acquisition, can read all 16
channels at up to 100kHz (input only)

This card is a M2i-4711exp from Spectrum instrumentation. Crappy wraps the
C library for a simple use with Python, allowing to stream data at nominal
frequency. It is possible to plot the data coming for this device during
the test, but not recommended as it may have an impact on performance.

The main motor
==============
This motor is driven by an analog voltage (coming from the first Labjack).
It can rotate at any speed between 10 and 4000 rpm). The gain for the command
is 412rpm/V. The converter also returns the actual speed of the axle, with
the same gain. It is driven in speed, so the converter has an internal corrector
regulating the current for the motor. This allows for a simple inertia
simulation by forcing the speed based on the readings of the torque-meter.
It is computed by the program so inertia simulation loops at around 300 Hz.

The pad motor
=============
It drives a screw/nut system that loads a spring to apply a given force
on the pad. This brushless motor is driven by the Kollmorgen conditioner.
It can be commanded by serial interface or, if explicitly enabled by a
special serial command, it can be driven in speed by an analog voltage.
This is used to control the force through a PID. Refer to the pad PID section
for more details

The hydraulic actuator
======================
It is used to block the pad in order to remove the spring quickly at the end
of the test, and preload the spring without touching the disc before the
breaking. It is driven by two servovalves: one to accumulate pressure and one
to actually drive the actuator.

To push the actuator out (blocking the pad):

* Open valve 1 and 2
* Wait .2 seconds
* Close valve 2

To pull it in (freeing the pad):

* Open valve 2 (1 is supposed already open)
* Wait .2 seconds
* close valve 1
* Wait .2 seconds
* close valve 2

Note: there are no sensors to check the state of the actuator, so it must
be initialized when starting the program.


Sensor list
===========
Torque meter
------------
Gain: -50 Nm/V

Located between the flywheel and the disc. It is conditioned by the
grey box on the left of the bench. The default offset may vary so
it is measured at initialisation of the bench and deduced to the readings.
THIS MEANS THAT THE AXLE MUST BE COMPLETELY FREE WHEN STARTING THE PROGRAM!

Spring force sensor
-------------------
Gain: 2061.3 N/V

Located between the spring and the pad. The converter is in the grey box
on the left of the bench.
Note that this force is not only applied to the pad, but also used to deform
the frame of the pad support, which require around 136 N, depending on the
settings of the bench. The offset is around 110 N.

3-axis force sensor
-------------------
Gain: 500N/V

The pad is mounted on this piezo-electric sensor. Due to high thermal
sensitivity, a water-cooled part is mounted between the pad and the sensor.
**Do not forget to open the water to prevent damaging the sensor!**
Each cell is read by an individual conditioner in the control room. The
zero can be made manually or through a serial command.


Speed
-----
Gain: 413 rpm/V

It is not really a sensor, it is the speed returned by the converter of the main
motor. It is used to make sure to reach the target speed before the breaking.

Position sensors
----------------
gain: 250 µm/V

One of them is mounted on the pad frame, the second is usually mounted
on a comparator arm in front of the disc. The conditioner is the
"Capacitec" black box on the left of the bench.
These capacitive sensors can measure the distance to the facing metallic
surface at up to 2.5mm. They have a very short response time and can
measure the disc profile at full speed. They resist heat up to 800°C but
are very sensitive to short circuits and must **not** touch any metallic surface
when powered. Make sure the gap is large enough to avoid contact during the
test and never manipulate this sensor without unplugging it.

Other sensors
-------------
Of course, any sensor can be added for specific tests. High frequency
acquisition can be done on the Spectrum with a BNC cable and a voltage
in a range between +/-50mV and +/- 10V.
