#
# Most of this code was taken from the pygerber2gcode project
# on Google Code.
#
# http://code.google.com/p/pygerber2gcode/
# Don't forget to give credit where credit is due!
#
# Code modified: February 2013
# 

from string import *
from math import *
import datetime
import re

# File locations
GERBER_FILE = "TestStencil.gtc"
GCODE_FILE = "TestStencil.gcode"
#GERBER_FILE = "Stencils\\FTDI Breakout\\FTDI_top_stencil.gtc"
#GCODE_FILE = "Stencils\\FTDI Breakout\\FTDI_top_stencil.gcode"

# User set variables
CUT_SPEED = 20
MOVE_SPEED = 200
gXSHIFT = 0
gYSHIFT = 0

################################

#Global Constant
HUGE = 2000
INCH = 25.4 #mm
MIL = INCH/1000
ON = 1
OFF = 0

#For file
OUT_INCH_FLAG = 0
IN_INCH_FLAG = 1
CAD_UNIT = MIL/10
gUNIT = INCH

#Global variable
gXMIN = HUGE
gYMIN = HUGE
gGCODE_DATA = ""

gTMP_X = 0 
gTMP_Y = 0
gTMP_LASER = OFF
CURRENT_SPEED = 0

gGERBER_TMP_X = 0
gGERBER_TMP_Y = 0
gDCODE = [0]*100
g54_FLAG = 0
gFIG_NUM = 0
gPOLYGONS = []
gGCODES = []


#Set Class
class POLYGON:
	def __init__(self, x_min, x_max, y_min, y_max, points, delete):
		self.x_min = x_min
		self.x_max = x_max
		self.y_min = y_min
		self.y_max = y_max
		self.points = points
		self.delete = delete

class D_DATA:
	def __init__(self, atype, mod1, mod2):
		self.atype = atype
		self.mod1 = mod1
		self.mod2 = mod2

class GCODE:
	def __init__(self, x1, y1, x2, y2, gtype, mod1, mod2):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.gtype = gtype
		self.mod1 = mod1
		self.mod2 = mod2


def read_Gerber(filename):
	global IN_INCH_FLAG
	f = filename #pen(filename,'r')
	print "Parse Gerber data"
	while 1:
		gerber = f.readline()
		if not gerber:
			break
		if (find(gerber, "%MOIN") != -1):
			IN_INCH_FLAG = 1

		if (find(gerber, "%ADD") != -1):
			parse_add(gerber)
		if (find(gerber, "G") != -1):
			parse_g(gerber)
		if (find(gerber, "D") == 0):
			parse_d(gerber)
		if (find(gerber, "X") == 0):
			parse_xy(gerber)
	f.close()
	gerber2polygon4draw()
	
def parse_add(gerber):
	global gDCODE,D_DATA
	dn = re.search("ADD([\d]+)([a-zA-Z]+)\,([\d\.]+)[a-zA-Z]+([\d\.]+)\W*",gerber)
	dm = re.search("ADD([\d]+)([a-zA-Z]+)\,([\d\.]+)\W*",gerber)
	mod2 = 0
	if (dn):
		d_num = dn.group(1)
		aperture_type = dn.group(2)
		mod1 = dn.group(3)
		mod2 = dn.group(4)
		print "Type dn"
	elif (dm):
		d_num = dm.group(1)
		aperture_type = dm.group(2)
		mod1 = dm.group(3)
		print "Type dm"
	else:
		return

	gDCODE[int(d_num)] = D_DATA(aperture_type,mod1,mod2)
	
def parse_d(gerber):
	global g54_FLAG, gFIG_NUM
	index_d=find(gerber, "D")
	index_ast=find(gerber, "*")
	g54_FLAG = 1
	gFIG_NUM=gerber[index_d+1:index_ast]
	print "Figure: " + gFIG_NUM
def parse_g(gerber):
	global gTMP_X, gTMP_Y, gTMP_LASER, g54_FLAG, gFIG_NUM
	index_d=find(gerber, "D")
	index_ast=find(gerber, "*")
	if (find(gerber, "54",1,index_d) !=-1):
		g54_FLAG = 1
	else:
		g54_FLAG = 0

	gFIG_NUM=gerber[index_d+1:index_ast]

def parse_xy(gerber):
	global gTMP_X, gTMP_Y, gTMP_LASER, g54_FLAG, gFIG_NUM
	d=0
	xx = re.search("X([\d\.\-]+)\D",gerber)
	yy = re.search("Y([\d\-]+)\D",gerber)
	dd = re.search("D([\d]+)\D",gerber)
	if (xx):
		x = xx.group(1)
		if (x != gTMP_X):
			gTMP_X = x

	if (yy):
		y = yy.group(1)
		if (y != gTMP_Y):
			gTMP_Y = y
	if (dd):
		d = dd.group(1)

	if (g54_FLAG):
		parse_data(x,y,d)
		
