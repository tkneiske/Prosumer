# -*- coding: utf-8 -*-
"""
MPC_Costen_CHP_PV_Battery_TES_Aux
Created on Mon Sep 28 20:33:54 2015
neue Idee angefangen am 9.11.2015 übernommen aus PV-Battery code
@author: tkneiske
"""
import matplotlib.pyplot as plt
import pandas as pd
import OptFlex_MPC as main

def AdHoc_MPC(Result_BAT_End, Result_PV_End, Result_Heat_End,\
            Result_TES_End, Result_CHP_End,\
            Result_Grid_End, PVavaFore, PVR,\
            ELoadFore, Q1LoadFore,Q2LoadFore,timestep, Battery, ThermalStorage,\
            ELoadR, Q1LoadR, Q2LoadR, CHP):    

   BattDis = Result_BAT_End['Battery dis-charging'][timestep]
   BattCh  = Result_BAT_End['Battery charging'][timestep]
   BattSOC = Result_BAT_End['SOC battery'][timestep]     
   
   TESDis = Result_TES_End['TES dis-charging'][timestep]
   TESCh  = Result_TES_End['TES charging'][timestep]
   TESSOC = Result_TES_End['SOC TES'][timestep]     
   
   PV2Load = Result_PV_End['PV load selfcon'][timestep] #sc
   PV2Batt = Result_PV_End['PV batt selfcon'][timestep]  #sc
   PVExp = Result_PV_End['PV Grid export'][timestep] 

   CHP2Load = Result_CHP_End['CHP load self'][timestep] #sc
   CHP2Batt = Result_CHP_End['CHP batt self'][timestep]  #sc
   CHPExp = Result_CHP_End['CHP Export'][timestep] 
   CHPel = Result_CHP_End['CHP el'][timestep]       
   CHPth = Result_CHP_End['CHP th'][timestep] 
   CHPonoff = Result_CHP_End['CHP on_off'][timestep] 
      
   GridExp = Result_Grid_End['Grid Export'][timestep]
   GridImp = Result_Grid_End['Grid Import'][timestep]
    
   AuxGas = Result_Heat_End['Aux Gasbrenner'][timestep]
   Precision = 1e-5
   # New values after correction
   CorrGridExp = GridExp 
   CorrGridImp = GridImp  
   CorrBattDis = BattDis
   CorrBattCh = BattCh
   CorrBatSOC = BattSOC
   CorrPVexp = PVExp
   CorrPV2Batt = PV2Batt #sc
   CorrPV2Load = PV2Load #sc
   CorrTESDis = TESDis
   CorrTESCh = TESCh
   CorrTESSOC = TESSOC
   CorrCHP2Load =  CHP2Load  
   CorrCHP2Batt = CHP2Batt 
   CorrCHPExp = CHPExp 
   CorrCHPel = CHPel 
   CorrCHPth = CHPth 
   CorrCHPonoff = CHPonoff 
   if AuxGas > Precision : # 1e-5
       CorrAuxGas = AuxGas
   elif AuxGas < -Precision:
       CorrAuxGas = -42
   else: 
       CorrAuxGas = 0
   CorrTEStoofull = 0
   CorrTEStooempty = 0
 

   #----------------------------------------------------------------
   #    TES
   #----------------------------------------------------------------
   print 'CH/Dis/SOC/Load /Aux: ',TESCh, TESDis, TESSOC, Q1LoadR+Q2LoadR, AuxGas
   print 'PVR/CH/Dis/SOC/Load : ',PVR,BattCh, BattDis, BattSOC, ELoadR
   # ---------- läd und entläd     , CHP oder Gasboiler ----------
   if TESDis > Precision and TESCh > Precision: 
       print "Ch 1 Dis 1"
       #Lade Wärmespeicher bis er voll ist und mehr, Frage Wieviel ist "mehr"?  
       if TESDis > Q1LoadR+Q2LoadR: # too much heat                      
           CorrTESDis = Q1LoadR+Q2LoadR   
           CorrTESCh = TESCh# + ??????(TESDis-Q1LoadR+Q2LoadR) # nur wenn speicher voll ist !
           TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                             - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
           checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                          - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
           if checkTESSOC > 100: # Lade trotzdem in Speicher
                              CorrTEStoofull = checkTESSOC-100#-checkTESSOC /ThermalStorage['eta_TES_char']/ThermalStorage['K_TES']                                                  
                              print "Warining: TES overload"  
                              
           CorrTESSOC = checkTESSOC                                              
       elif TESDis == Q1LoadR+Q2LoadR:    
           CorrTESCh = TESCh
           CorrTESDis = TESDis
           CorrTESSOC = TESSOC
       elif TESDis < Q1LoadR+Q2LoadR:    # not enough heat, discharge storage  
           CorrTESCh = TESCh
           CorrTESDis = Q1LoadR+Q2LoadR           
           print 'More QLoad than Discharge', CorrTESDis       
           TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                                 - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
           checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                  - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
           if checkTESSOC <= 0:               #if TES Empty start Gasboiler
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
               CorrTESDis = Q1LoadR+Q2LoadR   
 #              CorrTESCh =  CorrTEStooempty # Charge Heat when TES empty
               print 'SOC = 100%, AuxGas'
         
           CorrTESSOC = checkTESSOC   
               
   #--------  nur entladen aus Speicher, CHP, Gasb AUS ----------      
   elif TESDis > Precision and TESCh < Precision:     
           print "Ch 0 Dis 1"
           CorrTESCh = 0
           if TESDis > Q1LoadR+Q2LoadR: # too much heat
               print "Wärme kommt aus Speicher!"
               if Q1LoadR+Q2LoadR > 0: 
                   print 'Q>0'
                   CorrTESDis = Q1LoadR+Q2LoadR   
                   
                   TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis'])*ThermalStorage['K_TES']                   
                   checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                              - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
                   if checkTESSOC > 100: # Lade trotzdem in Speicher
                       CorrTEStoofull = checkTESSOC-100#-checkTESSOC /ThermalStorage['eta_TES_char']/ThermalStorage['K_TES']                                                  
                       print "Warining: TES overload"  
                   CorrTESSOC = checkTESSOC                                    
               elif Q1LoadR+Q2LoadR == 0:                    
                    print 'Q=0'
                    CorrTESDis = 0
                   
                    TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis'])*ThermalStorage['K_TES']                       
                    CorrTESSOC = TESSOCalt
           elif TESDis == Q1LoadR+Q2LoadR:    
               print 'Dis == QLoad'
               
               CorrTESDis = TESDis
               CorrTESSOC = TESSOC
           elif TESDis < Q1LoadR+Q2LoadR:    # not enough heat, discharge storage 
                   
                   CorrTESDis = Q1LoadR+Q2LoadR                                    
                   print "Wärme kommt aus Speicher, Last ist größer !", CorrTESDis 
                   TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                       - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
                   checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                       - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES'] 
                   if checkTESSOC <= 0:               #if TES Empty start Gasboiler
                       CorrTESSOC = 0
                       CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
                       CorrTESDis = Q1LoadR+Q2LoadR           
