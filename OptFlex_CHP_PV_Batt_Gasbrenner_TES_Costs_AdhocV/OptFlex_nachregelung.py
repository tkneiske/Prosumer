# -*- coding: utf-8 -*-
"""
MPC_Costen_PV_Battery
Created on Mon Sep 28 20:33:54 2015
Neue Idee fertig und validiert am 9.11
@author: tkneiske
"""
import matplotlib.pyplot as plt
import pandas as pd


def AdHoc_MPC(Result_BAT_End, Result_PV_End,\
            Result_Grid_End, PVavaFore, PVR,\
            ELoadFore, timestep, Battery, \
             ELoadR, Q1LoadR, Q2LoadR):    

   BattDis = Result_BAT_End['Battery dis-charging'][timestep]
   BattCh  = Result_BAT_End['Battery charging'][timestep]
   BattSOC = Result_BAT_End['SOC battery'][timestep]     
   
   PV2Load = Result_PV_End['PV load selfcon'][timestep] #sc
   PV2Batt = Result_PV_End['PV batt selfcon'][timestep]  #sc
   PVExp = Result_PV_End['PV Grid export'][timestep] 
      
   GridExp = Result_Grid_End['Grid Export'][timestep]
   GridImp = Result_Grid_End['Grid Import'][timestep]
    

   # New values after correction
   CorrGridExp = GridExp 
   CorrGridImp = GridImp  
   CorrPVexp = PVExp
   CorrBattDis = BattDis
   CorrBattCh = BattCh
   CorrBatSOC = BattSOC
   CorrPV2Batt = PV2Batt #sc
   CorrPV2Load = PV2Load #sc
     
   #------------------------------------------------------------------------
   #   Get real values for Energyflows: PV2Load, PV2Batt, GridExp, GridImp  
   #------------------------------------------------------------------------

   #------------------------------------------------------------------------
   # Step 1: check if PV2Load and PV2Batt possible ?
   #------------------------------------------------------------------------

   # -- PV2Load -- 1.Priorität
   if ELoadR >= PV2Load  and PVR >= PV2Load: #beides ok
       PV2LoadR = PV2Load
   elif ELoadR >= PV2Load :  # nicht genug PV
       PV2LoadR = PVR
   elif PVR >= PV2Load:    # nicht genug ELoad
       PV2LoadR = ELoadR
   else:
       if PVR <= ELoadR:
           PV2LoadR = PVR
       else:
           PV2LoadR = ELoadR
                
   # -- PV2Batt -- 2.Priorität
   if PVR - PV2LoadR >= PV2Batt:  #  ok
       PV2BattR = PV2Batt
   else:
       PV2BattR = PVR - PV2LoadR # Rest PV in Battery
   
   #----------------------------------------------------------------
   #  Step 2) Battery charging and discharging possible ?
   #----------------------------------------------------------------  
   #print 'Battery: ', BattDis, BattCh, BattSOC
   if BattDis > 0:   # Batterie entläd   
   #       print "Batterie DIS"
          if BattDis > ELoadR-PV2LoadR:  
               CorrBattDis = ELoadR-PV2LoadR                          
               BattSOCalt = BattSOC + BattDis / Battery['eta_batt_dis']*Battery['K_batt']            
               CorrBatSOC = BattSOCalt - CorrBattDis / Battery['eta_batt_dis']*Battery['K_batt']
          elif BattDis <= ELoadR-PV2LoadR:  # ok
               CorrBattDis = BattDis
               CorrBatSOC = BattSOC 
   elif BattDis == 0: #   1) Battery läd oder 2) Battery ruht
    #       print "Batterie NO"
           if BattCh > PVR - PV2LoadR:
               CorrBattCh = PVR - PV2LoadR
               BattSOCalt = BattSOC - BattCh * Battery['eta_batt_char']*Battery['K_batt']
               CorrBatSOC = BattSOCalt + BattCh * Battery['eta_batt_char']*Battery['K_batt']           
           elif BattCh <= PVR - PV2LoadR:
               CorrBattCh = BattCh
               CorrBatSOC = BattSOC
   else:
       print 'Battery Discharing is negativ!'

   #----------------------------------------------------------------
   #  Step 3)    Correct  Grid  Import and Export
   #----------------------------------------------------------------
   CorrGridImp = ELoadR - PV2LoadR - CorrBattDis   
   CorrPVexp = PVR - PV2BattR - PV2LoadR
   CorrPV2Load = PV2LoadR
   CorrPV2Batt = PV2BattR
   CorrGridExp = CorrPVexp
   
   if CorrGridImp > 0 and CorrGridExp > 0:
       if CorrPVexp < CorrGridImp:
           CorrPV2Load = CorrPV2Load + CorrPVexp
           CorrPVexp = 0
       elif CorrPVexp > CorrGridImp:
           CorrPV2Load = CorrPV2Load + CorrGridImp
           CorrPVexp = CorrPVexp-CorrGridImp
           CorrGridImp = 0           
       else:
           CorrPV2Load = CorrPVexp
           CorrPVexp = 0
           CorrGridImp = 0
            
   CorrGridExp = CorrPVexp       
   # ------------------------------------------------------------------
        
   CorrTerms = pd.Series([ CorrBattDis, CorrBattCh, CorrBatSOC, \
   CorrGridImp, CorrGridExp,  CorrPVexp, CorrPV2Batt, CorrPV2Load],\
           index = ['CorrBattDis', 'CorrBattCh','CorrBatSOC',\
           'CorrGridImp', 'CorrGridExp', 'CorrPVexp', 'CorrPV2Batt','CorrPV2Load'])
   #print CorrTerms
   return CorrTerms                                    
                                    
if __name__ == '__main__':
    plt.close("all")
    print "I am just a poor Correction-Programm without any idea of running.\
    Please ask my friend OptFlex_MPC!"
   