def parse_data(x,y,d):
	global gDCODE, gFIG_NUM,INCH, CAD_UNIT, gGERBER_TMP_X, gGERBER_TMP_Y, gGCODES, gUNIT
	mod1 = float(gDCODE[int(gFIG_NUM)].mod1) * gUNIT
	mod2 = float(gDCODE[int(gFIG_NUM)].mod2) * gUNIT
	x = float(x) * CAD_UNIT
	y = float(y) * CAD_UNIT
	if(d == "03" or d == "3"):
		#Flash
		if( gDCODE[int(gFIG_NUM)].atype == "C"):
			#Circle
			gGCODES.append(GCODE(x,y,0,0,1,mod1,0))
		elif(gDCODE[int(gFIG_NUM)].atype ==  "R"):
			#Rect
			gGCODES.append(GCODE(x,y,0,0,2,mod1,mod2))
	elif(d == "02" or d == "2"):
		#move  w light off
		gGERBER_TMP_X = x
		gGERBER_TMP_Y = y
	elif(d == "01" or d == "1"):
		#move w Light on
		if(gDCODE[int(gFIG_NUM)].atype == "C"):
			gGCODES.append(GCODE(gGERBER_TMP_X,gGERBER_TMP_Y,x,y,3,mod1,mod2))
		elif(gDCODE[int(gFIG_NUM)].atype == "R"):
			#Rect
			gGCODES.append(GCODE(gGERBER_TMP_X,gGERBER_TMP_Y,x,y,4,mod1,mod2))
		gGERBER_TMP_X = x
		gGERBER_TMP_Y = y

def gerber2polygon4draw():
	global gGCODES
	for gcode in gGCODES:
		if(gcode.gtype == 5):
			continue
		#print gcode
		x1=gcode.x1
		y1=gcode.y1
		x2=gcode.x2
		y2=gcode.y2
		mod1=gcode.mod1
		mod2=gcode.mod2
		if(gcode.gtype == 1):
			polygon(circle_points(x1,y1,mod1/2,20))
		elif(gcode.gtype == 2):
			points = [x1-mod1/2,y1-mod2/2,x1-mod1/2,y1+mod2/2,x1+mod1/2,y1+mod2/2,x1+mod1/2,y1-mod2/2,x1-mod1/2,y1-mod2/2]
			polygon(points)
		elif(gcode.gtype == 3):
			line2poly(x1,y1,x2,y2,mod1/2,1,8)
		elif(gcode.gtype == 4):
			line2poly(x1,y1,x2,y2,mod2/2,0,8)

def arc_points(cx,cy,r,s_angle,e_angle,kaku):
	points=[]
	if(s_angle == e_angle):
		print "Start and End angle are same"
	int(kaku)
	if(kaku <= 2):
		print "Too small angle"
	ang_step=(e_angle-s_angle)/(kaku-1)
	i = 0
	while i < kaku:
		arc_x=cx+r*cos(s_angle+ang_step*float(i))
		arc_y=cy+r*sin(s_angle+ang_step*float(i))
		points.extend([arc_x,arc_y])
		i += 1

	return points

def line2poly(x1,y1,x2,y2,r,atype,ang_n):
	points = []
	deg90=pi/2.0
	dx = x2-x1
	dy = y2-y1
	ang=atan2(dy,dx)
	xa1=x1+r*cos(ang+deg90)
	ya1=y1+r*sin(ang+deg90)
	xa2=x1-r*cos(ang+deg90)
	ya2=y1-r*sin(ang+deg90)
	xb1=x2+r*cos(ang+deg90)
	yb1=y2+r*sin(ang+deg90)
	xb2=x2-r*cos(ang+deg90)
	yb2=y2-r*sin(ang+deg90)
	if(atype==1):
		points = points + arc_points(x1,y1,r,ang+3*deg90,ang+deg90,ang_n)
		points = points + arc_points(x2,y2,r,ang+deg90,ang-deg90,ang_n)
		points = points + [xa2,ya2]
	elif(atype==2):
		points = points + [xa2,ya2,xa1,ya1]
		points = points + arc_points(x2,y2,r,ang+deg90,ang-deg90,ang_n)
		points = points + [xa2,ya2]
	else:
		points=(xa1,ya1,xb1,yb1,xb2,yb2,xa2,ya2,xa1,ya1)
	polygon(points)

def polygon(points):
	global HUGE, gPOLYGONS, gXMIN, gYMIN
	x_max=-HUGE
	x_min=HUGE
	y_max=-HUGE
	y_min=HUGE
	if(len(points)<=2):
		print "Error: polygon point"
		return
	i = 0
	while i< len(points):
		if(points[i] > x_max):
			x_max=points[i]
		if(points[i] < x_min):
			x_min=points[i]
		if(points[i+1] > y_max):
			y_max=points[i+1]
		if(points[i+1] < y_min):
			y_min=points[i+1]
		i += 2

	gPOLYGONS.append(POLYGON(x_min,x_max,y_min,y_max,points,0))

	if(gXMIN>x_min):
		gXMIN = x_min
	if(gYMIN>y_min):
		gYMIN=y_min

