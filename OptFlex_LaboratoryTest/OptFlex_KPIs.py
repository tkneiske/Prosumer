# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 18:19:42 2015
CHP, PV, Battery Tes Gasboiler Kostenoptimal
20.05.2016 Neue Costs und Eigenverbrauch CHP, PV hinzugefügt
@author: tkneiske
"""
import pandas as pd
import matplotlib as plt
import OptFlex_MPC as main

def Calc_KPI(Result_BAT_End, Result_PV_End, Result_Grid_End,\
      Result_CHP_End, Result_TES_End, Result_Heat_End,\
      LoadPeriod, PVavaPeriod, Costs, PrHoBin, maxx, Delta_t,\
      Battery, CHP, Auxilary,name,CompTime, INOUT_string, CO2):

        #-------- CONVERT Power To Energy !       -----------------------------------------   
    if Delta_t == 10: # min
        P2E = Delta_t / 60.
        # 10 min pro Bin mal Bin Anzahl für Gesamtabschnitt
    # --------------------------------------------------------------
    #    CO2   [g]
    # --------------------------------------------------------------
    totalCO2gas = CO2['CO2_gas'] * (sum(Result_Heat_End['Aux Gas'][:maxx])\
                                + sum(Result_CHP_End['CHP Gas'][:maxx])) *P2E
    totalCO2grid = sum(CO2['CO2_grid'] * Result_Grid_End['Grid Import']) *P2E
    totalCO2PV = CO2['CO2_PV'] * (sum(Result_PV_End['PV Grid export']) + \
                                + sum(Result_PV_End['PV batt selfcon'][:maxx])\
                                + sum(Result_PV_End['PV load selfcon'][:maxx])) *P2E
                 
    totalCO2 = totalCO2gas + totalCO2grid + totalCO2PV                     
 
    # --------------------------------------------------------------
    # KOSTENBERECHNUNG    
    # --------------------------------------------------------------
    totalCHP2BattCost = -sum(Costs['C_CHP_ex']*Result_CHP_End['CHP batt self'][:maxx]) *P2E  
    totalCHP2eLoadCost = -sum(Costs['C_CHP_ex']*Result_CHP_End['CHP load self'][:maxx])*P2E   
    totalCHPonofCost = sum(Costs['C_CHP_cs']*Result_CHP_End['CHP on_off'][:maxx]) *P2E 
    totalCHPFeedInCost = -sum(Costs['C_CHP_FIT']*Result_CHP_End['CHP Export'][:maxx]) *P2E  
    totalCHPEigenCost = totalCHP2BattCost+totalCHP2eLoadCost
    
    totalPV2BattCost = 0
    totalPV2LoadCost  = 0               
    totalPVEigenCost = totalPV2BattCost+totalPV2LoadCost
    totalPVFeedInCost = -sum(Costs['C_PV_FIT']*Result_PV_End['PV Grid export'][:maxx])*P2E    

    totalGasCost = sum(Costs['C_gas']*(Result_Heat_End['Aux Gasbrenner'][:maxx]/Auxilary['eta_aux']\
                                 + Result_CHP_End['CHP Gas'][:maxx]))*P2E                             
    totalStromCost = sum(Costs['C_grid_el']*Result_Grid_End['Grid Import'][:maxx])*P2E  
        
    totalCost = totalGasCost + totalStromCost + totalCHPonofCost\
                + totalCHPFeedInCost + totalPVFeedInCost \
                + totalCHPEigenCost + totalPVEigenCost 
                
#    totalCost = sum(Costs['C_gas']*(Result_Heat_End['Aux Gasbrenner']/Auxilary['eta_aux']\
#                                 + Result_CHP_End['CHP Gas']))*P2E   \
#                  +sum(Costs['C_grid_el']*Result_Grid_End['Grid Import'][:maxx])*P2E   \
#                  -sum(Costs['C_CHP_FIT']*Result_CHP_End['CHP Export'][:maxx]) *P2E  \
#                  -sum(Costs['C_CHP_ex']*Result_CHP_End['CHP batt self'][:maxx]) *P2E  \
#                  -sum(Costs['C_CHP_ex']*Result_CHP_End['CHP load self'][:maxx])*P2E   \
#                  +sum(Costs['C_CHP_cs']*Result_CHP_End['CHP on_off'][:maxx]) *P2E  \
#                  -sum(Costs['C_PV_FIT']*Result_PV_End['PV Grid export'][:maxx])*P2E    

    
    # --------------------------------------------------------------
    # CHP     
    # --------------------------------------------------------------
    totalCHP2Batt = sum(Result_CHP_End['CHP batt self'][:maxx]) *P2E  
    totalCHP2eLoad = sum(Result_CHP_End['CHP load self'][:maxx])*P2E   
    totalCHPExp= sum(Result_CHP_End['CHP Export'][:maxx])*P2E  
    totalCHPelProd= sum(Result_CHP_End['CHP el'][:maxx])*P2E  
    totalCHPthProd= sum(Result_CHP_End['CHP th'][:maxx])*P2E  
    totalCHP2qLoad = sum(Result_CHP_End['CHP th2load'][:maxx])*P2E  
    totalCHP2TES = sum(Result_CHP_End['CHP th2TES'][:maxx])*P2E  
    
    CHPsc= sum(Result_CHP_End['CHP load self'][:maxx])*P2E + sum(Result_CHP_End['CHP batt self'][:maxx])*P2E  
    SelfconsumptionCHP = CHPsc/totalCHPelProd *100
    CHPstarts= 0
    meanCHPtime= 0
    CHPrunningTime = sum(Result_CHP_End['CHP on_off'][:maxx])*P2E   # [h]
    # om/off entspricht der echten On-Off Fahrweise der CHP Anlage 9.11.2015 
               
    # --------------------------------------------------------------
    # PV
    # --------------------------------------------------------------
    totalPV2Batt = sum(Result_PV_End['PV batt selfcon'][:maxx]) *P2E 
    totalPV2Load  = sum(Result_PV_End['PV load selfcon'][:maxx])*P2E                
    totalPVExp= sum(Result_PV_End['PV Grid export'][:maxx]) *P2E  
    PVsc= sum(Result_PV_End['PV batt selfcon'][:maxx])*P2E + sum(Result_PV_End['PV load selfcon'][:maxx])*P2E  
    totalPV= sum(PVavaPeriod['PV 2013, Kassel, 10min'][:maxx])*P2E 
    SelfconsumptionPV = (PVsc)/totalPV * 100.
                 
    # --------------------------------------------------------------
    # Grid
    # --------------------------------------------------------------
    totalGridExp= sum(Result_Grid_End['Grid Export'][:maxx]) *P2E    
    totalGridImp = sum(Result_Grid_End['Grid Import'][:maxx])  *P2E   

    # --------------------------------------------------------------
    # Load Profiles
    # --------------------------------------------------------------
    totalEcon= sum(LoadPeriod['ELoad'][:maxx])*P2E  
    totalQcon= sum(LoadPeriod['QLoad1'][:maxx])*P2E+sum(LoadPeriod['QLoad2'][:maxx])*P2E  

    # --------------------------------------------------------------
    # AUX Gasboiler
    # --------------------------------------------------------------
    totalAUX= sum(Result_Heat_End['Aux Gasbrenner'][:maxx])*P2E  

    # --------------------------------------------------------------
    # Thermal Storage
    # --------------------------------------------------------------
    totalTES2Load = totalQcon - totalAUX - totalCHP2qLoad

    # --------------------------------------------------------------
    # E-Heater
    # --------------------------------------------------------------    
    totalEHeater = 0
    
    # --------------------------------------------------------------
    # Battery
    # --------------------------------------------------------------
    BatteryCyc= (sum(Result_BAT_End['Battery charging'][:maxx]) \
              + sum(Result_BAT_End['Battery dis-charging'][:maxx]))*P2E/2./Battery['Cap_batt']
              #  [(kW +kW) / kWh] ??? check equation
    totalBattdis = sum(Result_BAT_End['Battery dis-charging'][:maxx])*P2E
    totalBattchar = sum(Result_BAT_End['Battery charging'][:maxx])*P2E
    
        
    
    # --------------------------------------------------------------
    # Total
    # --------------------------------------------------------------
    totalEff= 0
    GesamtSC = (PVsc + CHPsc) / (totalPV+totalCHPelProd) * 100
#    Autarcy = (PVsc + CHPsc) / totalEcon * 100    
    # in beiden ändern in Batt2Load+PV2Load+CHP2Load statt PVsc*CHPsc       
    Autarcy = (totalBattdis+totalPV2Load+totalCHP2eLoad)/totalEcon * 100
  
    CompTime_Max = CompTime['Computational Time'].max()
   
    KPIs = pd.Series([totalCost, totalGridExp, totalGridImp, totalPVExp, \
    totalCHPExp, totalCHPelProd, totalCHPthProd, CHPsc, PVsc, totalPV, totalEcon, totalQcon, totalAUX, totalEHeater, Autarcy, \
    totalEff, BatteryCyc, CHPstarts, meanCHPtime, SelfconsumptionPV,SelfconsumptionCHP, GesamtSC, CHPrunningTime,\
    totalCHP2BattCost, totalCHP2eLoadCost, totalPV2BattCost, totalPV2LoadCost, \
    totalGasCost, totalStromCost, totalPVFeedInCost, totalCHPFeedInCost, totalCHPEigenCost, \
    totalCHPonofCost, totalCHP2Batt, totalCHP2eLoad, totalPV2Batt, totalPV2Load,\
    totalBattdis,totalTES2Load,totalBattchar,totalCHP2qLoad,totalCHP2TES, CompTime_Max, totalCO2,\
    totalCO2gas, totalCO2PV, totalCO2grid],\
    index = ['totalCost [Euro]', 'totalGridExp [kWh]', 'totalGridImp [kWh]', 'totalPVExp [kWh]', \
    'totalCHPExp [kWh]','totalCHPelProd [kWh]', 'totalCHPthProd [kWh]', 'CHPsc [kWh]', 'PVsc [kWh]', \
    'totalPV [kWh]', \
    'totalEcon [kWh]', 'totalQcon [kWh]', 'totalAUX [kWh]', 'totalEH [kWh]', 'Autarcy [%]', \
    'totalEff ?', 'BatteryCyc ', 'CHPstarts ?', 'meanCHPtime ?', 'SelfconsumptionPV [%]',\
    'SelfconsumptionCHP [%]', 'GesamtSC [%]', 'CHPrunningTime [h]','totalCHP2BattCost [Euro]',
    'totalCHP2eLoadCost [Euro]', 'totalPV2BattCost [Euro]', 'totalPV2LoadCost [Euro]',   
    'totalGasCost [Euro]', 'totalStromCost [Euro]', 'totalPVFeedInCost [Euro]', 
    'totalCHPFeedInCost [Euro]', 'totalCHPEigenCost [Euro]', 'totalCHPonofCost [Euro]',    
    'totalCHP2Batt[kWh]', 'totalCHP2eLoad[kWh]', 'totalPV2Batt[kWh]', 'totalPV2Load[kWh]', \
    'totalBattdis [kWh]','totalTES2Load [kWh]','totalBattchar [kWh]','totalCHP2qLoad [kWh]',\
    'totalCHP2TES [kWh]', 'CompTime Max [s]','totalCO2 [g]',\
    'totalCO2gas [g]', 'totalCO2PV [g]', 'totalCO2grid [g]'])
    print '--------------------------------'     
    print '  Key Performance Indicators:', PrHoBin
    print '--------------------------------'     
    print KPIs       
    KPIs.to_csv('Results\KPIs'+str(name)+'_'+INOUT_string+'_10.csv')                                  
    
    return KPIs
    
    # Dummy if something is wrong
def Calc_KPI_dummy(name, PrHoBin,CompTime, INOUT_string):
    
    totalCost = 0
    totalGridExp= 0
    totalGridImp= 0
    totalPVExp= 0
    totalCHPExp= 0
    totalCHPelProd= 0
    totalCHPthProd= 0 
    CHPsc= 0
    PVsc= 0
    totalPV= 0
    totalEcon= 0
    totalQcon= 0
    totalAUX= 0
    totalEHeater= 0
    Autarcy= 0
    totalEff= 0
    BatteryCyc= 0
    CHPstarts= 0
    meanCHPtime= 0
    SelfconsumptionPV= 0
    SelfconsumptionCHP= 0
    GesamtSC= 0
    CHPrunningTime= 0
    totalCHP2BattCost= 0
    totalCHP2eLoadCost= 0
    totalPV2BattCost= 0
    totalPV2LoadCost= 0
    totalGasCost= 0
    totalStromCost= 0
    totalPVFeedInCost= 0
    totalCHPFeedInCost= 0
    totalCHPEigenCost= 0
    totalCHPonofCost= 0
    totalCHP2Batt= 0
    totalCHP2eLoad= 0
    totalPV2Batt= 0
    totalPV2Load= 0
    totalBattDis =0
    totalTES2Load = 0
    totalBattchar =0
    totalCHP2qLoad=0
    totalCHP2TES=0   
    CompTime=0
    totalCO2=0
    totalCO2gas=0
    totalCO2PV=0
    totalCO2grid=0
    
    KPIs = pd.Series([totalCost, totalGridExp, totalGridImp, totalPVExp, \
    totalCHPExp, totalCHPelProd, totalCHPthProd, CHPsc, PVsc, totalPV, totalEcon, totalQcon, totalAUX, totalEHeater, Autarcy, \
    totalEff, BatteryCyc, CHPstarts, meanCHPtime, SelfconsumptionPV,SelfconsumptionCHP, GesamtSC, CHPrunningTime,\
    totalCHP2BattCost, totalCHP2eLoadCost, totalPV2BattCost, totalPV2LoadCost, \
    totalGasCost, totalStromCost, totalPVFeedInCost, totalCHPFeedInCost, totalCHPEigenCost, \
    totalCHPonofCost, totalCHP2Batt, totalCHP2eLoad, totalPV2Batt, \
    totalPV2Load, totalBattDis,totalTES2Load, totalBattchar,totalCHP2qLoad,totalCHP2TES, CompTime, totalCO2,\
    totalCO2gas, totalCO2PV, totalCO2grid],\
    index = ['totalCost [Euro]', 'totalGridExp [kWh]', 'totalGridImp [kWh]', 'totalPVExp [kWh]', \
    'totalCHPExp [kWh]','totalCHPelProd [kWh]', 'totalCHPthProd [kWh]', 'CHPsc [kWh]', 'PVsc [kWh]', \
    'totalPV [kWh]', \
    'totalEcon [kWh]', 'totalQcon [kWh]', 'totalAUX [kWh]', 'totalEH [kWh]', 'Autarcy [%]', \
    'totalEff ?', 'BatteryCyc ', 'CHPstarts ?', 'meanCHPtime ?', 'SelfconsumptionPV [%]',\
    'SelfconsumptionCHP [%]', 'GesamtSC [%]', 'CHPrunningTime [h]','totalCHP2BattCost [Euro]',
    'totalCHP2eLoadCost [Euro]', 'totalPV2BattCost [Euro]', 'totalPV2LoadCost [Euro]',   
    'totalGasCost [Euro]', 'totalStromCost [Euro]', 'totalPVFeedInCost [Euro]', 
    'totalCHPFeedInCost [Euro]', 'totalCHPEigenCost [Euro]', 'totalCHPonofCost [Euro]',    
    'totalCHP2Batt[kWh]', 'totalCHP2eLoad[kWh]', 'totalPV2Batt[kWh]', \
    'totalPV2Load[kWh]', 'totalBattdis [kWh]', 'totalTES2Load [kWh]', 'totalBattchar [kWh]','totalCHP2qLoad [kWh]',\
    'totalCHP2TES [kWh]','CompTime Max [s]','totalCO2 [g]',\
    'totalCO2gas [g]', 'totalCO2PV [g]', 'totalCO2grid [g]'])
    print '--------------------------------'     
    print '  Key Performance Indicators:', PrHoBin
    print '--------------------------------'     
    print KPIs       
    KPIs.to_csv('Results\KPIs'+str(name)+'_'+INOUT_string+'_10.csv')   
    
    return KPIs
   
if __name__ == '__main__':
    main.MPC()      
  #  print "I am just a poor Calculator without any idea of running.\
  #  Please ask my friend OptFlex_MPC!"    