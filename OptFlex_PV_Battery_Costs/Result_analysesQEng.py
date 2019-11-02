# -*- coding: utf-8 -*-
"""
@author: jvonappen, bburgenmeister
"""

from __future__ import division
import numpy as np
import bwf_functions as bwff
import itertools as itto
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.sankey import Sankey
import scipy.special as ssp
import seaborn as sns

def cFixY(Sets, Parameter, Variables):
    EFixY=sum([Parameter['FixCost_Y']['data'][T]*Variables['Size']['data'][T]\
    *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['FixCost_Inc']['data'][T],Parameter['RRR']['data'])\
    for T in Sets['FixCost_Y_Set']['data']])
    QFixY=sum([Parameter['QFixCost_Y']['data'][T]*Variables['Num']['data'][T]\
    *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['QFixCost_Inc']['data'][T],Parameter['RRR']['data'])\
    for T in Sets['QFixCost_Y_Set']['data']])
    return EFixY, QFixY
def cFixI(Sets, Parameter, Variables):
    EFixI=sum([Parameter['FixCost_I']['data'][T]*Variables['Size']['data'][T]\
    for T in Sets['FixCost_I_Set']['data']])
    QFixI=sum([Parameter['QFixCost_I']['data'][T]*Variables['Num']['data'][T]\
    for T in Sets['QFixCost_I_Set']['data']])
    return EFixI, QFixI
def cVar(Sets, Parameter, Variables):
    cEVar=+sum([Parameter['Sign']['data'][T]*sum([Parameter['EVarCost']['data'][T][t-1]*Variables['EFlow']['data'][T][t-1] for t in set(Sets['Time_Set']['data'])])\
    *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['EVarCost_Inc']['data'][T],Parameter['RRR']['data'])\
    for T in Sets['EVarCost_Set']['data']])
    cQVar=+sum([Parameter['QSign']['data'][T]*Parameter['NG2QEff']['data'][T]*sum([Parameter['QVarCost']['data'][T][t-1]*Variables['QFlow']['data'][T][t-1] for t in set(Sets['Time_Set']['data'])])\
    *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['QVarCost_Inc']['data'][T],Parameter['RRR']['data'])\
    for T in Sets['QVarCost_Set']['data']])
    return cEVar, cQVar
def cSaved(Sets, Parameter, Variables, Timesteps, NoYes):
    if NoYes['MaxDem'] == 1: 
        GridSave=Parameter['FixCost_I']['data']['Grid']+Parameter['FixCost_Y']['data']['Grid']\
        *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['FixCost_Inc']['data']['Grid'],Parameter['RRR']['data'])\
        +Parameter['FixCost_Y']['data']['MaxDem']*max(Parameter['EProfil']['data']['Load'])*Timesteps/8760.\
        *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['FixCost_Inc']['data']['MaxDem'],Parameter['RRR']['data'])\
        +sum([Parameter['EVarCost']['data']['GridLoad'][t-1]*Parameter['EProfil']['data']['Load'][t-1] for t in set(Sets['Time_Set']['data'])])\
        *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['EVarCost_Inc']['data']['GridLoad'],Parameter['RRR']['data'])
    else:
        GridSave=Parameter['FixCost_I']['data']['Grid']+Parameter['FixCost_Y']['data']['Grid']\
        *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['FixCost_Inc']['data']['Grid'],Parameter['RRR']['data'])\
        +sum([Parameter['EVarCost']['data']['GridLoad'][t-1]*Parameter['EProfil']['data']['Load'][t-1] for t in set(Sets['Time_Set']['data'])])\
        *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['EVarCost_Inc']['data']['GridLoad'],Parameter['RRR']['data'])
    return GridSave
#------------------------------------------------------------------------------
#STANDARD VALUATION
#------------------------------------------------------------------------------
def Standard_Valuation(Sets, Variables, Parameter,NoYes,Timesteps,Week,plotEFlows,plotAnalyses,plotSankey):
#------------------------------------------------------------------------------
#Calculate net present value
#------------------------------------------------------------------------------
    Eco={'npv':[],'Invest':[],'EStorSub':[],'LoadGridCost':[],'PVGridSales':[]}
    SysSize={'PVkWp':[],'EStorkW':[],'EStorkWh':[]}
    PVdata={'PV_total':[],'PVGrid_total':[],'PVSelf_total':[],'PVLosses_total':[],'PVGrid_percentage':[],'PVSelf_percentage':[],'PVLosses_percentage':[]}
    ELoaddata={'ELoad_total':[],'ELoadGrid_total':[],'ELoadSelf_total':[],'ELoadGrid_percentage':[],'ELoadSelf_percentage':[]}
    
    [EFix_Y, QFix_Y] = cFixY(Sets, Parameter, Variables)        
    [EFix_I, QFix_I] = cFixI(Sets, Parameter, Variables)
    [cEVar, cQVar] =cVar(Sets, Parameter, Variables)
    if NoYes['GridLoad'] == 1:
        Saved=cSaved(Sets, Parameter, Variables, Timesteps, NoYes)
    else:
        Saved=0
    if NoYes['EStorSub'] == 1:
        ESub=Variables['EStorSub']['data']
    else:
        ESub=0
    npv=-EFix_Y-EFix_I-cEVar-QFix_Y-QFix_I-cQVar+Saved+ESub
    Fix_I = EFix_I + QFix_I