#                       CorrTESCh =  CorrTEStooempty # Charge Heat when TES empty
                   else:  #tes soc ok
                       CorrTESSOC = checkTESSOC  
           else: 
                 print "Warning: Something wrong with Charge = ON & Discharge == off!"
  #--------  nur laden CHP, Gasb , no Q-LOAD ----------              
   elif TESCh > Precision and TESDis < Precision:     # no discharge  
        print "Ch 1 Dis 0"   
        if Q1LoadR+Q2LoadR <= 0:
            CorrTESCh = TESCh
            CorrTESDis = TESDis
            CorrTESSOC = TESSOC
        elif Q1LoadR+Q2LoadR >= 0:
            CorrTESDis = Q1LoadR+Q2LoadR
            CorrTESCh =  TESCh
            TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                                 - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
            checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                  - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES'] 
            if checkTESSOC < 0:               #if TES Empty start Gasboiler
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
               CorrTESDis = Q1LoadR+Q2LoadR         
 #              CorrTESCh = CorTEStooempty
            else:  #tes soc ok
               CorrTESSOC = checkTESSOC    
        elif Q1LoadR+Q2LoadR <= 0:  
            print 'Warning: negativ QLoads!'                         
   elif TESCh < Precision and TESDis < Precision: # both are 0 or negative
        print "Ch 0 Dis 0"
        CorrTESCh = 0
        if Q1LoadR+Q2LoadR == 0: # no load          
            CorrTESDis = 0
            CorrTESSOC = TESSOC
        elif Q1LoadR+Q2LoadR > 0: # load exists
            CorrTESDis = Q1LoadR+Q2LoadR           
            TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                                 - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
            checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                  - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES'] 
            if checkTESSOC <= 0:               #if TES Empty start Gasboiler
               print 'TES LEER!' 
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
               CorrTESDis = Q1LoadR+Q2LoadR    
 #              CorrTESCh =CorrTEStooempty
            #   AuxGas =  restPower
          #     CorrTESCh = AuxGas
            else:  #tes soc ok
               print 'SOC ok'
               CorrTESSOC = checkTESSOC    
        elif Q1LoadR+Q2LoadR < 0:    # load negative??
            print 'Warning: negativ QLoads!'                
   else: 
       print "CH - Dis -  --- Warning, something wrong ---"                    
   #----------------------------------------------------------------
   # CorrTEStooempty
   #----------------------------------------------------------------
   if CorrTEStooempty > 0:
       print 'CorrTEStooempty', CorrTESCh, CorrAuxGas, CorrTEStooempty
       CorrAuxGas = CorrAuxGas +  CorrTEStooempty
       CorrTESCh = CorrTESCh + CorrTEStooempty
       print 'CorrTEStooempty', CorrTESCh, CorrAuxGas, CorrTEStooempty
   
   #----------------------------------------------------------------
   #   CHP 
   #----------------------------------------------------------------
  # print 'CHP: ', CHPel, CHPth, CHPonoff          
   # No Change for CHP so far 
   CHPelR = CHPel
   CorrCHPel = CHPelR    
          
