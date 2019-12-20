# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 20:33:54 2015

@author: tkneiske
"""
import matplotlib.pyplot as plt
import pandas as pd

def Correct_MPC(Opt_Result, PVavaPeriodReal, PVavaPeriodFore, 
                                        LoadPeriodReal, LoadPeriodFore,Battery):    
    LoadDiff =  LoadPeriodReal['ELoad'][Opt_Result.index[0]]-LoadPeriodFore['ELoad'][Opt_Result.index[0]] 
    PVDiff =  PVavaPeriodReal['PV 2013, Kassel, 10min'][Opt_Result.index[0]]-PVavaPeriodFore['PV 2013, Kassel, 10min'][Opt_Result.index[0]]                                        
    CorrGridImp = 0
    CorrPVexp = 0
    CorrBatDiss = 0
    CorrBatChar = 0
    #Precision = 0.001    # How close to 0 is allowed
    CorrBatSOC = 0
    CorrGridexp = 0 
    CorrPVsc =0
    

               
    CorrTerms = pd.Series([LoadDiff, PVDiff, CorrBatDiss, CorrBatChar, CorrBatSOC, \
    CorrGridImp, CorrPVexp, CorrGridexp, CorrPVsc],\
           index = ['LoadDiff', 'PVDiff', 'CorrBatDiss', 'CorrBatChar','CorrBatSOC',\
           'CorrGridImp', 'CorrPVexp','CorrGridexp', 'CorrPVsc'])
   
    return CorrTerms


def Correct_MPC_dummy(Opt_Result, PVavaPeriodReal, PVavaPeriodFore, 
                                        LoadPeriodReal, LoadPeriodFore,Battery):    
    LoadDiff =  LoadPeriodReal['ELoad'][Opt_Result.index[0]]-LoadPeriodFore['ELoad'][Opt_Result.index[0]] 
    PVDiff =  PVavaPeriodReal['PV 2013, Kassel, 10min'][Opt_Result.index[0]]-PVavaPeriodFore['PV 2013, Kassel, 10min'][Opt_Result.index[0]]                                        
    CorrGridImp = 0
    CorrPVexp = 0
    CorrBatDiss = 0
    CorrBatChar = 0
   # Precision = 0.001    # How close to 0 is allowed
    CorrBatSOC = 0
    CorrGridexp = 0 
    CorrPVsc =0

    CorrTerms = pd.Series([LoadDiff, PVDiff, CorrBatDiss, CorrBatChar, CorrBatSOC, \
    CorrGridImp, CorrPVexp, CorrGridexp, CorrPVsc],\
           index = ['LoadDiff', 'PVDiff', 'CorrBatDiss', 'CorrBatChar','CorrBatSOC',\
           'CorrGridImp', 'CorrPVexp','CorrGridexp', 'CorrPVsc'])
    
    return CorrTerms

if __name__ == '__main__':
    plt.close("all")
    print "I am just a poor Correction-Programm without any idea of running.\
    Please ask my friend OptFlex_MPC!"
   