#------------------------------------------------------------------------------
#Print results
#------------------------------------------------------------------------------
    print ' '    
    if NoYes['Grid'] == 1:
        print 'The following system configuration delivers the highest net present value:'
    else: 
        MLS=Parameter['MinLoadSupply']['data']*100.
        print 'The cheapest system to supply', \
        ('%.2f' % MLS), \
        '% of the load in the isolated network:'
        del MLS
    if NoYes['PV'] == 1:            
        print 'Size of PV-generator:'
        print ('%.2f' % (Variables['Size']['data']['PV'])), ' kWp'
    if NoYes['EStor'] == 1:
        print 'Capacity of battery storage system: '
        print ('%.2f' % Variables['Size']['data']['EStor']), ' kWh'
        print 'Size of battery inverter: '
        print ('%.2f' % (Variables['Size']['data']['BatC'])), ' kW'
        if Variables['Size']['data']['EStor'] >= 0.005:             
            Cycles=sum([Variables['EFlow']['data']['BatCEStor'][t-1]*Parameter['EStorEfficiencyC']['data'] for t in Sets['Time_Set']['data']])\
            *Parameter['CalcPeriod']['data']/Variables['Size']['data']['EStor']/Parameter['UseableEStorCap']['data']
            print 'Charging/discharging cycles over years: '
            print ('%.2f' % Cycles)
        if NoYes['EStorSub'] == 1:
            if Variables['EStorSubNY']['data'] == 1:
                print 'Subsidy for the battery system:'
                print ('%.2f' % (Variables['EStorSub']['data'])), ' Euro'        
    if  NoYes['NGBurner1'] == 1:       
        print 'Number of NG burners1: '
        print ('%.2f' % Variables['Num']['data']['NGBurner1'])
        print 'Total size of NG burners1: '
        print ('%.2f' % (Variables['Num']['data']['NGBurner1']*Parameter['QMaxSize']['data']['NGBurner1'])), ' kW'
        if Variables['Num']['data']['NGBurner1'] >= 0.005:             
            OpHNG=(np.count_nonzero([Variables['QFlow']['data']['NGBurner1']])*8760./Timesteps)
            print 'Operation hours per year: '
            print ('%.2f' % OpHNG), ' h'  
    if  NoYes['NGBurner2'] == 1:       
        print 'Number of NG burners2: '
        print ('%.2f' % Variables['Num']['data']['NGBurner2'])
        print 'Total size of NG burners2: '
        print ('%.2f' % (Variables['Num']['data']['NGBurner2']*Parameter['QMaxSize']['data']['NGBurner2'])), ' kW'
        if Variables['Num']['data']['NGBurner2'] >= 0.005:             
            OpHNG=(np.count_nonzero([Variables['QFlow']['data']['NGBurner2']])*8760./Timesteps)
            print 'Operation hours per year: '
            print ('%.2f' % OpHNG), ' h'  
    if  NoYes['NGBurner3'] == 1:       
        print 'Number of NG burners3: '
        print ('%.2f' % Variables['Num']['data']['NGBurner3'])
        print 'Total size of NG burners3: '
        print ('%.2f' % (Variables['Num']['data']['NGBurner3']*Parameter['QMaxSize']['data']['NGBurner3'])), ' kW'
        if Variables['Num']['data']['NGBurner3'] >= 0.005:             
            OpHNG=(np.count_nonzero([Variables['QFlow']['data']['NGBurner3']])*8760./Timesteps)
            print 'Operation hours per year: '
            print ('%.2f' % OpHNG), ' h'  
    if  NoYes['CHP1'] == 1:       
        print 'Number of ecopower1.0: '
        print ('%.2f' % Variables['Num']['data']['CHP1'])
        print 'Total size of ecopower1.0: '
        print ('%.2f' % (Variables['Num']['data']['CHP1']*Parameter['QMaxSize']['data']['CHP1'])), ' kW'  
        if Variables['Num']['data']['CHP1'] >= 0.005:             
            OpH=(np.count_nonzero([Variables['QFlow']['data']['CHP1']])*8760./Timesteps)
            print 'Operation hours per year: '
            print ('%.2f' % OpH), ' h'
    if  NoYes['CHP2'] == 1:       
        print 'Number of ecopower3.0: '
        print ('%.2f' % Variables['Num']['data']['CHP2'])
        print 'Total size of ecopower3.0: '
        print ('%.2f' % (Variables['Num']['data']['CHP2']*Parameter['QMaxSize']['data']['CHP2'])), ' kW'  
        if Variables['Num']['data']['CHP2'] >= 0.005:             
            OpH=(np.count_nonzero([Variables['QFlow']['data']['CHP2']])*8760./Timesteps)
            print 'Operation hours per year: '
            print ('%.2f' % OpH), ' h'   
    if  NoYes['CHP3'] == 1:       
        print 'Number of ecopower4.7: '
        print ('%.2f' % Variables['Num']['data']['CHP3'])
        print 'Total size of ecopower4.7: '
        print ('%.2f' % (Variables['Num']['data']['CHP3']*Parameter['QMaxSize']['data']['CHP3'])), ' kW'  
        if Variables['Num']['data']['CHP3'] >= 0.005:             
            OpH=(np.count_nonzero([Variables['QFlow']['data']['CHP3']])*8760./Timesteps)
            print 'Operation hours per year: '
            print ('%.2f' % OpH), ' h'   
    if  NoYes['EHeatQStor'] == 1:       
        print 'Number of E-heaters for Q-storage systems: '
        print ('%.2f' % Variables['Num']['data']['EHeatQStor'])
        print 'Total size of E-heaters for Q-storage systems: '
        print ('%.2f' % (Variables['Num']['data']['EHeatQStor']*Parameter['QMaxSize']['data']['EHeatQStor'])), ' kW'  
        if Variables['Num']['data']['EHeatQStor'] >= 0.005:             
            OpHEHQ=(np.count_nonzero([Variables['QFlow']['data']['EHeatQStor']])*8760./Timesteps)
            print 'Operation hours per year: '
            print ('%.2f' % OpHEHQ), ' h'    
    if NoYes['QStor1'] == 1:
        print 'Number of thermal storage systems (300l): '
        print ('%.2f' % Variables['Num']['data']['QStor1C'])
        if Variables['Num']['data']['QStor1C'] >= 0.005:             
            Cycles=sum([Variables['QFlow']['data']['QStor1C'][t-1]*Parameter['QStorEff']['data']['QStor1C']for t in Sets['Time_Set']['data']])\
            *Parameter['CalcPeriod']['data']/(Variables['Num']['data']['QStor1C']*Parameter['QStorCapSize']['data']['QStor1C'])/Parameter['QStorUseCap']['data']['QStor1C']
            print 'Charging/discharging cycles over years: '
            print ('%.2f' % Cycles)
    if NoYes['QStor2'] == 1:
        print 'Number of thermal storage systems (800l): '
        print ('%.2f' % Variables['Num']['data']['QStor2C'])
        if Variables['Num']['data']['QStor2C'] >= 0.005:             
            Cycles=sum([Variables['QFlow']['data']['QStor2C'][t-1]*Parameter['QStorEff']['data']['QStor2C']for t in Sets['Time_Set']['data']])\
            *Parameter['CalcPeriod']['data']/(Variables['Num']['data']['QStor2C']*Parameter['QStorCapSize']['data']['QStor2C'])/Parameter['QStorUseCap']['data']['QStor2C']
            print 'Charging/discharging cycles over years: '
            print ('%.2f' % Cycles)
    if NoYes['QStor3'] == 1:
        print 'Number of thermal storage systems (1000l): '
        print ('%.2f' % Variables['Num']['data']['QStor3C'])
        if Variables['Num']['data']['QStor3C'] >= 0.005:             
            Cycles=sum([Variables['QFlow']['data']['QStor3C'][t-1]*Parameter['QStorEff']['data']['QStor3C']for t in Sets['Time_Set']['data']])\
            *Parameter['CalcPeriod']['data']/(Variables['Num']['data']['QStor3C']*Parameter['QStorCapSize']['data']['QStor3C'])/Parameter['QStorUseCap']['data']['QStor3C']
            print 'Charging/discharging cycles over years: '
            print ('%.2f' % Cycles)
    print ' '
    if NoYes['Grid'] == 1:       
        print 'The net present value of this system is:'
        print ('%.2f' % npv), ' Euro'
    print 'The investment costs to build this system are:'
    print ('%.2f' % Fix_I), ' Euro'
    print 'Investment cost related to electricity:'
    print ('%.2f' % EFix_I), ' Euro'
    print 'Investment cost related to heat:'
    print ('%.2f' % QFix_I), ' Euro'
    print ' ' 
    print 'Yearly cost related to fixed electricity:'
    print ('%.2f' % (EFix_Y/20)), ' Euro'
    print 'Yearly cost related to var. electricity:'
    print ('%.2f' % (cEVar/20)), ' Euro'
    print 'Yearly cost related to fixed heat:'
    print ('%.2f' % (QFix_Y/20)), ' Euro'
    print 'Yearly cost related to var. heat:'
    print ('%.2f' % (cQVar/20)), ' Euro'
    print ' '
    ELoad_tot = sum([Parameter['EProfil']['data']['Load'][t-1] for t in Sets['Time_Set']['data']])  
    QLoad_tot = sum([Parameter['QProfil']['data']['QLoad'][t-1] for t in Sets['Time_Set']['data']])  
    NG_tot = sum([Parameter['NG2QEff']['data'][T]*sum([Variables['QFlow']['data'][T][t-1] for t in Sets['Time_Set']['data']])\
    for T in Sets['QVarCost_Set']['data']])
    ELoadGrid_tot = sum([Variables['EFlow']['data']['GridLoad'][t-1] for t in Sets['Time_Set']['data']])
    ELoadGrid_per = ELoadGrid_tot*100/ELoad_tot
    ELoadSelf_tot = ELoad_tot - ELoadGrid_tot
    ELoadSelf_per = ELoadSelf_tot*100/ELoad_tot
    print 'Yearly E-load demand: '
    print ('%.2f' % ELoad_tot), ' kWh/year'
    print 'E-Load supply through grid: '
    print ('%.2f' % ELoadGrid_tot), ' kWh/year'
    print ('%.2f' % ELoadGrid_per), ' % of yearly load demand'
    print 'Local E-load supply: '
    print ('%.2f' % ELoadSelf_tot), ' kWh/year'
    print ('%.2f' % ELoadSelf_per), ' % of yearly load demand'
    print ' '
    if NoYes['PV'] == 1:                          
        PV_tot=sum([Parameter['EProfil']['data']['PV'][t-1]*Variables['Size']['data']['PV'] for t in Sets['Time_Set']['data']])
        PVBurner_tot=sum([Variables['EFlow']['data']['PVBurner'][t-1] for t in Sets['Time_Set']['data']])       
        PVBurner_per=PVBurner_tot*100/PV_tot
        PV2Load_tot=sum([Variables['EFlow']['data']['PV2Load'][t-1] for t in Sets['Time_Set']['data']])
        PV2Load_per=PV2Load_tot*100/PV_tot
        if NoYes['EStor'] == 1:
            PV2Bat_tot=sum([Variables['EFlow']['data']['PV2Bat'][t-1] for t in Sets['Time_Set']['data']])
            PV2Bat_per=PV2Bat_tot*100/PV_tot
            PVSelf_tot= PV2Load_tot + PV2Bat_tot
        else:
            PVSelf_tot= PV2Load_tot
        PVSelf_per=PVSelf_tot*100/PV_tot            
        print 'PV self-consumption (directly by load and stored by battery): '
        print ('%.2f' % PVSelf_tot), ' kWh/year'
        print ('%.2f' % PVSelf_per), ' % of produced PV Energy'
        print 'PV direct-consumption by load: '
        print ('%.2f' % PV2Load_tot), ' kWh/year'
        print ('%.2f' % PV2Load_per), ' % of produced PV Energy'
        if NoYes['EStor'] == 1:
            print 'PV battery-charging: '
            print ('%.2f' % PV2Bat_tot), ' kWh/year'
            print ('%.2f' % PV2Bat_per), ' % of produced PV Energy'
        if NoYes['SellToGrid'] == 1:            
            PVGrid_tot=sum([Variables['EFlow']['data']['PVGrid'][t-1] for t in Sets['Time_Set']['data']])
            PVGrid_per=PVGrid_tot/PV_tot*100.
            print 'Directly sold PV energy: '
            print ('%.2f' % PVGrid_tot), ' kWh/year'
            print ('%.2f' % PVGrid_per), ' % of produced PV Energy'            
            if NoYes['PVGridRestricted'] == 1:
                print 'Curtailed PV energy: '
                print ('%.2f' % PVBurner_tot), ' kWh/year'
                print ('%.2f' % PVBurner_per), ' % of produced PV Energy'
        print ' '
    if NoYes['EStor'] == 1:
         BatCh_tot=sum([Variables['EFlow']['data']['BatCEStor'][t-1] for t in Sets['Time_Set']['data']])       
         BatDisch_tot=sum([Variables['EFlow']['data']['EStorBatD'][t-1] for t in Sets['Time_Set']['data']]) 
         BatBurner_tot = BatCh_tot - BatDisch_tot
    if NoYes['QStor'] == 1:  
        if NoYes['EHeatQStor'] == 1:        
            EEHeatQStor_tot = sum([Variables['EFlow']['data']['EHeatQStor'][t-1] for t in Sets['Time_Set']['data']])    
            print 'Load consumption by E-heaters: '
            print ('%.2f' % EEHeatQStor_tot), ' kWh/year'
            print ' '
    if NoYes['CHP1'] == 1: 
        if Variables['Num']['data']['CHP1'] >= 0.005:
            CHP1_tot = sum([Variables['EFlow']['data']['CHP1'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Total E-production from CHP (ecopower1.0): '
            print ('%.2f' % CHP1_tot), ' kWh/year'
            CHP12Load_tot = sum([Variables['EFlow']['data']['CHP12Load'][t-1] for t in Sets['Time_Set']['data']])  
            CHP12Load_per = CHP12Load_tot*100/CHP1_tot
            print 'Direct E-load supply by CHP (ecopower1.0): '
            print ('%.2f' % CHP12Load_tot), ' kWh/year'
            print ('%.2f' % CHP12Load_per), ' % of produced CHP E-energy'
            if NoYes['EStor'] == 1:
                CHP12Bat_tot = sum([Variables['EFlow']['data']['CHP12Bat'][t-1] for t in Sets['Time_Set']['data']])  
                CHP12Bat_per = CHP12Bat_tot*100/CHP1_tot
                print 'E-Storage system charging by CHP (ecopower1.0): '
                print ('%.2f' % CHP12Bat_tot), ' kWh/year'
                print ('%.2f' % CHP12Bat_per), ' % of produced CHP E-energy'         
            if NoYes['SellToGrid'] == 1:
                CHP1Grid_tot = sum([Variables['EFlow']['data']['CHP1Grid'][t-1] for t in Sets['Time_Set']['data']])  
                CHP1Grid_per = CHP1Grid_tot*100/CHP1_tot
                print 'Direct CHP grid feed-in (ecopower1.0): '
                print ('%.2f' % CHP1Grid_tot), ' kWh/year'
                print ('%.2f' % CHP1Grid_per), ' % of produced CHP E-energy'
            print ' '
    if NoYes['CHP2'] == 1:  
        if Variables['Num']['data']['CHP2'] >= 0.005:
            CHP2_tot = sum([Variables['EFlow']['data']['CHP2'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Total E-production from CHP (ecopower3.0): '
            print ('%.2f' % CHP2_tot), ' kWh/year'
            CHP22Load_tot = sum([Variables['EFlow']['data']['CHP22Load'][t-1] for t in Sets['Time_Set']['data']])  
            CHP22Load_per = CHP22Load_tot*100/CHP2_tot
            print 'Direct E-load supply by CHP (ecopower3.0): '
            print ('%.2f' % CHP22Load_tot), ' kWh/year'
            print ('%.2f' % CHP22Load_per), ' % of produced CHP E-energy'
            if NoYes['EStor'] == 1:
                CHP22Bat_tot = sum([Variables['EFlow']['data']['CHP22Bat'][t-1] for t in Sets['Time_Set']['data']])  
                CHP22Bat_per = CHP22Bat_tot*100/CHP2_tot
                print 'E-Storage system charging by CHP (ecopower3.0): '
                print ('%.2f' % CHP22Bat_tot), ' kWh/year'
                print ('%.2f' % CHP22Bat_per), ' % of produced CHP E-energy'         
            if NoYes['SellToGrid'] == 1:
                CHP2Grid_tot = sum([Variables['EFlow']['data']['CHP2Grid'][t-1] for t in Sets['Time_Set']['data']])  
                CHP2Grid_per = CHP2Grid_tot*100/CHP2_tot
                print 'Direct CHP grid feed-in (ecopower3.0): '
                print ('%.2f' % CHP2Grid_tot), ' kWh/year'
                print ('%.2f' % CHP2Grid_per), ' % of produced CHP E-energy'
            print ' '
    if NoYes['CHP3'] == 1:  
        if Variables['Num']['data']['CHP3'] >= 0.005:
            CHP3_tot = sum([Variables['EFlow']['data']['CHP3'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Total E-production from CHP (ecopower4.7): '
            print ('%.2f' % CHP3_tot), ' kWh/year'
            CHP32Load_tot = sum([Variables['EFlow']['data']['CHP32Load'][t-1] for t in Sets['Time_Set']['data']])  
            CHP32Load_per = CHP32Load_tot*100/CHP3_tot
            print 'Direct E-load supply by CHP (ecopower4.7): '
            print ('%.2f' % CHP32Load_tot), ' kWh/year'
            print ('%.2f' % CHP32Load_per), ' % of produced CHP E-energy'
            if NoYes['EStor'] == 1:
                CHP32Bat_tot = sum([Variables['EFlow']['data']['CHP32Bat'][t-1] for t in Sets['Time_Set']['data']])  
                CHP32Bat_per = CHP32Bat_tot*100/CHP3_tot
                print 'E-Storage system charging by CHP (ecopower4.7): '
                print ('%.2f' % CHP32Bat_tot), ' kWh/year'
                print ('%.2f' % CHP32Bat_per), ' % of produced CHP E-energy'         
            if NoYes['SellToGrid'] == 1:
                CHP3Grid_tot = sum([Variables['EFlow']['data']['CHP3Grid'][t-1] for t in Sets['Time_Set']['data']])  
                CHP3Grid_per = CHP3Grid_tot*100/CHP3_tot
                print 'Direct CHP grid feed-in (ecopower4.7): '
                print ('%.2f' % CHP3Grid_tot), ' kWh/year'
                print ('%.2f' % CHP3Grid_per), ' % of produced CHP E-energy'
            print ' '        
    print 'Yearly NG demand: '
    print ('%.2f' % NG_tot), ' NGkWth/year'
    print 'Yearly Q-load demand: '
    print ('%.2f' % QLoad_tot), ' kWth/year'
    if NoYes['NGBurner1'] == 1:
        NGBurner12QLoad_tot = sum([Variables['QFlow']['data']['NGBurner12QLoad'][t-1] for t in Sets['Time_Set']['data']])  
        print 'Direct Q-Load supply by NGBurner1: '
        print ('%.2f' % NGBurner12QLoad_tot), ' kWth/year'
    if NoYes['NGBurner2'] == 1:
        NGBurner22QLoad_tot = sum([Variables['QFlow']['data']['NGBurner22QLoad'][t-1] for t in Sets['Time_Set']['data']])  
        print 'Direct Q-Load supply by NGBurner2: '
        print ('%.2f' % NGBurner22QLoad_tot), ' kWth/year'
    if NoYes['NGBurner3'] == 1:
        NGBurner32QLoad_tot = sum([Variables['QFlow']['data']['NGBurner32QLoad'][t-1] for t in Sets['Time_Set']['data']])  
        print 'Direct Q-Load supply by NGBurner3: '
        print ('%.2f' % NGBurner32QLoad_tot), ' kWth/year'
    if NoYes['CHP1'] == 1:
        CHP12QLoad_tot = sum([Variables['QFlow']['data']['CHP12QLoad'][t-1] for t in Sets['Time_Set']['data']])  
        print 'Direct Q-Load supply by CHPs (ecopower1.0): '
        print ('%.2f' % CHP12QLoad_tot), ' kWth/year'
    if NoYes['CHP2'] == 1:
        CHP22QLoad_tot = sum([Variables['QFlow']['data']['CHP22QLoad'][t-1] for t in Sets['Time_Set']['data']])  
        print 'Direct Q-Load supply by CHPs (ecopower3.0): '
        print ('%.2f' % CHP22QLoad_tot), ' kWth/year'
    if NoYes['CHP3'] == 1:
        CHP32QLoad_tot = sum([Variables['QFlow']['data']['CHP32QLoad'][t-1] for t in Sets['Time_Set']['data']])  
        print 'Direct Q-Load supply by CHPs (ecopower4.7): '
        print ('%.2f' % CHP32QLoad_tot), ' kWth/year'
    if NoYes['QStor1'] == 1:  
        if NoYes['EHeatQStor'] == 1:        
            EHeatQStor2QStor1_tot = sum([Variables['QFlow']['data']['EHeatQStor2QStor1'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (300l) charging by E-heaters: '
            print ('%.2f' % EHeatQStor2QStor1_tot), ' kWth/year'
        if NoYes['CHP1'] == 1:
            CHP12QStor1_tot = sum([Variables['QFlow']['data']['CHP12QStor1'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (300l) charging by CHPs (ecopower1.0): '
            print ('%.2f' % CHP12QStor1_tot), ' kWth/year'
        if NoYes['CHP2'] == 1:
            CHP22QStor1_tot = sum([Variables['QFlow']['data']['CHP22QStor1'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (300l) charging by CHPs (ecopower3.0): '
            print ('%.2f' % CHP22QStor1_tot), ' kWth/year'   
        if NoYes['CHP3'] == 1:
            CHP32QStor1_tot = sum([Variables['QFlow']['data']['CHP32QStor1'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (300l) charging by CHPs (ecopower4.7): '
            print ('%.2f' % CHP32QStor1_tot), ' kWth/year'     
        if NoYes['NGBurner1'] == 1:
            NGBurner12QStor1_tot = sum([Variables['QFlow']['data']['NGBurner12QStor1'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (300l) charging by NG burners1: '
            print ('%.2f' % NGBurner12QStor1_tot), ' kWth/year'
        if NoYes['NGBurner2'] == 1:
            NGBurner22QStor1_tot = sum([Variables['QFlow']['data']['NGBurner22QStor1'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (300l) charging by NG burners2: '
            print ('%.2f' % NGBurner22QStor1_tot), ' kWth/year'
        if NoYes['NGBurner3'] == 1:
            NGBurner22QStor1_tot = sum([Variables['QFlow']['data']['NGBurner32QStor1'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (300l) charging by NG burners3: '
            print ('%.2f' % NGBurner22QStor1_tot), ' kWth/year'
    if NoYes['QStor2'] == 1:  
        if NoYes['EHeatQStor'] == 1:        
            EHeatQStor2QStor2_tot = sum([Variables['QFlow']['data']['EHeatQStor2QStor2'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by E-heaters: '
            print ('%.2f' % EHeatQStor2QStor2_tot), ' kWth/year'
        if NoYes['CHP1'] == 1:
            CHP12QStor2_tot = sum([Variables['QFlow']['data']['CHP12QStor2'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by CHPs (ecopower1.0): '
            print ('%.2f' % CHP12QStor2_tot), ' kWth/year'
        if NoYes['CHP2'] == 1:
            CHP22QStor2_tot = sum([Variables['QFlow']['data']['CHP22QStor2'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by CHPs (ecopower3.0): '
            print ('%.2f' % CHP22QStor2_tot), ' kWth/year'   
        if NoYes['CHP3'] == 1:
            CHP32QStor2_tot = sum([Variables['QFlow']['data']['CHP32QStor2'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by CHPs (ecopower4.7): '
            print ('%.2f' % CHP32QStor2_tot), ' kWth/year'     
        if NoYes['NGBurner1'] == 1:
            NGBurner12QStor2_tot = sum([Variables['QFlow']['data']['NGBurner12QStor2'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by NG burners1: '
            print ('%.2f' % NGBurner12QStor2_tot), ' kWth/year'
        if NoYes['NGBurner2'] == 1:
            NGBurner22QStor2_tot = sum([Variables['QFlow']['data']['NGBurner22QStor2'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by NG burners2: '
            print ('%.2f' % NGBurner22QStor2_tot), ' kWth/year'
        if NoYes['NGBurner3'] == 1:
            NGBurner22QStor2_tot = sum([Variables['QFlow']['data']['NGBurner32QStor2'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by NG burners3: '
            print ('%.2f' % NGBurner22QStor2_tot), ' kWth/year'
    if NoYes['QStor3'] == 1:  
        if NoYes['EHeatQStor'] == 1:        
            EHeatQStor2QStor3_tot = sum([Variables['QFlow']['data']['EHeatQStor2QStor3'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by E-heaters: '
            print ('%.2f' % EHeatQStor2QStor3_tot), ' kWth/year'
        if NoYes['CHP1'] == 1:
            CHP12QStor3_tot = sum([Variables['QFlow']['data']['CHP12QStor3'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by CHPs (ecopower1.0): '
            print ('%.2f' % CHP12QStor3_tot), ' kWth/year'
        if NoYes['CHP2'] == 1:
            CHP22QStor3_tot = sum([Variables['QFlow']['data']['CHP22QStor3'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by CHPs (ecopower3.0): '
            print ('%.2f' % CHP22QStor3_tot), ' kWth/year'   
        if NoYes['CHP3'] == 1:
            CHP32QStor3_tot = sum([Variables['QFlow']['data']['CHP32QStor3'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by CHPs (ecopower4.7): '
            print ('%.2f' % CHP32QStor3_tot), ' kWth/year'     
        if NoYes['NGBurner1'] == 1:
            NGBurner12QStor3_tot = sum([Variables['QFlow']['data']['NGBurner12QStor3'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by NG burners1: '
            print ('%.2f' % NGBurner12QStor3_tot), ' kWth/year'
        if NoYes['NGBurner2'] == 1:
            NGBurner22QStor3_tot = sum([Variables['QFlow']['data']['NGBurner22QStor3'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by NG burners2: '
            print ('%.2f' % NGBurner22QStor3_tot), ' kWth/year'
        if NoYes['NGBurner3'] == 1:
            NGBurner22QStor3_tot = sum([Variables['QFlow']['data']['NGBurner32QStor3'][t-1] for t in Sets['Time_Set']['data']])  
            print 'Q-Storage system (800l) charging by NG burners3: '
            print ('%.2f' % NGBurner22QStor3_tot), ' kWth/year'        
    print ' '
    print ' '
           
    if plotEFlows == 1:

# Colors for EFlows        
        CPV2Load=sns.xkcd_rgb["medium green"]
        CPV2Bat=sns.xkcd_rgb["light violet"]
        CPVGrid=sns.xkcd_rgb["pale red"]
        CPVBurner=sns.xkcd_rgb["sun yellow"]
        
        CCHP2Load=sns.xkcd_rgb["emerald green"]
        CCHP2Bat=sns.xkcd_rgb["dark violet"]
        CCHPGrid=sns.xkcd_rgb["deep red"]        
                
        CGridLoad=sns.xkcd_rgb["dark grey"]
        CBurnerLoad=sns.xkcd_rgb["black"]
        CBat2Load=sns.xkcd_rgb["pale pink"]
        CEStor=sns.xkcd_rgb["pinkish"]
        
# Colors for QFlows  
        CNGBurner2QLoad=sns.xkcd_rgb["khaki"]
        CNGBurner2QStor=sns.xkcd_rgb["army green"]
        
        CCHP2QLoad=sns.xkcd_rgb["emerald green"]
        CCHP2QStor=sns.xkcd_rgb["dark violet"]
        
        CEHeat2QStor=sns.xkcd_rgb["black"]    
       
        CQStor2QLoad=sns.xkcd_rgb["pale pink"]
        CQStor=sns.xkcd_rgb["pinkish"]
        
        SubPlots1=0  
        SubPlots2=0 
        SubPlots3=0 
        SubPlots4=0 
        SubPlots5=0 
        
        LengthWeek=Timesteps//365*7
                             
        if NoYes['Load'] == 1:
            if NoYes['GridLoad'] == 1:
                GridLoadWeek = Variables['EFlow']['data']['GridLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.            
            if NoYes['LoadSupply'] == 0:
                BurnerLoadWeek = Variables['EFlow']['data']['BurnerLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.            
            if NoYes['EStor'] == 1:
                Bat2LoadWeek = Variables['EFlow']['data']['Bat2Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.
            SubPlots1=SubPlots1+1
        if NoYes['SellToGrid'] == 1:
            SubPlots1=SubPlots1+1
        if NoYes['PV'] == 1:
            PV2LoadWeek=Variables['EFlow']['data']['PV2Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.
            PVBurnerWeek=Variables['EFlow']['data']['PVBurner'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.
            if NoYes['SellToGrid'] == 1:
                PVGridWeek=Variables['EFlow']['data']['PVGrid'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.
                GridFeedIn=Variables['EFlow']['data']['PVGrid']*Timesteps/8760.
            if NoYes['EStor'] == 1:
                PV2BatWeek=Variables['EFlow']['data']['PV2Bat'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.            
            if Variables['Size']['data']['PV'] >= 0.005:
                SubPlots2=SubPlots2+1 
        if NoYes['CHP1'] == 1 or NoYes['CHP2'] == 1 or NoYes['CHP3'] == 1:  
            CHP12LoadWeek=np.zeros(LengthWeek)
            CHP22LoadWeek=np.zeros(LengthWeek)
            CHP32LoadWeek=np.zeros(LengthWeek)
            CHP1GridWeek=np.zeros(LengthWeek)
            CHP2GridWeek=np.zeros(LengthWeek)
            CHP3GridWeek=np.zeros(LengthWeek)
            CHP1GridFeedIn=np.zeros(Timesteps)
            CHP2GridFeedIn=np.zeros(Timesteps)
            CHP3GridFeedIn=np.zeros(Timesteps)
            CHP12BatWeek=np.zeros(LengthWeek)
            CHP22BatWeek=np.zeros(LengthWeek)
            CHP32BatWeek=np.zeros(LengthWeek)
            
            if NoYes['CHP1'] == 1:
                CHP12LoadWeek=Variables['EFlow']['data']['CHP12Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.                
                if NoYes['SellToGrid'] == 1:
                    CHP1GridWeek=Variables['EFlow']['data']['CHP1Grid'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
                    CHP1GridFeedIn=Variables['EFlow']['data']['CHP1Grid']*Timesteps/8760.
                if NoYes['EStor'] == 1:
                    CHP12BatWeek=Variables['EFlow']['data']['CHP12Bat'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
            if NoYes['CHP2'] == 1:            
                CHP22LoadWeek=Variables['EFlow']['data']['CHP22Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.                
                if NoYes['SellToGrid'] == 1:
                    CHP2GridWeek=Variables['EFlow']['data']['CHP2Grid'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
                    CHP2GridFeedIn=Variables['EFlow']['data']['CHP2Grid']*Timesteps/8760.
                if NoYes['EStor'] == 1:
                    CHP22BatWeek=Variables['EFlow']['data']['CHP22Bat'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
            if NoYes['CHP3'] == 1:            
                CHP32LoadWeek=Variables['EFlow']['data']['CHP32Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.                
                if NoYes['SellToGrid'] == 1:
                    CHP3GridWeek=Variables['EFlow']['data']['CHP3Grid'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
                    CHP3GridFeedIn=Variables['EFlow']['data']['CHP3Grid']*Timesteps/8760.
                if NoYes['EStor'] == 1:
                    CHP32BatWeek=Variables['EFlow']['data']['CHP32Bat'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
            CHP2LoadWeek= CHP12LoadWeek + CHP22LoadWeek + CHP32LoadWeek
            if NoYes['SellToGrid'] == 1:
                CHPGridWeek = CHP1GridWeek + CHP2GridWeek + CHP3GridWeek 
                CHPGridFeedIn = CHP1GridFeedIn+ CHP2GridFeedIn + CHP3GridFeedIn                   
            if NoYes['EStor'] == 1:
                CHP2BatWeek = CHP12BatWeek + CHP22BatWeek + CHP32BatWeek

            if NoYes['CHP1'] == 1 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 1:            
                if Variables['Num']['data']['CHP1'] or Variables['Num']['data']['CHP2'] or Variables['Num']['data']['CHP3']>= 0.005:
                    SubPlots2=SubPlots2+3  
            elif NoYes['CHP1'] == 1 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0: 
                if Variables['Num']['data']['CHP1'] or Variables['Num']['data']['CHP2'] >= 0.005:
                    SubPlots2=SubPlots2+2
            elif NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 1:            
                if Variables['Num']['data']['CHP1'] or Variables['Num']['data']['CHP3']>= 0.005:
                    SubPlots2=SubPlots2+2 
            elif NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 1:            
                if Variables['Num']['data']['CHP2'] or Variables['Num']['data']['CHP3']>= 0.005:
                    SubPlots2=SubPlots2+2  
            elif NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 0:            
                if Variables['Num']['data']['CHP1']:
                    SubPlots2=SubPlots2+1                  
            elif NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:            
                if Variables['Num']['data']['CHP2']:
                    SubPlots2=SubPlots2+1
            elif NoYes['CHP1'] == 0 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 1:            
                if Variables['Num']['data']['CHP3']:
                    SubPlots2=SubPlots2+1
 
        if NoYes['EStor'] == 1:
            if Variables['Size']['data']['EStor'] >= 0.005:
                SubPlots3=SubPlots3+2
        if NoYes['QLoad'] == 1:
            NGBurner12QLoadWeek=np.zeros(LengthWeek)
            NGBurner22QLoadWeek=np.zeros(LengthWeek)
            NGBurner32QLoadWeek=np.zeros(LengthWeek)
            CHP12QLoadWeek=np.zeros(LengthWeek)
            CHP22QLoadWeek=np.zeros(LengthWeek)
            CHP32QLoadWeek=np.zeros(LengthWeek)
            QStor12QLoadWeek=np.zeros(LengthWeek)
            QStor22QLoadWeek=np.zeros(LengthWeek)
            QStor32QLoadWeek=np.zeros(LengthWeek)
                        
            if NoYes['NGBurner1'] == 1:
                NGBurner12QLoadWeek=Variables['QFlow']['data']['NGBurner12QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['NGBurner2'] == 1:
                NGBurner22QLoadWeek=Variables['QFlow']['data']['NGBurner22QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['NGBurner3'] == 1:
                NGBurner32QLoadWeek=Variables['QFlow']['data']['NGBurner32QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760                    
            if NoYes['CHP1'] == 1:
                CHP12QLoadWeek=Variables['QFlow']['data']['CHP12QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['CHP2'] == 1:
                CHP22QLoadWeek=Variables['QFlow']['data']['CHP22QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['CHP3'] == 1:
                CHP32QLoadWeek=Variables['QFlow']['data']['CHP32QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['QStor1'] == 1:
                QStor12QLoadWeek=Variables['QFlow']['data']['QStor12QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['QStor2'] == 1:
                QStor22QLoadWeek=Variables['QFlow']['data']['QStor22QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['QStor3'] == 1:
                QStor32QLoadWeek=Variables['QFlow']['data']['QStor32QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            NGBurner2QLoadWeek=NGBurner12QLoadWeek + NGBurner22QLoadWeek + NGBurner32QLoadWeek
            CHP2QLoadWeek=CHP12QLoadWeek + CHP22QLoadWeek +CHP32QLoadWeek
            QStor2QLoadWeek=QStor12QLoadWeek+QStor22QLoadWeek+QStor32QLoadWeek
            
            SubPlots4=SubPlots4+1

        if NoYes['QStor'] == 1:
            NGBurner12QStor1Week=np.zeros(LengthWeek)
            NGBurner22QStor1Week=np.zeros(LengthWeek)
            NGBurner32QStor1Week=np.zeros(LengthWeek)
            CHP12QStor1Week=np.zeros(LengthWeek)
            CHP22QStor1Week=np.zeros(LengthWeek)
            CHP32QStor1Week=np.zeros(LengthWeek)
            NGBurner12QStor2Week=np.zeros(LengthWeek)
            NGBurner22QStor2Week=np.zeros(LengthWeek)
            NGBurner32QStor2Week=np.zeros(LengthWeek)
            CHP12QStor2Week=np.zeros(LengthWeek)
            CHP22QStor2Week=np.zeros(LengthWeek)
            CHP32QStor2Week=np.zeros(LengthWeek)
            NGBurner12QStor3Week=np.zeros(LengthWeek)
            NGBurner22QStor3Week=np.zeros(LengthWeek)
            NGBurner32QStor3Week=np.zeros(LengthWeek)
            CHP12QStor3Week=np.zeros(LengthWeek)
            CHP22QStor3Week=np.zeros(LengthWeek)
            CHP32QStor3Week=np.zeros(LengthWeek)
            EHeatQStor2QStor1Week=np.zeros(LengthWeek)
            EHeatQStor2QStor2Week=np.zeros(LengthWeek)
            EHeatQStor2QStor3Week=np.zeros(LengthWeek)
            QStor1C=np.zeros(Timesteps)
            QStor2C=np.zeros(Timesteps)
            QStor3C=np.zeros(Timesteps)
            QStor1D=np.zeros(Timesteps)
            QStor2D=np.zeros(Timesteps)
            QStor3D=np.zeros(Timesteps)
            QinS1=np.zeros(Timesteps)
            QinS2=np.zeros(Timesteps)
            QinS3=np.zeros(Timesteps)
            
            if NoYes['QStor1'] == 1:
                QStor1C = Timesteps/8760.*Variables['QFlow']['data']['QStor1C']
                QStor1D =Timesteps/8760.*Variables['QFlow']['data']['QStor1D'] 
                QinS1 = Variables['QinS']['data']['QStor1C']\
                /(Variables['Num']['data']['QStor1C']*Parameter['QStorCapSize']['data']['QStor1C'])*100\
                /Parameter['QStorUseCap']['data']['QStor1C']
                if NoYes['NGBurner1'] == 1:  
                    NGBurner12QStor1Week=Variables['QFlow']['data']['NGBurner12QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['NGBurner2'] == 1:  
                    NGBurner12QStor1Week=Variables['QFlow']['data']['NGBurner22QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                if NoYes['NGBurner3'] == 1:  
                    NGBurner12QStor1Week=Variables['QFlow']['data']['NGBurner32QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760                  
                if NoYes['CHP1'] == 1:   
                    CHP12QStor1Week=Variables['QFlow']['data']['CHP12QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP2'] == 1:   
                    CHP22QStor1Week=Variables['QFlow']['data']['CHP22QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP3'] == 1:   
                    CHP32QStor1Week=Variables['QFlow']['data']['CHP32QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['EHeatQStor'] == 1:   
                    EHeatQStor2QStor1Week=Variables['QFlow']['data']['EHeatQStor2QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                    EEHeatQStorWeek=Variables['EFlow']['data']['EHeatQStor'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760 
                    
            if NoYes['QStor2'] == 1:
                QStor2C = Timesteps/8760.*Variables['QFlow']['data']['QStor2C']
                QStor2D =Timesteps/8760.*Variables['QFlow']['data']['QStor2D']               
                QinS2 = Variables['QinS']['data']['QStor2C']\
                /(Variables['Num']['data']['QStor2C']*Parameter['QStorCapSize']['data']['QStor2C'])*100\
                /Parameter['QStorUseCap']['data']['QStor2C']
                if NoYes['NGBurner1'] == 1:  
                    NGBurner12QStor2Week=Variables['QFlow']['data']['NGBurner12QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['NGBurner2'] == 1:  
                    NGBurner12QStor2Week=Variables['QFlow']['data']['NGBurner22QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                if NoYes['NGBurner3'] == 1:  
                    NGBurner12QStor2Week=Variables['QFlow']['data']['NGBurner32QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760                  
                if NoYes['CHP1'] == 1:   
                    CHP12QStor2Week=Variables['QFlow']['data']['CHP12QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP2'] == 1:   
                    CHP22QStor2Week=Variables['QFlow']['data']['CHP22QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP3'] == 1:   
                    CHP32QStor2Week=Variables['QFlow']['data']['CHP32QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['EHeatQStor'] == 1:   
                    EHeatQStor2QStor2Week=Variables['QFlow']['data']['EHeatQStor2QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                    EEHeatQStorWeek=Variables['EFlow']['data']['EHeatQStor'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760 
                    
            if NoYes['QStor3'] == 1:
                QStor3C = Timesteps/8760.*Variables['QFlow']['data']['QStor3C']
                QStor3D =Timesteps/8760.*Variables['QFlow']['data']['QStor3D']
                QinS3 = Variables['QinS']['data']['QStor3C']\
                /(Variables['Num']['data']['QStor3C']*Parameter['QStorCapSize']['data']['QStor3C'])*100\
                /Parameter['QStorUseCap']['data']['QStor3C']
                if NoYes['NGBurner1'] == 1:  
                    NGBurner12QStor3Week=Variables['QFlow']['data']['NGBurner12QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['NGBurner2'] == 1:  
                    NGBurner12QStor3Week=Variables['QFlow']['data']['NGBurner22QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                if NoYes['NGBurner3'] == 1:  
                    NGBurner12QStor3Week=Variables['QFlow']['data']['NGBurner32QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760                  
                if NoYes['CHP1'] == 1:   
                    CHP12QStor3Week=Variables['QFlow']['data']['CHP12QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP2'] == 1:   
                    CHP22QStor3Week=Variables['QFlow']['data']['CHP22QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP3'] == 1:   
                    CHP32QStor3Week=Variables['QFlow']['data']['CHP32QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['EHeatQStor'] == 1:   
                    EHeatQStor2QStor3Week=Variables['QFlow']['data']['EHeatQStor2QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                    EEHeatQStorWeek=Variables['EFlow']['data']['EHeatQStor'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760 
                
            NGBurner2QStorWeek=NGBurner12QStor1Week + NGBurner22QStor1Week + NGBurner32QStor1Week + NGBurner12QStor2Week \
            + NGBurner22QStor2Week + NGBurner32QStor2Week + NGBurner12QStor3Week + NGBurner22QStor3Week + NGBurner32QStor3Week
            CHP2QStorWeek=CHP12QStor1Week + CHP22QStor1Week +CHP32QStor1Week + CHP12QStor2Week + CHP22QStor2Week +CHP32QStor2Week \
            + CHP12QStor3Week + CHP22QStor3Week +CHP32QStor3Week
            
            EHeatQStor2QStorWeek= EHeatQStor2QStor1Week + EHeatQStor2QStor2Week +EHeatQStor2QStor3Week
            
            QStorC=QStor1C + QStor2C + QStor3C
            QStorD=QStor1D + QStor2D + QStor3D            
            QinS = QinS1 + QinS2+ QinS3
                
            if max(QStorD) >= 0.005:
                SubPlots5=SubPlots5+2 
                
        if NoYes['CHP'] == 1 and NoYes['PV'] == 1 and NoYes['SellToGrid'] == 1:
            GridFeedIn=Variables['EFlow']['data']['PVGrid']*Timesteps/8760.+CHPGridFeedIn
        elif NoYes['CHP'] == 1 and NoYes['PV'] == 0 and NoYes['SellToGrid'] == 1:
            GridFeedIn=CHPGridFeedIn
        elif NoYes['CHP'] == 0 and NoYes['PV'] == 1 and NoYes['SellToGrid'] == 1:
            GridFeedIn=Variables['EFlow']['data']['PVGrid']*Timesteps/8760.
        else:
            GridFeedIn = np.zeros(Timesteps)
        
        Plotcounter = 1
        
        if SubPlots1 > 0:        
            plt.figure(Plotcounter, figsize=(6,3*SubPlots1))         
            SubPlotCounter=1
            x_axis=np.arange(0,LengthWeek)/(Timesteps/365.)
            
            if NoYes['Load'] == 1:  
                plt.subplot(SubPlots1*100+10+SubPlotCounter)
                SubPlotCounter=SubPlotCounter+1
                if NoYes['EHeatQStor'] == 1:
                    plt.plot(x_axis,Parameter['EProfil']['data']['Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='E-Load, HH',linewidth=0.7)
                    plt.plot(x_axis,Parameter['EProfil']['data']['Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.+EEHeatQStorWeek,label='E-Load, HH (inc. e-heating)',linewidth=0.7)
                else:                     
                    plt.plot(x_axis,Parameter['EProfil']['data']['Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='load, gesamt',linewidth=0.7) 
                                
                if NoYes['GridLoad'] == 1: 
                    if NoYes['PV'] == 1 and NoYes['CHP'] == 1 and NoYes['EStor'] == 1: 
                        fcolors=[CPV2Load, CCHP2Load, CBat2Load, CGridLoad]
                        plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,Bat2LoadWeek,GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                        plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-Load-discharging')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')                  
                    elif NoYes['PV'] == 1 and NoYes['CHP'] == 1 and NoYes['EStor'] == 0: 
                        fcolors=[CPV2Load, CCHP2Load, CGridLoad]
                        plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')
                    elif NoYes['PV'] == 1 and NoYes['CHP'] == 0 and NoYes['EStor'] == 1:
                        fcolors=[CPV2Load, CBat2Load, CGridLoad]
                        plt.stackplot(x_axis,PV2LoadWeek,Bat2LoadWeek,GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                        plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-Load-discharging')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')
                    elif NoYes['PV'] == 1 and NoYes['CHP'] == 0 and NoYes['EStor'] == 0:
                        fcolors=[CPV2Load, CGridLoad]
                        plt.stackplot(x_axis,PV2LoadWeek,GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')     
                    elif NoYes['PV'] == 0 and NoYes['CHP'] == 1 and NoYes['EStor'] == 1:
                        fcolors=[CCHP2Load, CBat2Load, CGridLoad]
                        plt.stackplot(x_axis,CHP2LoadWeek,Bat2LoadWeek,GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                        plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-Load-discharging')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')
                    elif NoYes['PV'] == 0 and NoYes['CHP'] == 1 and NoYes['EStor'] == 0:
                        fcolors=[CCHP2Load, CGridLoad]
                        plt.stackplot(x_axis,CHP2LoadWeek,GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')
                    elif NoYes['PV'] == 0 and NoYes['CHP'] == 0 and NoYes['EStor'] == 1:
                        fcolors=[CBat2Load, CGridLoad]
                        plt.stackplot(x_axis,Bat2LoadWeek,GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-Load-discharging')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')                    
                    else:
                        fcolors=[CGridLoad]
                        plt.stackplot(x_axis,GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')  
                else:
                    if NoYes['PV'] == 1:               
                        if NoYes['CHP1'] == 1:
                            if NoYes['EStor'] == 1:
                                fcolors=[CPV2Load, CCHP2Load, CBat2Load, CBurnerLoad]
                                plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,Bat2LoadWeek,BurnerLoadWeek,colors=fcolors)  
                                plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                                plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                                plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging')
                                plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')
                            else:
                                fcolors=[CPV2Load, CCHP2Load, CBurnerLoad]
                                plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,BurnerLoadWeek,colors=fcolors)  
                                plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                                plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                                plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')
                        elif NoYes['EStor'] == 1:
                            fcolors=[CPV2Load, CBat2Load, CBurnerLoad]
                            plt.stackplot(x_axis,PV2LoadWeek,Bat2LoadWeek,BurnerLoadWeek,colors=fcolors)  
                            plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                            plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging')
                            plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')
                        else:
                            fcolors=[CPV2Load, CBurnerLoad]
                            plt.stackplot(x_axis,PV2LoadWeek,BurnerLoadWeek,colors=fcolors)  
                            plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                            plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')                     
                    else:
                        fcolors=[CBurnerLoad]
                        plt.stackplot(x_axis,BurnerLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')  
    
                plt.ylabel('Power [kW]')
                plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                plt.xlim(0,7)
                if NoYes['EHeatQStor'] == 1:
                    plt.ylim(0,np.round(max((Parameter['EProfil']['data']['Load']+Variables['EFlow']['data']['EHeatQStor'])*Timesteps/8760)+.5),0)                    
                else:
                    plt.ylim(0,np.round(max(Parameter['EProfil']['data']['Load']*Timesteps/8760)+.5),0)
                plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            
            if NoYes['SellToGrid'] == 1:  
                plt.subplot(SubPlots1*100+10+SubPlotCounter)
                SubPlotCounter=SubPlotCounter+1
                
                if NoYes['GridLoad'] == 1:                 
                    if NoYes['PV'] == 1 and NoYes['CHP'] == 1:
                        plt.plot(x_axis,(PVGridWeek+CHPGridWeek-GridLoadWeek),label='Grid exchange',linewidth=0.7) 
                        fcolors=[CPVGrid, CCHPGrid, CGridLoad]
                        plt.stackplot(x_axis,PVGridWeek,CHPGridWeek,-GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in')
                        plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')                
                    elif NoYes['PV'] == 0 and NoYes['CHP'] == 1:
                        plt.plot(x_axis,(CHPGridWeek-GridLoadWeek),label='Grid exchange',linewidth=0.7) 
                        fcolors=[CCHPGrid, CGridLoad]
                        plt.stackplot(x_axis,CHPGridWeek,-GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')                                             
                    elif NoYes['PV'] == 1 and NoYes['CHP'] == 0:
                        plt.plot(x_axis,(PVGridWeek-GridLoadWeek),label='Grid exchange',linewidth=0.7) 
                        fcolors=[CPVGrid, CGridLoad]
                        plt.stackplot(x_axis,PVGridWeek,-GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in')
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption') 
                    else:
                        plt.plot(x_axis,(-GridLoadWeek),label='Grid exchange',linewidth=0.7) 
                        fcolors=[CGridLoad]
                        plt.stackplot(x_axis,-GridLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')  
                
                    plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(-np.round((max(Variables['EFlow']['data']['GridLoad']*Timesteps/8760)+.5),0),\
                    np.round((max(GridFeedIn)+.5),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            
            plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
            plt.savefig('Results\GridFlowsWeek.png', dpi=300, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, bbox_inches='tight', pad_inches=0.1,
                frameon=None)
            Plotcounter=Plotcounter+1
               
        # Generation plots 
        if SubPlots2 > 0:
            plt.figure(Plotcounter, figsize=(6,3*SubPlots2))         
            SubPlotCounter=1
            
            if NoYes['PV'] == 1:
                if Variables['Size']['data']['PV'] >= 0.005:
                    plt.subplot(SubPlots2*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.plot(x_axis,Parameter['EProfil']['data']['PV'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Variables['Size']['data']['PV']*Timesteps/8760.,label='PV, generated',linewidth=0.7)                
                                                                   
                    if NoYes['SellToGrid'] == 1:                    
                        if NoYes['EStor'] == 1:
                            fcolors=[CPV2Load, CPV2Bat, CPVGrid, CPVBurner]
                            plt.stackplot(x_axis,PV2LoadWeek,PV2BatWeek,PVGridWeek,PVBurnerWeek,colors=fcolors)
                            plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                            plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')   
                            plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in') 
                            plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')                         
                        else:  
                            fcolors=[CPV2Load, CPVGrid, CPVBurner]
                            plt.stackplot(x_axis,PV2LoadWeek,PVGridWeek,PVBurnerWeek,colors=fcolors) 
                            plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                            plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in') 
                            plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')    
                    elif NoYes['EStor'] == 1:
                        fcolors=[CPV2Load, CPV2Bat, CPVBurner]
                        plt.stackplot(x_axis,PV2LoadWeek,PV2BatWeek,PVBurnerWeek,colors=fcolors)       
                        plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                        plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')   
                        plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')                                    
                    else:
                        fcolors=[CPV2Load, CPVBurner]
                        plt.stackplot(x_axis,PV2LoadWeek,PVBurnerWeek,colors=fcolors)  
                        plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                        plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')
                   
                    plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(0,np.round((max(Parameter['EProfil']['data']['PV']\
                    *Variables['Size']['data']['PV']*Timesteps/8760)+.5),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                    
            if NoYes['CHP1'] == 1: 
                if Variables['Num']['data']['CHP1'] >= 0.005:
                    plt.subplot(SubPlots2*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.plot(x_axis,Variables['EFlow']['data']['CHP1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='E-CHP eco1.0, generated',linewidth=0.7) 
    
                    if NoYes['SellToGrid'] == 1:                    
                        if NoYes['EStor'] == 1:
                            fcolors=[CCHP2Load, CCHP2Bat, CCHPGrid]
                            plt.stackplot(x_axis,CHP12LoadWeek,CHP12BatWeek,CHP1GridWeek,colors=fcolors)
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                            plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')   
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')                     
                        else:  
                            fcolors=[CCHP2Load, CCHPGrid]
                            plt.stackplot(x_axis,CHP12LoadWeek, CHP1GridWeek,colors=fcolors) 
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption') 
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')     
                    elif NoYes['EStor'] == 1:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP12LoadWeek,CHP12BatWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                        plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')   
                    else:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP12LoadWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                                   
                    plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(0,np.round((Variables['Num']['data']['CHP1']*Parameter['CHP1FixedSize']['data']),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                    
            if NoYes['CHP2'] == 1: 
                if Variables['Num']['data']['CHP2'] >= 0.005:
                    plt.subplot(SubPlots2*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.plot(x_axis,Variables['EFlow']['data']['CHP2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='E-CHP eco3.0, generated',linewidth=0.7) 
    
                    if NoYes['SellToGrid'] == 1:                    
                        if NoYes['EStor'] == 1:
                            fcolors=[CCHP2Load, CCHP2Bat, CCHPGrid]
                            plt.stackplot(x_axis,CHP22LoadWeek,CHP22BatWeek,CHP2GridWeek,colors=fcolors)
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption')
                            plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP2-Battery charging')   
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP2-Grid feed-in')                     
                        else:  
                            fcolors=[CCHP2Load, CCHPGrid]
                            plt.stackplot(x_axis,CHP22LoadWeek, CHP2GridWeek,colors=fcolors) 
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption') 
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')     
                    elif NoYes['EStor'] == 1:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP22LoadWeek,CHP22BatWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption')
                        plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP2-Battery charging')   
                    else:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP22LoadWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption')
                                   
                    plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(0,np.round((Variables['Num']['data']['CHP2']*Parameter['CHP2FixedSize']['data']),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            
            if NoYes['CHP3'] == 1: 
                if Variables['Num']['data']['CHP3'] >= 0.005:
                    plt.subplot(SubPlots2*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.plot(x_axis,Variables['EFlow']['data']['CHP3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='E-CHP eco4.7, generated',linewidth=0.7) 
    
                    if NoYes['SellToGrid'] == 1:                    
                        if NoYes['EStor'] == 1:
                            fcolors=[CCHP2Load, CCHP2Bat, CCHPGrid]
                            plt.stackplot(x_axis,CHP32LoadWeek,CHP32BatWeek,CHP3GridWeek,colors=fcolors)
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption')
                            plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP3-Battery charging')   
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP3-Grid feed-in')                     
                        else:  
                            fcolors=[CCHP2Load, CCHPGrid]
                            plt.stackplot(x_axis,CHP32LoadWeek, CHP3GridWeek,colors=fcolors) 
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption') 
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP3-Grid feed-in')     
                    elif NoYes['EStor'] == 1:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP32LoadWeek,CHP32BatWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption')
                        plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP3-Battery charging')   
                    else:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP32LoadWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption')
                                   
                    plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(0,np.round((Variables['Num']['data']['CHP3']*Parameter['CHP3FixedSize']['data']),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))            
            plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
            plt.savefig('Results\GenerationFlowsWeek.png', dpi=300, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, bbox_inches='tight', pad_inches=0.1,
                frameon=None)
            Plotcounter=Plotcounter+1
               
        # E-Storage plots 
        if SubPlots3 > 0:
            plt.figure(Plotcounter, figsize=(6,3*SubPlots3))         
            SubPlotCounter=1
                
            if NoYes['EStor'] == 1:
                if Variables['Size']['data']['EStor'] >= 0.005:
                    plt.subplot(SubPlots3*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.plot(x_axis,(Timesteps/8760.*Variables['EFlow']['data']['BatCEStor'][LengthWeek*(Week-1):LengthWeek*Week]\
                    -Timesteps/8760.*Variables['EFlow']['data']['EStorBatD'][LengthWeek*(Week-1):LengthWeek*Week])
                    ,label='Battery power',linewidth=0.5)
                    
                    if NoYes['PV'] == 1 and NoYes['CHP'] == 1:
                        fcolors=[CPV2Bat, CCHP2Bat, CBat2Load]                
                        plt.stackplot(x_axis,PV2BatWeek,CHP2BatWeek,-Bat2LoadWeek,colors=fcolors)                  
                        plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')
                        plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')
                        plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging') 
                    elif NoYes['PV'] == 0 and NoYes['CHP'] == 1:
                        fcolors=[CCHP2Bat, CBat2Load]                
                        plt.stackplot(x_axis,CHP2BatWeek,-Bat2LoadWeek,colors=fcolors)                  
                        plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')
                        plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging') 
                    elif NoYes['PV'] == 1 and NoYes['CHP'] == 0:
                        fcolors=[CPV2Bat, CBat2Load]                
                        plt.stackplot(x_axis,PV2BatWeek,-Bat2LoadWeek,colors=fcolors)                        
                        plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')
                        plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging') 
                            
                    plt.ylabel('Power [kW]')
                    plt.xlim(0,7)
                    plt.ylim(-np.round((Variables['Size']['data']['BatC']*Timesteps/8760+.25),0),np.round((Variables['Size']['data']['BatC']*Timesteps/8760+.25),0))
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                    
                    plt.subplot(SubPlots3*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.stackplot(x_axis,(Variables['EinS']['data'][LengthWeek*(Week-1):LengthWeek*Week]*100/Variables['Size']['data']['EStor']/Parameter['UseableEStorCap']['data']),colors=[CEStor])  
                    plt.plot([], [], color=CEStor, linewidth=10, label='Energy in battery')                
                    plt.ylabel('SOC [%]')
                    plt.xlim(0,7)
                    plt.ylim(0,100)
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))   
            
                    plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
                    plt.savefig('Results\EStorageWeek.png', dpi=300, facecolor='w', edgecolor='w',
                        orientation='portrait', papertype=None, format=None,
                        transparent=False, bbox_inches='tight', pad_inches=0.1,
                        frameon=None)
                    Plotcounter=Plotcounter+1
               
        # Q-Load plots   
        if SubPlots4 > 0:       
            plt.figure(Plotcounter, figsize=(6,3*SubPlots4))         
            SubPlotCounter=1
            
            if NoYes['QLoad'] == 1:  
                plt.subplot(SubPlots4*100+10+SubPlotCounter)
                SubPlotCounter=SubPlotCounter+1
                plt.plot(x_axis,Parameter['QProfil']['data']['QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.,label='Q-load, total',linewidth=0.7) 
                            
                if NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['QStor'] == 1:
                    fcolors=[CCHP2QLoad, CNGBurner2QLoad, CQStor2QLoad]
                    plt.stackplot(x_axis,CHP2QLoadWeek,NGBurner2QLoadWeek,QStor2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-load')                        
                    plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-load')
                    plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')
                elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['QStor'] == 0:
                    fcolors=[CCHP2QLoad, CNGBurner2QLoad]
                    plt.stackplot(x_axis,CHP2QLoadWeek,NGBurner2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-load')
                    plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-load')
                elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['QStor'] == 1:
                    fcolors=[CNGBurner2QLoad, CQStor2QLoad]
                    plt.stackplot(x_axis,NGBurner2QLoadWeek,QStor2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-load')            
                    plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')
                elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['QStor'] == 0:
                    fcolors=[CNGBurner2QLoad]
                    plt.stackplot(x_axis,NGBurner2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-load')     
                elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['QStor'] == 1:
                    fcolors=[CCHP2QLoad, CQStor2QLoad]
                    plt.stackplot(x_axis,CHP2QLoadWeek,QStor2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-load')
                    plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')
                elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['QStor'] == 0:
                    fcolors=[CCHP2QLoad]
                    plt.stackplot(x_axis,CHP2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-load')  
                elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 0 and NoYes['QStor'] == 1:
                    fcolors=[CQStor2QLoad,]
                    plt.stackplot(x_axis,QStor2QLoadWeek,Week,colors=fcolors)  
                    plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')                     
    
                plt.ylabel('Power [kW]')
                plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                plt.xlim(0,7)
                plt.ylim(0,np.round(max(Parameter['QProfil']['data']['QLoad']*Timesteps/8760)+.5),0)
                plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))  
                
                plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
                plt.savefig('Results\QFlowsWeek.png', dpi=300, facecolor='w', edgecolor='w',
                    orientation='portrait', papertype=None, format=None,
                    transparent=False, bbox_inches='tight', pad_inches=0.1,
                    frameon=None)
                Plotcounter=Plotcounter+1
               
        # Q-Storage plots  
        if SubPlots5 > 0:
            plt.figure(Plotcounter, figsize=(6,3*SubPlots5))         
            SubPlotCounter=1
                
            if NoYes['QStor'] == 1:                           
                if max(QStorD) >= 0.005:
                    plt.subplot(SubPlots5*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.plot(x_axis,QStorC[LengthWeek*(Week-1):LengthWeek*Week],color=sns.xkcd_rgb["light blue"],label='Q-storage charging power',linewidth=0.7)                 
                    plt.plot(x_axis,-QStorD[LengthWeek*(Week-1):LengthWeek*Week],color=sns.xkcd_rgb["dark blue"],label='Q-storage discharging power',linewidth=0.7)                             
                    if NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 0:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CNGBurner2QStor, CCHP2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,NGBurner2QStorWeek,CHP2QStorWeek,colors=fcolors2)  
                        plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
                        plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['EHeatQStor'] == 0:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CNGBurner2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,NGBurner2QStorWeek,colors=fcolors2)   
                        plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['EHeatQStor'] == 1:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CNGBurner2QStor,CEHeat2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,NGBurner2QStorWeek,EHeatQStor2QStorWeek,colors=fcolors2)   
                        plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
                        plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 1:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CNGBurner2QStor,CCHP2QStor,CEHeat2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,NGBurner2QStorWeek,CHP2QStorWeek,EHeatQStor2QStorWeek,colors=fcolors2)   
                        plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
                        plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
                        plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 0:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CCHP2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,CHP2QStorWeek,colors=fcolors2)    
                        plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 0 and NoYes['EHeatQStor'] == 1:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CEHeat2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,EHeatQStor2QStorWeek,colors=fcolors2)    
                        plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 1:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CCHP2QStor,CEHeat2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,CHP2QStorWeek,EHeatQStor2QStorWeek,colors=fcolors2)   
                        plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
                        plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))    
                    plt.xlim(0,7)
                    plt.ylim(-np.round((max(QStorD)+.5),0)*Timesteps/8760.,\
                    np.round((max(QStorC)+.5),0)*Timesteps/8760.)                                        
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                    
                    plt.subplot(SubPlots5*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.stackplot(x_axis,QinS[LengthWeek*(Week-1):LengthWeek*Week],colors=[CQStor])
                    plt.plot([], [], color=CQStor, linewidth=10, label='Energy in Q-storage')                
                    plt.ylabel('SOC [%]')
                    plt.xlim(0,7)
                    plt.ylim(0,100)
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5)) 
                    
                    plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
                    plt.savefig('Results\QStorageWeek.png', dpi=300, facecolor='w', edgecolor='w',
                        orientation='portrait', papertype=None, format=None,
                        transparent=False, bbox_inches='tight', pad_inches=0.1,
                        frameon=None)
                    Plotcounter=Plotcounter+1
        
    if plotAnalyses == 1:  
# Energy usage
            
        CPV2Load=sns.xkcd_rgb["medium green"]
        CPV2Bat=sns.xkcd_rgb["dark lavender"]
        CPVGrid=sns.xkcd_rgb["pale red"]
        CPVBurner=sns.xkcd_rgb["dark yellow"]

        CCHP2Load=sns.xkcd_rgb["deep green"]
        CCHP2Bat=sns.xkcd_rgb["dark violet"]
        CCHPGrid=sns.xkcd_rgb["deep red"]
        CCHPBurner=sns.xkcd_rgb["dark yellow"]      

        CCHP2Load=sns.xkcd_rgb["light green"]
        CCHP2Bat=sns.xkcd_rgb["violet"]
        CCHPGrid=sns.xkcd_rgb["light red"]
        CCHP2Burner=sns.xkcd_rgb["yellow"]  
    
        y_ticks=np.arange(0,101,20)
        tickslabel=np.arange(0,101,20) 
        SubPlots=2    
        plt.figure((Plotcounter), figsize=(6,3*SubPlots))
        SubPlotCounter=1              
        plt.subplot(SubPlots*100+10+SubPlotCounter)
        SubPlotCounter=SubPlotCounter+1
        width = 0.5  
               
        if NoYes['PV'] == 1 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP1Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1'])        
            
            elif Variables['Num']['data']['CHP1'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
            
            elif Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])
                
        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP2Grid_per)            
                Gen2Load = (PV2Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP22Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP2'])        
            
            elif Variables['Num']['data']['CHP2'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])
        
        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 0 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 1:
            if Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP3'])        
            
            elif Variables['Num']['data']['CHP3'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (CHP3Grid_per)            
                Gen2Load = (CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP32Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])
    
        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2,3])                
                Gen2Grid = (PVGrid_per, CHP1Grid_per, CHP2Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per, CHP22Bat_per)
                Gen2Burner = (PVBurner_per, 0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1', 'CHP2'])  
            
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP1Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1'])  
                
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP2Grid_per)            
                Gen2Load = (PV2Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP22Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP2']) 
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005:
                BarCounter = np.array([1,2])                
                Gen2Grid = (CHP1Grid_per, CHP2Grid_per)            
                Gen2Load = (CHP12Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per, CHP22Bat_per)
                Gen2Burner = (0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1', 'CHP2'])                 
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
            
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])  

        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 1:
            if Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2,3])               
                Gen2Grid = (PVGrid_per, CHP1Grid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1', 'CHP2'])  
            
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP1Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1'])  
                
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP2']) 
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005:
                BarCounter = np.array([1,2])                
                Gen2Grid = (CHP1Grid_per, CHP3Grid_per)            
                Gen2Load = (CHP12Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per, CHP32Bat_per)
                Gen2Burner = (0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1', 'CHP2'])                 
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
            
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP3Grid_per)            
                Gen2Load = (CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP32Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])  
                
        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 1:
            if Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2,3])               
                Gen2Grid = (PVGrid_per, CHP2Grid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP22Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP22Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1', 'CHP2'])  
            
            elif Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP2Grid_per)            
                Gen2Load = (PV2Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP22Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1'])  
                
            elif Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP2']) 
                
            elif Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005:
                BarCounter = np.array([1,2])                
                Gen2Grid = (CHP2Grid_per, CHP3Grid_per)            
                Gen2Load = (CHP22Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per, CHP32Bat_per)
                Gen2Burner = (0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1', 'CHP2'])                 
                
            elif Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
            
            elif Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP3Grid_per)            
                Gen2Load = (CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP32Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV']) 
                
        elif NoYes['PV'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 0:
            if Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])        
                
        elif NoYes['PV'] == 0 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP1'] >= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
                
        elif NoYes['PV'] == 0 and NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP2'] >= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])    
                
        elif NoYes['PV'] == 0 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
                
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005:  
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])  
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (CHP1Grid_per, CHP2Grid_per)            
                Gen2Load = (CHP12Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per, CHP22Bat_per)
                Gen2Burner = (0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1', 'CHP2']) 
        
        plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
        plt.xlabel('Installed DER')
        plt.ylabel('Energy [%]')
        plt.ylim(0,100)
        plt.yticks(y_ticks, tickslabel)
        plt.savefig('Results\EnergyDistribution.png', dpi=300, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches='tight', pad_inches=0.1,
        frameon=None)
        Plotcounter=Plotcounter + 1
               
# Power distribution 
        if NoYes['NGBurner'] == 1 or NoYes['CHP'] == 1 \
        or NoYes['EStor'] == 1:          
            x_axis=np.arange(0,Timesteps)
            x_ticks=np.arange(0,(Timesteps+1),Timesteps/5)
            SubPlots=0
            if NoYes['NGBurner1'] == 1:
                if Variables['Num']['data']['NGBurner1'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['NGBurner2'] == 1:
                if Variables['Num']['data']['NGBurner2'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['NGBurner3'] == 1:
                if Variables['Num']['data']['NGBurner3'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['CHP1'] == 1:
                if Variables['Num']['data']['CHP1'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['CHP2'] == 1:
                if Variables['Num']['data']['CHP2'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['CHP3'] == 1:
                if Variables['Num']['data']['CHP3'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['EStor'] == 1:
                if Variables['Size']['data']['EStor'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
            SubPlotCounter=1
            if NoYes['NGBurner1'] == 1:
                if Variables['Num']['data']['NGBurner1'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['QFlow']['data']['NGBurner1']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['NGBurner1']*Parameter['QMaxSize']['data']['NGBurner1'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of NG burner1 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            if NoYes['NGBurner2'] == 1:
                if Variables['Num']['data']['NGBurner2'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['QFlow']['data']['NGBurner2']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['NGBurner2']*Parameter['QMaxSize']['data']['NGBurner2'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of NG burner2 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))   
            if NoYes['NGBurner3'] == 1:
                if Variables['Num']['data']['NGBurner3'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['QFlow']['data']['NGBurner3']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['NGBurner3']*Parameter['QMaxSize']['data']['NGBurner3'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of NG burner3 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))                     
            if NoYes['CHP1'] == 1:
                if Variables['Num']['data']['CHP1'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['EFlow']['data']['CHP1']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['CHP1']*Parameter['CHP1FixedSize']['data'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of CHP1 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            if NoYes['CHP2'] == 1:
                if Variables['Num']['data']['CHP2'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['EFlow']['data']['CHP2']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['CHP2']*Parameter['CHP2FixedSize']['data'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of CHP2 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))   
            if NoYes['CHP3'] == 1:
                if Variables['Num']['data']['CHP3'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['EFlow']['data']['CHP3']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['CHP3']*Parameter['CHP3FixedSize']['data'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of CHP3 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5)) 
            if NoYes['EStor'] == 1:
                if Variables['Size']['data']['EStor'] >= 0.005:
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort((Variables['EFlow']['data']['BatCEStor']+Variables['EFlow']['data']['EStorBatD'])))*\
                    100*(Timesteps/8760)/Variables['Size']['data']['BatC'],0,facecolor=sns.xkcd_rgb["medium green"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["medium green"],label='Distribution of battery power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            plt.xlabel('Percentage of opertion hours [%/a]')
            plt.savefig('Results\PowerDistribution.png', dpi=300, facecolor='w', edgecolor='w',
            orientation='portrait', papertype=None, format=None,
            transparent=False, bbox_inches='tight', pad_inches=0.1,
            frameon=None)
            
    if plotSankey == 1:
        fig = plt.figure(figsize=(8, 3))
        ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[])
        sankey = Sankey(ax=ax, format='%.1G', unit=' MWh', gap=0.5, scale=0.6/PV_tot)
        
        sankey.add(label='PV', facecolor='#37c959', rotation=-90,
           flows=[-PVGrid_tot, -PVBurner_tot, PV_tot, -PV2Load_tot, -PV2Bat_tot,],
           labels=['', '', '', '', ''],
           pathlengths=[0.5,0.5,0.5,0.5,0.1],
           orientations=[-1, -1, 0, 1, 1])        
        sankey.add(label='Battery', facecolor='r',
           flows=[PV2Bat_tot, -BatDisch_tot, -BatBurner_tot],
           labels=[None, None, None],
           pathlengths=[0.05, 0.1, 0.1],
           orientations=[0, 1, -1], prior=0, connect=(4, 0))
        sankey.add(label='Load', facecolor='g',
           flows=[BatDisch_tot, PV2Load_tot, ELoadGrid_tot, -ELoad_tot],
           labels=['', '', '', ''],
           pathlengths=[0.3, 0.01, 0.1, 0.5],
           orientations=[-1, 0, -1, 0], prior=0, connect=(3, 1))
        sankey.add(label='Grid exchange', facecolor='b',
           flows=[PVGrid_tot, -ELoadGrid_tot],
           labels=['', ''],
           pathlengths=0.25,
           orientations=[-1, 1], prior=0, connect=(0, 0))
        diagrams = sankey.finish()
        plt.legend(loc='best')
        plt.show()
        fig.savefig('Sankey.png', dpi=300, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches='tight', pad_inches=0.1,
        frameon=None)
                    
    Eco['npv']=npv
    Eco['Invest'] = Fix_I
    Eco['EInvest'] = EFix_I
    Eco['QInvest'] = QFix_I
    if NoYes['PV'] == 1:
        Eco['PVGridSales'] = sum([Parameter['Sign']['data']['PVGrid']*sum([Parameter['EVarCost']['data']['PVGrid'][t-1]*Variables['EFlow']['data']['PVGrid'][t-1] for t in set(Sets['Time_Set']['data'])])\
        *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['EVarCost_Inc']['data']['PVGrid'],Parameter['RRR']['data'])])
        Eco['LoadGridCost'] = sum([Parameter['Sign']['data']['GridLoad']*sum([Parameter['EVarCost']['data']['GridLoad'][t-1]*Variables['EFlow']['data']['GridLoad'][t-1] for t in set(Sets['Time_Set']['data'])])\
        *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['EVarCost_Inc']['data']['GridLoad'],Parameter['RRR']['data'])])
    Eco['NGcost']= cQVar
    if NoYes['EStorSub'] == 1:    
        Eco['EStorSub'] = Variables['EStorSub']['data']    
    
    if NoYes['PV'] == 1:
        SysSize['PVkWp'] = Variables['Size']['data']['PV']
    
    if NoYes['EStor'] == 1:
        SysSize['EStorkWh'] = Variables['Size']['data']['EStor']
        SysSize['EStorkW'] = Variables['Size']['data']['BatC']    
    
    if NoYes['PV'] == 1:
        PVdata['PV_total'] = PV_tot  
        PVdata['PVGrid_total'] = PVGrid_tot
        PVdata['PVGrid_percentage'] = PVGrid_per
        PVdata['PVSelf_total'] = PVSelf_tot
        PVdata['PVSelf_percentage'] = PVSelf_per
        PVdata['PVLosses_total'] = PVBurner_tot
        PVdata['PVLosses_percentage'] = PVBurner_per
    
    ELoaddata['ELoad_total'] = ELoad_tot 
    ELoaddata['ELoadGrid_total'] = ELoadGrid_tot
    ELoaddata['ELoadGrid_percentage'] = ELoadGrid_per
    ELoaddata['ELoadSelf_total'] = ELoadSelf_tot
    ELoaddata['ELoadSelf_percentage'] = ELoadSelf_per
            
    return Eco, SysSize, PVdata, ELoaddata
     

        
