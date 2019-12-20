# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 18:19:42 2015
CHP, PV, Battery Tes Gasboiler Kostenoptimal
@author: tkneiske
"""
import pandas as pd
import matplotlib as plt
import OptFlex_MPC as main

def Calc_KPI(Result_BAT_End, Result_PV_End, Result_Grid_End,\
      Result_TES_End, Result_Heat_End,\
      LoadPeriod, PVavaPeriod, Costs, PrHoBin, maxx, Delta_t,\
      Battery, Auxilary, name):
 #    Battery, Auxilary, EHeater, name):

        #-------- CONVERT Power To Energy !       -----------------------------------------   
    if Delta_t == 10: # min
        P2E = Delta_t / 60.
        # 10 min pro Bin mal Bin Anzahl für Gesamtabschnitt
    totalCost = sum(Costs['C_gas']*(Result_Heat_End['Aux Gasbrenner']/Auxilary['eta_aux']))\
    +sum(Costs['C_grid_el']*Result_Grid_End['Grid Import'])*P2E\
    -sum(Costs['C_PV_FIT']*Result_PV_End['PV Grid export'])*P2E 
                                  
    totalGridExp= sum(Result_Grid_End['Grid Export'][:maxx]) *P2E    
    totalGridImp = sum(Result_Grid_End['Grid Import'][:maxx])  *P2E   
    totalPVExp= sum(Result_PV_End['PV Grid export'][:maxx]) *P2E  
    PVsc= sum(Result_PV_End['PV batt selfcon'][:maxx])*P2E + sum(Result_PV_End['PV load selfcon'][:maxx])*P2E  
    totalEcon= sum(LoadPeriod['ELoad'][:maxx])*P2E  
    totalQcon= sum(LoadPeriod['QLoad1'][:maxx])*P2E+sum(LoadPeriod['QLoad2'][:maxx])*P2E  
    totalAUX= sum(Result_Heat_End['Aux Gasbrenner'][:maxx])*P2E  
 #   totalEHeaterth = sum(Result_Heat_End['EHeater th'][:maxx])*P2E  
 #   totalEHeaterel = sum(Result_Heat_End['EHeater el'][:maxx])*P2E  
    totalEff= 0
    BatteryCyc= (sum(Result_BAT_End['Battery charging'][:maxx]) \
              + sum(Result_BAT_End['Battery dis-charging'][:maxx]))*P2E/2./Battery['Cap_batt']
              #  [(kW +kW) / kWh] ??? check equation
  
    totalPV= sum(PVavaPeriod['PV 2013, Kassel, 10min'][:maxx])*P2E 
    SelfconsumptionPV = (PVsc)/totalPV * 100.
    Autarcy = (PVsc) / totalEcon * 100    
    
    KPIs = pd.Series([totalCost, totalGridExp, totalGridImp, totalPVExp, \
    PVsc,\
    totalPV, \
    totalEcon, totalQcon, totalAUX,  Autarcy, \
    totalEff, BatteryCyc, SelfconsumptionPV,\
  ],\
    index = ['totalCost [Euro]', 'totalGridExp [kWh]', 'totalGridImp [kWh]','totalPVExp [kWh]',\
    'PVsc [kWh]', \
    'totalPV [kWh]', \
    'totalEcon [kWh]', 'totalQcon [kWh]', 'totalAUX [kWh]','Autarcy [%]', \
    'totalEff ?', 'BatteryCyc ', 'SelfconsumptionPV [%]'])
#    totalEHeaterel, totalEHeaterth,
#,'totalEHeaterel [kWh]',  'totalEHeaterth[kWh]', 
    print '--------------------------------'     
    print '  Key Performance Indicators:', PrHoBin
    print '--------------------------------'     
    print KPIs       
    KPIs.to_csv('Results\KPIs'+str(name)+'.csv')                                  
    
    return KPIs
    
    
   
if __name__ == '__main__':
    main.MPC()      
  #  print "I am just a poor Calculator without any idea of running.\
  #  Please ask my friend OptFlex_MPC!"    