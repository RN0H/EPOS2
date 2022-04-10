 #!/usr/bin/env python3 
# -*- coding: utf-8 -*- 

#================================================
# Author : Rohan Panicker
# Created Date: 10/4/22
# version ='1.0'
#================================================


import serial
import time
from ctypes import *
import os
import math
import matplotlib.pyplot as plt

# EPOS Command Library path
path='your_path'

# Load library
cdll.LoadLibrary(path)
epos = CDLL(path)

# Defining return variables from Library Functions
ret = 0
pErrorCode = c_uint()
pDeviceErrorCode = c_uint()

# Defining a variable NodeID and configuring connection

class Epos2:

    def __init__ (self, **configs):
#--------------------------Initializing path,lib and return types-------------------------------------------------------------
        global path, epos, ret, pErrorCode, pDeviceErrorCode     #GLOBAL_CONSTANTS
#----------------------------------------Node_Parameters----------------------------------------------------------------------
        self.__dict__.update()
#---------------------------------------------Cache---------------------------------------------------------------------------
        self.cache_pos, self.cache_cur = [], []
#---------------------------------------------SubPlots------------------------------------------------------------------------
        self.curr_plt, self.pos_plt = plt.subplot(1,2,1), plt.subplot(1,2,2)
        self.curr_plt.axis([0,50,0,50])
        self.pos_plt.axis([0,100,0,100])
        plt.ion()
#----------------------------Initiating connection and setting motion profile-------------------------------------------------
        self.keyHandle = epos.VCS_OpenDevice(b'EPOS2', b'MAXON SERIAL V2', b'USB', b'USB0', byref(pErrorCode)) # specify EPOS version and interface
        epos.VCS_SetProtocolStackSettings(self.keyHandle, self.baudrate, self.timeout, byref(pErrorCode))   # set baudrate
        epos.VCS_ClearFault(self.keyHandle, self.nodeID, byref(pErrorCode))     # clear all faults
        epos.VCS_SetEnableState(self.keyHandle, self.nodeID, byref(pErrorCode)) # enable device

    # Disable epos
    def Disable(self):
        epos.VCS_SetDisableState(self.keyHandle, self.nodeID, byref(pErrorCode)) # disable device
        epos.VCS_CloseDevice(self.keyHandle, byref(pErrorCode)) # close device

    #cacheing
    def Cacheing(self):
        self.cache_pos.append(self.pos_position/10**6)
        self.cache_cur.append(self.pos_current)

    def Plotter(self):
        self.curr_plt.plot(self.cache_cur)
        self.pos_plt.plot(self.cache_pos)
        plt.show()
        plt.pause(0.05)

    # Query motor position
    def GetPositionIsAvg(self):
        pPositionIsAveraged, pErrorCode=c_long(), c_uint()
        ret=epos.VCS_GetPositionIs(self.keyHandle, self.nodeID, byref(pPositionIs), byref(pErrorCode))
        return pPositionIs.value # motor steps


    # Query motor avg position
    def GetPositionIs(self):
        pPositionIs, pErrorCode=c_long(), c_uint()
        ret=epos.VCS_GetPositionIs(self.keyHandle, self.nodeID, byref(pPositionIs), byref(pErrorCode))
        return pPositionIsAveraged.value # motor avg steps


    # Query motor current
    def GetCurrentIs(self):
        pCurrentIs, pErrorCode=c_short(), c_uint()
        ret=epos.VCS_GetCurrentIs(self.keyHandle, self.nodeID, byref(pCurrentIs), byref(pErrorCode))
        return pCurrentIs.value # motor current


    # Query motor avg current
    def GetCurrentIsAvg(self):
        pCurrentIsAveraged, pErrorCode=c_short(), c_uint()
        ret=epos.VCS_GetCurrentIsAveraged(self.keyHandle, self.nodeID, byref(pCurrentIsAveraged), byref(pErrorCode))
        return pCurrentIsAveraged.value # motor avg current


    #Target_Current
    def SetCurrent(self, target_current):
        epos.VCS_ActivateCurrentMode(self.keyHandle, self.nodeID, byref(pErrorCode)) # set profile parameters
        while self.DigIn():
            epos.VCS_SetCurrentMust(self.keyHandle, self.nodeID, target_current, byref(pErrorCode)) # move to posi
            self.cur_position = self.GetPositionIs()
            self.cur_current  = self.GetCurrentIsAvg()
            self.Cacheing();                                             #Cache
            self.Plotter
            print("Current mode Current: ",self.cur_current)
            if self.current in range(target_current-5,target_current+5): #MAYBE INFINITE LOOP
                time.sleep(2)
                break


    #Target_State
    def MoveToPositionSpeed(self,target_position,target_speed):
        while not self.DigIn():
            if target_speed != 0:
                epos.VCS_SetPositionProfile(self.keyHandle, self.nodeID, target_speed, self.acceleration, self.deceleration, byref(pErrorCode)) # set profile parameters
                epos.VCS_MoveToPosition(self.keyHandle, self.nodeID, target_position, True, True, byref(pErrorCode)) # move to position
            elif target_speed == 0:
                epos.VCS_HaltPositionMovement(self.keyHandle, self.nodeID, byref(pErrorCode)) # halt motor
            self.pos_position = self.GetPositionIs()
            self.pos_current = self.GetCurrentIsAvg()
            self.Cacheing();                                        #cacheing
            print("Position Mode Current: ",self.pos_current);
            if self.pos_position in range(target_position-2,target_position+2):
                return self.pos_current


    #Position Mode
    def Position_Mode(self, steps,rpm):
        time.sleep(0.5)
        epos.VCS_ActivateProfilePositionMode(self.keyHandle, self.nodeID, byref(pErrorCode)) # activate profile position mode
        self.pos_current = self.MoveToPositionSpeed(steps,rpm) # move to position 500,000 steps at 2000 rpm/
        print('Motor position (New Position): %s' % (self.GetPositionIs()))
        print("Position Mode Current: ",self.pos_current);


    #Current Mode
    def Current_Mode(self, current):
        time.sleep(0.5)
        print('Motor position (New Position): %s' % (self.GetPositionIs()))
        time.sleep(1)
        self.SetCurrent(current) # move to position 500,000 steps at 2000 rpm/s
        print('Current mode Current: %s' % (self.GetCurrentIs()))


    #Go Home
    def Go_Home(self,steps,rpm):
        epos.VCS_ActivateProfilePositionMode(self.keyHandle, self.nodeID, byref(pErrorCode)) # activate profile position mode
        self.MoveToPositionSpeed(steps,rpm) # move to position 500,000 steps at 2000 rpm/
        print('Motor position (Home): %s' % (self.GetPositionIs()))

    #Set_Home
    def Homing_Mode(self,set_position):
        epos.VCS_ActivateHomingMode(self.keyHandle, self.nodeID, byref(pErrorCode))
        epos.VCS_DefinePosition(self.keyHandle, self.nodeID, set_position, byref(pErrorCode))
        print('Motor position (Home): %s' % (self.GetPositionIs()))

    #Digiin
    def DigIn(self)->bool:
        pInputs,pErrorCode=c_int(),c_uint();
        epos.VCS_GetAllDigitalInputs(self.KeyHandle, self.nodeID, byref(pInputs), byref(pErrorCode))
        return pInputs.value



if __name__== "__main__":
        print("run driver")
        pass
