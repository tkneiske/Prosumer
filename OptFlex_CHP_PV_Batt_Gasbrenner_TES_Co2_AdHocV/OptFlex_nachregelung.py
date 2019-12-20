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
            ELoadR, Q1LoadR, Q2LoadR, CHP, OptiMarker, Auxilary):    

            
   BattDis = Result_BAT_End['Battery dis-charging'][timestep]
   BattCh  = Result_BAT_End['Battery charging'][timestep]
   BattSOC = Result_BAT_End['SOC battery'][timestep]   
  # print 'adhoc begin ',BattSOC
   
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
   CHPGas = Result_CHP_End['CHP Gas'][timestep]    
 
   GridExp = Result_Grid_End['Grid Export'][timestep]
   GridImp = Result_Grid_End['Grid Import'][timestep]
    
   AuxGas = Result_Heat_End['Aux Gasbrenner'][timestep]
   Precision = 1e-5
   # New values after correction
   CorrGridExp = GridExp 
   CorrGridImp = GridImp  
   CorrBattDis = BattDis
   CorrBattCh = BattCh
 #  CorrBatSOC = BattSOC_R
   CorrBattSOC = BattSOC
   CorrPVexp = PVExp
   CorrPV2Batt = PV2Batt #sc
   CorrPV2Load = PV2Load #sc
   CorrTESDis = TESDis
   CorrTESCh = TESCh
   CorrTESSOC = TESSOC
  # CorrTESSOC = TESSOC_R
   CorrCHP2Load =  CHP2Load  
   CorrCHP2Batt = CHP2Batt 
   CorrCHPExp = CHPExp 
   CorrCHPel = CHPel 
   CorrCHPth = CHPth 
   CorrCHPonoff = CHPonoff 
  # CorrCHPonoff = CHPonoff_R 
   CorrCHPGas = CHPGas

   #print 'nachr.Begin :', BattSOC
   
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
  # print 'CH/Dis/SOC/Load /Aux: ',TESCh, TESDis, TESSOC, Q1LoadR+Q2LoadR, AuxGas
  # print 'PVR/CH/Dis/SOC/Load : ',PVR,BattCh, BattDis, BattSOC, ELoadR
   # ---------- läd und entläd     , CHP oder Gasboiler ----------
   if TESDis > Precision and TESCh > Precision: 
       #print "Ch 1 Dis 1"
       #Lade Wärmespeicher bis er voll ist und mehr, Frage Wieviel ist "mehr"?  
       CorrTESDis = Q1LoadR+Q2LoadR   
       CorrTESCh = TESCh                             
       if TESDis > Q1LoadR+Q2LoadR: # too much heat                      
           if Q1LoadR+Q2LoadR > 0: 
               TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                                 - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
               checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                 - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
               if checkTESSOC > 100: # Lade trotzdem in Speicher
                   CorrTEStoofull = checkTESSOC-100#-checkTESSOC /ThermalStorage['eta_TES_char']/ThermalStorage['K_TES']                                                  
                   print "Warining: TES overload"                                
                   CorrTESSOC = checkTESSOC                                              
           elif Q1LoadR+Q2LoadR == 0:                    
                    CorrTESDis = Q1LoadR+Q2LoadR                                    
                    print 'Q=0'
                    TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis'])*ThermalStorage['K_TES']                       
                    CorrTESSOC = TESSOCalt
           elif Q1LoadR+Q2LoadR < 0:    # load negative??
                    print 'Warning: negativ QLoads!'   
                
       elif TESDis == Q1LoadR+Q2LoadR:    
           CorrTESSOC = TESSOC
       elif TESDis < Q1LoadR+Q2LoadR:    # not enough heat, discharge storage  
           #print 'More QLoad than Discharge', CorrTESDis       
           TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                                 - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
           checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                  - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
           if checkTESSOC <= 0:               #if TES Empty start Gasboiler
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
               #CorrTESCh =  CorrTEStooempty # Charge Heat when TES empty
               #print 'SOC = 100%, AuxGas' 
           else:    
               CorrTESSOC = checkTESSOC   
               
   #--------  nur entladen aus Speicher, CHP, Gasb AUS ----------      
   elif TESDis > Precision and TESCh < Precision:     
           #print "Ch 0 Dis 1"
           CorrTESCh = 0
           CorrTESDis = Q1LoadR+Q2LoadR                                                
           if TESDis > Q1LoadR+Q2LoadR: # too much heat
               #print "Wärme kommt aus Speicher!"
               if Q1LoadR+Q2LoadR > 0: 
                   print 'Q>0'
                   TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis'])*ThermalStorage['K_TES']                   
                   checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                              - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
                   if checkTESSOC > 100: # Lade trotzdem in Speicher
                       CorrTEStoofull = checkTESSOC-100#-checkTESSOC /ThermalStorage['eta_TES_char']/ThermalStorage['K_TES']                                                  
                       print "Warining: TES overload"  
                   CorrTESSOC = checkTESSOC                                    
               elif Q1LoadR+Q2LoadR == 0:                    
                    print 'Q=0'
                    TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis'])*ThermalStorage['K_TES']                       
                    CorrTESSOC = TESSOCalt
               elif Q1LoadR+Q2LoadR < 0:    # load negative??
                    print 'Warning: negativ QLoads!'   
           elif TESDis == Q1LoadR+Q2LoadR:    
               #print 'Dis == QLoad'               
               CorrTESSOC = TESSOC
           elif TESDis < Q1LoadR+Q2LoadR:    # not enough heat, discharge storage               
                #print "Wärme kommt aus Speicher, Last ist größer !", CorrTESDis 
                TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                       - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
                checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                       - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES'] 
                if checkTESSOC <= 0:               #if TES Empty start Gasboiler
                       CorrTESSOC = 0
                       CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
