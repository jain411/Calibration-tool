import serial, time, sys, os, struct, cPickle

__DEV_ID__ = 'nrv'
__MODEL_NAME__ = 'nanoREV'
__MODE__ = 'STM'		#AFM,MFM,NSOM ..
__HW_VERSION__ = '7.2.1'
__SW_VERSION__ = '7'
__INSTRUMENT__ = __MODEL_NAME__ + ' ' + __MODE__ + ' ' + __HW_VERSION__ 
__SOFTWARE__ = 'SiM' + __SW_VERSION__
__COMPANY__ = 'Quazar Technologies, New Delhi, India'

BUFSIZE = 3500

# commands without any arguments (1 to 20)
GETVERSION		= 1	# Get the nanoREV firmware version
READ_SPI_ADC		= 4	# Read SPI ADC on the Lockin ADDON card
ENABLE_BIAS_MODULATION 	= 5 	# Modulation Input added to Bias final adder
DISABLE_BIAS_MODULATION = 6 	# Bias Modulation Input to adder grounded
ENABLE_Z_MODULATION 	= 7 	# Modulation Input added to Z HVA
DISABLE_Z_MODULATION 	= 8 	# Z Modulation Input to adder grounded
SINGLE_STEP     	= 9    	# Move walker by One step
FINE_SLOPE_ADJ          = 10    # Fine Slope Adjestment
COARSE_SLOPE_ADJ        = 11    # Coarse Slope Adjestment
SELECT_SA_SCANNER       = 12    # Small Area Scanner Select
SELECT_LA_SCANNER       = 13    # Large Area Scanner Select
SELECT_LV_BIAS          = 14    # Select Low Voltage Bias
SELECT_HV_BIAS          = 15    # Select High Voltage Bias

# Commands with One byte argument (21 to 40) 
READ_ADC	= 21		# ADC Channel
SETGAIN		= 22		# PGA Gain Value 0 to 7
SWSET1		= 23		# controlling BITs of Switch1 reg.
SWCLR1		= 24		# controlling BITs of Switch1 reg.
SWSET2		= 26		# controlling BITs of Switch2 reg.
SWCLR2		= 27		# controlling BITs of Switch2 reg.
SWSET3		= 28		# controlling BITs of Switch2 reg.
SWCLR3		= 29		# controlling BITs of Switch2 reg.
SET_AIN1_GAIN	= 30		# analog Input Channel 0 PGA Gain Value 0 to 3
SET_AIN2_GAIN	= 31		# analog Input Channel 1 PGA Gain Value 0 to 3
SELECT_PID_IN	= 32		# AINx channel to PID input

# Commands with Two bytes argument (41 to 60)
SET_SPI_DAC	= 44	# Set SPI DAC on the Lockin ADDON card

# Commands with Three bytes argument (61 to 80)
SETDAC		= 61	# DAC Channel(0-8), HByte, LByte(0-4096)
SETPOT		= 62	# Pot Channel(0-3), HByte, LByte(0-4096)

# Commands with Four bytes argument (81 to 100)
LITHO_PULSE_MS	= 82	# Bias HByte, LByte, 2 bytes delay in ms
LITHO_PULSE_US	= 83	# Bias HByte, LByte, 2 bytes delay in us
SIMUL_READBLOCK_FAST 	= 84	# np_h, np_l (no. of points), delay_l, channel
SIMUL_READBLOCK_SLOW	= 85	# np_h, np_l (no. of points), delay_l, channel

# Commands with Five bytes argument (101 to 120)

# Commands with Six bytes argument (121 to 140)
LITHO_PULSE_TRAIN_MS	= 121	# Bias HByte, LByte, 2 bytes delay in ms, no. of pulses 
LITHO_PULSE_TRAIN_US	= 122	# Bias HByte, LByte, 2 bytes delay in us, no. of pulses 

# Commands with Seven bytes argument (141 to 160)
FILTERSCAN_SINGLE	= 142           # np_h, np_l, start_h, start_l step, delay, dac_choice

# Commands with Eight bytes argument (161 to 180)
IVSPECTRA		= 161	# np_h, np_l, start_h, start_l, step_h, delay_h, delay_l, mavg
HIRES_SCAN		= 162   # np_h, np_l, start_h, start_l, step, delay, dac_choice, dir
SIMUL_SCAN_DUAL_TRACE	= 163   # For normal single channel scan with simultanoeus ADC... np_h, np_l, start_h, start_l, step, delay, dac_choice, channels

# Commands with nine bytes argument (181 to 200)
SIMUL_SCAN_SINGLE_TRACE_SLOW	= 182   # For MulltiChannel LDOS/LBH Scanning...  np_h, np_l, start_h, start_l, step, delay_code, dac_choice, scan/ret dir, no. of channels
SIMUL_SCAN_SINGLE_TRACE_FAST	= 183   # For HiRes Scanning... np_h, np_l, start_h, start_l, step, delay_code, dac_choice, scan/ret dir, no. of channels

# Commands with ten bytes argument (201 to 220)
SIMUL_IVSPECTRA		= 201	# For spectra with LIA channels... np_h, np_l, start_h, start_l, step_h, step_l, delay_h, delay_l, mavg, ch
SIMUL_IVSPECTRA_RETRACE	= 202	# For spectra with LIA channels... np_h, np_l, start_h, start_l, step_h, step_l, delay_h, delay_l, mavg, ch

#Delay Constants

''' STM REGISTER SWITCH 1 NIBBLE 1 '''
REG_AIN1_G0 = 1		# Gain for Analog Input Channel 1 (normally TC Input) i.e. 1, 10, 100, 1000
REG_AIN1_G1 = 2		
REG_AIN2_G0 = 4		# Gain for Analog Input Channel 2 (QTF Amplitude / BEEM ...) 1, 10, 100, 1000
REG_AIN2_G1 = 8		

''' STM REGISTER SWITCH 1 NIBBLE 2 '''
REG_HI_BIAS 	= 16	# Bias selection between LVA/HVA output
REG_XLA		= 32	# Select between XLA/LA
REG_WPULSE	= 64	# Walker Pulse
REG_WDIR	= 128	# Walker direction

''' STM REGISTER SWITCH 2 NIBBLE 1 '''
REG_HOLD	= 1	# Feedback On/Off for CH and CC modes
REG_RESET	= 2	# Feedback Reset On/Off while auto-walking 
REG_SHR_LED 	= 4	# Shroud LED  on/off
REG_SEL_PIDIN 	= 8	# Slects whether AIN1 or AIN2 goes to feedback control section

''' STM REGISTER SWITCH 2 NIBBLE 2 '''
REG_ADCIN_G0	= 16	# Gain selection before ADC Input (goof-up on PCB 1000, 100, 10, 1)
REG_ADCIN_G1	= 32	
REG_TCZ		= 64	# Select TC/Z mode
REG_SEL_GAINPOT = 128	# Feedback's Proportional Gain Pot Enable/Disable

