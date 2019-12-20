# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 20:33:54 2015

@author: tkneiske
"""
import matplotlib.pyplot as plt
import pandas as pd


def AdHoc_MPC(Result_BAT_End, Result_PV_End,\
            Result_Grid_End, PVavaFore, PVavaRealnow,\
            ELoadFore, timestep, Battery, \
             ELoadR, Q1LoadR, Q2LoadR):    
   Precision = 0.001    # How close to 0 is allowed
   CorrGridExp = 0  
   CorrGridImp = 0  
   CorrPVexp = 0
   CorrBattDis = 0
   CorrBattCh = 0
   CorrBatSOC = 0
   CorrPV2Batt =0 #sc
   CorrPV2Load =0 #sc
     
   BattDis = Result_BAT_End['Battery dis-charging'][timestep]
   BattCh  = Result_BAT_End['Battery charging'][timestep]
   BattSOC = Result_BAT_End['SOC battery'][timestep]     
   
   PV2Load = Result_PV_End['PV load selfcon'][timestep] #sc
   PV2Batt = Result_PV_End['PV batt selfcon'][timestep]  #sc
   PVExp = Result_PV_End['PV Grid export'][timestep] 
      
   GridExp = Result_Grid_End['Grid Export'][timestep]
   GridImp = Result_Grid_End['Grid Import'][timestep]
    
   # --------------------------------------------  
   # ------------- E-Load ------------------------
   # --------------------------------------------  
   LoadDiff =  ELoadR-ELoadFore[timestep]
   #print 'LoadDiff', LoadDiff,  'GridImp', GridImp, 'BattDis',BattDis, 'PV2Load', PV2Load

   if LoadDiff<-Precision:
         print 'too much Load predicted: ',LoadDiff
         
         # Check load from Battery --> Battery less discharge
         if BattDis > -LoadDiff:
             CorrBattDis =LoadDiff
             CorrBatSOC = -LoadDiff/Battery['eta_batt_dis']*Battery['K_batt']  
             print 'reduce 100% Battery'        
             
         #  reduce GridImport        
         elif GridImp > -LoadDiff:
             CorrGridImp = LoadDiff
             print 'reduce 100% Import'
    
         #  reduce Grid, Batt AND PV Consumption   
         else:
             #reduce Grid AND Batt
             CorrGridImp = -GridImp    # GridImp = 0 
             if LoadDiff- CorrGridImp >= -BattDis :   #neg neg
                 CorrBattDis = LoadDiff- CorrGridImp
                 CorrBatSOC = -CorrBattDis/Battery['eta_batt_dis']*Battery['K_batt']              
                 print 'reduce battery and Import'
             else:
                 CorrBattDis = -BattDis    # BatDis = 0
                 CorrBatSOC = -CorrBattDis/Battery['eta_batt_dis']*Battery['K_batt'] 
                 #                            neg          neg           neg
                 CorrPV2Load = LoadDiff -CorrGridImp - CorrBattDis
                 print 'reduce battery and Import and PV2Load'
     #elif -Precision<LoadDiff<Precision:
     #    print 'Load ok!'
   elif LoadDiff>Precision:
         print 'not enough Load: ', LoadDiff
         CorrGridImp = LoadDiff  # Get load from Gridimport, add grid import
   else: print 'Load ok!'

 #      #-------------- ADD self discharge of BATTERY--------------
                                       
   # --------------------------------------------  
   # -------------- Q-Load ----------------------                                        
   # --------------------------------------------  
   
   # --------------------------------------------  
   # -------------- PV---------------------------
   # --------------------------------------------  
   PVDiff =  PVavaRealnow-PVavaFore[timestep]
   print PVDiff
   if PVDiff<=-Precision:   
        print 'too much PV predicted: ',PVDiff
        if PVExp > -PVDiff:
             CorrPVexp = PVDiff  # reduce PVexport - not necessarily (min_Costs)
             print '100% Reduce a part of PVexport'
        elif BattCh  > -PVDiff:
             CorrBattCh = PVDiff   # reduce battery charge
             CorrPV2Batt = CorrBattCh                     
             CorrBatSOC = PVDiff * Battery['eta_batt_char']*Battery['K_batt']              
             print '100% Reduce a part of Battery charge'
        else:
             # first: no PVexport
             CorrPVexp = CorrPVexp-PVExp  #neg
             # rest from Battery charge
             # PV_Differenz - PVexp > BattCh
             if PVDiff- CorrPVexp >= -BattCh :   #neg neg
                 CorrBattCh = PVDiff- CorrGridExp
                 CorrPV2Batt = CorrBattCh
                 CorrBatSOC = CorrBattCh*Battery['eta_batt_char']*Battery['K_batt']              
                 print 'reduce battery charge and Export completely'                 
             else: 
                 CorrBattCh = -BattCh
                 CorrPV2Batt = CorrBattCh
                 CorrBatSOC = CorrBattCh*Battery['eta_batt_char']*Battery['K_batt']              
                 # rest from Load              neg     neg        neg
                 CorrPV2Load =  PVDiff - CorrPVexp- CorrBattCh 
                 print 'reduce battery charing and Export  AND Load'
 #                print 'TEST PVsc:',PVDiff,'-', CorrPVexp,'+', CorrBatChar             
   #elif -Precision<=PVDiff<=Precision:
   #       print 'PV ok!'
   elif PVDiff>Precision:
         print 'not enough PV predicted: ', PVDiff
         SOCtot = (PVDiff + BattCh + CorrBattCh) *\
         Battery['eta_batt_char']*Battery['K_batt']        
         # wenn Batterie noch nicht voll und Ladeleistung noch nicht erreicht
         if  BattSOC + CorrBatSOC + SOCtot<=Battery['SOC_batt_max']\
             and BattCh + CorrBattCh + PVDiff <= Battery['P_batt_char_max']:
             # Charge/Load Battery     # Load Battery if possible
             CorrBattCh = PVDiff                  
             CorrPV2Batt = CorrBattCh
             #  SOC
             CorrBatSOC = PVDiff*Battery['eta_batt_char']*Battery['K_batt']  
             #print 'New Battery:', CorrBatChar, CorrBatSOC
             print 'Charge battery'
         else:
            # else add to PVexport
            CorrPVexp = PVDiff 
   else: 
         print 'PV ok!'
 
#==============================================================================
#    # Extreme Case: PV and Load was predicted so high that GridImport is needed
#    # to cover the load  instead of PVsc
#    if  PV2Load+CorrPV2Load < 0:
#        #print PV2Load,'+',CorrPV2Load
#        CorrGridImp = -(PV2Load+CorrPV2Load)
#        CorrPV2Load = - PV2Load
#        
#    CorrGridExp = CorrGridExp + CorrPVexp 
#    
#==============================================================================
   
   CorrTerms = pd.Series([LoadDiff, CorrBattDis, CorrBattCh, CorrBatSOC, \
   CorrGridImp, CorrGridExp, CorrPV2Batt, CorrPVexp, CorrPV2Load],\
           index = ['LoadDiff', 'CorrBattDis', 'CorrBattCh','CorrBatSOC',\
           'CorrGridImp', 'CorrGridexp', 'CorrPV2Batt','CorrPVexp', 'CorrPV2Load'])
   
   return CorrTerms                                    
                                    


#==============================================================================
# def Correct_MPC(Opt_Result, PVavaPeriodReal, PVavaPeriodFore, 
#                                         LoadPeriodReal, LoadPeriodFore,Battery):    
#     LoadDiff =  LoadPeriodReal['ELoad'][Opt_Result.index[0]]-LoadPeriodFore['ELoad'][Opt_Result.index[0]] 
#     PVDiff =  PVavaPeriodReal['PV 2013, Kassel, 10min'][Opt_Result.index[0]]-PVavaPeriodFore['PV 2013, Kassel, 10min'][Opt_Result.index[0]]                                        
#     CorrGridImp = 0
#     CorrPVexp = 0
#     CorrBatDiss = 0
#     CorrBatChar = 0
#     Precision = 0.001    # How close to 0 is allowed
#     CorrBatSOC = 0
#     CorrGridexp = 0 
#     CorrPVsc =0
#     
#     # Load Differenz
#     if LoadDiff<-Precision:
# #        print 'too much Load: ',LoadDiff
#         # Check load from Battery --> Battery less discharge
#         if Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss > -LoadDiff:
#             CorrBatDiss = LoadDiff
# #            print 'reduce 100% Battery', Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss
#             CorrBatSOC = -LoadDiff/Battery['eta_batt_dis']*Battery['K_batt']  
#         #  reduce GridImport        
#         elif Opt_Result['P_Grid_import'][Opt_Result.index[0]]+CorrGridImp > -LoadDiff:
#             CorrGridImp = LoadDiff
# #            print 'reduce 100% Import', Opt_Result['P_Grid_import'][Opt_Result.index[0]]
#         #  reduce PV Consumption   
#         else:
#             CorrGridImp = -Opt_Result['P_Grid_import'][Opt_Result.index[0]]+CorrGridImp    
#             if LoadDiff- CorrGridImp >= -Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss :   #neg neg
#                 CorrBatDiss = LoadDiff- CorrGridImp
#                 CorrBatSOC = -CorrBatDiss/Battery['eta_batt_dis']*Battery['K_batt']              
# #                print 'reduce battery and Import'
#             else:
#                 CorrBatDiss = -Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss    
#                 CorrBatSOC = -CorrBatDiss/Battery['eta_batt_dis']*Battery['K_batt']              
#                 CorrPVsc = LoadDiff- CorrGridImp - CorrBatDiss
# #                print 'reduce battery and Import AND PV'
#     elif -Precision<LoadDiff<Precision:
#         print 'Load ok!'
#     elif LoadDiff>Precision:
# #        print 'not enough Load: ', LoadDiff
#         CorrGridImp = LoadDiff  # Get load from Gridimport, add grid import
#     else: print 'WARNUNG Nachregelung Load!'
#      
#      
#      #-------------- ADD self discharge of BATTERY--------------
#       
#     # PV Differenz  
#     if PVDiff<=-Precision:   
# #        print 'too much PV: ',PVDiff
#         if Opt_Result['P_PV_exp'][Opt_Result.index[0]]+CorrPVexp > -PVDiff:
#             CorrPVexp = PVDiff  # reduce PVexport - not necessarily (min_Costs)
#             CorrPVsc = -PVDiff  # add to SC
# #            print '100% Reduce PVexport'
#         elif Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar > -PVDiff:
#             CorrBatChar = PVDiff   # reduce battery charge
#             CorrBatSOC = PVDiff * Battery['eta_batt_char']*Battery['K_batt']                      
#             CorrPVsc = PVDiff # reduce to SC
# #            print '100% Reduce Battery charge'
#         else:
#             # first no PVexport
#             CorrPVexp = -(Opt_Result['P_PV_exp'][Opt_Result.index[0]]+CorrPVexp)  #neg
#             # rest from Battery charge
#             if PVDiff- CorrPVexp >= -(Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar) :   #neg neg
#                 CorrBatChar = PVDiff- CorrGridexp
#                 CorrBatSOC = CorrBatChar*Battery['eta_batt_char']*Battery['K_batt']              
# #               print 'reduce battery charge and Exprt'
#                 CorrPVsc = -CorrBatChar + CorrPVexp
#             else:
#                 CorrBatChar = -(Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar)    
#                 CorrBatSOC = CorrBatChar*Battery['eta_batt_char']*Battery['K_batt']              
#                 #                neg        neg           neg
#                 CorrPVsc = PVDiff-CorrPVexp-CorrBatChar
#                 # --- Load ??? CorrPVsc = LoadDiff- CorrGridImp - CorrBatDiss
# #                print 'reduce battery charing and Export  AND Load'
# #                print 'TEST PVsc:',PVDiff,'-', CorrPVexp,'+', CorrBatChar             
#     elif -Precision<=PVDiff<=Precision:
#          print 'PV ok!'
#     elif PVDiff>Precision:
# #        print 'not enough PV: ', PVDiff
#         SOCtot = (PVDiff + Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar) *\
#         Battery['eta_batt_char']*Battery['K_batt']        
#         if  Opt_Result['SOC_batt'][Opt_Result.index[0]]+CorrBatSOC+SOCtot<=Battery['SOC_batt_max']\
#             and Opt_Result['P_batt_char'][Opt_Result.index[0]]+CorrBatChar+PVDiff<=Battery['P_batt_char_max']:
#             # Charge/Load Battery                
#             CorrBatChar = PVDiff                  
#             #  SOC
#             CorrBatSOC = PVDiff*Battery['eta_batt_char']*Battery['K_batt']  
#             CorrPVsc = PVDiff # check for SC-equation
#             #print 'New Battery:', CorrBatChar, CorrBatSOC
# #            print 'Charge battery'
#         else:
#             CorrPVexp = PVDiff # Add to Gridimp
#             
#             CorrPVsc = PVDiff # check for SC-equation
#         # Load Battery if possible
#        # else add to PVexport
#     else: 
#         print 'WARNUNG Nachregelung PV!'
# 
#     #-----------------------------------------------------------------            
#        # only to test if Battery can still discharge into the grid
#     BattLoadDiff = LoadPeriodReal['ELoad'][Opt_Result.index[0]] \
#     -Opt_Result['P_batt_dis'][Opt_Result.index[0]]- CorrBatDiss    
#         # Discharge into the grid ?
#     if BattLoadDiff < Precision:
# #        print 'Battery --------------------',BattLoadDiff,\
#         LoadPeriodReal['ELoad'][Opt_Result.index[0]],\
#         Opt_Result['P_batt_dis'][Opt_Result.index[0]]+CorrBatDiss
#     else: 
#          print 'Battery ok'   
#    #-----------------------------------------------------------------                    
#     CorrGridexp = CorrPVexp 
#                
#     CorrTerms = pd.Series([LoadDiff, PVDiff, CorrBatDiss, CorrBatChar, CorrBatSOC, \
#     CorrGridImp, CorrPVexp, CorrGridexp, CorrPVsc],\
#            index = ['LoadDiff', 'PVDiff', 'CorrBatDiss', 'CorrBatChar','CorrBatSOC',\
#            'CorrGridImp', 'CorrPVexp','CorrGridexp', 'CorrPVsc'])
#    
#     return CorrTerms
# 
#==============================================================================

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
   