#                       CorrTESCh =  CorrTEStooempty # Charge Heat when TES empty
                else:  #tes soc ok
                      CorrTESSOC = checkTESSOC  
           else: 
                 print "Warning: Something wrong with Charge = ON & Discharge == off!"
  #--------  nur laden CHP, Gasb , no Q-LOAD ----------              
   elif TESCh > Precision and TESDis < Precision:     # no discharge         
       # print "Ch 1 Dis 0"   
        CorrTESDis = Q1LoadR+Q2LoadR
        CorrTESCh =  TESCh
        if Q1LoadR+Q2LoadR < 0:
            print 'Warning! QLoad negativ!!!'
        else:
            TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                                 - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
            checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                  - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES'] 
            if checkTESSOC < 0:               #if TES Empty start Gasboiler
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
            else:  #tes soc ok
               CorrTESSOC = checkTESSOC    
        
   elif TESCh < Precision and TESDis < Precision: # both are 0 or negative
       # print "Ch 0 Dis 0"
        CorrTESCh = 0
        CorrTESDis = Q1LoadR+Q2LoadR 
        if Q1LoadR+Q2LoadR == 0: # no load          
            CorrTESSOC = TESSOC
        elif Q1LoadR+Q2LoadR > 0: # load exists                      
            TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
                                 - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
            checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                  - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES'] 
            if checkTESSOC <= 0:               #if TES Empty start Gasboiler
               print 'TES LEER!' 
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
            else:  #tes soc ok
               CorrTESSOC = checkTESSOC    
        elif Q1LoadR+Q2LoadR < 0:    # load negative??
            print 'Warning: negativ QLoads!'                
   else: 
       print "CH - Dis -  --- Warning, something wrong ---"                    
   #----------------------------------------------------------------
   # CorrTEStooempty
   #----------------------------------------------------------------
   if CorrTEStooempty > 0:
       #print 'CorrTEStooempty', CorrTESCh, CorrAuxGas, CorrTEStooempty
       CorrAuxGas = CorrAuxGas +  CorrTEStooempty
       CorrTESCh = CorrTESCh + CorrTEStooempty
      # print 'CorrTEStooempty', CorrTESCh, CorrAuxGas, CorrTEStooempty
   
   #----------------------------------------------------------------
   #   CHP 
   #----------------------------------------------------------------
  # print 'CHP: ', CHPel, CHPth, CHPonoff          
   # No Change for CHP so far 
   CHPelR = CHPel
   CorrCHPel = CHPelR    
          
   #------------------------------------------------------------------------
   # PV2Load and PV2Batt
   #------------------------------------------------------------------------
   
   # -- PV2Load/CHP2Load -- 1.Priorität
   if ELoadR >= PV2Load + CHP2Load  and PVR >= PV2Load and CHPelR >= CHP2Load: #alles ok
       PV2LoadR = PV2Load
       CHP2LoadR = CHP2Load    
       #print 'L PV CHP'            
   elif ELoadR >= PV2Load + CHP2Load and PVR >= PV2Load : # nicht genug CHPel
       #print 'L PV -'            
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
        #print 'L - CHP'            
        if PVR < ELoadR - CHP2Load: # CHP Eigenverbrauch vor PV Eigenverbrauch 
           PV2LoadR = PVR  # reduziere PV2Load
           CHP2LoadR = CHP2Load        
        else:
           CHP2LoadR = CHP2Load               
           PV2LoadR = ELoadR-CHP2LoadR        # 100% Eigenverbrauch
   elif PVR >= PV2Load and CHPelR >= CHP2Load:   # nicht genug ELoad
       #print '- PV CHP'            
       if CHP2Load <= ELoadR:  #genug load für CHP?
           CHP2LoadR = CHP2Load                      
           PV2LoadR = ELoadR - CHP2LoadR       # rest durch PV
       else:
           CHP2LoadR = ELoadR # 100% lastdeckung durch CHP
           PV2LoadR = 0
   elif PVR >= PV2Load:   # nicht genug ELoad und CHPel
       #print '- PV -'            
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
      #print 'L - - '            
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
       #print '- - CHP'                   
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
       #print '- - - '                   
       if ELoadR > CHPelR:
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
   #  Battery charging and discharging possible AdHoc
   #----------------------------------------------------------------  
   # print 'Battery: ', BattDis, BattCh, BattSOC
   if BattDis > Precision:   # Batterie entläd   
          if BattDis > ELoadR-CHP2LoadR - PV2LoadR:  
               #print 'BattDis:', BattDis,  ELoadR-CHP2LoadR - PV2LoadR
               CorrBattDis = ELoadR-CHP2LoadR - PV2LoadR   #reduce to real value                           
               BattSOCalt = BattSOC + BattDis / Battery['eta_batt_dis']*Battery['K_batt']            
               checkBattSOC = BattSOCalt - CorrBattDis / Battery['eta_batt_dis']*Battery['K_batt']               
               if checkBattSOC > 100:  # darf nicht vorkommen
                   CorrBattSOC = 100
                   CorrBattCh = (CorrBattSOC - BattSOCalt) / Battery['eta_batt_dis']/Battery['K_batt']              
                   print BattDis, CorrBattDis, checkBattSOC, CorrBattSOC
                   print '------------------- >ERROR - Battery too full !'
               else:                   
                   BattSOC = checkBattSOC                    
                   CorrBattSOC = BattSOC 
 
     #          print 'OPTI if_dis', BattDis, CorrBattDis, ELoadR
    #           print 'OPTI if_dis', BattSOC, BattSOCalt, CorrBattSOC, checkBattSOC
                                                   
          elif BattDis <= ELoadR-CHP2LoadR  - PV2LoadR:  # Bat could charge more 
               CorrBattDis = BattDis                    # grid import
               CorrBattSOC = BattSOC 
   #            print 'OPTI:elif_dis',BattDis, CorrBattDis
   #            print 'OPTI:elif_dis',BattSOC, CorrBattSOC
   elif BattDis < 0: 
       print 'Warning BattDis < 0 '
   else:                 #1) Battery läd 
       if BattCh > Precision:
           if BattCh > PVR - PV2LoadR + CHPel - CHP2LoadR:
               CorrBattCh = PVR - PV2LoadR  + CHPel - CHP2LoadR # reduce to real value
               BattSOCalt = BattSOC - BattCh * Battery['eta_batt_char']*Battery['K_batt']
               checkBattSOC = BattSOCalt + CorrBattCh * Battery['eta_batt_dis']*Battery['K_batt']                 
               if checkBattSOC > 100: 
                   CorrBattSOC = 100  #zu voll
                   CorrBattCh = (CorrBattSOC - BattSOCalt) / Battery['eta_batt_dis']/Battery['K_batt']
      #             print 'Opti ',BattCh, CorrBattCh, checkBattSOC, CorrBattSOC
               else:
                   CorrBattSOC = checkBattSOC  #alles ok
                   CorrBattCh = CorrBattCh     
      #         print 'OPTI:if_ch', BattDis, CorrBattDis
       #        print 'OPTI:if_ch', BattSOC, BattSOCalt, CorrBattSOC
      
           elif BattCh <= PVR - PV2LoadR + CHPel - CHP2LoadR:
               CorrBattCh = BattCh   # Bat could discharge more
               CorrBattSOC = BattSOC   # grid export
      #         print 'OPTI:elif_ch',BattCh, CorrBattCh
       #        print 'OPTI:elif_ch',BattSOC, CorrBattSOC
       elif BattCh < 0 : 
           print 'Warning BattCH < 0'
       else: #2) Battery ruht  
             CorrBattCh = BattCh   # Bat could do more
             CorrBattSOC = BattSOC   # grid export or import  
      #       print 'opti ELSE ruht ', CorrBattSOC
    
 
 #----------------------------------------------------------------
   #    Correct  Grid  Import and Export
   #----------------------------------------------------------------
   CorrGridImp = ELoadR - PV2LoadR - CorrBattDis - CHP2LoadR #+ GridImpBatt 
   #print CorrGridImp, ELoadR, PV2LoadR, CorrBattDis, CHP2LoadR
   CorrPVexp = PVR - PV2BattR - PV2LoadR 
   CorrPV2Load = PV2LoadR
   CorrPV2Batt = PV2BattR
   CorrCHPExp = CHPel -  CHP2BattR - CHP2LoadR 
   CorrCHP2Load = CHP2LoadR
   CorrCHP2Batt = CHP2BattR
   CorrGridExp = CorrPVexp + CorrCHPExp 
   
   #print CorrGridImp, CorrGridExp, CorrPV2Load
   # To get rid of simultanious GridExp und GridImp
   if CorrGridImp > 0 and CorrGridExp > 0:
       if CorrPVexp > 0 and CorrCHPExp > 0:
           #print 'PV>0  CHPExp>0' 
           if CorrCHPExp < CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrCHPExp
               CorrGridImp = CorrGridImp-CorrCHPExp
               CorrCHPExp = 0
               if CorrPVexp < CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrPVexp
                   CorrGridImp = CorrGridImp-CorrPVexp
                   CorrPVexp = 0
                   #print "1", CorrPV2Load
               elif CorrPVexp > CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrGridImp
                   CorrPVexp = CorrPVexp-CorrGridImp
                   #print "2", CorrPV2Load, CorrGridImp
                   CorrGridImp = 0           
               else:
                   CorrPV2Load = CorrPVexp
                   CorrPVexp = 0
                   CorrGridImp = 0
                   #print "3", CorrPV2Load
           elif CorrCHPExp > CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrGridImp
               CorrCHPExp = CorrCHPExp-CorrGridImp
               CorrGridImp = 0           
               if CorrPVexp < CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrPVexp
                   CorrGridImp = CorrGridImp-CorrPV2exp
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
                   CorrGridImp = CorrGridImp-CorrPVexp
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
           #print 'PVexp>0  CHPExp<0' 
           if CorrPVexp < CorrGridImp:
               CorrPV2Load = CorrPV2Load + CorrPVexp
               CorrGridImp = CorrGridImp-CorrPVexp
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
           #print 'PV<0  CHPExp>0' 
           if CorrCHPExp < CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrCHPExp
               CorrGridImp = CorrGridImp - CorrCHPExp # -->  total CHP Self-consumption -- Wollen wir das?
               CorrCHPExp = 0
               #print 'bugfix', CorrGridImp, CorrCHPExp
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
   CorrGridExp = CorrPVexp + CorrCHPExp #+ GridExpBatt
   # ------------------------------------------------------------------
  
  # Correction of Gasverbrauch for Auxilary gasburner
   CorrAuxGasmenge = CorrAuxGas*Auxilary['eta_aux']
   # ------------------------------------------------------------------
  
  
   OptiMarker = 0         
    
   CorrTerms = pd.Series([CorrBattDis, CorrBattCh, CorrBattSOC, \
       CorrGridImp, CorrGridExp,  CorrPVexp, CorrPV2Batt, CorrPV2Load,\
       CorrTESDis, CorrTESCh, CorrTESSOC, CorrCHPExp, CorrCHP2Batt, CorrCHP2Load,\
       CorrAuxGas, CorrCHPth, CorrCHPel, CorrCHPonoff, CorrCHPGas, CorrTEStoofull, \
       CorrTEStooempty,OptiMarker,CorrAuxGasmenge],\
           index = ['CorrBattDis', 'CorrBattCh','CorrBatSOC',\
           'CorrGridImp', 'CorrGridExp', 'CorrPVexp', 'CorrPV2Batt','CorrPV2Load',\
           'CorrTESDis','CorrTESCh', 'CorrTESSOC', 'CorrCHPExp', 'CorrCHP2Batt', \
           'CorrCHP2Load', 'CorrAuxGas', 'CorrCHPth', 'CorrCHPel', 'CorrCHPonoff',\
           'CorrCHPGas','CorrTEStoofull', 'CorrTEStooempty', 'OptiMarker','CorrAuxGasmenge'])
   #print CorrTerms
   return CorrTerms                                    
                                 

