# Nozzle alignment module for 3d kinematic probes.
#
# This module has been adapted from code written by Kevin O'Connor <kevin@koconnor.net> and Martin Hierholzer <martin@hierholzer.info>
# Sourced from https://github.com/ben5459/Klipper_ToolChanger/blob/master/probe_multi_axis.py

import logging
direction_types = {'x+': [0, +1], 'x-': [0, -1], 'y+': [1, +1], 'y-': [1, -1],
                   'z+': [2, +1], 'z-': [2, -1]}

class ToolsCalibrate:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()
        self.gcode_move = self.printer.load_object(config, "gcode_move")
        self.probe = self.printer.lookup_object("probe")
        self.tool_probe_endstop = self.printer.lookup_object("tool_probe_endstop", default=None)
        self.probe_multi_axis = self.printer.lookup_object("probe_multi_axis", default=None)
        if not self.probe_multi_axis:
            # no probe multi axis, let's make one using our config then.
            self.probe_multi_axis = self.printer.load_object(config, "probe_multi_axis")
        self.travel_speed = config.getfloat('travel_speed', 10.0, above=0.)
        self.spread = config.getfloat('spread', 5.0)
        self.lower_z = config.getfloat('lower_z', 0.5)
        self.lift_z = config.getfloat('lift_z', 1.0)
        self.lift_speed = config.getfloat('lift_speed', self.probe_multi_axis.lift_speed)
        self.final_lift_z = config.getfloat('final_lift_z', 4.0)
        self.sensor_location = None
        self.last_result = [0.,0.,0.]

        # Register commands
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command('TOOL_LOCATE_SENSOR', self.cmd_TOOL_LOCATE_SENSOR,
                                    desc=self.cmd_TOOL_LOCATE_SENSOR_help)
        self.gcode.register_command('TOOL_CALIBRATE_TOOL_OFFSET', self.cmd_TOOL_CALIBRATE_TOOL_OFFSET,
                                    desc=self.cmd_TOOL_CALIBRATE_TOOL_OFFSET_help)
        self.gcode.register_command('TOOL_CALIBRATE_PROBE_OFFSET', self.cmd_TOOL_CALIBRATE_PROBE_OFFSET,
                                    desc=self.cmd_TOOL_CALIBRATE_PROBE_OFFSET_help)

    def probe_xy(self, toolhead, top_pos, direction, gcmd):
        offset = direction_types[direction]
        start_pos = list(top_pos)
        start_pos[offset[0]] -= offset[1] * self.spread
        toolhead.manual_move([None, None, top_pos[2]+self.lift_z], self.lift_speed)
        toolhead.manual_move([start_pos[0], start_pos[1], None], self.travel_speed)
        toolhead.manual_move([None, None, top_pos[2]-self.lower_z], self.lift_speed)
        return self.probe_multi_axis.run_probe(direction, gcmd)[offset[0]]

    def calibrate_xy(self, toolhead, top_pos, gcmd):
        left_x = self.probe_xy(toolhead, top_pos, 'x+', gcmd)
        right_x = self.probe_xy(toolhead, top_pos, 'x-', gcmd)
        near_y = self.probe_xy(toolhead, top_pos, 'y+', gcmd)
        far_y = self.probe_xy(toolhead, top_pos, 'y-', gcmd)
        return [(left_x + right_x) / 2., (near_y + far_y) / 2.]

    def locate_sensor(self, gcmd):
        toolhead = self.printer.lookup_object('toolhead')
        downPos = self.probe_multi_axis.run_probe("z-", gcmd)
        center_x, center_y = self.calibrate_xy(toolhead, downPos, gcmd)

        toolhead.manual_move([None, None, downPos[2]+self.lift_z], self.lift_speed)
        toolhead.manual_move([center_x, center_y, None], self.travel_speed)
        center_z = self.probe_multi_axis.run_probe("z-", gcmd, speed_ratio=0.5)[2]
        # Now redo X and Y, since we have a more accurate center.
        center_x, center_y = self.calibrate_xy(toolhead, [center_x, center_y, center_z], gcmd)

        # rest above center
        toolhead.manual_move([None, None, center_z+self.final_lift_z], self.lift_speed)
        toolhead.manual_move([center_x, center_y, None], self.travel_speed)
        return [center_x, center_y, center_z]

    cmd_TOOL_LOCATE_SENSOR_help = ("Locate the tool calibration sensor, "
                                  "use with tool 0.")
    def cmd_TOOL_LOCATE_SENSOR(self, gcmd):
        self.last_result = self.locate_sensor(gcmd)
        self.sensor_location = self.last_result
        self.gcode.respond_info("Sensor location at %.6f,%.6f,%.6f"
                                % (self.last_result[0], self.last_result[1], self.last_result[2]))

    cmd_TOOL_CALIBRATE_TOOL_OFFSET_help = "Calibrate current tool offset relative to tool 0"
    def cmd_TOOL_CALIBRATE_TOOL_OFFSET(self, gcmd):
        if not self.sensor_location:
            gcmd.error("No recorded sensor location, please run TOOL_LOCATE_SENSOR first")
            return
        tool_nr = gcmd.get_int("T", default=-1)
        detected_tool_nr = self.tool_probe_endstop.active_tool_number if self.tool_probe_endstop else -1
        if tool_nr == -1 and detected_tool_nr > -1:
            tool_nr = detected_tool_nr
        elif tool_nr > -1 and detected_tool_nr > -1 and tool_nr != detected_tool_nr:
            gcmd.error("Tool number specified differs from what is detected by tool_probe_endstop")
            return

        location = self.locate_sensor(gcmd)
        self.last_result=[location[i]-self.sensor_location[i] for i in range(3)]
        self.gcode.respond_info("Tool %d offset is %.6f,%.6f,%.6f"
                                % (tool_nr, self.last_result[0], self.last_result[1], self.last_result[2]))

    cmd_TOOL_CALIBRATE_PROBE_OFFSET_help = "Calibrate the tool probe offset to nozzle tip"
    def cmd_TOOL_CALIBRATE_PROBE_OFFSET(self, gcmd):
        toolhead = self.printer.lookup_object('toolhead')
        start_pos = toolhead.get_position()
        nozzle_z = self.probe_multi_axis.run_probe("z-", gcmd, speed_ratio=0.5)[2]
        # now move down with the tool probe
        probe_z = self.probe.run_probe(gcmd)[2]

        z_offset = probe_z - nozzle_z
        self.gcode.respond_info(
            "%s: z_offset: %.3f\n"
            "The SAVE_CONFIG command will update the printer config file\n"
            "with the above and restart the printer." % (self.probe.name, z_offset))
        configfile = self.printer.lookup_object('configfile')
        if self.tool_probe_endstop:
            configfile.set(self.tool_probe_endstop.active_probe.name, 'z_offset', "%.3f" % (z_offset,))
        else:
            configfile.set(self.probe.name, 'z_offset', "%.3f" % (z_offset,))
        # back to start pos
        toolhead.move(start_pos, self.travel_speed)

    def get_status(self, eventtime):
        return {'last_result': self.last_result,
                'last_x_result': self.last_result[0],
                'last_y_result': self.last_result[1],
                'last_z_result': self.last_result[2]}

def load_config(config):
    return ToolsCalibrate(config)
