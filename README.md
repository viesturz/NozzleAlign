# NozzleAlign Probe
A stationary probe to align multiple tools. And Tap probe offset.
So far has been very reliable, <0.01 mm drift.

[Video](https://www.youtube.com/watch?v=_GQEc5kIMZE)
![Preview](/images/outsides.jpg)
![Preview](/images/insides.jpg)

## Commands

* TOOL_LOCATE_SENSOR - calibrate sensor location for tool 0
* TOOL_CALIBRATE_TOOL_OFFSET - measure tool offset versus calibrated, use for tools 1...n
* TOOL_CALIBRATE_PROBE_OFFSET - measure offset from nozzle touching the probe to tool's nozzle probe activating. For direct nozzle probes, like Tap.

## Config example

```
[probe_multi_axis]
pin: ^!PF5
speed: 2
lift_speed: 4

samples:3
sample_retract_dist:2
samples_tolerance:0.1
samples_tolerance_retries:2
samples_result:average

[tools_calibrate]
travel_speed: 20
spread: 7
lower_z: 0.7
```

## BOM
* MGN7h rail and carriage. Cut the rail down to 34mm.
* A piece of spring, 8-9mm dia
* A threaded steel ball with m3 thread, salvaged mine from a delta printer.  There is plenty on [AliExprees](https://www.aliexpress.com/w/wholesale-steel-ball--thread.html).
* 6x M2x8 bolts and nuts.
* 4x M2x12 self tapping screws to close it up.
* ~5mmx10mm self tapping countersunk screw for the base, I found a [Ikea drawer rail scew](https://www.google.com/search?q=ikea+drawer+rail+screw) in my randoms bin.