def AdHoc_MPC_Rulebased(Result_BAT_End, Result_PV_End, Result_Heat_End,\
            Result_TES_End, Result_CHP_End,\
            Result_Grid_End, PVavaFore, PVR,\
            ELoadFore, Q1LoadFore,Q2LoadFore,timestep, Battery, ThermalStorage,\
            ELoadR, Q1LoadR, Q2LoadR, CHP, OptiMarker, RuleIni, Auxilary):    

            
   BattDis = Result_BAT_End['Battery dis-charging'][timestep]
   BattCh  = Result_BAT_End['Battery charging'][timestep]
 #  BattSOC = Result_BAT_End['SOC battery'][timestep]     
   BattSOCalt = RuleIni['BattSOC_R'][0]    
   BattSOC_opti = RuleIni['BattSOC_opti'][0]
   BattSOC = BattSOCalt # noch nicht bekannt für diesen Zeitschritt default "alt"
 #  BattSOC = Battery['SOC_batt_ini']
   
   TESDis = Result_TES_End['TES dis-charging'][timestep]
   TESCh  = Result_TES_End['TES charging'][timestep]
   #TESSOC = Result_TES_End['SOC TES'][timestep]     
   TESSOCalt = RuleIni['TESSOC_R'][0]     
   TESSOC = TESSOCalt # default ist "alt", Wert wird hier erst neu bestimmt
   TESSOC_opti = RuleIni['TESSOC_opti'][0] 
   #TESSOC = ThermalStorage['SOC_TES_ini'] 
   TESSOC = 0 #noch nicht bekannt für diesen Zeitschritt   
   
   PV2Load = Result_PV_End['PV load selfcon'][timestep] #sc
   PV2Batt = Result_PV_End['PV batt selfcon'][timestep]  #sc
   PVExp = Result_PV_End['PV Grid export'][timestep] 

   CHP2Load = Result_CHP_End['CHP load self'][timestep] #sc
   CHP2Batt = Result_CHP_End['CHP batt self'][timestep]  #sc
   CHPExp = Result_CHP_End['CHP Export'][timestep] 
   CHPel = Result_CHP_End['CHP el'][timestep]       
   CHPth = Result_CHP_End['CHP th'][timestep] 
   CHPonoff = Result_CHP_End['CHP on_off'][timestep] 
   CHPGas = Result_CHP_End['CHP Gas'][timestep]    