''' STM REGISTER SWITCH 3 NIBBLE 1 '''
REG_SEL_TIMEPOT = 1	# Feedback's Integerator time Constant Pot Enable/Disable
REG_SEL_XSLOPE 	= 2	# X-slope Pot Enable/Disable
REG_SEL_YSLOPE 	= 4	# Y-slope Pot Enable/Disable
REG_SCANNER_SEL	= 8	# Select between Tube Scanner or Bimorph Scanner  


''' STM DACS '''
DACS16BIT = range(4)
DACS12BIT = range(4,8)
OXDAC   = 4		# +X OffSet, +/- 10V	
XDAC	= 0		# +X, +/- 1V	
OYDAC	= 5		# +Y OffSet, +/- 10V	
YDAC	= 1		# +Y, +/- 1V	
OZDAC	= 2		# Z Offset, +/- 10V
BIASDAC = 3		# Bias +/- 10V
TC_SETP_DAC = 6		# TC Setpoint DAC +/- 10V -> +/-10nA

MAX_BIAS 	= 100.0		# V
MIN_BIAS 	= -100.0	# V
MAX_TC 		= 10000		# pA
MIN_TC 		= -10000	# pA
BIAS_GAIN	= 10

#-----------------------------------------------------------------------
# These variables can be changed from the gui
TIP_VELOCITY = 2.5		#V/s
#-----------------------------------------------------------------------

madc = 20000.0 / 65535		        # 16 bit ADC from -10V to 10V
cadc = -10000.0
mdac = [20000.0 / 65535] * 4 +  [20000.0 / 4095] * 4	# 0-3:12 bit, 4-7: 16bit, -10V to 10V
cdac = [-10000.0] * 8
OFFSET_DAC_RESOLUTION = 20000.0 / 4095
ZDAC_RESOLUTION = 20000.0 / 65535
BIAS_DAC_RESOLUTION = ZDAC_RESOLUTION
ADC_GAIN = [1, 2, 5, 10] #
AIN1_GAIN = [1, 10, 100, 1000] #
AIN2_GAIN = [1, 10, 100, 1000] #

""" Digitial Potentiometer Settings """
GAIN_POT, TIMEK_POT, XSLOPE_POT, YSLOPE_POT = range(4)
POTS = [GAIN_POT, TIMEK_POT, XSLOPE_POT, YSLOPE_POT]
POT_LABELS = ['GAIN_POT', 'TIMEK_POT', 'XSLOPE_POT', 'YSLOPE_POT']
POT_VALUES = (100e3, 100e3, 100e3, 100e3)
POT_RESOLUTION = 1024 - 1
mpot = [(x / POT_RESOLUTION) for x in POT_VALUES]

# Scan step delays : Fast Scan Modes (delays are in us) for CC & CH particularly
LEAST_DELAY = 150
MIN_DELAY = 200
MAX_DELAY = 1500					
DELAY_STEP = 100						

# extended delay List
EXT_MIN_DELAY = 2000
EXT_MAX_DELAY = 10000					
EXT_DELAY_STEP = 500
ext_step_delay_list = range (EXT_MIN_DELAY, EXT_MAX_DELAY + EXT_DELAY_STEP, EXT_DELAY_STEP)	

step_delay_list = [LEAST_DELAY] + range (MIN_DELAY, MAX_DELAY + DELAY_STEP, DELAY_STEP)	

step_delay_list += ext_step_delay_list 

# Scan step delays : Slow Scan Modes (delays are in us) for LIA involved modes
MIN_STEPDELAY_LIA = 1		# in msec 
MAX_STEPDELAY_LIA = 32		# in msec
DELAY_STEP_LIA = 1		# in msec
lia_step_delay_list = range(MIN_STEPDELAY_LIA, MAX_STEPDELAY_LIA + DELAY_STEP_LIA, DELAY_STEP_LIA)

SIMUL_ADC_CHANNELS = 4	# No. of channel simultaneously sampled
ADC_CHANNEL_TCZ = 0
ADC_CHANNEL_IN_PHASE = 1
ADC_CHANNEL_QUAD_PHASE = 2

""" Acknowledgement Types from MCU """
VALID_CMD = 'D'     # Done

offsetlogpath = os.path.join(os.curdir, 'log')		# default directory for log files

# for standalone testing of stm.py 
INSTALL_PATH = '/usr/local/stm/SiM721'
if os.path.exists(offsetlogpath) == False:
    if os.path.exists(INSTALL_PATH) == False:
        print 'Log directory not found'           
    else:
        offsetlogpath = os.path.join(INSTALL_PATH, 'log')

globlogfile = os.path.join(offsetlogpath, 'glob.dat')
xfilename = os.path.join(offsetlogpath, 'xlog.dat')	# Logfile containing Xoffet value
yfilename = os.path.join(offsetlogpath, 'ylog.dat')	# Logfile containing Yoffset value
zfilename = os.path.join(offsetlogpath, 'zlog.dat')	# Logfile containing Zoffset value
biaslogfile = os.path.join(offsetlogpath, 'biaslog.dat')	# Logfile containing Bias value
tclogfile = os.path.join(offsetlogpath, 'tcsetpoint.dat')	# Tunneling Current Setpoint saved
potlogfile = os.path.join(offsetlogpath, 'pots.dat')	# Pot values saved


#Serial devices to search for STM hardware.  
device_list = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',\
		'/dev/tts/USB0','/dev/tts/USB1',\
		'COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9','COM10','COM11','COM12',1,2,3]

def readLogOffsetX():
    try:
        xlog = open(xfilename,'r')
    except:
        prev_offsetx_value = 0
        xlog = open(xfilename,'w')
        xlog.write(str(prev_offsetx_value))
        xlog.close()
	return prev_offsetx_value
 
    xlog = open(xfilename,'r')
    prev_offsetx_value = xlog.read()
    xlog.close()
    if prev_offsetx_value == '':
	prev_offsetx_value = 0
	xlog = open(xfilename,'w')
	xlog.write(str(prev_offsetx_value))
	xlog.close()
    return round(float(prev_offsetx_value), 1) 

def readLogOffsetY():
    try:
        ylog = open(yfilename,'r')
    except:
        prev_offsety_value = 0
        ylog = open(yfilename,'w')
        ylog.write(str(prev_offsety_value))
        ylog.close()
	return prev_offsety_value
 
    ylog = open(yfilename,'r')
    prev_offsety_value = ylog.read()
    ylog.close()
    if prev_offsety_value == '':
	prev_offsety_value = 0
	ylog = open(yfilename,'w')
	ylog.write(str(prev_offsety_value))
	ylog.close()
    return round(float(prev_offsety_value), 1) 

def readLogOffsetZ():
    try:
        zlog = open(zfilename,'r')
    except:
        prev_offsetz_value = 0
        zlog = open(zfilename,'w')
        zlog.write(str(prev_offsetz_value))
        zlog.close()
	return prev_offsetz_value
 
    zlog = open(zfilename,'r')
    prev_offsetz_value = zlog.read()
    zlog.close()
    if prev_offsetz_value == '':
	prev_offsetz_value = 0
	zlog = open(zfilename,'w')
	zlog.write(str(prev_offsetz_value))
	zlog.close()
    return round(float(prev_offsetz_value), 1) 

