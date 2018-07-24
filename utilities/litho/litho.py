###################
#   Litho Class   #
###################

import time
import app_litho
import offset
import stm7 as stm
	
__DEBUG__ 	= True
CLR_HOLD	= 0			# bit value for Feedback on
SET_HOLD	= 1			# bit value for Feedback off

if __DEBUG__ == True:
	from Tkinter import *

def litho(f=None, oStm=None,oToolBar=None):		
    """
    Creates Litho Interface
    """
    oAppLitho = app_litho.app_litho()
    oAppLitho.createLSwindow(f)
    oLitho = Litho(oAppLitho, oStm, oToolBar)		
    return oLitho

class Litho:

	MIN_DELAY = 0		# ms
	MAX_DELAY = 1000	# ms
	MIN_DELAY_US = 0	# us
	MAX_DELAY_US = 950	# us
	DELAY_STEP = 1		# ms
	MIN_PULSES = 1	
	MAX_PULSES = (2**16 - 1)

	def __init__(self, oAppLitho, oStm, oToolBar):
		"""
		Class Contructor : Litho
		"""
		self.DELAY_CODE_MS = 0
		self.DELAY_CODE_US = 1
		self.oStm = oStm
		self.oToolBar = oToolBar
		self.oAppLitho = oAppLitho
		self.feedbackOffMode = BooleanVar()
		self.feedbackOffMode.set(False)
		self.delayVar = IntVar()
		self.delayVar.set(self.DELAY_CODE_MS)
		self.sampleBias = stm.getCurrentSampleBias()
		print 'Present Sample Bias', self.sampleBias
		self._configureCB()
		self.feedbackOffModeSettings(self.feedbackOffMode.get())
		return	

	def _configureCB(self):
		"""
		Attaches Callbacks to LithoGui widgets 
		"""
		INITIAL_SPIKE_HT = 5	# V
		self.INITIAL_SPIKE_WD_MS = 1	# ms
		self.INITIAL_SPIKE_WD_US = 50	# us
		PRE_PULSE_DELAY = 1 	# ms
		POST_PULSE_DELAY = 1 	# ms
		self.oAppLitho.BtnPuncture.configure(command=self.vPunctureCB)
		self.oAppLitho.EntryV1.limits([int(stm.MIN_BIAS /stm.BIAS_GAIN), int(stm.MAX_BIAS / stm.BIAS_GAIN)])
		self.oAppLitho.EntryD1.limits([self.MIN_DELAY, self.MAX_DELAY])
		self.oAppLitho.EntryNoOfPulses.limits([0, self.MAX_PULSES])
		self.oAppLitho.EntryV1.insert(0, int(INITIAL_SPIKE_HT))
		self.oAppLitho.EntryD1.insert(0, int(self.INITIAL_SPIKE_WD_MS))
		self.oAppLitho.EntryNoOfPulses.insert(0, int(self.MIN_PULSES))
		self.oAppLitho.CB_FeedbackOff.configure(variable = self.feedbackOffMode, \
								command = self.feedbackOffModeSettingsCB)
		self.oAppLitho.EntryPrePulseDelay.insert(0, int(PRE_PULSE_DELAY))
		self.oAppLitho.EntryPostPulseDelay.insert(0, int(POST_PULSE_DELAY))
		self.oAppLitho.RBms.configure(variable = self.delayVar, value = 0, command = self.updateDelayLimits)
		self.oAppLitho.RBus.configure(variable = self.delayVar, value = 1, command = self.updateDelayLimits)
		self.oAppLitho.lsGroup.protocol('WM_DELETE_WINDOW',self.vQuitCB)
		return


	def updateDelayLimits(self):
		if self.delayVar.get() == 0:
			self.oAppLitho.EntryD1.limits([self.MIN_DELAY, self.MAX_DELAY])
			self.oAppLitho.EntryD1.delete(0, END)
			self.oAppLitho.EntryD1.insert(0, int(self.INITIAL_SPIKE_WD_MS))
		else:
			self.oAppLitho.EntryD1.limits([self.MIN_DELAY_US, self.MAX_DELAY_US])
			self.oAppLitho.EntryD1.delete(0, END)
			self.oAppLitho.EntryD1.insert(0, int(self.INITIAL_SPIKE_WD_US))
		return

	def feedbackOffModeSettingsCB(self):
		self.feedbackOffModeSettings(self.feedbackOffMode.get())
		return

	def feedbackOffModeSettings(self, mode):
		if mode == True:
			self.oAppLitho.EntryPrePulseDelay.config(state = NORMAL) 
			self.oAppLitho.EntryPostPulseDelay.config(state = NORMAL) 
		else:
			self.oAppLitho.EntryPrePulseDelay.config(state = DISABLED) 
			self.oAppLitho.EntryPostPulseDelay.config(state = DISABLED) 
		return

	def lReadEntry(self):
		"""
		Reads puncturing voltage and delay
		"""
		spike_ht = float(self.oAppLitho.EntryV1.get())
		spike_wd = float(self.oAppLitho.EntryD1.get())
		if self.feedbackOffMode.get() == True:
			pre_delay = float(self.oAppLitho.EntryPrePulseDelay.get())
			post_delay = float(self.oAppLitho.EntryPostPulseDelay.get())
		else:
			pre_delay = 0
			post_delay = 0
		return spike_ht, spike_wd, pre_delay, post_delay
 
	def vPunctureCB(self):
		"""
		Punctures sample with desired spike type and delays
		"""
		spike_ht, spike_wd, pre_delay, post_delay = self.lReadEntry()
		delay_code = self.delayVar.get()

		# Rounding off to Min Delay allowed...
		if delay_code == self.DELAY_CODE_US:
			if spike_wd < self.INITIAL_SPIKE_WD_US:
				spike_wd = self.INITIAL_SPIKE_WD_US
			else:
				spike_wd = int (round (spike_wd * 1.0 / self.INITIAL_SPIKE_WD_US) * self.INITIAL_SPIKE_WD_US)
			# Updating the correct pulse-width on UI
			self.oAppLitho.EntryD1.delete(0, END)
			self.oAppLitho.EntryD1.insert(0, str(spike_wd))

		if delay_code == self.DELAY_CODE_MS:
			if spike_wd < self.INITIAL_SPIKE_WD_MS:
				spike_wd = self.INITIAL_SPIKE_WD_MS
			# Updating the correct pulse-width on UI
			self.oAppLitho.EntryD1.delete(0, END)
			self.oAppLitho.EntryD1.insert(0, str(spike_wd))

		nop = int(self.oAppLitho.EntryNoOfPulses.get())
		if nop == 0:	# Min No. of Pulses allowed is 1
			nop = 1 
			self.oAppLitho.EntryNoOfPulses.delete(0, END)
			self.oAppLitho.EntryNoOfPulses.insert(0, str(nop))

		self.vLithoHandler(spike_ht, spike_wd, \
					self.feedbackOffMode.get(), \
					pre_delay, post_delay, \
					delay_code, nop)		
		return

	def vQuitCB(self):
		"""
		Terminates Lithography utility
		"""
		self.oAppLitho.lsGroup.destroy()
		self.oToolBar.Litho_Instance = 0 
		return

	########## HANDLER FUNCTIONS ################
	def vLithoHandler(self, spike_ht, spike_wd, fb_off_mode, \
				pre_delay, post_delay, delay_code = 0, \
				nop = 1):
		"""
		Generate Bias Spikes
		"""
		self.oStm.set_bias (0)	# in mV
		if (spike_ht <= 10) and (spike_ht >= -10):
			self.oStm.bias_mode_low()
			time.sleep(0.01)	# Relay Response
			flagBiasHV = False
		else:
			#print 'High Voltage Spike'
			self.oStm.bias_mode_high()
			time.sleep(0.01)	# Relay Response	
			flagBiasHV = True 
			spike_ht /= (-10.0)	# high bias mode is -10x low bias mode
		spike_ht *= 1e3	# set bias dac in mV

		if fb_off_mode == True:
			self.vFBOff()
			time.sleep(pre_delay / 1e3)	# Pre Pulse delay
		if nop == 1:
			self.oStm.litho (int (spike_ht), int (spike_wd), delay_code)
		else:
			self.oStm.litho_pulse_train (int (spike_ht), int (spike_wd), delay_code, nop)

		if fb_off_mode == True:
			time.sleep(post_delay / 1e3)	# Pre Pulse delay
			self.vFBOn()

		if flagBiasHV:
			self.oStm.bias_mode_low()
			time.sleep(0.01)	# Relay Response	
			#print 'Low Voltage Bias Mode'
		self.oStm.set_bias (self.sampleBias * 1e3)	# in mV
		return

	def vFBOff(self):
		"""
		FeedBack Off
		"""
		self.oStm.hold_on()
		return

	def vFBOn(self):
		"""
		FeedBack On
		"""
		self.oStm.hold_off()
		return

########## Only for Testing ################
if __name__ == '__main__':
	litho()