#  CHPonoff_opti = RuleIni['CHPonoff_opti'][0]  
   CHPonoff = RuleIni['CHPonoff_R'][0] # Wird hier nicht geändert!
  # CHPonoff = CHP['b_CHP_on_ini'] 

   GridExp = Result_Grid_End['Grid Export'][timestep]
   GridImp = Result_Grid_End['Grid Import'][timestep]
    
   AuxGas = Result_Heat_End['Aux Gasbrenner'][timestep]
   Precision = 1e-3
   percent = 10  # Abweichung Speicherfüllstand bis zu nächsten Optimierung
   
   # New values after correction
   CorrGridExp = GridExp 
   CorrGridImp = GridImp  
   CorrBattDis = BattDis
   CorrBattCh = BattCh
   CorrBattSOC = BattSOC
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
   CorrCHPGas = CHPGas

   GridExpBatt = 0
   GridImpBatt = 0
  # print 'nachr.Begin :', BattSOC, CorrBatSOC, BattSOCalt, BattSOC_opti
   
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
  # print 'CH/Dis/SOC/Load /Aux: ',TESCh, TESDis, TESSOC, Q1LoadR+Q2LoadR, AuxGas
  # print 'PVR/CH/Dis/SOC/Load : ',PVR,BattCh, BattDis, BattSOC, ELoadR
   # ---------- läd und entläd     , CHP oder Gasboiler ----------
   if TESDis > Precision and TESCh > Precision: 
       #print "Ch 1 Dis 1"
       #Lade Wärmespeicher bis er voll ist und mehr, Frage Wieviel ist "mehr"?  
       CorrTESDis = Q1LoadR+Q2LoadR   
       CorrTESCh = TESCh                             
       if TESDis > Q1LoadR+Q2LoadR: # too much heat                      
           if Q1LoadR+Q2LoadR > 0: 
             #  TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
             #                    - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
               checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                 - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
               if checkTESSOC > 100: # Lade trotzdem in Speicher
                   CorrTEStoofull = checkTESSOC-100#-checkTESSOC /ThermalStorage['eta_TES_char']/ThermalStorage['K_TES']                                                  
                   print "Warining: TES overload"                                
                   CorrTESSOC = checkTESSOC                                              
           elif Q1LoadR+Q2LoadR == 0:                    
                    CorrTESDis = Q1LoadR+Q2LoadR                                    
                    print 'Q=0'
                 #   TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis'])*ThermalStorage['K_TES']                       
                    CorrTESSOC = TESSOCalt
           elif Q1LoadR+Q2LoadR < 0:    # load negative??
                    print 'Warning: negativ QLoads!'   
                
       elif TESDis == Q1LoadR+Q2LoadR: 
           checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                 - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
           if checkTESSOC <= 0:               #if TES Empty start Gasboiler
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
               print 'Dis/Ch elif', TESSOC
           else:                       
               TESSOC = checkTESSOC
               CorrTESSOC = TESSOC

       elif TESDis < Q1LoadR+Q2LoadR:    # not enough heat, discharge storage  
           #print 'More QLoad than Discharge', CorrTESDis       
     #      TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
       #                          - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
           checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                  - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
           if checkTESSOC <= 0:               #if TES Empty start Gasboiler
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
               #CorrTESCh =  CorrTEStooempty # Charge Heat when TES empty
               #print 'SOC = 100%, AuxGas' 
           else:    
               CorrTESSOC = checkTESSOC   
               
   #--------  nur entladen aus Speicher, CHP, Gasb AUS ----------      
   elif TESDis > Precision and TESCh < Precision:     
           #print "Ch 0 Dis 1"
           CorrTESCh = 0
           CorrTESDis = Q1LoadR+Q2LoadR                                                
           if TESDis > Q1LoadR+Q2LoadR: # too much heat
               #print "Wärme kommt aus Speicher!"
               if Q1LoadR+Q2LoadR > 0: 
                   print 'Q>0'
        #           TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis'])*ThermalStorage['K_TES']                   
                   checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                              - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']   
                   if checkTESSOC > 100: # Lade trotzdem in Speicher
                       CorrTEStoofull = checkTESSOC-100#-checkTESSOC /ThermalStorage['eta_TES_char']/ThermalStorage['K_TES']                                                  
                       print "Warining: TES overload"  
                   CorrTESSOC = checkTESSOC                                    
               elif Q1LoadR+Q2LoadR == 0:                    
                    print 'Q=0'
         #           TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis'])*ThermalStorage['K_TES']                       
                    CorrTESSOC = TESSOCalt
               elif Q1LoadR+Q2LoadR < 0:    # load negative??
                    print 'Warning: negativ QLoads!'   
           elif TESDis == Q1LoadR+Q2LoadR:    
               #print 'Dis == QLoad'   
           
               checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                 - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']               
               if checkTESSOC <= 0:               #if TES Empty start Gasboiler
                   CorrTESSOC = 0
                   CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
                   print 'Dis elif', TESSOC
               else:
                   TESSOC = checkTESSOC
                   CorrTESSOC = TESSOC
               
           elif TESDis < Q1LoadR+Q2LoadR:    # not enough heat, discharge storage               
                #print "Wärme kommt aus Speicher, Last ist größer !", CorrTESDis 
         #       TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
         #              - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
                checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                       - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES'] 
                if checkTESSOC <= 0:               #if TES Empty start Gasboiler
                       CorrTESSOC = 0
                       print 'TES LEER!' 
                       CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