def saveLogOffsetX(mv):
    xlog = open(xfilename,'w')
    xlog.write(str(round(mv,1)))
    xlog.close()
    return

def saveLogOffsetY(mv):
    ylog = open(yfilename,'w')
    ylog.write(str(round(mv,1)))
    ylog.close()
    return

def saveLogOffsetZ(mv):
    zlog = open(zfilename,'w')
    zlog.write(str(round(mv,1)))
    zlog.close()
    return

def readCurrentSetpoint():
    """
    Returns the Current Setpoint as set on the front panel pot.
    """
    try:
	tclog = open(tclogfile)
	nCurrentSetpoint = cPickle.load(tclog)
	tclog.close()
    except:
	print 'Could not open TC setpoint log file... setting default TC setpoint 200pA'
	nCurrentSetpoint = 200		# Default value = 200 pA
    return nCurrentSetpoint

def saveSetpointTC(nCurrentSetpoint):
    """
    Writes Tunnel Current Setpoint info to a file
    """
    try:
	tclog = open(tclogfile,'w')
	cPickle.dump(nCurrentSetpoint, tclog)
	tclog.close()
    except:
	print 'Failed to save TC setpoint log...plz check permisions'

    return

def saveSampleBias(bias):
    """
    """
    try:
	biaslog = open(biaslogfile,'w')
	cPickle.dump(bias, biaslog)
	biaslog.close()
    except:
	print 'Failed to save sample bias log...plz check permissions'


def getCurrentSampleBias():
    """
    """
    try:
	biaslog = open(biaslogfile)
	bias = cPickle.load(biaslog)
    	biaslog.close()
    except:
	print 'Could not open bias log file... setting default bias -0.2V'
	bias = -0.2	#V
	saveSampleBias(bias)
    return bias	


def lGetDeviceList():
    f = open(globlogfile)
    dicGlobalParam = cPickle.load(f)
    f.close()
    return dicGlobalParam['DeviceList']


def savePotLog(values):
	f = open(potlogfile, 'w')
	cPickle.dump(values, f)
	f.close()
 	return


def readPotLog():
	try:
		f = open(potlogfile)
		values = cPickle.load(f)
		f.close()
	except:
		print 'Previous Pot Values not found'
		values = [0] * len(POT_VALUES)
		values[GAIN_POT] = 4e3		# 2:0 in 20k
		values[TIMEK_POT] = 70e3	# 7:0 in 100k
		values[XSLOPE_POT] = POT_VALUES[XSLOPE_POT] / 2 # Mid 
		values[YSLOPE_POT] = POT_VALUES[YSLOPE_POT] / 2 # Mid
		savePotLog(values)
 	return values


def stm(dev = None):
	'''
	Check if nanoREV hardware is connected. But creates the application
	window for offline analysis
	'''
	oSTM = Stm(dev)
	if oSTM.fd != None:
		#obj.disable_actions()
		return oSTM
	print 'Could not find nanoREV hardware'
	print 'Check the connections.'
	return oSTM  # None

BAUDRATE = 230400   # Serial communication