def circle_points(cx,cy,r,points_num):
	points=[]
	if(points_num <= 2):
		print "Too small angle at Circle"
		return
	i = points_num
	while i > 0:
		cir_x=cx+r*cos(2.0*pi*float(i)/float(points_num))
		cir_x=cx+r*cos(2.0*pi*float(i)/float(points_num))
		cir_y=cy+r*sin(2.0*pi*float(i)/float(points_num))
		points.extend([cir_x,cir_y])
		i -= 1
	cir_x=cx+r*cos(0.0)
	cir_y=cy+r*sin(0.0)
	points.extend([cir_x,cir_y])
	return points

def polygon2gcode(move_speed, cut_speed):
	global gPOLYGONS
	print "Converting to G-code..."
	for poly in gPOLYGONS:
		if (poly.delete):
			continue
		path(move_speed, cut_speed,poly.points)

def path(move_speed, cut_speed,points):
	global gGCODE_DATA, gXSHIFT, gYSHIFT, gTMP_X, gTMP_Y, gTMP_LASER, CURRENT_SPEED
	if(len(points) % 2):
		print "Number of points is illegal "
		
	if (CURRENT_SPEED != MOVE_SPEED):
		CURRENT_SPEED = move_speed
		gGCODE_DATA +="G0 F" + str(CURRENT_SPEED) + "\n"
		
	#move to Start position
	move("G0", points[0]+float(gXSHIFT),points[1]+float(gYSHIFT), CURRENT_SPEED)
	
	#move to cuting heght
	if(gTMP_LASER != ON):
		gTMP_LASER=ON
		gGCODE_DATA += "M52" + "\n"
		CURRENT_SPEED = cut_speed
		gGCODE_DATA +="G1 F" + str(CURRENT_SPEED) + "\n"
		
	i = 0
	while i< len(points):
		px=points[i]+gXSHIFT
		py=points[i+1]+gYSHIFT		
		move("G1", px,py, CURRENT_SPEED)		
		i += 2
		
	if(gTMP_LASER!=OFF):
		gTMP_LASER = OFF
		gGCODE_DATA += "M53" + "\n"
		gGCODE_DATA += "\n"
		CURRENT_SPEED = move_speed
		gGCODE_DATA +="G0 F" + str(CURRENT_SPEED) + "\n"
	

def move(cmd, x,y, speed):
	global gGCODE_DATA, gTMP_X, gTMP_Y, gTMP_LASER
	out_data = cmd
	gcode_tmp_flag = 0
	gTMP_X = x
	#out_data += " X" + str(x)
	out_data += " X" + ("%.3f" % x)
	gTMP_Y = y
	#out_data +=" Y" + str(y)
	out_data +=" Y" + ("%.3f" % y)
	gGCODE_DATA += out_data + "\n"
		
def get_date():
	d = datetime.datetime.today()
	return d.strftime("%Y-%m-%d %H:%M:%S")
		
def gcode_init():
	global gGCODE_DATA, OUT_INCH_FLAG, MCODE_FLAG
	gGCODE_DATA += "\n;( Generated on: " + get_date() +" )\n"
	gGCODE_DATA += ";(Initialize)\n"
	gGCODE_DATA += "G90 ; use absolute coordinates\n"
	
	if OUT_INCH_FLAG:
		gGCODE_DATA += "G20 ; set units to inches\n"
	else:
		gGCODE_DATA += "G21 ; set units to millimeters\n"

	gGCODE_DATA += "G28 ; home all axes\n"
	
	gGCODE_DATA += "\n\n" + ";(Start here)\n\n"

def gcode_end():
	global gGCODE_DATA, MCODE_FLAG
	end_data = ""
	
	end_data += "\n;( End Code )\n"
	end_data += "M53 ; turn off laser\n"

	end_data += "G28 ; home all axes\n"
	end_data += "M84 ; disable motors\n"
	
	gGCODE_DATA += end_data
	
	
def end(out_file_name):
	global gGCODE_DATA, CUT_SPEED
	
	gcode_init()
	polygon2gcode(MOVE_SPEED, CUT_SPEED)
	gcode_end()
	#File open
	out = open(out_file_name, 'w')
	out.write(gGCODE_DATA)
	out.close()

	
import Tkinter,tkFileDialog

root = Tkinter.Tk()
GERBER_FILE = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a file')

#GERBER_FILE = open(GERBER_FILE,'r')

if GERBER_FILE != None:
	read_Gerber(GERBER_FILE)


myFormats = [
    ('G-Code','*.gcode'),
    ]
GCODE_FILE = tkFileDialog.asksaveasfilename(parent=root,filetypes=myFormats ,title="Save the image as...")
	

if(len(gPOLYGONS) > 0):
	end(GCODE_FILE)
else:
	print "No Polygons Found!"

		