#                       CorrTESCh =  CorrTEStooempty # Charge Heat when TES empty
                else:  #tes soc ok
                      CorrTESSOC = checkTESSOC  
           else: 
                 print "Warning: Something wrong with Charge = ON & Discharge == off!"
  #--------  nur laden CHP, Gasb , no Q-LOAD ----------              
   elif TESCh > Precision and TESDis < Precision:     # no discharge         
       # print "Ch 1 Dis 0"   
        CorrTESDis = Q1LoadR+Q2LoadR
        CorrTESCh =  TESCh
        if Q1LoadR+Q2LoadR < 0:
            print 'Warning! QLoad negativ!!!'
        else:
      #      TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
     #                            - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
            checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                  - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES'] 
            if checkTESSOC <= 0:               #if TES Empty start Gasboiler
               print 'TES LEER!'             
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
            else:  #tes soc ok
               CorrTESSOC = checkTESSOC    
        
   elif TESCh < Precision and TESDis < Precision: # both are 0 or negative
       # print "Ch 0 Dis 0"
        CorrTESCh = 0
        CorrTESDis = Q1LoadR+Q2LoadR 
        if Q1LoadR+Q2LoadR == 0: # no load    
            TESSOC = TESSOCalt
            CorrTESSOC = TESSOC
           # print 'NO elif', TESSOC
        elif Q1LoadR+Q2LoadR > 0: # load exists                      
        #    TESSOCalt = TESSOC + (TESDis/ThermalStorage['eta_TES_dis']\
        #                         - TESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES']                   
            checkTESSOC = TESSOCalt - (CorrTESDis/ThermalStorage['eta_TES_dis']\
                                  - CorrTESCh *ThermalStorage['eta_TES_char'])*ThermalStorage['K_TES'] 
            if checkTESSOC <= 0:               #if TES Empty start Gasboiler
               print 'TES LEER!' 
               CorrTESSOC = 0
               CorrTEStooempty =-checkTESSOC*ThermalStorage['eta_TES_dis']/ThermalStorage['K_TES']                           
            else:  #tes soc ok
               CorrTESSOC = checkTESSOC    
        elif Q1LoadR+Q2LoadR < 0:    # load negative??
            print 'Warning: negativ QLoads!'                
   else: 
       print "CH - Dis -  --- Warning, something wrong ---"                    
   #----------------------------------------------------------------
   # CorrTEStooempty
   #----------------------------------------------------------------
   if CorrTEStooempty > 0:
       #print 'CorrTEStooempty', CorrTESCh, CorrAuxGas, CorrTEStooempty
       CorrAuxGas = CorrAuxGas +  CorrTEStooempty
       CorrTESCh = CorrTESCh + CorrTEStooempty
      # print 'CorrTEStooempty', CorrTESCh, CorrAuxGas, CorrTEStooempty
   
   #----------------------------------------------------------------
   #   CHP 
   #----------------------------------------------------------------
  # print 'CHP: ', CHPel, CHPth, CHPonoff          
   # No Change for CHP so far 
   CHPelR = CHPel
   CorrCHPel = CHPelR    
          
   #------------------------------------------------------------------------
   # PV2Load and PV2Batt
   #------------------------------------------------------------------------
   
   # -- PV2Load/CHP2Load -- 1.Priorität
   if ELoadR >= PV2Load + CHP2Load  and PVR >= PV2Load and CHPelR >= CHP2Load: #alles ok
       PV2LoadR = PV2Load
       CHP2LoadR = CHP2Load    
       #print 'L PV CHP'            
   elif ELoadR >= PV2Load + CHP2Load and PVR >= PV2Load : # nicht genug CHPel
       #print 'L PV -'            
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
        #print 'L - CHP'            
        if PVR < ELoadR - CHP2Load: # CHP Eigenverbrauch vor PV Eigenverbrauch 
           PV2LoadR = PVR  # reduziere PV2Load
           CHP2LoadR = CHP2Load        
        else:
           CHP2LoadR = CHP2Load               
           PV2LoadR = ELoadR-CHP2LoadR        # 100% Eigenverbrauch
   elif PVR >= PV2Load and CHPelR >= CHP2Load:   # nicht genug ELoad
       #print '- PV CHP'            
       if CHP2Load <= ELoadR:  #genug load für CHP?
           CHP2LoadR = CHP2Load                      
           PV2LoadR = ELoadR - CHP2LoadR       # rest durch PV
       else:
           CHP2LoadR = ELoadR # 100% lastdeckung durch CHP
           PV2LoadR = 0
   elif PVR >= PV2Load:   # nicht genug ELoad und CHPel
       #print '- PV -'            
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
      #print 'L - - '            
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
       #print '- - CHP'                   
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
       #print '- - - '                   
       if ELoadR > CHPelR:
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
   #  Battery charging and discharging AdHochRuleBased
   #----------------------------------------------------------------  
   # print 'Battery: ', BattDis, BattCh, BattSOC
   if BattDis > Precision:   # Batterie entläd   
          if BattDis > ELoadR-CHP2LoadR - PV2LoadR:  # entlade weniger
               CorrBattDis = ELoadR-CHP2LoadR - PV2LoadR   #reduce to real value                           
               checkBattSOC = BattSOCalt - CorrBattDis * Battery['eta_batt_dis']*Battery['K_batt']  
               if checkBattSOC > 100:  # darf nicht vorkommen
                   CorrBattSOC = 100
                   CorrBattCh = (CorrBattSOC - BattSOCalt) / Battery['eta_batt_dis']/Battery['K_batt']              
                   print BattDis, CorrBattDis, checkBattSOC, CorrBattSOC
                   print 'Warning - adhocRule- Dis Battery too full !'
             #      print 'if_dis', BattDis, CorrBattDis, ELoadR
            #       print 'if_dis', BattSOC, BattSOCalt, CorrBattSOC, checkBattSOC, BattSOC_opti 
               elif checkBattSOC < 0:
                   print '-Warning - adhocRule - Ch Battery too empty!'
                   BattSOC = 0
                   CorrBattSOC = BattSOC
                   CorrBattDis = (BattSOCalt) / Battery['eta_batt_dis']/Battery['K_batt']    
               else:                   
                   BattSOC = checkBattSOC  # wird hier zum ersten mal festgelegt                  
                   CorrBattSOC = BattSOC #Korrektur nicht nötig
          #         print 'if_else_dis', BattDis, CorrBattDis, ELoadR
           #        print 'if_else_dis', BattSOC, BattSOCalt, CorrBattSOC, checkBattSOC, BattSOC_opti 
          
          elif BattDis <= ELoadR-CHP2LoadR  - PV2LoadR:  # Bat could charge more                
               if (ELoadR-CHP2LoadR - PV2LoadR)<= Battery['P_batt_dis_max']:
               # check if discharging < dischargeMAX
                      CorrBattDis = ELoadR-CHP2LoadR - PV2LoadR
                  #    print BattDis, CorrBattDis
               else:
                      CorrBattDis = Battery['P_batt_dis_max']       
          #     BattSOCalt = BattSOC + BattDis / Battery['eta_batt_dis']*Battery['K_batt']  
               checkBattSOC = BattSOCalt - CorrBattDis * Battery['eta_batt_dis']*Battery['K_batt']                 
               if checkBattSOC > 0:
                   BattSOC = checkBattSOC  # wird hier zum ersten mal festgelegt                  
                   CorrBattSOC = BattSOC # Korrektur nicht nötig
                   CorrBattDis = CorrBattDis
               else:
                   BattSOC = 0
                   print 'Warning - adhocRule Dis - Battery too empty !'
                   CorrBattSOC = BattSOC
                   CorrBattDis = (BattSOCalt) / Battery['eta_batt_dis']/Battery['K_batt']
                      
           #    print 'elif_dis',BattDis, CorrBattDis, ELoadR-CHP2LoadR  - PV2LoadR
            #   print 'elif_dis',BattSOC, BattSOCalt, CorrBattSOC, checkBattSOC, BattSOC_opti
   elif BattDis < 0: 
       print 'Warning BattDis < 0 '
   else:                 #1) Battery läd 
       if BattCh > Precision:
           if BattCh > PVR - PV2LoadR + CHPel - CHP2LoadR: # charge too much
               CorrBattCh = PVR - PV2LoadR  + CHPel - CHP2LoadR # reduce to real value
               checkBattSOC = BattSOCalt + CorrBattCh * Battery['eta_batt_dis']*Battery['K_batt']                 
               if checkBattSOC > 100: 
                   CorrBattSOC = 100  #zu voll
                   #GridExpBatt = (checkBattSOC-100) / Battery['eta_batt_dis']/Battery['K_batt']
                   CorrBattCh = (CorrBattSOC - BattSOCalt) / Battery['eta_batt_dis']/Battery['K_batt']
                  # print BattCh, CorrBattCh, checkBattSOC, CorrBattSOC
               else:
                   CorrBattSOC = checkBattSOC  #alles ok
                   CorrBattCh = CorrBattCh
            #   print 'if_ch', BattDis, CorrBattDis
             #  print 'if_ch', BattSOC, BattSOCalt, CorrBattSOC, BattSOC_opti
      
           elif BattCh <= PVR - PV2LoadR + CHPel - CHP2LoadR:
               CorrBattCh = BattCh   # Bat could charge more
               checkBattSOC = BattSOCalt + CorrBattCh * Battery['eta_batt_dis']*Battery['K_batt'] 
               if checkBattSOC > 100:  # zu voll
                   CorrBattSOC = 100                   
                   CorrBattCh = (CorrBattSOC - BattSOCalt) / Battery['eta_batt_dis']/Battery['K_batt']
                   print 'Warning - adhocRule - Ch Battery too full !'
                   print BattCh, CorrBattCh, checkBattSOC, CorrBattSOC
               else:   
                   CorrBattSOC = checkBattSOC # alles ok
                   CorrBattCh = CorrBattCh
                   

            #   print 'elif_ch',BattCh, CorrBattCh
             #  print 'elif_ch', BattSOC, CorrBattSOC, BattSOC_opti
       elif BattCh < 0 : 
           print 'Warning BattCH < 0'
       else: #2) Battery ruht  
             CorrBattCh = BattCh   # Bat could do more
             BattSOC = BattSOCalt 
             CorrBattSOC = BattSOC   # grid export or import             
           #  print 'ELSE ruht ', CorrBattSOC
    