class Stm:
    fd = None

    def __init__(self, new_port = None):
        """
        Searches for nanoREV hardware on RS232 ports and the USB-to-Serial adapters. Presence of the
        device is done by reading the version string.
        The timeout at Python end is set to 3.2 milliseconds, twice the minimum 555 output time period.
        TODO : Supporting more than one EYES on a PC to be done. The question is how to find out 
        whether a port is already open or not, without doing any transactions to it.
        """
	self.potValues = readPotLog()
	self.vDetectSTM(new_port)
        return

    def vDetectSTM(self, new_port = None):
        device_list = lGetDeviceList()
        if new_port != None:
            device_list.append(new_port)
        for dev in device_list:
            try:
                handle = serial.Serial(dev, BAUDRATE, stopbits=1, timeout = 1, parity=serial.PARITY_EVEN)
            except:
                continue
            print 'Port %s is existing '%dev,
            if handle.isOpen() != True:
                print 'but could not open'				
                continue
            print 'and opened. ',
            handle.flush()
            handle.flushInput()
	    ver = self.strGetVersionString(handle)
            if ver[:3] != __DEV_ID__:
	        self.bPersistCheck(handle)
	    ver = self.strGetVersionString(handle)
            if ver[:3] == __DEV_ID__:
                    self.device = dev
                    self.fd = handle
                    self.version = ver
                    handle.timeout = 16.0	# MAX LIA scan step delay = 30ms * 2 * 256 
                    print 'Found nanoREV version ', ver
                    break
            else:
                    print 'No nanoREV hardware detected'
		    handle.close()
                    self.fd = None
        if self.fd != None:
            self.vReadPrevDACValues()
            self.reset_off()
	    print 'Initiliazing PI and Slope values...'
	    for pot in POTS:
		self.set_pot(pot, self.potValues[pot])
	    self.set_ain1_gain(1)
	    self.set_ain2_gain(1)
	    self.fine_slope_adj()
 
        return

    def strGetVersionString(self, handle):
	handle.write(chr(GETVERSION))
	res = handle.read(1)
	ver = handle.read(5)		# 3 characters device descriptor
	return ver

    def bPersistCheck(self, handle):
	RETRY_COUNT = 3
	res = ''
	rcount = 0
	while res != 'D' and rcount < RETRY_COUNT:
	    print 'Retrying...'
	    ver = self.strGetVersionString(handle)
	    rcount +=1
	    if ver[:3] == 'nrv':
        	handle.flush()
		print '...OK'
		return True
	print '...Failed'
	return False

    def bValidDevice(self):
	if self.fd != None:
	    return True
	else:
	    print 'nanoREV device not detected...'
	    return False
	return

    def vReadPrevDACValues(self):
	prev_offsetx_value = readLogOffsetX()
	print 'X-Offset Log:', prev_offsetx_value
	prev_offsety_value = readLogOffsetY()
	print 'Y-Offset Log:', prev_offsety_value
	prev_offsetz_value = readLogOffsetZ()
	print 'Z-Offset Log:', prev_offsetz_value
        return

    ############# CALLS TO FIRMWARE FUNCTIONS ############
    
    def set_dac(self, dac, val):
        """
        Sets the DAC of channel 'dac' to value 'val' (for 12-bit dac: 0-4095, for 16-bit DAC: 0-65535)
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SETDAC))              # Command
        self.fd.write(chr(dac & 0x0F))          # DAC Channel
        self.fd.write(chr((val/256) & 0xFF))    # MSByte
        self.fd.write(chr(val%256))             # LSByte
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SETDAC', ack
        return


    def send_pot_val(self, pot, val):
        if not self.bValidDevice():
			return

        self.fd.write(chr(SETPOT))              # Command
        self.fd.write(chr(pot & 0x0F))          # Pot Channel
        self.fd.write(chr((val/256) & 0xFF))    # MSByte
        self.fd.write(chr(val%256))             # LSByte
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SETPOT', ack
	return

    def set_pot(self, pot, ohms):
        """
        Sets the DAC of channel 'pot' to value 'val' (for 10-bit pot: 0-1023)
        """
        if not self.bValidDevice():
			return

	val = int (ohms / mpot[pot])
	self.send_pot_val(pot, val)
	self.potValues[pot] = ohms
	savePotLog(self.potValues)
        return

    '''
    def set_gain_pot(self, ohms):
	x = int (ohms / mpot[GAIN_POT])
	self.send_pot_val(GAIN_POT, x)
	return


    def set_timek_pot(self, ohms):
	x = int (ohms / mpot[TIMEK_POT])
	self.send_pot_val(TIMEK_POT, x)
	return


    def set_xslope_pot(self, ohms):
	x = int (ohms / mpot[XSLOPE_POT])
	self.send_pot_val(XSLOPE_POT, x)
	return


    def set_yslope_pot(self, ohms):
	x = int (ohms / mpot[YSLOPE_POT])
	self.send_pot_val(YSLOPE_POT, x)
	return

    '''

    def set_spi_dac(self, val):
        """
        Sets the DAC of channel 'dac' to value 'val' (for 12-bit dac: 0-4095, for 16-bit DAC: 0-65535)
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SET_SPI_DAC))         # Command
        self.fd.write(chr((val/256) & 0xFF))    # MSByte
        self.fd.write(chr(val%256))             # LSByte
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SET_SPI_DAC', ack
        return


    def read_adc(self, channel=0):
        if not self.bValidDevice():
			return

        self.fd.write(chr(READ_ADC))            # Command
        self.fd.write(chr(channel))             # ADC Channel
        ack = self.fd.read(1)
        val = self.fd.read(2)
        adc16bit = struct.unpack('>H', val)[0]
        if ack != VALID_CMD:
            print 'Invalid Ack: READ_ADC', ack
	#print 'ADC Val: ', hex(adc16bit)
        return adc16bit

    def read_spi_adc(self):
        if not self.bValidDevice():
			return

        self.fd.write(chr(READ_SPI_ADC))            # Command
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: READ_SPI_ADC', ack
        val = self.fd.read(2 * SIMUL_ADC_CHANNELS)
        all_chn_out = struct.unpack('<'+'h'*SIMUL_ADC_CHANNELS, val)
        madc = 20000.0 / 65536
        all_chn_out_mv = [madc * int(val) for val in all_chn_out]
        return all_chn_out_mv
 
    def set_voltage(self, dac, mv):
        """
        Sets the DAC value, given in millivolts
        """
        if not self.bValidDevice():
			return

	if dac in DACS12BIT:
            x = (mv - cdac[dac]) / mdac[dac] + 0.51;
            if mv > 0 and mv < 10000:
        	x += 1
            self.set_dac(dac, int(x))
	if dac in DACS16BIT:
            x = (mv - cdac[dac]) / mdac[dac];
            self.set_dac(dac, int(x))

        if dac == OXDAC:
	    saveLogOffsetX(mv)
        if dac == OYDAC:
	    saveLogOffsetY(mv)
        if dac == OZDAC:
	    saveLogOffsetZ(mv)
        return

    def read_voltage(self, channel = 0):
        if not self.bValidDevice():
			return

        adc16bit = self.read_adc(channel)
        mv = madc * adc16bit + cadc;
        return mv

    def set_tc(self, tc, delay = 0.01):
	'''
	TC avlues are given in picoamperes, 1pA = 1mV
	'''
        if not self.bValidDevice():
			return

	step = mdac[TC_SETP_DAC]	# ~5mV steps
	mv = -1.0 * tc

	if (delay == 0):		# For quick setting of TC setpoint - during 'Init'ialize
            	x = (mv - cdac[TC_SETP_DAC]) / mdac[TC_SETP_DAC] 
            	self.set_dac(TC_SETP_DAC, int(x))
		saveSetpointTC(tc)
		return

        prev_tc = readCurrentSetpoint()
        __delay = 0.01	# 10ms 
	dac_out = -1.0 * prev_tc

        if mv > dac_out:
            while True:
            	x = (dac_out - cdac[TC_SETP_DAC]) / mdac[TC_SETP_DAC]; 
            	self.set_dac(TC_SETP_DAC, int(x))
            	time.sleep(__delay)
		dac_out += step
		if (dac_out >= mv):
		    break
		#print 'DDD', dac_out
        if mv <= dac_out:
            while True: 
            	x = (dac_out - cdac[TC_SETP_DAC]) / mdac[TC_SETP_DAC]; 
            	self.set_dac(TC_SETP_DAC, int(x))
            	time.sleep(__delay)
		dac_out -= step
		if (dac_out <= mv):
		    break
		#print 'DDD', dac_out
	saveSetpointTC(tc)
	return

    def  set_scandacs(self, dac, mV):
        """
        Sets the Scan X or Y scanning DAC to 'mv' millivolts
        """
        if not self.bValidDevice():
			return

        x = (mV - cdac[dac]) / mdac[dac];
        self.set_dac(dac, int(x))
        return

    def set_scanx(self, mv):
        """
        Sets the Scan X DAC to 'mv' millivolts (-1000 mV to 1000 mV)
        """
        if not self.bValidDevice():
			return

        x = (mv - cdac[XDAC]) / mdac[XDAC]; 
        self.set_dac(XDAC, int(x))
        return

    def set_scany(self, mv):
        """
        Sets the Scan Y DAC to 'mv' millivolts (-1000 mV to 1000 mV)
        """
        if not self.bValidDevice():
			return

        x = (mv - cdac[YDAC]) / mdac[YDAC]; 
        self.set_dac(YDAC, int(x))
        return

    def set_offsetx(self, mv):
        """
        Sets the X Offset DAC to 'mv' millivolts (-10V to 10 V)
        """
        if not self.bValidDevice():
			return

        prev_offsetx_value = int(readLogOffsetX())
        if prev_offsetx_value < mv:
            step = 5
        else:
            step = -5
        __delay = abs(step)/(float(TIP_VELOCITY)*1000) 
        for i in range(prev_offsetx_value,int(mv),step):
            x = (i- cdac[OXDAC]) / mdac[OXDAC] + 0.51; 
            self.set_dac(OXDAC, int(x) )
            time.sleep(__delay)
        x = (mv - cdac[OXDAC]) / mdac[OXDAC] + 0.51;
        if mv > 0 and mv < 10000:
            x += 1
        self.set_dac(OXDAC, int(x))
	saveLogOffsetX(mv)
        return
    
    def set_offsety(self, mv):
        """
        Sets the Y Offset DAC to 'mv' millivolts (-10V to 10 V)
        """
        if not self.bValidDevice():
			return

        prev_offsety_value = int(readLogOffsetY())
        if prev_offsety_value < mv:
            step = 5
        else:
            step = -5
        __delay = abs(step)/(float(TIP_VELOCITY)*1000) 
        for i in range(prev_offsety_value, int(mv), step):
            x = (i- cdac[OYDAC]) / mdac[OYDAC] + 0.51; 
            self.set_dac(OYDAC, int(x) )
            time.sleep(__delay)
        x = (mv - cdac[OYDAC]) / mdac[OYDAC] + 0.51;
        if mv > 0 and mv < 10000:
            x += 1
        self.set_dac(OYDAC, int(x))
	saveLogOffsetY(mv)
        return
    
    def set_offsetz(self, mv):
        """
        Sets the Z Offset DAC to 'mv' millivolts (-10V to 10 V)
        m and c should be changed according to the actual Z gain.
        """
        if not self.bValidDevice():
			return

        prev_offsetz_value = readLogOffsetZ()

	step = 16 * mdac[OZDAC]	# ~5mV steps

        __delay = abs(step) / (float(TIP_VELOCITY) * 1000) 

	dac_out = prev_offsetz_value

        if mv > dac_out:
            while (dac_out <= mv):
            	x = (dac_out - cdac[OZDAC]) / mdac[OZDAC]; 
            	self.set_dac(OZDAC, int(x))
            	time.sleep(__delay)
		dac_out += step
        if mv < dac_out:
            while (dac_out >= mv):
            	x = (dac_out - cdac[OZDAC]) / mdac[OZDAC]; 
            	self.set_dac(OZDAC, int(x))
            	time.sleep(__delay)
		dac_out -= step
	saveLogOffsetZ(mv) 
        return

    def set_bias(self, mv):
        """
        Sets the BIAS DAC Channel to 'mv' millivolts (-10V to 10 V)
        m and c should be changed according to the actual gain.
        """
        if not self.bValidDevice():
			return

        x = (mv - cdac[BIASDAC]) / mdac[BIASDAC]; 
        self.set_dac(BIASDAC, int(x))
        return

    def set_bias_slow(self, bias, delay=0.001):
        """
        Sets the BIAS DAC Channel to 'mv' millivolts (-10V to 10 V)
        m and c should be changed according to the actual gain.
        """
	flagBiasHV = False

	if (bias >= MAX_BIAS / BIAS_GAIN) or (bias <= MIN_BIAS / BIAS_GAIN):
		flagBiasHV = True
		dac_mv = -1.0 * (bias / BIAS_GAIN) * 1e3
	else:
		dac_mv = bias * 1e3

        __delay = delay	# in ms 

	# Fast setting of sample bias
	if __delay == 0:
		if flagBiasHV == True:
			self.bias_mode_high ()
		else:
			self.bias_mode_low ()
            	x = (dac_mv - cdac [BIASDAC]) / mdac [BIASDAC]; 
            	self.set_dac(BIASDAC, int(x))
		saveSampleBias(bias)
		return

	# Slow setting of sample bias
        prev_bias = getCurrentSampleBias()
	if (prev_bias >= MAX_BIAS / BIAS_GAIN) or (prev_bias <= MIN_BIAS / BIAS_GAIN):
		dac_out = -1.0 * (prev_bias / BIAS_GAIN) * 1e3
	else:
		dac_out = prev_bias * 1e3

	step = mdac[BIASDAC]

        if dac_mv > dac_out:
            while True:
            	x = (dac_out - cdac[BIASDAC]) / mdac[BIASDAC]; 
            	self.set_dac(BIASDAC, int(x))
            	time.sleep(__delay)
		dac_out += step
		if abs (dac_out) < (2 * BIAS_DAC_RESOLUTION):
			if flagBiasHV == True:
				self.bias_mode_high ()
			else:
				self.bias_mode_low ()
		if (dac_out >= dac_mv):
		    break
		#print 'DDD', dac_out
        if dac_mv <= dac_out:
            while True:
            	x = (dac_out - cdac[BIASDAC]) / mdac[BIASDAC]; 
            	self.set_dac(BIASDAC, int(x))
            	time.sleep(__delay)
		dac_out -= step
		if abs (dac_out) < (2 * BIAS_DAC_RESOLUTION):
			if flagBiasHV == True:
				self.bias_mode_high ()
			else:
				self.bias_mode_low ()
		if (dac_out <= dac_mv):
		    break
		#print 'DDD', dac_out
	saveSampleBias(bias)
        return


    def set_gain(self, gain_factor):
        """
        Set the ADC gain selection switch from 0 to 3
        """
        if not self.bValidDevice():
			return

	gain_factor = ADC_GAIN.index(gain_factor)
        self.fd.write(chr(SETGAIN))              # Command
        self.fd.write(chr(gain_factor))          # 0 to 3
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SETGAIN', ack
        return


    def set_ain1_gain(self, gain_factor):
        """
        Set the analog input channel gain from 0 to 3 
        """		
        if not self.bValidDevice():
			return

	gain_factor = AIN1_GAIN.index(gain_factor)
        self.fd.write(chr(SET_AIN1_GAIN))
        self.fd.write(chr(gain_factor))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SET_AIN1_GAIN', ack
        return


    def set_ain2_gain(self, gain_factor):
        """
        Set the analog input channel gain from 0 to 3 
        """		
        if not self.bValidDevice():
			return

	gain_factor = AIN2_GAIN.index(gain_factor)
        self.fd.write(chr(SET_AIN2_GAIN))
        self.fd.write(chr(gain_factor))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SET_AIN2_GAIN', ack
        return



    def hold_on(self):
        """
        For CH Mode setting
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWSET2))               # Command
        self.fd.write(chr(REG_HOLD))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_HOLD', ack
        return

    def hold_off(self):
        """
        For CC Mode setting
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWCLR2))               # Command
        self.fd.write(chr(REG_HOLD))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_HOLD', ack
        return

    def ela_on(self):
        """
        Selct HVA Gain Stage
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWSET1))               # Command
        self.fd.write(chr(REG_XLA))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_XLA', ack
        return

    def ela_off(self):
        """
        Remove HVA Gain Stage
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWCLR1))               # Command
        self.fd.write(chr(REG_XLA))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_XLA', ack
        return

    def reset_on(self):
        """
        Feedback circuit reset
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWCLR2))               # Command
        self.fd.write(chr(REG_RESET))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_RESET', ack
        return

    def reset_off(self):
        """
        Feedback circuit reset cleared
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWSET2))               # Command
        self.fd.write(chr(REG_RESET))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_RESET', ack
        return

    def bias_mode_high(self):
        """
        Sample Bias from High Voltage Amplifier 
        """
        if not self.bValidDevice():
			return

	print 'Bias HV Mode'
        self.fd.write(chr(SELECT_HV_BIAS))               # Command
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SELECT_HV_BIAS', ack
        return

    def bias_mode_low(self):
        """
        Sample Bias from Low Voltage Amplifier 
        """
        if not self.bValidDevice():
			return

	print 'Bias LV Mode'
        self.fd.write(chr(SELECT_LV_BIAS))               # Command
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SELECT_LV_BIAS', ack
        return

    def select_sa_scanner(self):
        """
        Sample Bias from High Voltage Amplifier 
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SELECT_SA_SCANNER))               # Command
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SELECT_SA_SCANNER', ack
        return

    def select_la_scanner(self):
        """
        Sample Bias from Low Voltage Amplifier 
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SELECT_LA_SCANNER))               # Command
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SELECT_LA_SCANNER', ack
        return

    def fine_slope_adj(self):
        """
        Sample Bias from High Voltage Amplifier 
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(FINE_SLOPE_ADJ))               # Command
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: FINE_SLOPE_ADJ', ack
        return

    def coarse_slope_adj(self):
        """
        Sample Bias from Low Voltage Amplifier 
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(COARSE_SLOPE_ADJ))               # Command
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: COARSE_SLOPE_ADJ', ack
        return


    def led_on(self):
        """
        Shroud LED switched on
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWCLR2))               # Command
        self.fd.write(chr(REG_SHR_LED))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_SHR_LED', ack
        return


    def led_off(self):
        """
        Shroud LED switched off
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWSET2))               # Command
        self.fd.write(chr(REG_SHR_LED))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_SHR_LED', ack
        return


    def set_Zmode(self):
        """
        ADC channel (before MUX) set to Z mode
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWSET2))               # Command
        self.fd.write(chr(REG_TCZ))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_TCZ', ack
        return

    def set_TCmode(self):
        """
        ADC channel (before MUX) set to TC mode
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWCLR2))               # Command
        self.fd.write(chr(REG_TCZ))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_TCZ', ack
        return

    def set_small_piezo_scanner(self):
        """
	Switch to small scanner i.e. tube-design
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWCLR3))               # Command
        self.fd.write(chr(REG_SCANNER_SEL))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_SCANNER_SEL', ack
        return

    def set_large_piezo_scanner(self):
        """
	Switch to large piezo scanner i.e. bimorph-design
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWSET3))               # Command
        self.fd.write(chr(REG_SCANNER_SEL))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_SCANNER_SEL', ack
        return

    def enableBiasModulation(self):
        """
        Bias modulation fed to final bias Adder 
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(ENABLE_BIAS_MODULATION))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: ENABLE_BIAS_MODULATION', ack
	return


    def disableBiasModulation(self):
        """
        Bias modulation input to final bias Adder grounded
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(DISABLE_BIAS_MODULATION))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: DISABLE_BIAS_MODULATION', ack
	return


    def enableZ_Modulation(self):
        """
        Z modulation fed to final HVA Adder 
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(ENABLE_Z_MODULATION))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: ENABLE_Z_MODULATION', ack
	return


    def disableZ_Modulation(self):
        """
        Z modulation input to final HVA Adder grounded
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(DISABLE_Z_MODULATION))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: DISABLE_Z_MODULATION', ack
	return


    def set_walker_forward(self):
        """
        Set Walker Direction forward (HIGH)
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWSET1))               # Command
        self.fd.write(chr(REG_WDIR))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_WDIR', ack
        return

    def set_walker_backward(self):
        """
        Set Walker backward
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SWCLR1))               # Command
        self.fd.write(chr(REG_WDIR))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: REG_WDIR', ack
        return


    def select_pidin(self, channel):
	'''
	Select analog input channel which is input to feedback control 
	'''
        if not self.bValidDevice():
			return

	if channel == 0:
	        self.fd.write(chr(SWCLR2))               # Command
        	self.fd.write(chr(REG_SEL_PIDIN))
	        ack = self.fd.read(1)
        	if ack != VALID_CMD:
	            print 'Invalid Ack: REG_SEL_PIDIN', ack
		return
	if channel == 1:
	        self.fd.write(chr(SWSET2))               # Command
        	self.fd.write(chr(REG_SEL_PIDIN))
	        ack = self.fd.read(1)
        	if ack != VALID_CMD:
	            print 'Invalid Ack: REG_SEL_PIDIN', ack
		return
	print 'Incorrect Channel No.', channel, 'specified...'
	return
	

    def init_tip(self):
        """
        Method : init_tip
                Initializes OXDAC, OYDAC ,OZDAC ,XDAC ,YDAC to 0
        """
        if not self.bValidDevice():
			return

        self.set_offsetx(0)
        self.set_offsety(0)
        self.set_offsetz(0)
        self.set_scanx(0)
        self.set_scany(0)
        return

    def walk(self, ns):
        """
        Move the walker by the specified number of steps
        """
        if not self.bValidDevice():
			return

        self.set_TCmode()
        for i in range(ns):
            self.single_step()
            time.sleep(0.03)		# 30 ms delay
            tc = self.read_spi_adc () [ADC_CHANNEL_TCZ]
            print tc
        return

    def single_step(self):
        """
        Move walker single step
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(SINGLE_STEP))              # Command
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SINGLE_STEP', ack
        time.sleep(0.01)		# 10 ms delay
        tc = self.read_spi_adc () [ADC_CHANNEL_TCZ]
        return tc

    def filter_scan(self, np, start, step, delay, dac_choice):
        """
        Arguments:
            np - no. of points,
            start - starting voltage (in mV),
            step - step increment for each pixel (in mV),
            delay - delay between subsequent pixel acquired (in microseconds)
            dac_choice - scan dacs
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(FILTERSCAN_SINGLE))
        self.fd.write(chr(np/256))         
        self.fd.write(chr(np%256))
        self.fd.write(chr(start/256))
        self.fd.write(chr(start%256))
        self.fd.write(chr(step))
	MIN_PIX_READ_TIME = 150         # 4 reads (One ADC read ~ 35us)
        mcu_delay = int((delay - MIN_PIX_READ_TIME)/10) # for MCU delay list
        self.fd.write(chr(mcu_delay))
        self.fd.write(chr(dac_choice))
        time.sleep(0.02)
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: FILTERSCAN_SINGLE', ack
        adc = self.fd.read(4*np)
        raw = struct.unpack('>'+'H'*(2*np), adc)
        mv = map(lambda(x): x*madc + cadc, raw)
        return mv

    def simultaneous_scan_dual_trace(self, np, start, step, delay, dac_choice, noc = 1):
        """
        np - no. of points,
        start - starting voltage (in mV),
        step - step increment for each pixel (in mV),
        delay - delay between subsequent pixel acquired (in microseconds)
        dac_choice - scan dacs
	noc - no. of channels to scan simultaneously
        """
        if not self.bValidDevice():
			return

        self.fd.write (chr (SIMUL_SCAN_DUAL_TRACE))
        self.fd.write (chr (np / 256))         
        self.fd.write (chr (np % 256))
        self.fd.write (chr (start / 256))
        self.fd.write (chr (start % 256))
        self.fd.write (chr (step))
	delay_code = step_delay_list.index (delay)
	#MIN_PIX_READ_TIME = 120         # One ADC read ~ 120us 
        #mcu_delay = int ((delay - MIN_PIX_READ_TIME)) # for MCU delay list in controller
        self.fd.write (chr (delay_code))
        self.fd.write (chr (dac_choice))
        self.fd.write (chr (noc))
        time.sleep ((delay /1e6) * np)
        ack = self.fd.read (1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SIMUL_SCAN_DUAL_TRACE', ack
        adc = self.fd.read (4 * np * noc)
        raw = struct.unpack ('<' + 'h' * (2 * np * noc), adc)
        madc = 20000.0 / 65536
        mv = [madc * (val) for val in raw]
        return mv

    def simultaneous_scan_single_trace_slow (self, np, start, step, delay, dac_choice, dir_, noc = 1):
        """
	### For LDOS LBH Scanning ####
        np - no. of points,
        start - starting voltage (in mV),
        step - step increment for each pixel (in mV),
        delay - delay between subsequent pixel acquired (in microseconds)
        dac_choice - scan dacs
	noc - no. of channels to scan simultaneously
        """
        if not self.bValidDevice():
			return

        self.fd.write (chr (SIMUL_SCAN_SINGLE_TRACE_SLOW))
        self.fd.write (chr (np/256))         
        self.fd.write (chr (np%256))
        self.fd.write (chr (start/256))
        self.fd.write (chr (start%256))
        self.fd.write (chr (step))
	delay_code = lia_step_delay_list.index (delay)
        self.fd.write (chr (delay_code))
        self.fd.write (chr (dac_choice))
        self.fd.write (chr (dir_))
        self.fd.write (chr (noc))
        time.sleep (0.2)# * np * delay / 1e3)
        ack = self.fd.read (1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SIMUL_SCAN_SINGLE_TRACE_SLOW', ack
        adc = self.fd.read (2 * np * noc)
        raw = struct.unpack ('<' + 'h' * (np * noc), adc)
        madc = 20000.0 / 65536
        mv = [madc * (val) for val in raw]
        return mv

    def simultaneous_scan_single_trace_fast (self, np, start, step, delay, dac_choice, dir_, noc=1):
        """
	### For HiRes Scanning ####
        np - no. of points,
        start - starting voltage (in mV),
        step - step increment for each pixel (in mV),
        delay - delay between subsequent pixel acquired (in microseconds)
        dac_choice - scan dacs
	noc - no. of channels to scan simultaneously
        """
        if not self.bValidDevice():
			return

        self.fd.write (chr (SIMUL_SCAN_SINGLE_TRACE_FAST))
        self.fd.write (chr (np/256))         
        self.fd.write (chr (np%256))
        self.fd.write (chr (start/256))
        self.fd.write (chr (start%256))
        self.fd.write (chr (step))
	#delay_code = lia_step_delay_list.index (delay)
	delay_code = step_delay_list.index (delay)
        self.fd.write (chr (delay_code))
        self.fd.write (chr (dac_choice))
        self.fd.write (chr (dir_))
        self.fd.write (chr (noc))
        time.sleep (0.02)# * np * delay / 1e3)
        ack = self.fd.read (1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SIMUL_SCAN_SINGLE_TRACE_FAST', ack
        adc = self.fd.read (2 * np * noc)
        raw = struct.unpack ('<' + 'h' * (np * noc), adc)
        madc = 20000.0 / 65536
        mv = [madc * (val) for val in raw]
        return mv


    def hires_scan(self, np, start, step, delay, dac_choice, dir_):
        """
        Arguments:
            np - no. of points,
            start - starting voltage (in mV),
            step - step increment for each pixel (in mV),
            delay - delay between subsequent pixel acquired (in microseconds)
            dac_choice - scan dacs
	    dir - 0 : Scan, (increase voltage from sp in steps)
		  1 : Retrace (decrease voltage from sp in steps)
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(HIRES_SCAN))
        self.fd.write(chr(np/256))         
        self.fd.write(chr(np%256))
        self.fd.write(chr(start/256))
        self.fd.write(chr(start%256))
        self.fd.write(chr(step))
	MIN_PIX_READ_TIME = 150         # 4 reads (One ADC read ~ 35us)
        mcu_delay = int((delay - MIN_PIX_READ_TIME)/10) # for MCU delay list
        #print 'Delay filter: ', mcu_delay
        self.fd.write(chr(mcu_delay))
        self.fd.write(chr(dac_choice))
        self.fd.write(chr(dir_))
        time.sleep(0.02)
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: HIRES_SCAN', ack
        adc = self.fd.read(2*np)
        raw = struct.unpack('>'+'H'*(np), adc)
        mv = map(lambda(x): x*madc + cadc, raw)
        return mv

    def simul_readblock_fast (self, np, delay, noc = 1):
        """
	### For Time Spectroscopy ####
        np - no. of points,
        step - step increment for each pixel (in mV),
        delay - delay between subsequent pixel acquired (in microseconds)
	noc - no. of channels to read simultaneously
        """
        self.fd.write (chr (SIMUL_READBLOCK_FAST))
        self.fd.write (chr (np/256))         
        self.fd.write (chr (np%256))
	delay_code = step_delay_list.index (delay)
        self.fd.write (chr (delay_code))
        self.fd.write (chr (noc))
        time.sleep (0.02)# * np * delay / 1e3)
        ack = self.fd.read (1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SIMUL_READBLOCK_FAST', ack
        adc = self.fd.read (2 * np * noc)
        raw = struct.unpack ('<' + 'h' * (np * noc), adc)
        madc = 20000.0 / 65536
        mv = [madc * (val) for val in raw]
        return mv

    def simul_readblock_slow (self, np, delay, noc = 1):
        """
	### For Time Spectroscopy ####
        np - no. of points,
        step - step increment for each pixel (in mV),
        delay - delay between subsequent pixel acquired (in microseconds)
	noc - no. of channels to read simultaneously
        """
        self.fd.write (chr (SIMUL_READBLOCK_SLOW))
        self.fd.write (chr (np/256))         
        self.fd.write (chr (np%256))
	delay_code = lia_step_delay_list.index (delay)
        self.fd.write (chr (delay_code))
        self.fd.write (chr (noc))
        time.sleep (0.02)# * np * delay / 1e3)
        ack = self.fd.read (1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SIMUL_READBLOCK_SLOW', ack
        adc = self.fd.read (2 * np * noc)
        raw = struct.unpack ('<' + 'h' * (np * noc), adc)
        madc = 20000.0 / 65536
        mv = [madc * (val) for val in raw]
        return mv

    def read_block(self, np, delay):
        self.fd.write(chr(READBLOCK))
        self.fd.write(chr(np/256))         
        self.fd.write(chr(np%256))
        self.fd.write(chr(delay/256))
        self.fd.write(chr(delay%256))
        time.sleep(0.02)
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: READBLOCK', ack
        adc = self.fd.read(2*np)
        raw = struct.unpack('>'+'H'*(np), adc)
        mv = map(lambda(x): x*madc + cadc, raw)
        res = []
        for i in range(len(mv)):
                res.append([i,mv[i]])
        return res
    
    def spectro_sweep(self, np, start, step, delay, mavg):
        """
        Acquire IV data with the following input parameters:
            np	        : no. of points in the spectro curve
            startbias   : initial bias value
            step	: bias voltage step size
            delay	: Delay between spectro steps
            mavg_points : no. readings taken to be averaged at each step
        """
        if not self.bValidDevice():
			return

        self.fd.write(chr(IVSPECTRA))
        self.fd.write(chr(np/256))         
        self.fd.write(chr(np%256))
        self.fd.write(chr(start/256))
        self.fd.write(chr(start%256))
        self.fd.write(chr(step))
        self.fd.write(chr(delay/256))
        self.fd.write(chr(delay%256))
        self.fd.write(chr(mavg))
        time.sleep(np * (delay / 1000.0) * mavg)
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: IVSPECTRA', ack
        adc = self.fd.read(2*np)
        raw = struct.unpack('>'+'H'*(np), adc)
        mv = map(lambda(x): x*madc + cadc, raw)
        return mv

    def simul_spectro_sweep(self, np, start, step, delay, mavg, ch_mask):
        """
        Acquire IV data with the following input parameters:
            np	        : no. of points in the spectro curve
            startbias   : initial bias value
            step	: bias voltage step size
            delay	: Delay between spectro steps
            mavg_points : no. readings taken to be averaged at each step
	    ch		: channel no. to be logged
	    noc		: no. of channels to be logged
        """
        if not self.bValidDevice():
			return

        self.fd.write (chr (SIMUL_IVSPECTRA))
        self.fd.write (chr (np / 256))
        self.fd.write (chr (np % 256))
        self.fd.write (chr (start / 256))
        self.fd.write (chr (start % 256))
        self.fd.write (chr (step / 256))
        self.fd.write (chr (step % 256))
        self.fd.write (chr (delay / 256))
        self.fd.write (chr (delay % 256))
        self.fd.write (chr (mavg))
        self.fd.write (chr (ch_mask))

	noc = 0
	print 'Acquire' ,
	for count in range (SIMUL_ADC_CHANNELS):
	    if (ch_mask & (1 << count)) != 0:
		noc += 1
		print 'Channel ', count, 
	print 'Total Channels: ', noc
	#print 'Vishesham...'
        time.sleep (1)#np * (delay / 1000.0))
        ack = self.fd.read (1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SIMUL_IVSPECTRA', ack
        adc = self.fd.read (2 * np * noc)
        raw = struct.unpack('<' + 'h' * (np * noc), adc)
	#print raw
        madc = 20000.0 / 65536
        mv = [madc * (val) for val in raw]
	if noc == 1:
	    return mv

	''' Split multi-channel data into different arrays'''
	spectra_channels = []
	for count in range (noc):
	    spectra_channels.append (mv [count::noc])
       	return spectra_channels


    def simul_spectro_retrace_sweep(self, np, start, step, delay, mavg, ch_mask):
        """
        Acquire IV data with the following input parameters:
            np	        : no. of points in the spectro curve
            startbias   : initial bias value
            step	: bias voltage step size
            delay	: Delay between spectro steps
            mavg_points : no. readings taken to be averaged at each step
	    ch		: channel no. to be logged
	    noc		: no. of channels to be logged
        """
        if not self.bValidDevice():
			return

        self.fd.write (chr (SIMUL_IVSPECTRA_RETRACE))
        self.fd.write (chr (np / 256))
        self.fd.write (chr (np % 256))
        self.fd.write (chr (start / 256))
        self.fd.write (chr (start % 256))
        self.fd.write (chr (step / 256))
        self.fd.write (chr (step % 256))
        self.fd.write (chr (delay / 256))
        self.fd.write (chr (delay % 256))
        self.fd.write (chr (mavg))
        self.fd.write (chr (ch_mask))

	noc = 0
	print 'Acquire' ,
	for count in range (SIMUL_ADC_CHANNELS):
	    if (ch_mask & (1 << count)) != 0:
		noc += 1
		print 'Channel ', count, 
	print 'Total Channels: ', noc
	#print 'Vishesham...'
        time.sleep (1)#np * (delay / 1000.0))
        ack = self.fd.read (1)
        if ack != VALID_CMD:
            print 'Invalid Ack: SIMUL_IVSPECTRA_RETRACE', ack
        adc = self.fd.read (2 * np * noc)
        raw = struct.unpack('<' + 'h' * (np * noc), adc)
	#print raw
        madc = 20000.0 / 65536
        mv = [madc * (val) for val in raw]
	if noc == 1:
	    return mv

	''' Split multi-channel data into different arrays'''
	spectra_channels = []
	for count in range (noc):
	    spectra_channels.append (mv [count::noc])
       	return spectra_channels


    def litho(self, spike_voltage, spike_delay, delay_code = 0):
	"""
	p = stm.stm()
	p.litho(spike_voltage, spike_delay, delay_code) 
	"""
        if not self.bValidDevice():
			return

	dac_val = int ((spike_voltage - cdac [BIASDAC]) / mdac [BIASDAC])

	if delay_code == 1:
		self.fd.write (chr (LITHO_PULSE_US))
		if spike_delay < 50:
			spike_delay = 50
			print 'Min. spike of 50us used...'
		spike_delay = int(round(spike_delay / 50)) - 1
		#print 'Litho Pulse Height', spike_voltage, 'V',  'Litho Pulse Width', spike_delay, 'us'
	else:
		self.fd.write (chr (LITHO_PULSE_MS))
		if spike_delay == 0:
			spike_delay = 1
			print 'Min. spike of 1ms used...'
		#print 'Litho Pulse Height', spike_voltage, 'V',  'Litho Pulse Width', spike_delay, 'ms'
	self.fd.write (chr ((dac_val / 256) & 0xFF))    # MSB
	self.fd.write (chr (dac_val % 256))            	# LSB
	self.fd.write (chr ((spike_delay / 256) & 0xFF))
	self.fd.write (chr (spike_delay % 256))
        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: LITHO_PULSE_xS', ack
	return


    def litho_pulse_train(self, spike_voltage, spike_delay, delay_code = 0, nop = 1):

	"""
	p = stm.stm()
	p.litho(spike_voltage, spike_delay, delay_code, no_of_pulses) 
	"""
        if not self.bValidDevice():
			return

	dac_val = int ((spike_voltage - cdac [BIASDAC]) / mdac [BIASDAC])

	if delay_code == 1:
		self.fd.write (chr (LITHO_PULSE_TRAIN_US))
		if spike_delay < 50:
			spike_delay = 50
			print 'Min. spike of 50us used...'
		spike_delay = int(round(spike_delay / 50)) - 1
		#print 'Litho Pulse Height', spike_voltage, 'V',  'Litho Pulse Width', spike_delay, 'us'
	else:
		self.fd.write (chr (LITHO_PULSE_TRAIN_MS))
		if spike_delay == 0:
			spike_delay = 1
			print 'Min. spike of 1ms used...'
		#print 'Litho Pulse Height', spike_voltage, 'V',  'Litho Pulse Width', spike_delay, 'ms'

	if nop > (2**16 - 1):	# Upper limit to no. of pulses   
		nop = (2**16 - 1)

	self.fd.write (chr ((dac_val / 256) & 0xFF))    # MSB
	self.fd.write (chr (dac_val % 256))            	# LSB
	self.fd.write (chr ((spike_delay / 256) & 0xFF))
	self.fd.write (chr (spike_delay % 256))
	self.fd.write (chr ((nop / 256) & 0xFF))
	self.fd.write (chr (nop % 256))

        ack = self.fd.read(1)
        if ack != VALID_CMD:
            print 'Invalid Ack: LITHO_PULSE_TRAIN_xS', ack
	return



if __name__ == '__main__':
    p = Stm()
