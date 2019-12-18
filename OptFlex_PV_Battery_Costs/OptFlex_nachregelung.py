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
    Precision = 0.001    # How close to 0 is allowed
    CorrBatSOC = 0
    CorrGridexp = 0 
    CorrPVsc =0
    
    # Load Differenz
    if LoadDiff<-Precision:
#        print ('too much Load: ',LoadDiff
        # Check load from Battery --> Battery less discharge
        if Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss > -LoadDiff:
            CorrBatDiss = LoadDiff
#            print ('reduce 100% Battery', Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss
            CorrBatSOC = -LoadDiff/Battery['eta_batt_dis']*Battery['K_batt']  
        #  reduce GridImport        
        elif Opt_Result['P_Grid_import'][Opt_Result.index[0]]+CorrGridImp > -LoadDiff:
            CorrGridImp = LoadDiff
#            print ('reduce 100% Import', Opt_Result['P_Grid_import'][Opt_Result.index[0]]
        #  reduce PV Consumption   
        else:
            CorrGridImp = -Opt_Result['P_Grid_import'][Opt_Result.index[0]]+CorrGridImp    
            if LoadDiff- CorrGridImp >= -Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss :   #neg neg
                CorrBatDiss = LoadDiff- CorrGridImp
                CorrBatSOC = -CorrBatDiss/Battery['eta_batt_dis']*Battery['K_batt']              
#                print ('reduce battery and Import'
            else:
                CorrBatDiss = -Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss    
                CorrBatSOC = -CorrBatDiss/Battery['eta_batt_dis']*Battery['K_batt']              
                CorrPVsc = LoadDiff- CorrGridImp - CorrBatDiss
#                print ('reduce battery and Import AND PV'
    elif -Precision<LoadDiff<Precision:
        print ('Load ok!')
    elif LoadDiff>Precision:
#        print ('not enough Load: ', LoadDiff
        CorrGridImp = LoadDiff  # Get load from Gridimport, add grid import
    else: print ('WARNUNG Nachregelung Load!')
     
     
     #-------------- ADD self discharge of BATTERY--------------
      
    # PV Differenz  
    if PVDiff<=-Precision:   
#        print ('too much PV: ',PVDiff
        if Opt_Result['P_PV_exp'][Opt_Result.index[0]]+CorrPVexp > -PVDiff:
            CorrPVexp = PVDiff  # reduce PVexport - not necessarily (min_Costs)
            CorrPVsc = -PVDiff  # add to SC
#            print ('100% Reduce PVexport'
        elif Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar > -PVDiff:
            CorrBatChar = PVDiff   # reduce battery charge
            CorrBatSOC = PVDiff * Battery['eta_batt_char']*Battery['K_batt']                      
            CorrPVsc = PVDiff # reduce to SC
#            print ('100% Reduce Battery charge'
        else:
            # first no PVexport
            CorrPVexp = -(Opt_Result['P_PV_exp'][Opt_Result.index[0]]+CorrPVexp)  #neg
            # rest from Battery charge
            if PVDiff- CorrPVexp >= -(Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar) :   #neg neg
                CorrBatChar = PVDiff- CorrGridexp
                CorrBatSOC = CorrBatChar*Battery['eta_batt_char']*Battery['K_batt']              
#               print ('reduce battery charge and Exprt'
                CorrPVsc = -CorrBatChar + CorrPVexp
            else:
                CorrBatChar = -(Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar)    
                CorrBatSOC = CorrBatChar*Battery['eta_batt_char']*Battery['K_batt']              
                #                neg        neg           neg
                CorrPVsc = PVDiff-CorrPVexp-CorrBatChar
                # --- Load ??? CorrPVsc = LoadDiff- CorrGridImp - CorrBatDiss
#                print ('reduce battery charing and Export  AND Load'
#                print ('TEST PVsc:',PVDiff,'-', CorrPVexp,'+', CorrBatChar
    elif -Precision<=PVDiff<=Precision:
         print ('PV ok!')
    elif PVDiff>Precision:
#        print ('not enough PV: ', PVDiff)
        SOCtot = (PVDiff + Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar) *\
        Battery['eta_batt_char']*Battery['K_batt']        
        if  Opt_Result['SOC_batt'][Opt_Result.index[0]]+CorrBatSOC+SOCtot<=Battery['SOC_batt_max']\
            and Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar+PVDiff<=Battery['P_batt_char_max']:
            # Charge/Load Battery                
            CorrBatChar = PVDiff                  
            #  SOC
            CorrBatSOC = PVDiff*Battery['eta_batt_char']*Battery['K_batt']  
            CorrPVsc = PVDiff # check for SC-equation
            #print ('New Battery:', CorrBatChar, CorrBatSOC
#            print ('Charge battery'
        else:
            CorrPVexp = PVDiff # Add to Gridimp
            
            CorrPVsc = PVDiff # check for SC-equation
        # Load Battery if possible
       # else add to PVexport
    else: 
        print ('WARNUNG Nachregelung PV!')

    #-----------------------------------------------------------------            
       # only to test if Battery can still discharge into the grid
    BattLoadDiff = LoadPeriodReal['ELoad'][Opt_Result.index[0]] \
    -Opt_Result['P_batt_dis'][Opt_Result.index[0]]- CorrBatDiss    
        # Discharge into the grid ?
    if BattLoadDiff < Precision:
#        print ('Battery --------------------',BattLoadDiff,\
        LoadPeriodReal['ELoad'][Opt_Result.index[0]],\
        Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss
    else: 
         print ('Battery ok'   )
   #-----------------------------------------------------------------                    
    CorrGridexp = CorrPVexp 
               
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
    print ("I am just a poor Correction-Programm without any idea of running.\
    Please ask my friend OptFlex_MPC!")
   