#==============================================================================
# JUST IN CASE THE CHP SHOULD BE SWITCHED ON AND OFF FOR CORRECTION "!!!!          
#    if CorrTESCh > 0.001:
#       ... 

#         ...  
#         if CHPth+AuxGas > CorrTESDis:
#            CorrAuxGas = CorrTESDis - CHPth
#            if CHPth > CorrTESDis - CorrAuxGas:
#                SOCcheck= (CHPth-CorrTESDis) * ThermalStorage['eta_TES_char']*ThermalStorage['K_TES']                          
#                if CorrTESSOC+SOCcheck <= ThermalStorage['SOC_TES_max']:
#                    # charge TES
#                    CorrTESCh = CorrTESCh + (CHPth-CorrTESDis)    
#                    CorrTESSOC = CorrTESSOC+SOCcheck
#                else:           
#                    CorrCHPth = CorrTESDis  # moduliert 
#
#            elif CHPth <= CorrTESDis:
#                CorrAuxGas = CorrTESDis-CHPth
#        else:
#            CorrAuxGas = CorrTESDis-CHPth-AuxGas
#    else:        
#        CorrAuxGas = 0
#        CorrCHPonoff = 0
#            
#   CHP_gas = CorrCHPth / CHP['eta_CHP_th']
#  CHPelR = CHP_gas * CHP['eta_CHP_el']
#    if CHPelR == 0:
#       CorrCHPonoff = 0
#    CorrCHPel = CHPelR
#==============================================================================
   #------------------------------------------------------------------------
   # PV2Load and PV2Batt
   #------------------------------------------------------------------------
   
   # -- PV2Load/CHP2Load -- 1.Priorität
   if ELoadR >= PV2Load + CHP2Load  and PVR >= PV2Load and CHPelR >= CHP2Load: #alles ok
       PV2LoadR = PV2Load
       CHP2LoadR = CHP2Load    
       print 'L PV CHP'            
   elif ELoadR >= PV2Load + CHP2Load and PVR >= PV2Load : # nicht genug CHPel
       print 'L PV -'            
       if CHPelR < ELoadR:
           if PV2Load >= ELoadR-CHPelR:
               CHP2LoadR = CHPelR  # CHP eigenverbrauch VOR PV Eigenverbrauch 
               PV2LoadR = ELoadR -CHP2LoadR  # mehr PV eigen möglich
           else:               
               CHP2LoadR = CHPelR  
               PV2LoadR = PV2Load   # PV Load - wie gehabt
       else:
           CHP2LoadR = ELoadR  # max CHP Eigenverbrauch
           PV2LoadR = 0 # kein PV Eigenverbrauch
   elif ELoadR >= PV2Load + CHP2Load and CHPelR >= CHP2Load:  # nicht genug PV
        print 'L - CHP'            
        if PVR < ELoadR - CHP2Load: # CHP Eigenverbrauch vor PV Eigenverbrauch 
           PV2LoadR = PVR  # reduziere PV2Load
           CHP2LoadR = CHPelR# statt CHP2Load vorschlag 25.5.16             
           print '1.Nachregelung-Schleife: ', CHP2LoadR, CHP2Load
        else:
           CHP2LoadR = CHP2Load               
           PV2LoadR = ELoadR-CHP2LoadR        # 100% Eigenverbrauch
   elif PVR >= PV2Load and CHPelR >= CHP2Load:   # nicht genug ELoad
       print '- PV CHP'            
       if CHP2Load <= ELoadR:  #genug load für CHP?
           CHP2LoadR = CHP2Load                      
           PV2LoadR = ELoadR - CHP2LoadR       # rest durch PV
       else:
           CHP2LoadR = ELoadR # 100% lastdeckung durch CHP
           PV2LoadR = 0
   elif PVR >= PV2Load:   # nicht genug ELoad und CHPel
       print '- PV -'            
       if PV2Load <= ELoadR:
           PV2LoadR = PV2Load # PV bevorzugt
           if CHP2Load <= ELoadR - PV2LoadR:  
              CHP2LoadR = ELoadR - PV2LoadR
           else:
               CHP2LoadR = ELoadR-PV2LoadR
       elif PV2Load > ELoadR:
           PV2LoadR = ELoadR # 100 PV Lastdeckung
           CHP2LoadR = 0
   elif ELoadR >= PV2Load + CHP2Load: # nicht genug CHPel und PV
      print 'L - - '            
      if ELoadR > CHPelR:
               CHP2LoadR = CHPelR
               if PVR > ELoadR - CHP2LoadR:  # ACHTUNG bei großen Netzeinspeisungen
                   PV2LoadR = ELoadR - CHP2LoadR
               else:
                   PV2LoadR = PVR #100% pv into Load
      else:                    
               CHP2LoadR = ELoadR # 100% Load Deckung from CHP
               PV2LoadR = 0 
   elif CHPelR >= CHP2Load:   # nicht genug ELaod and PV       
       print '- - CHP'                   
       if ELoadR > CHP2Load:        
           CHP2LoadR = CHP2Load
           if PVR > ELoadR - CHP2LoadR:  # ACHTUNG bei großen Netzeinspeisungen
                   PV2LoadR = ELoadR - CHP2LoadR
           else:
                   PV2LoadR = PVR #100% pv into Load
       else:           
           CHP2LoadR = ELoadR #100 Lastdeckung durhc CHP
           PV2LoadR = 0
   else:   # everthing not enough
       print '- - - '                   
       if ELoadR > CHPelR: #----> hier FEHLER 25.5.16 ************************************  
           CHP2LoadR = CHPelR
           if PVR >= ELoadR - CHP2LoadR:
               PV2LoadR = ELoadR - CHP2LoadR # 100%  Deckung durch PV und CHP
           else:
               PV2LoadR = PVR  
       else:
          CHP2LoadR = ELoadR
          PV2LoadR = 0
           
   # -- CHP2Batt Prio2
   if CHPelR-CHP2LoadR >= CHP2Batt:
        CHP2BattR = CHP2Batt
   else:
        CHP2BattR = CHPelR-CHP2LoadR
                
   # -- PV2Batt -- 2.Priorität
   if PVR - PV2LoadR >= PV2Batt:  #  ok
       PV2BattR = PV2Batt
       #print 'PV2BAtt', PVR, PV2Batt
   elif PVR - PV2Load<0 :
       print "'Warning PV2Batt NEGATIV!"
       PV2BattR = PVR - PV2LoadR
   else:
       PV2BattR = PVR - PV2LoadR # Rest PV in Battery
       #print 'else:PV2BAtt', PVR, PV2Batt

   #----------------------------------------------------------------
   #  Battery charging and discharging possible ?
   #----------------------------------------------------------------  
  # print 'Battery: ', BattDis, BattCh, BattSOC
   if BattDis > Precision:   # Batterie entläd   
          if BattDis > ELoadR-CHP2LoadR - PV2LoadR:  
               print BattDis,  ELoadR-CHP2LoadR - PV2LoadR
               CorrBattDis = ELoadR-CHP2LoadR - PV2LoadR   #reduce to real value                       
               BattSOCalt = BattSOC + BattDis / Battery['eta_batt_dis']*Battery['K_batt']            
               CorrBatSOC = BattSOCalt - CorrBattDis / Battery['eta_batt_dis']*Battery['K_batt']
          elif BattDis <= ELoadR-CHP2LoadR  - PV2LoadR:  # Bat could charge more 
               CorrBattDis = BattDis                    # grid import
               CorrBatSOC = BattSOC 
   elif BattDis < 0: 
       print 'Warning BattDis < 0 '
   else:                 #1) Battery läd 
       if BattCh > Precision:
           if BattCh > PVR - PV2LoadR + CHPel - CHP2LoadR:
               CorrBattCh = PVR - PV2LoadR  + CHPel - CHP2LoadR # reduce to real value
               BattSOCalt = BattSOC - BattCh * Battery['eta_batt_char']*Battery['K_batt']
               CorrBatSOC = BattSOCalt + BattCh * Battery['eta_batt_char']*Battery['K_batt']           
           elif BattCh <= PVR - PV2LoadR + CHPel - CHP2LoadR:
               CorrBattCh = BattCh   # Bat could discharge more
               CorrBatSOC = BattSOC   # grid export
       elif BattCh < 0 : 
           print 'Warning BattCH < 0'
       else: #2) Battery ruht  
             CorrBattCh = BattCh   # Bat could do more
             CorrBatSOC = BattSOC   # grid export or import             
  
    

   #----------------------------------------------------------------
   #    Correct  Grid  Import and Export
   #----------------------------------------------------------------
   CorrGridImp = ELoadR - PV2LoadR - CorrBattDis - CHP2LoadR   
   CorrPVexp = PVR - PV2BattR - PV2LoadR 
   CorrPV2Load = PV2LoadR
   CorrPV2Batt = PV2BattR
   CorrCHPExp = CHPel -  CHP2BattR - CHP2LoadR
   CorrCHP2Load = CHP2LoadR
   CorrCHP2Batt = CHP2BattR
   CorrGridExp = CorrPVexp + CorrCHPExp

   print '2.Nachregelung: ', CorrGridImp, ELoadR, CorrCHP2Load 
      
   
   # - -- - --   CHP integrieren !!!!  - - - - ---
   if CorrGridImp > 0 and CorrGridExp > 0:
       if CorrPVexp > 0 and CorrCHPExp > 0:
           if CorrCHPExp < CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrCHPExp
               CorrCHPExp = 0
               if CorrPVexp < CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrPVexp
                   CorrPVexp = 0
               elif CorrPVexp > CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrGridImp
                   CorrPVexp = CorrPVexp-CorrGridImp
                   CorrGridImp = 0           
               else:
                   CorrPV2Load = CorrPVexp
                   CorrPVexp = 0
                   CorrGridImp = 0
           elif CorrCHPExp > CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrGridImp
               CorrCHPExp = CorrCHPExp-CorrGridImp
               CorrGridImp = 0           
               if CorrPVexp < CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrPVexp
                   CorrPVexp = 0
               elif CorrPVexp > CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrGridImp
                   CorrPVexp = CorrPVexp-CorrGridImp
                   CorrGridImp = 0           
               else:
                   CorrPV2Load = CorrPVexp
                   CorrPVexp = 0
                   CorrGridImp = 0
           else:
               CorrCHP2Load = CorrCHPExp
               CorrCHPExp = 0
               CorrGridImp = 0
               if CorrPVexp < CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrPVexp
                   CorrPVexp = 0
               elif CorrPVexp > CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrGridImp
                   CorrPVexp = CorrPVexp-CorrGridImp
                   CorrGridImp = 0           
               else:
                   CorrPV2Load = CorrPVexp
                   CorrPVexp = 0
                   CorrGridImp = 0
   
           
       elif CorrPVexp > 0 and CorrCHPExp <= 0:
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
               
       elif CorrPVexp <= 0 and CorrCHPExp > 0:
           if CorrCHPExp < CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrCHPExp
               CorrCHPExp = 0
           elif CorrCHPExp > CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrGridImp
               CorrCHPExp = CorrCHPExp-CorrGridImp
               CorrGridImp = 0           
           else:
               CorrCHP2Load = CorrCHPExp
               CorrCHPExp = 0
               CorrGridImp = 0
               
       else: 
           print 'Grid ok'   
   print '3. Nachregelung: ', CorrGridImp, ELoadR, CorrCHP2Load 
            
   CorrGridExp = CorrPVexp + CorrCHPExp       
   # ------------------------------------------------------------------
        
   CorrTerms = pd.Series([CorrBattDis, CorrBattCh, CorrBatSOC, \
   CorrGridImp, CorrGridExp,  CorrPVexp, CorrPV2Batt, CorrPV2Load,\
   CorrTESDis, CorrTESCh, CorrTESSOC, CorrCHPExp, CorrCHP2Batt, CorrCHP2Load,\
   CorrAuxGas, CorrCHPth, CorrCHPel, CorrCHPonoff, CorrTEStoofull, CorrTEStooempty],\
           index = ['CorrBattDis', 'CorrBattCh','CorrBatSOC',\
           'CorrGridImp', 'CorrGridExp', 'CorrPVexp', 'CorrPV2Batt','CorrPV2Load',\
           'CorrTESDis','CorrTESCh', 'CorrTESSOC', 'CorrCHPExp', 'CorrCHP2Batt', \
           'CorrCHP2Load', 'CorrAuxGas', 'CorrCHPth', 'CorrCHPel', 'CorrCHPonoff',\
           'CorrTEStoofull', 'CorrTEStooempty'])
   #print CorrTerms
   return CorrTerms                                    
                                 

if __name__ == '__main__':
    plt.close("all")
    main.MPC()  
   # print "I am just a poor Correction-Programm without any idea of running.\
   # Please ask my friend OptFlex_MPC!"
   