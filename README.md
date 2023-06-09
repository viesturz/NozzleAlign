# NozzleAlign Probe
A stationary probe to align multiple tools. And Tap probe offset.
So far has been very reliable, repeatable to ~0.01 mm.

[Video](https://www.youtube.com/watch?v=_GQEc5kIMZE)
![Preview](/images/outsides.jpg)

## Commands

* TOOL_LOCATE_SENSOR - calibrate sensor location for tool 0
* TOOL_CALIBRATE_TOOL_OFFSET - measure tool offset versus calibrated, use for tools 1...n
* TOOL_CALIBRATE_PROBE_OFFSET - measure offset from nozzle touching the probe to tool's nozzle probe activating. For direct nozzle probes, like Tap.

## Config example

See [macros](/macros/calibrate-offsets.cfg)

## BOM
* MGN7h rail and carriage. Cut the rail down to 34mm.
* A threaded steel ball with m3 thread, salvaged mine from a delta printer.  There is plenty on [AliExprees](https://www.aliexpress.com/w/wholesale-steel-ball--thread.html).
* a D2F microswitch - same as Voron 0 BOM.
* 6x M2x8 bolts and nuts.
* 4x M2x12 self tapping screws to close it up.
* ~5mmx10mm self tapping countersunk screw for the base, I found a [Ikea drawer rail scew](https://www.google.com/search?q=ikea+drawer+rail+screw) in my randoms bin.
* 2x M2 heat set inserts, or mod for nuts

## Assembly

![Preview](/images/insides.jpg)