# ---- check if unpossible cases occur
   if CorrBattSOC > 100 or CorrBattSOC < 0 :
        print ' '
        print 'ERROR in Nachregelung - BattSOC > 100 or SOC < 0 ',CorrBattSOC  
        print ' '
   if CorrTESSOC > 100 or CorrTESSOC < 0 :
        print ' '
        print 'ERROR in Nachregelung - TESSOC > 100 or SOC < 0 ',CorrTESSOC   
        print ' '

   #----------------------------------------------------------------
   #  Bei großer Abweichung neue OPtimierung anstossen
   #----------------------------------------------------------------
 
   if abs(CorrBattSOC-BattSOC_opti)>percent :
       OptiMarker = 1  # --> Optimiere
       print  'OPTIMIZE Batterie!',abs(CorrBattSOC-BattSOC_opti)
   if abs(CorrTESSOC-TESSOC_opti)>percent :
       OptiMarker = 1
       print  'OPTIMIZE ThermalStorage!',abs(CorrBattSOC-BattSOC_opti)
       
   #----------------------------------------------------------------
   #    Correct  Grid  Import and Export
   #----------------------------------------------------------------
   CorrGridImp = ELoadR - PV2LoadR - CorrBattDis - CHP2LoadR #+ GridImpBatt 
   #print CorrGridImp, ELoadR, PV2LoadR, CorrBattDis, CHP2LoadR
   CorrPVexp = PVR - PV2BattR - PV2LoadR 
   CorrPV2Load = PV2LoadR
   CorrPV2Batt = PV2BattR
   CorrCHPExp = CHPel -  CHP2BattR - CHP2LoadR 
   CorrCHP2Load = CHP2LoadR
   CorrCHP2Batt = CHP2BattR
   CorrGridExp = CorrPVexp + CorrCHPExp 
   
   #print CorrGridImp, CorrGridExp, CorrPV2Load
   # To get rid of simultanious GridExp und GridImp
   if CorrGridImp > 0 and CorrGridExp > 0:
       if CorrPVexp > 0 and CorrCHPExp > 0:
           #print 'PV>0  CHPExp>0' 
           if CorrCHPExp < CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrCHPExp
               CorrGridImp = CorrGridImp-CorrCHPExp
               CorrCHPExp = 0
               if CorrPVexp < CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrPVexp
                   CorrGridImp = CorrGridImp-CorrPVexp
                   CorrPVexp = 0
                   #print "1", CorrPV2Load
               elif CorrPVexp > CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrGridImp
                   CorrPVexp = CorrPVexp-CorrGridImp
                   #print "2", CorrPV2Load, CorrGridImp
                   CorrGridImp = 0           
               else:
                   CorrPV2Load = CorrPVexp
                   CorrPVexp = 0
                   CorrGridImp = 0
                   #print "3", CorrPV2Load
           elif CorrCHPExp > CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrGridImp
               CorrCHPExp = CorrCHPExp-CorrGridImp
               CorrGridImp = 0           
               if CorrPVexp < CorrGridImp-CorrCHPExp:
                   CorrPV2Load = CorrPV2Load + CorrPVexp
                   CorrGridImp = CorrGridImp-CorrPVexp
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
                   CorrGridImp = CorrGridImp-CorrPVexp
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
           #print 'PVexp>0  CHPExp<0' 
           if CorrPVexp < CorrGridImp:
               CorrPV2Load = CorrPV2Load + CorrPVexp
               CorrGridImp = CorrGridImp-CorrPV2Load
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
           #print 'PV<0  CHPExp>0' 
           if CorrCHPExp < CorrGridImp:
               CorrCHP2Load = CorrCHP2Load + CorrCHPExp
               CorrGridImp = CorrGridImp - CorrCHPExp # -->  total CHP Self-consumption -- Wollen wir das?
               CorrCHPExp = 0
               #print 'bugfix', CorrGridImp, CorrCHPExp
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
   CorrGridExp = CorrPVexp + CorrCHPExp #+ GridExpBatt
   # ------------------------------------------------------------------
   # Correction of Gasverbrauch for Auxilary gasburner
   CorrAuxGasmenge = CorrAuxGas*Auxilary['eta_aux']
   # ------------------------------------------------------------------


        
   CorrTermsRuleBased = pd.Series([CorrBattDis, CorrBattCh, CorrBattSOC, \
   CorrGridImp, CorrGridExp,  CorrPVexp, CorrPV2Batt, CorrPV2Load,\
   CorrTESDis, CorrTESCh, CorrTESSOC, CorrCHPExp, CorrCHP2Batt, CorrCHP2Load,\
   CorrAuxGas, CorrCHPth, CorrCHPel, CorrCHPonoff, CorrCHPGas, CorrTEStoofull, \
   CorrTEStooempty,OptiMarker,CorrAuxGasmenge],\
           index = ['CorrBattDis', 'CorrBattCh','CorrBatSOC',\
           'CorrGridImp', 'CorrGridExp', 'CorrPVexp', 'CorrPV2Batt','CorrPV2Load',\
           'CorrTESDis','CorrTESCh', 'CorrTESSOC', 'CorrCHPExp', 'CorrCHP2Batt', \
           'CorrCHP2Load', 'CorrAuxGas', 'CorrCHPth', 'CorrCHPel', 'CorrCHPonoff',\
           'CorrCHPGas','CorrTEStoofull', 'CorrTEStooempty', 'OptiMarker', 'CorrAuxGasmenge'])
   #print CorrTerms
   return CorrTermsRuleBased          

if __name__ == '__main__':
    plt.close("all")
    main.MPC()  
   # print "I am just a poor Correction-Programm without any idea of running.\
   # Please ask my friend OptFlex_MPC!"
   