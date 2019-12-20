# -*- coding: utf-8 -*-
"""
Created on Tue May 31 13:21:46 2016

@author: tkreiske
Auswertung von CO2 Ergebnissen
"""
import pandas as pd
import numpy as np

def SensitivityAnalyseModes(Pfad, foremethod):

    #Haushalt = ['EFH','MFH']    
    Haushalt = ['MFH']    # not in Kombination with LPG
    #Haushalt = ['EFH']       
    
    #TimeSeriesIn = ['VDE', 'LPG']    
    TimeSeriesIn = ['VDE']   
    #TimeSeriesIn = ['LPG']   
     
    #InChoice = ['Default','ohneFIT']     
    InChoice = ['Default']    
         
    #IncentiveLO = ['LOoff','LOon','LOart']
    #IncentiveLO = ['LOFITon']    
    IncentiveLO = ['LOoff']       
    #IncentiveLO = ['LOart']       
    
    #IncentiveER = ['ERoff','ERon','ERart']
    #IncentiveER = ['ERFITon']    
    IncentiveER = ['ERoff']       
    #IncentiveER = ['ERart']       
     
    #Abregelung = ['ABon']         
    Abregelung = ['ABoff']     
     
    # Nur Perfekt möglich - keine Prognose implementiert !!! 
    fore_method = foremethod   
    
    #Horizon = [2, 15, 36, 72, 144] 
    Horizon = [36]
    #Horizon = [144]    
    
    for e in range (0, len(IncentiveLO)):   
     for f in range (0, len(IncentiveER)):   
      for g in range (0, len(Haushalt)):
       for h in range(0, len(TimeSeriesIn)):  
        for l in range(0, len(InChoice)):
         for k in range(0, len(fore_method)):
          fore = fore_method 
          for i in range(0, len(Horizon)):        
                PrHoBin = Horizon[i]  #72;        
                KPI = readKPI(Pfad, PrHoBin, fore, InChoice[l], TimeSeriesIn[h], Haushalt[g], IncentiveLO[e]\
                ,IncentiveER[f], Abregelung[0])   
    return KPI

def SensitivityAnalyseCases(Pfad, foremethod, InChoice, IncentiveLO, IncentiveER, Abregelung):

    #Haushalt = ['EFH','MFH']    
    Haushalt = ['MFH']    # add values and InputFiles TMK 3.6.16
    #Haushalt = ['EFH']       
    
    #TimeSeriesIn = ['VDE', 'LPG']    
    TimeSeriesIn = ['VDE']   
    #TimeSeriesIn = ['LPG']   
        
    #Horizon = [2, 15, 36, 72, 144] 
    Horizon = [36]
    #Horizon = [144]    
    print Pfad, Horizon[0], foremethod, InChoice, TimeSeriesIn[0], Haushalt[0], IncentiveLO\
                ,IncentiveER, Abregelung
    KPI = readKPI(Pfad, Horizon[0], foremethod, InChoice, TimeSeriesIn[0], Haushalt[0], IncentiveLO\
                ,IncentiveER, Abregelung)   
    return KPI
  

