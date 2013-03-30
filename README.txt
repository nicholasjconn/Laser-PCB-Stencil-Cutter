This repository is for the PCB laser stencil cutter project posted on Hardware Breakout.

http://hardwarebreakout.com/2013/03/diy-laser-cutter-for-pcb-stencils

The folder "NJC Laser Sprinter Firmware" is based off of the RAMPS sprinter firmware, built for the RepRap. The eagle_stencil.cam is the CAM process which creates gerber files for each stencil for a given board layout. The GerberToGCODE python file will convert a gerber file created in Eagle CAD to gcode readable by the RAMPS firmware. Finally, an example stencil is provided in the Stencils folder.

Feel free to modify all of these as needed, just please give credit where credit is due.

Nicholas J. Conn
Hardware Breakout
NJC@hardwarebreakout.com
http://hardwarebreakout.com