# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 18:19:42 2015
PV Battery Kosten
26.10.2015 Output in csv-File 

@author: tkneiske
"""
import pandas as pd

def Calc_KPI(Result_BAT_End, Result_PV_End, Result_Grid_End,\
      LoadPeriod, PVavaPeriod, Costs, PrHoBin, maxx, Battery,Delta_t):
    
    #-------- CONVERT Power To Energy !       -----------------------------------------   
    if Delta_t == 10: # min
        P2E = Delta_t / 60.
        # 10 min pro Bin mal Bin Anzahl für Gesamtabschnitt

    totalCost =  sum(Costs['C_grid_el']*Result_Grid_End['Grid Import'])*P2E -\
               sum(Costs['C_PV_FIT']*Result_PV_End['PV Grid export'])*P2E
               
    totalGridExp= sum(Result_Grid_End['Grid Export'])*P2E   
    totalGridImp = sum(Result_Grid_End['Grid Import'])*P2E   
    totalPVExp= sum(Result_PV_End['PV Grid export'])*P2E 
    PVsc= sum(Result_PV_End['PV batt selfcon'][:maxx])*P2E + sum(Result_PV_End['PV load selfcon'][:maxx])*P2E
    totalEcon= sum(LoadPeriod['ELoad'][:maxx])*P2E
    #totalQcon= sum(LoadPeriod['QLoad1'][:maxx])+sum(LoadPeriod['QLoad2'][:maxx])
    Autarcy= (PVsc) / totalEcon * 100.
    totalEff= 0
    #Diego:???Total_Eff = (np.sum(Load_Tot+ P_grid_exp + P_sh_th_Tot[:len(P_dhw_th_Tot)-71] + P_dhw_th_Tot[:len(P_dhw_th_Tot)-71])/np.sum(P_CHP_gas + P_aux_gas + P_grid_imp + P_PV))*100# in [#]
    BatteryCyc= (sum(Result_BAT_End['Battery charging'][:maxx]) \
              + sum(Result_BAT_End['Battery dis-charging'][:maxx]))*P2E/2./Battery['Cap_batt']
              #  [(kW +kW) / kWh] ??? check equation
    totalPV= sum(PVavaPeriod['PV 2013, Kassel, 10min'][:maxx])*P2E 
    SelfconsumptionPV = (PVsc)/totalPV * 100.
    
    
    
    KPIs = pd.Series([totalCost, totalGridExp, totalGridImp, totalPVExp, \
    PVsc, totalPV, totalEcon,  Autarcy, \
    totalEff, BatteryCyc, SelfconsumptionPV],\
    index = ['totalCost', 'totalGridExp', 'totalGridImp', 'totalPVExp', \
    'PVsc', 'totalPV', 'totalEcon',  'Autarcy', \
    'totalEff', 'BatteryCyc',  'SelfconsumptionPV'])
    print ('--------------------------------'     )
    print ('  Key Performance Indicators:', PrHoBin)
    print ('--------------------------------'     )
    print (KPIs                                    )
         
    KPIs.to_csv('Results\KPIs.csv')                                

    return KPIs
    
    
   
if __name__ == '__main__':
    plt.close("all")
    Calc_KPI(1,2,3)
    
    print ("I am just a poor Calculator without any idea of running.\
    Please ask my friend OptFlex_MPC!"    )