def readKPI(Pfad, PrHoBin, fore_method, InputChoice, TimeSeriesIn, Haushalt, IncentiveLO,IncentiveER, Abregelung):
    
    #Horizon = [2, 15, 36, 72, 144]  
    Saison = ['Winter','Sommer','Uebergang']
    
  
      # --------------------------------
      # READ KPI
      # --------------------------------
    for j in range(0, len(Saison)):
        #for i in range(0, len(Horizon)):
         INOUT_string = '_'+str(PrHoBin/6.)+'_'+Saison[j]+'_'+fore_method+'_'+InputChoice\
        +'_'+TimeSeriesIn+'_'+Haushalt+'_'+ IncentiveLO+'_'+ IncentiveER+'_'+Abregelung
         OUT_string = '_'+str(PrHoBin/6.)+'_'+InputChoice\
        +'_'+TimeSeriesIn+'_'+Haushalt+'_'+ IncentiveLO+'_'+ IncentiveER+'_'+Abregelung               

         if j==0:
            #PrHoBin = Horizon[i]    
            KPI = pd.read_csv(Pfad+INOUT_string+'_10.csv')             
             # --------------------------------
            # First row is falsly the index, new row index is added ???
            # Try to fix it here
            # --------------------------------
            INDEX1 = KPI.columns[0]
            INDEX2 = KPI.columns[1]
            INDEX_df = pd.DataFrame(np.array([[INDEX1, INDEX2]]), index=['100'], \
            columns=['name',''+Saison[j]+''])
            #print INDEX1, INDEX2
            #print INDEX_df
            KPI.columns = ['name', ''+Saison[j]+'']
            KPI = KPI.append(INDEX_df)
            #print KPI.ix[:,1]
            # --------------------------------
           # print KPI
            
         else:
            #PrHoBin = Horizon[i]    
            #KPIlocal = pd.read_csv(PfadCost+'\Results\KPIs'+str(mode)+str(name)+'_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')    
            KPIlocal = pd.read_csv(Pfad+INOUT_string+'_10.csv')             
          
            # --------------------------------
            # First row is falsly the index, new row index is added ???
            # Try to fix it here
            # --------------------------------
            INDEX1 = KPIlocal.columns[0]
            INDEX2 = float(KPIlocal.columns[1])
            INDEX_df = pd.DataFrame(np.array([[INDEX1, INDEX2]]), index=['100'], \
            columns=['name',''+Saison[j]+''])
            #print INDEX1, INDEX2
            #print INDEX_df
            KPIlocal.columns = ['name', ''+Saison[j]+'']
            KPIlocal = KPIlocal.append(INDEX_df)
            #print KPI.ix[:,0].values
            # --------------------------------
 
            KPI = pd.concat([KPI, KPIlocal.ix[:,1]], axis=1)
    # change to correct index         
    KPI.index = KPI.ix[:,0].values  
    del KPI['name']
    #print KPI
 
    # -------------- Ändert x und y achse und erzeugt numerische Werte   
    KPI=KPI.T
    KPI = KPI.convert_objects(convert_numeric=True)    
    # ----------------------------------------------------------------        
    return KPI, OUT_string
    
#==============================================================================
# def readTimeSeries(PfadCost, name, mode):
# 
#     Horizon = [2, 15, 36, 72, 144]  
#     Saison = ['Winter','Sommer','Uebergang']
#     
#       # --------------------------------
#       # READ TimeSeries
#       # --------------------------------
#     for j in range(0, len(Saison)):
#         for i in range(0, len(Horizon)):
#             
#             if i==0 and j==0:
#                 PrHoBin = Horizon[i]    
#                 Grid = pd.read_csv(PfadCost+'\RESULTS\Results_'+str(mode)+'_'+str(name)+'Grid_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv') 
#   #              Grid = pd.read_csv(PfadCost+'\RESULTS\'+str(mode)+'Results_'+str(name)+'Grid_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv') 
#                 PV = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'PV_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')  
#                 BAT = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'BAT_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')    
#                 CHP = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'CHP_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')    
#                 TES = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'TES_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')    
#                 HEAT = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'Heat_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')    
#             else:
#                 PrHoBin = Horizon[i]    
#                 Gridlocal = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'Grid_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv') 
#                 PVlocal = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'PV_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')  
#                 BATlocal = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'BAT_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')    
#                 CHPlocal = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'CHP_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')    
#                 TESlocal = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'TES_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')    
#                 HEATlocal = pd.read_csv(PfadCost+'\RESULTS\Results'+str(mode)+'_'+str(name)+'Heat_'+str(PrHoBin/6)+'_'+Saison[j]+'_10.csv')    
#                 
#                 Grid = pd.concat([Grid, Gridlocal.ix[:,1]], axis=1)
#                 PV = pd.concat([PV, PVlocal.ix[:,1]], axis=1)
#                 BAT = pd.concat([BAT, BATlocal.ix[:,1]], axis=1)
#                 CHP = pd.concat([CHP, CHPlocal.ix[:,1]], axis=1)
#                 TES = pd.concat([TES, TESlocal.ix[:,1]], axis=1)
#                 HEAT = pd.concat([HEAT, HEATlocal.ix[:,1]], axis=1)
# 
#     print PV    
#                 
#     Components = pd.Panel([Grid, PV, BAT, CHP, TES, HEAT],\
#            index = ['Grid', 'PV', 'BAT', 'CHP', 'TES', 'HEAT'])                
#            
#     return Components
#         
#==============================================================================
        