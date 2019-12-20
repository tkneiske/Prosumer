# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 21:21:28 2015
26.9 Ziel: CHP, TES, Battery, Gasboiler
CHP, PV, Battery Tes Gasboiler Kostenoptimal
12.10.15 PV ist auch implementiert !
       Forecast vom Vortag 
13.10.15 (einige) KPI und Plotting wie in OptIn implementiert       
23.10.15 Unterscheidung des Eigenverbrauchs in load and bat für PV und CHP
26.10.15 Jahressimulation implementiert
26.10.15 Ausgabe in csv Files       
19.4.16  Umbau zu Vaillant Regelung, Optimierung nur 1 mal für 24 Stunden
17.05.16 Einfügen der Option Strom-Wärme-LPG Daten statt VDI in inputvalues.py
01.06.16 Einfügen der Prognose Auswahl und OptFlex_forecast.py
9.9.2016 add CO2 optimierung und CO2 KPI

@author: tkneiske
"""
import OptFlex_inputvalues as ipv
import OptFlex_optimierer as opt
import matplotlib.pyplot as plt
import OptFlex_plotting as pl
import OptFlex_nachregelung as cor
import seaborn
import pandas as pd
import numpy as np
import OptFlex_KPIs as kpi
import OptFlex_Analyse as ana
import time as ti
import OptFlex_forecast as fore
#from copy import deepcopy

def Sensitivity():   
    Haushalt = ['EFH']    
    #Haushalt = ['MFH']  # only fpr LPG possible
    #Haushalt = ['EFH']    
    
    #TimeSeriesIn = ['VDE', 'LPG']    
    TimeSeriesIn = ['VDE']    
    #TimeSeriesIn = ['LPG']    
    
    #InChoice = ['ohneFIT','Default']     
    #InChoice = ['ohneFIT']     
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
    
    #fore_method = ['Persistenz', 'Mittel']
    fore_method = ['Persistenz']
    #fore_method = ['Mittel']
    #fore_method = ['Perfekt']   
    
    #Horizon = [2, 15, 36, 72, 144] 
    Horizon = [36]
    #Horizon = [144]
    
    Saison = ['Winter','Sommer','Uebergang']    
    #Saison = ['Winter']    
    #Saison = ['Uebergang']
    #Saison = ['Sommer']
    
   
    for e in range (0, len(IncentiveLO)):     
      for f in range (0, len(IncentiveER)):
        for g in range (0, len(Haushalt)):
            for h in range(0, len(TimeSeriesIn)):  
                #datachoice = TimeSeriesIn[h]
                for l in range(0, len(InChoice)):
                    for k in range(0, len(fore_method)):
                        fore = fore_method[k] 
                        for j in range(0, len(Saison)):       
                            Season = Saison[j]         
                            for i in range(0, len(Horizon)):        
                                PrHoBin = Horizon[i]  #72;        
                                print PrHoBin, Season
                                MPC(PrHoBin, Season, fore, InChoice[l], TimeSeriesIn[h], Haushalt[g],  IncentiveER[f],IncentiveLO[e], Abregelung[0])   
    return 0

def MPC(PrHoBin, Season, fore_method, InChoice,TimeSeriesIn, Haushalt, IncentiveER, IncentiveLO, Abregel):
    plt.close("all")

    #-----------------------------------------------
    # ---------------  INPUT DATA  -----------------   
    #-----------------------------------------------
    Delta_t = 10 # 10 min bins
    
    Saison = Season        
#    if Saison == "Winter":
#        start_date = '1/5/2013'    # 1/2/2013 kritischer Tag für Persistenz
#        end_date = '1/6/2013'
        #end_date = '1/5/2013'
#    elif Saison == "Uebergang":
#        start_date = '4/1/2013'    
#        end_date = '4/2/2013'
 #   elif Saison == "Sommer":
#        start_date = '6/16/2013'    
#        end_date = '6/17/2013'
#    else:
#        print "Fehler in Saison-Auswahl"b
        
    if Saison == "Winter":
        start_date = '1/5/2013'    
        end_date = '1/6/2013'
    elif Saison == "Uebergang":
        start_date = '4/9/2013'    
        end_date = '4/10/2013'
 #   elif Saison == "Sommer":
 #       start_date = '6/16/2013'    
 #       end_date = '6/17/2013'
    elif Saison == "Sommer":
        start_date = '8/2/2013'    
        end_date = '8/3/2013'
    else:
        print "Fehler in Saison-Auswahl"

        
    INOUT_string = '_CO2_'+str(PrHoBin/6.)+'_'+Saison+'_'+fore_method+'_'+InChoice+'_'+TimeSeriesIn+'_'+Haushalt+'_'+ IncentiveLO+'_'+ IncentiveER+'_'+Abregel
    if Saison == 'Uebergang' and PrHoBin > 143:
        PrHoBin = 1000000
        INOUT_string = '_CO2_'+str(144/6.)+'_'+Saison+'_'+fore_method+'_'+InChoice+'_'+TimeSeriesIn+'_'+Haushalt+'_'+ IncentiveLO+'_'+ IncentiveER+'_'+Abregel
    
    if InChoice == 'ohneFIT' and PrHoBin > 143:
        PrHoBin = 100000
        INOUT_string = '_CO2_'+str(144/6.)+'_'+Saison+'_'+fore_method+'_'+InChoice+'_'+TimeSeriesIn+'_'+Haushalt+'_'+ IncentiveLO+'_'+ IncentiveER+'_'+Abregel
 
    
    
    date_year = '1/1/2013'
    #-----------------------------------------------
    
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print '%                                                  %'
    print '%     CO2 Optimierung von CHP, TES, GASboiler      %'     
    print '%         PV, Battery nach KOSTEN + adhocVariable  %'     
    print '%                                                  %'
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        
    # -- Get number of days 
    helpdf = pd.date_range(start_date, end_date, freq='D') 
    numberOfdays = len(helpdf)
    if numberOfdays <= 0:
        print 'ERROR: Dates are wrong. Please check. Calculating days in August....'
        start_date = '8/11/2013'    
        end_date = '8/12/2013'

    if Delta_t == 10:    
        TimeStepSize = '10min'
        BIN = 144*numberOfdays
        year_bins = 52560
        PrHoBinRange = range(0, PrHoBin)  # PredHorizonBin
    else:
        print 'ERROR: Implemented only for 10 min Bins.'
                
    print 'Calculating the time period: ', start_date, 'to', end_date
    print 'for', numberOfdays, 'days'
    print 'Year: ', date_year
    year_stamps = pd.date_range(date_year, periods=year_bins, freq=TimeStepSize)  
                    
    # -------------------------------------------------------------------------
    # Get Input Parameter
    # -------------------------------------------------------------------------      
     #    PV und Lastzeitreihen
    if Haushalt == 'EFH':                      
        if TimeSeriesIn == 'VDE':
            PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                        ipv.Input_PV_Load_VDE_EFH(Delta_t, TimeStepSize,year_stamps)
        elif TimeSeriesIn == 'LPG':
                            PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                            ipv.Input_PV_Load_LPG_EFH(Delta_t, TimeStepSize,year_stamps)
        else:# default ist VDE  
                    print 'ERROR - TimeSeriesIn EFH'
#                            PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
#                            ipv.Input_PV_Load_VDE_EFH(Delta_t, TimeStepSize,year_stamps)
                    
                    # Components
        if InChoice == 'Default':                    
                        Battery, Auxilary, ThermalStorage, \
                        CHP, Costs, CO2  = ipv.inputvaluesDefault_EFH(Delta_t, TimeStepSize,year_stamps)
        elif InChoice == 'ohneFIT':
                            Battery, Auxilary, ThermalStorage, \
                            CHP, Costs, CO2  = ipv.inputvaluesOHNE_Verg_EFH(Delta_t, TimeStepSize,year_stamps)
        else: #default
                    print 'ERROR - InChoice EFH'
              #              Battery, Auxilary, ThermalStorage, \
              #              CHP, Costs = ipv.inputvaluesDefault_EFH(Delta_t, TimeStepSize,year_stamps)
                            
    elif Haushalt == 'MFH':
        if TimeSeriesIn == 'VDE': # will not be implemented
                PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                            ipv.Input_PV_Load_VDE_MFH(Delta_t, TimeStepSize,year_stamps)
        elif TimeSeriesIn == 'LPG':
                PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                            ipv.Input_PV_Load_LPG_MFH(Delta_t, TimeStepSize,year_stamps)
        else:# default ist VDE  
             print 'ERROR - TimeSeriesIn MFH', TimeSeriesIn
        #                    PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
        #                    ipv.Input_PV_Load_VDE_MFH(Delta_t, TimeStepSize,year_stamps)
                    
                    # Components
        if InChoice == 'Default':                    
                        Battery, Auxilary, ThermalStorage, \
                        CHP, Costs, CO2  = ipv.inputvaluesDefault_MFH(Delta_t, TimeStepSize,year_stamps)
        elif InChoice == 'ohneFIT':
                            Battery, Auxilary, ThermalStorage, \
                            CHP, Costs, CO2  = ipv.inputvaluesOHNE_Verg_MFH(Delta_t, TimeStepSize,year_stamps)
        else: #default
                        print 'ERROR - InChoice MFH'
        #                    Battery, Auxilary, ThermalStorage, \
        #                    CHP, Costs = ipv.inputvaluesDefault_MFH(Delta_t, TimeStepSize,year_stamps)
    else: #(default) 
                        print 'ERROR - Haushalt'                           
#        if TimeSeriesIn == ['VDE']:
#            PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
#                        ipv.Input_PV_Load_VDE_MFH(Delta_t, TimeStepSize,year_stamps)
#        elif TimeSeriesIn == ['LPG']:
#                            PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
#                            ipv.Input_PV_Load_LPG_MFH(Delta_t, TimeStepSize,year_stamps)
#        else:# default ist VDE  
#                            PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
#                            ipv.Input_PV_Load_VDE_MFH(Delta_t, TimeStepSize,year_stamps)
#                    
#                    # Components
#        if InChoice == 'Default':                    
#                        Battery, Auxilary, ThermalStorage, \
#                        CHP, Costs = ipv.inputvaluesDefault_MFG(Delta_t, TimeStepSize,year_stamps)
#        elif InChoice == 'ohneFIT':
#                            Battery, Auxilary, ThermalStorage, \
#                            CHP, Costs = ipv.inputvaluesOHNE_Verg_MFG(Delta_t, TimeStepSize,year_stamps)
#        else: #default
#                            Battery, Auxilary, ThermalStorage, \
#                            CHP, Costs = ipv.inputvaluesDefault_MFG(Delta_t, TimeStepSize,year_stamps)
#    
    day_stamps_date = pd.date_range(start_date, periods=BIN, freq=TimeStepSize)          
  
    # -------------------------------------------------------------------------
    #  Preiszeitreihe als Dataframe   EPEX und PV Vergütung
    # -------------------------------------------------------------------------
    if IncentiveLO == 'LOoff':   
        PreisProfilLO = Costs['C_grid_el']*pd.DataFrame(np.ones(BIN), index=day_stamps_date)
    elif IncentiveLO == 'LOon' :
        PreisProfilLO = ipv.PreisProfileLO(Delta_t, TimeStepSize,year_stamps,date_year, year_bins)
    elif IncentiveLO == 'LOart':
        PreisProfilLO = Costs['C_grid_el'] * ipv.ArtPreisProfileLO(Delta_t, TimeStepSize,year_stamps,date_year, year_bins)
    else: #PreisProfil = pd.DataFrame(Costs['C_grid_el']*np.ones(BIN))
        print 'ERROR - Incentive'
       
    if IncentiveER == 'ERoff':
        PreisProfilER = Costs['C_PV_FIT']*pd.DataFrame(np.ones(BIN), index=day_stamps_date)                
    elif IncentiveER == 'ERart':
        PreisProfilER = Costs['C_PV_FIT'] *ipv.ArtPreisProfileER(Delta_t, TimeStepSize,year_stamps,date_year, year_bins)
    elif IncentiveER == 'ERon':
        PreisProfilER = ipv.PreisProfile(Delta_t, TimeStepSize,year_stamps,date_year, year_bins)
    else: #PreisProfil = pd.DataFrame(Costs['C_grid_el']*np.ones(BIN))
        print 'ERROR - Incentive'
        
    print start_date, end_date
    PreisPlotER = PreisProfilER[start_date:end_date]
    PreisPlotLO = PreisProfilLO[start_date:end_date]
    #PreisProfilER.plot()
    #PreisProfilLO.plot()
    if IncentiveER == 'ERoff' or IncentiveLO == 'LOoff':
        print ("No time dependent prices used")
    else:   
        PreisPlotLO.plot(title='Strompreis')
        PreisPlotER.plot(title='Feed-In Tarif')
    #print PreisProfil.values              
    # -------------------------------------------------------------------------
  
    # -------------------------------------------------------------------------
    # REAL VALUES 
    # -------------------------------------------------------------------------
    day_stamps_date = pd.date_range(start_date, periods=BIN, freq=TimeStepSize)          
    # ---- Load
    LoadPeriodReal = LoadAll_TOT_df[start_date:end_date]
    # ---- PV
    PVavaPeriodReal = PVava_TOT_df[start_date:end_date]
    
    # -------------------------------------------------------------------------
    # FORECAST  Values -- Tagespersistenz oder 3 Tage Mittelwert
    # -------------------------------------------------------------------------    
    if fore_method == 'Persistenz':
        LoadPeriodFore = fore.TagesPersistenz(LoadAll_TOT_df, day_stamps_date, BIN)#
        PVavaPeriodFore = fore.TagesPersistenz(PVava_TOT_df, day_stamps_date, BIN)
    elif fore_method == 'Mittel':
        LoadPeriodFore = fore.DreiTageRunAverage(LoadAll_TOT_df, day_stamps_date, BIN)
        PVavaPeriodFore = fore.DreiTageRunAverage(PVava_TOT_df, day_stamps_date, BIN)
    elif fore_method == 'Perfekt':
        LoadPeriodFore = LoadPeriodReal
        PVavaPeriodFore = PVavaPeriodReal
    else: 
        LoadPeriodFore = LoadPeriodReal
        PVavaPeriodFore = PVavaPeriodReal
    
    # -------------------------------------------------------------------------        
    # --- Plot differenz Forecast-Real Values
    # PV_LOAD_R_F = pd.concat([PVavaPeriodReal-PVavaPeriodFore, 
    # LoadPeriodReal['ELoad']-LoadPeriodFore['ELoad']], axis=1)                          
    # PV_LOAD_R_F = pd.concat([PVavaPeriodReal, PVavaPeriodFore, 
    # LoadPeriodReal['ELoad'],LoadPeriodFore['ELoad']], axis=1)                          
    # PV_LOAD_R_F.plot(title="real-forecast")                            
        
    #-------------------------------------------------------------------------        
    # Erzeuge Loop für Optimierung, Optimierung findet immer nach Ablauf des
    # Prediction Horizon statt     
    # -------------------------------------------------------------------------        
    Loop = np.array(0)
    print len(LoadPeriodFore), PrHoBin
    for iloop in range(0, (len(LoadPeriodFore)-PrHoBin)/PrHoBin):
        Loop = np.append(Loop, iloop*PrHoBin)             
    print 'OptimierungsBins[] max', Loop, len(LoadPeriodFore)-PrHoBin   
    # -------------------------------------------------------------------------
    # Prepare: Ausgabe Dataframes
    # -------------------------------------------------------------------------
    #BAT    
    SOCbatEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['SOC battery']) 
    PbattcharEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Battery charging']) 
    PbattdisEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Battery dis-charging']) 
    Result_BAT_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['ELoad'], 
                            SOCbatEnd, PbattcharEnd, PbattdisEnd], axis=1)                      
    Result_BATFore_End = pd.concat([PVavaPeriodFore,-LoadPeriodFore['ELoad'], 
                            SOCbatEnd, PbattcharEnd, PbattdisEnd], axis=1)                      
    #Grid    
    GridImpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Grid Import'])
    GridExpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Grid Export'])    
    Result_Grid_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['ELoad'], 
                            GridImpEnd, GridExpEnd], axis=1)
    Result_GridFore_End = pd.concat([PVavaPeriodFore,-LoadPeriodFore['ELoad'], 
                            GridImpEnd, GridExpEnd], axis=1)
    #TES                                         
    SOCTESEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['SOC TES']) 
    PTEScharEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['TES charging']) 
    PTESdisEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['TES dis-charging']) 
    TES2fullEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['TES too full']) 
    Result_TES_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['QLoad1']*2, \
                SOCTESEnd, PTEScharEnd, PTESdisEnd, TES2fullEnd], axis=1)                      
    Result_TESFore_End = pd.concat([-LoadPeriodFore['QLoad1'], \
                -LoadPeriodFore['QLoad2'],SOCTESEnd, PTEScharEnd, PTESdisEnd], axis=1)                      

    CompTime = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Computational Time'])   
    
    #CHP
    CHPelEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CHP el'])                              
    CHPthEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CHP th'])                              
    CHPscloadEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CHP load self'])                              
    CHPscbattEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CHP batt self'])                              
    CHPexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CHP Export'])                              
    CHPonoffEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CHP on_off']) 
    CHPGas = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CHP Gas'])                              
    CHP2QLoad = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CHP th2load'])                             
    CHP2TES = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CHP th2TES'])                             
    Result_CHP_End = pd.concat([-LoadPeriodReal['ELoad'], -LoadPeriodReal['QLoad1']-LoadPeriodFore['QLoad2'],\
                            CHPelEnd, CHPthEnd, CHPscloadEnd,CHPscbattEnd, CHPexpEnd,\
                            CHPonoffEnd,CHPGas,CHP2QLoad ,CHP2TES], axis=1)                      
    Result_CHPFore_End = pd.concat([-LoadPeriodFore['ELoad'], -LoadPeriodFore['QLoad2']-LoadPeriodFore['QLoad1'],\
                            CHPelEnd, CHPthEnd, CHPscloadEnd,CHPscbattEnd, CHPexpEnd,\
                            CHPonoffEnd,CHPGas,CHP2QLoad ,CHP2TES], axis=1)                      
    #Heat                            
    AuxEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Aux Gasbrenner'])                              
    AuxGasEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Aux Gas'])                              
    AuxEndLoad = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Aux Gas2Load'])                              
    AuxEndTES = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Aux Gas2TES'])                              
    Result_Heat_End = pd.concat([-LoadPeriodReal['QLoad1']-LoadPeriodReal['QLoad2'], \
                            AuxEnd,AuxEndLoad,AuxEndTES,AuxGasEnd], axis=1)                                 	
    Result_HeatFore_End = pd.concat([-LoadPeriodFore['QLoad1']-LoadPeriodReal['QLoad2'],\
                            AuxEnd,AuxEndLoad,AuxEndTES,AuxGasEnd], axis=1)                                 	

    CompTime = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Computational Time'])   
    
    # ---------- PV ----------                       
    PVselfconbattEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV batt selfcon']) 
    PVselfconloadEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV load selfcon']) 
    PVexportEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Grid export']) 
    PVsumEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Summe'])     
    Result_PV_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'],\
                             PVselfconloadEnd,PVselfconbattEnd, PVexportEnd,PVsumEnd], axis=1)   
    Result_PVFore_End = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'],\
                             PVselfconloadEnd,PVselfconbattEnd, PVexportEnd,PVsumEnd], axis=1)   
    
    #Corrections for MPC                             
    CorrBatDissEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrBattDis'])
    CorrBatChEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrBattCh'])
    CorrBattSOCEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrBatSOC'])

    CorrGridImpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrGridImp'])
    CorrGridexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrGridExp'])

    CorrPVexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrPVexp'])
    CorrPV2BattEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrPV2Batt'])        
    CorrPV2LoadEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrPV2Load'])        
    
    CorrCHP2BattEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrCHP2Batt'])        
    CorrCHP2LoadEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrCHP2Load'])        
    CorrCHPexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrCHPExp'])
    CorrCHPthEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrCHPth'])             	                                   
    CorrCHPelEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrCHPel'])             	                                   
    CorrCHPGasEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrCHPGas'])             	                                   

    CorrTESDissEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrTESDis'])
    CorrTESChEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrTESCh'])
    CorrTESSOCEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrTESSOC'])

    CorrAuxEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrAux'])
    CorrAuxGasEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrAuxGas'])                                                        
   
    Result_Corr_End = pd.concat([ CorrBatChEnd,CorrBatDissEnd,CorrBattSOCEnd,\
                      CorrGridImpEnd, CorrPVexpEnd, CorrGridexpEnd, CorrPV2BattEnd,\
                      CorrPV2LoadEnd, CorrCHP2BattEnd,CorrCHP2LoadEnd,CorrCHPthEnd, \
                      CorrCHPexpEnd,CorrCHPelEnd,CorrCHPGasEnd, CorrTESDissEnd,CorrTESChEnd,\
                      CorrTESSOCEnd,CorrAuxEnd,CorrAuxGasEnd])

    # -------------------------------------------------------------------------
    # ------------  MPC Loop --------------------------------------------------    
    # -------------------------------------------------------------------------
    ELoadF = LoadPeriodFore['ELoad'].values  
    Q1LoadF = LoadPeriodFore['QLoad1'].values
    Q2LoadF = LoadPeriodFore['QLoad2'].values                       
    ELoadR = LoadPeriodReal['ELoad'].values  
    Q1LoadR = LoadPeriodReal['QLoad1'].values
    Q2LoadR = LoadPeriodReal['QLoad2'].values                       
    PVavaFore = PVavaPeriodFore['PV 2013, Kassel, 10min'].values #PV2013, Kassel, 10min
    PVavaReal = PVavaPeriodReal['PV 2013, Kassel, 10min'].values #PV2013, Kassel, 10min
    PPER = PreisProfilER[0].values
    PPLO = PreisProfilLO[0].values
 
    # --- for Rulebased loop: Übergabe von Speicherständen und CHP Zustand
    RuleIni = pd.DataFrame(np.zeros((1,3)), columns=['BattSOC_opti','TESSOC_opti','CHPooffn_opti'])    
    print RuleIni
    OptiMarker = 1
    
    #maxx = PrHoBin
    maxx = len(LoadPeriodFore)-PrHoBin
    t1 = ti.clock()    
    if len(LoadPeriodFore)-PrHoBin < 0:
        print 'Prediction Horizon out of Range!!!'   
    else:        
        maxx = 144
        for timestep in range(0, maxx):    # 10 min OptimierugsStep ++ Input Aufösung
            print timestep, maxx, [Result_Corr_End.index[timestep]]
            #print ' ' 
            #print PrHoBin, timestep, maxx, Saison,[Result_Corr_End.index[timestep]]
            #print PrHoBin, timestep, maxx, Saison, fore_method, InChoice, TimeSeriesIn,Haushalt,IncentiveER, IncentiveLO, Abregel        
            # -----------------------------------------------------------------            
            # ------------------ Initialize for the next step ---------------------
            # -----------------------------------------------------------------            
            Load = {i: ELoadF[i+timestep] for i in PrHoBinRange}; 
            P_sh_th = {i: Q1LoadF[i+timestep] for i in PrHoBinRange};
            P_dhw_th = {i: Q2LoadF[i+timestep] for i in PrHoBinRange};
            P_PV_ava = {i: PVavaFore[i+timestep] for i in PrHoBinRange};            
            PreisProfilER_cut ={i: PPER[i+timestep] for i in PrHoBinRange};                
            PreisProfilLO_cut ={i: PPLO[i+timestep] for i in PrHoBinRange};            
#==============================================================================
            # -----------------------------------------------------------------            
            # -------------------  Optimze ----------------------------------------    
            # -----------------------------------------------------------------
#==============================================================================
            #print 'vor Opt',	Battery['SOC_batt_ini'], \
            #                   RuleIni['BattSOC_opti'][0]
            horizon_stamps = day_stamps_date[timestep:PrHoBin+timestep]
            if timestep in Loop or OptiMarker == 1:    
            #if OptiMarker == 1:    
                print 'Optimierung findet statt bei ', timestep
                Opt_Result=opt.OptFlex_optimierer(
                    horizon_stamps, PrHoBin, Load, P_PV_max, P_Load_max,\
                    P_sh_th, P_dhw_th, P_PV_ava, Battery, Auxilary, \
                    ThermalStorage, CHP, Costs, CO2,PreisProfilER_cut, PreisProfilLO_cut, Abregel)
                loop = timestep 
                OptiMarker = 1                      
            #else:
                # Use values from nachregelung.py, not the time-schedule data
                       
#==============================================================================
#             # --- Einzelplots ----Test Prediction Horizon --------------------
#             Result_el_df = pd.concat([-LoadPeriodFore['ELoad'], 
#                                     -Opt_Result['P_Grid_import'], 
#                                      Opt_Result['P_Grid_export'],
#                                      Opt_Result['SOC_batt']/50,
#                                     -Opt_Result['P_batt_dis'],
#                                      Opt_Result['P_batt_char'],             
#                                     -Opt_Result['P_CHP2load'],
#                                     -Opt_Result['P_CHP_el'], 
#                                     -Opt_Result['P_CHP_el_exp'], ],axis=1)                                   
#             Result_th_df = pd.concat([-LoadPeriodFore['QLoad1']*2,
#                                     -Opt_Result['P_aux_th'],
#                                     -Opt_Result['P_TES_dis'],
#                                      Opt_Result['P_TES_char'],
#                                      Opt_Result['SOC_TES']/50,
#                                      Opt_Result['P_CHP_th'],
#                                      Opt_Result['b_CHP_on'],
#                                       ],axis=1) 
#             Result_PV_Grid = pd.concat([-PVavaPeriodFore['PV 2013, Kassel, 10min'],
#                                     -LoadPeriodReal['ELoad'],
#                                     -Opt_Result['P_Grid_import'], 
#                                      Opt_Result['P_Grid_export'],
#                                      Opt_Result['P_PV_exp'],
#                                      Opt_Result['P_CHP_el_exp'], ],axis=1)
#             if timestep==5 or timestep==76 or timestep==79:
#                  #plt.figure(title=')                         
#                  Result_el_df.plot(title='elek')              
#                  #plt.figure()                                                            
#                  Result_th_df.plot(title='therm')
#                  Result_PV_Grid.plot(title='PV_Grid')
# #            if timestep==38:
# #                 Result_el_df.plot(title='elek')              
# #                 Result_th_df.plot(title='therm')
# #                 Result_PV_Grid.plot(title='PV_Grid')
#                  
#              #if timestep==2 or timestep==max*0.5+1 or timestep==max-1:
#               #   Result_th_df.plot()
# 
#==============================================================================

            # -----------------------------------------------------------------            
            # --- Sammle Eintröge für Gesamtergebnis -----------------------
            # -----------------------------------------------------------------            
                    
          # Battery                        
            Result_BAT_End['SOC battery'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['SOC_batt'][Opt_Result.index[timestep-loop]]               	                                                      
            Result_BAT_End['Battery charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_char'][Opt_Result.index[timestep-loop]]                	                                   
            Result_BAT_End['Battery dis-charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_dis'][Opt_Result.index[timestep-loop]]                	                                   
            # Grid
            Result_Grid_End['Grid Import'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_import'][Opt_Result.index[timestep-loop]]                	                                   
            Result_Grid_End['Grid Export'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_export'][Opt_Result.index[timestep-loop]]                	                                   
            # Aux Gasbrenner
            Result_Heat_End['Aux Gasbrenner'][Result_Heat_End.index[timestep]] \
                    = Opt_Result['P_aux_th'][Opt_Result.index[timestep-loop]]
            Result_Heat_End['Aux Gas'][Result_Heat_End.index[timestep]] \
                    = Opt_Result['P_aux_gas'][Opt_Result.index[0]]                	                                                                                                          	                                                                                          
            #Result_Heat_End['TES dis-charging'][Result_Heat_End.index[timestep]] \
            #         = Opt_Result['P_TES_dis'][Opt_Result.index[0]]                	                                   
            #Result_Heat_End['SOC TES'][Result_Heat_End.index[timestep]] \
            #         = Opt_Result['SOC_TES'][Opt_Result.index[0]]                	                                   
            #Result_Heat_End['CHP th'][Result_Heat_End.index[timestep]] \
            #         = Opt_Result['P_CHP_th'][Opt_Result.index[0]]   
            	                                                        
            # Thermal Storage                                 
            Result_TES_End['SOC TES'][Result_TES_End.index[timestep]] \
                     = Opt_Result['SOC_TES'][Opt_Result.index[timestep-loop]]               	                                   
            Result_TES_End['TES charging'][Result_TES_End.index[timestep]] \
                     = Opt_Result['P_TES_char'][Opt_Result.index[timestep-loop]]                	                                   
            Result_TES_End['TES dis-charging'][Result_TES_End.index[timestep]] \
                     = Opt_Result['P_TES_dis'][Opt_Result.index[timestep-loop]]                	                                   
            #CHP         
            Result_CHP_End['CHP on_off'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['b_CHP_on'][Opt_Result.index[timestep-loop]] 
            Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_th'][Opt_Result.index[timestep-loop]]               	                                   
            Result_CHP_End['CHP el'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_el'][Opt_Result.index[timestep-loop]] 
            Result_CHP_End['CHP Export'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_el_exp'][Opt_Result.index[timestep-loop]]               	                                   
            Result_CHP_End['CHP load self'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP2load'][Opt_Result.index[timestep-loop]] 
            Result_CHP_End['CHP batt self'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP2batt'][Opt_Result.index[timestep-loop]] 
            Result_CHP_End['CHP Gas'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_gas'][Opt_Result.index[0]] 
         # PV
            #Result_PV_End['PV'][Result_PV_End.index[timestep]] \
            #        = Opt_Result['P_PV'][Opt_Result.index[0]]                	                                            
            Result_PV_End['PV batt selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2batt'][Opt_Result.index[timestep-loop]]
            Result_PV_End['PV load selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2load'][Opt_Result.index[timestep-loop]]
            Result_PV_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_exp'][Opt_Result.index[timestep-loop]] 
                    
#==============================================================================
            # -----------------------------------------------------------------            
            # check and correct forecast schedule    
            # -----------------------------------------------------------------               
#==============================================================================
            # wenn gerade optimiert wurde 
            if OptiMarker == 1 :                     
                CorrTerms = cor.AdHoc_MPC(Result_BAT_End, Result_PV_End,Result_Heat_End,\
                Result_TES_End, Result_CHP_End,\
                Result_Grid_End, PVavaPeriodFore['PV 2013, Kassel, 10min'], PVavaReal[timestep],\
                LoadPeriodFore['ELoad'],LoadPeriodFore['QLoad1'],LoadPeriodFore['QLoad2'], \
                timestep, Battery,ThermalStorage, \
                ELoadR[timestep], Q1LoadR[timestep], Q2LoadR[timestep], CHP, OptiMarker, Auxilary)
                # --> OptiMarker = 0
            # wenn gerade nicht optimiert wurde
            elif OptiMarker == 0:
                CorrTerms = cor.AdHoc_MPC_Rulebased(Result_BAT_End, Result_PV_End,Result_Heat_End,\
                Result_TES_End, Result_CHP_End,\
                Result_Grid_End, PVavaPeriodFore['PV 2013, Kassel, 10min'], PVavaReal[timestep],\
                LoadPeriodFore['ELoad'],LoadPeriodFore['QLoad1'],LoadPeriodFore['QLoad2'], \
                timestep, Battery,ThermalStorage, \
                ELoadR[timestep], Q1LoadR[timestep], Q2LoadR[timestep], CHP, OptiMarker,\
                RuleIni, Auxilary)
                
                # --> OptiMarker = 0 ODER OptiMarker = 1
            else:
                print 'ERROR - OptiMarker out of range !!!'
            # -----------------------------------------------------------------               

            # Correction after MPC
            OptiMarker = CorrTerms['OptiMarker']
            # Battery
            Result_Corr_End['CorrBattDis'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrBattDis']
            Result_Corr_End['CorrBattCh'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrBattCh']
            Result_Corr_End['CorrBatSOC'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrBatSOC']
            # TES                     
            Result_Corr_End['CorrTESDis'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrTESDis']
            Result_Corr_End['CorrTESCh'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrTESCh']
            Result_Corr_End['CorrTESSOC'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrTESSOC']
            # Grid
            Result_Corr_End['CorrGridImp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrGridImp']
            Result_Corr_End['CorrGridExp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrGridExp']
            # PV
            Result_Corr_End['CorrPVexp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrPVexp']
            Result_Corr_End['CorrPV2Batt'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrPV2Batt']                                        
            Result_Corr_End['CorrPV2Load'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrPV2Load']                                        
            # CHP            
            Result_Corr_End['CorrCHPExp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrCHPExp']
            Result_Corr_End['CorrCHP2Batt'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrCHP2Batt']                                        
            Result_Corr_End['CorrCHP2Load'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrCHP2Load']                                        
            Result_Corr_End['CorrCHPel'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrCHPel']                                        
            Result_Corr_End['CorrCHPth'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrCHPth']                                        
            Result_Corr_End['CorrCHPGas'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrCHPGas']                                        
            # Aux           
            Result_Corr_End['CorrAux'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrAuxGas']                                        
            Result_Corr_End['CorrAuxGas'][Result_Corr_End.index[timestep]] \
                    = CorrTerms['CorrAuxGasmenge']                                      
        
            
            # -----------------------------------------------------------------            
            # ----------------Re-Initialize SOC for the next step -----------------
            # -----------------------------------------------------------------            
            # --- in case next step is "optinmierung"
            Battery['SOC_batt_ini'] = CorrTerms['CorrBatSOC']
            if CorrTerms['CorrTESSOC'] >= 100:
                    CorrTerms['CorrTESSOC'] = 100
                    print 'Main-Warning - TES > 100% '
            ThermalStorage['SOC_TES_ini'] = CorrTerms['CorrTESSOC']            
            CHP['b_CHP_on_ini'] = CorrTerms['CorrCHPonoff']
            # --- in case next step is "nachreglung"
            RuleIni['BattSOC_opti'] = Opt_Result['SOC_batt'][Opt_Result.index[timestep-loop]] 
            RuleIni['TESSOC_opti'] = Opt_Result['SOC_TES'][Opt_Result.index[timestep-loop]]            
            RuleIni['CHPonoff_opti'] = Opt_Result['b_CHP_on'][Opt_Result.index[timestep-loop]]
            RuleIni['BattSOC_R'] = CorrTerms['CorrBatSOC']
            RuleIni['TESSOC_R'] =  CorrTerms['CorrTESSOC']         
            RuleIni['CHPonoff_R'] = CorrTerms['CorrCHPonoff']
                #print 'Re-Ini: ',RuleIni['BattSOC_opti']
#==============================================================================
#             # -----------------------------------------------------------------            
#             # ----------------Re-Initialize SOC for the next step -----------------
#             # -----------------------------------------------------------------            
#             Battery['SOC_batt_ini'] = Opt_Result['SOC_batt'][Opt_Result.index[1]] 
#             ThermalStorage['SOC_TES_ini'] = Opt_Result['SOC_TES'][Opt_Result.index[1]]            
#             CHP['b_CHP_on_ini'] = Opt_Result['b_CHP_on'][Opt_Result.index[1]]
#==============================================================================
            
   #         print 'On/Off', Opt_Result['b_CHP_on'][Opt_Result.index[1]]           
            # Battery                                 
            Result_BAT_End['SOC battery'][Result_BAT_End.index[timestep]] \
                      = CorrTerms['CorrBatSOC']                      
            Result_BAT_End['Battery charging'][Result_BAT_End.index[timestep]] \
                     = CorrTerms['CorrBattCh']
            Result_BAT_End['Battery dis-charging'][Result_BAT_End.index[timestep]] \
                     = CorrTerms['CorrBattDis']           	                                   

            Result_BATFore_End['SOC battery'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['SOC_batt'][Opt_Result.index[timestep-loop]]               	                                   
            Result_BATFore_End['Battery charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_char'][Opt_Result.index[timestep-loop]]                	                                   
            Result_BATFore_End['Battery dis-charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_dis'][Opt_Result.index[timestep-loop]]                	                                   

            # Grid
            Result_Grid_End['Grid Import'][Result_Grid_End.index[timestep]] \
                    = CorrTerms['CorrGridImp']
            Result_Grid_End['Grid Export'][Result_Grid_End.index[timestep]] \
                    = CorrTerms['CorrGridExp']        	                                   
            
            Result_GridFore_End['Grid Import'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_import'][Opt_Result.index[timestep-loop]]                	                                   
            Result_GridFore_End['Grid Export'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_export'][Opt_Result.index[timestep-loop]]                	                                   
                        
            # Aux Gasbrenner
            Result_Heat_End['Aux Gasbrenner'][Result_Heat_End.index[timestep]] \
                    = CorrTerms['CorrAuxGas']             	                                   
            Result_Heat_End['Aux Gas'][Result_Heat_End.index[timestep]] \
                    = CorrTerms['CorrAuxGasmenge']             	                                   
           # Result_Heat_End['TES dis-charging'][Result_Heat_End.index[timestep]] \
           #          = CorrTerms['CorrTESDis']             	                                   
           # Result_Heat_End['SOC TES'][Result_Heat_End.index[timestep]] \
           #          = CorrTerms['CorrTESSOC']             	                                   
           # Result_Heat_End['CHP th'][Result_Heat_End.index[timestep]] \
           #          = CorrTerms['CorrCHPth']             	                                   
                     
            Result_HeatFore_End['Aux Gasbrenner'][Result_Heat_End.index[timestep]] \
                    = Opt_Result['P_aux_th'][Opt_Result.index[timestep-loop]]                	                                                                                          
           # Result_HeatFore_End['TES dis-charging'][Result_Heat_End.index[timestep]] \
           #          = Opt_Result['P_TES_dis'][Opt_Result.index[0]]                	                                   
           # Result_HeatFore_End['SOC TES'][Result_Heat_End.index[timestep]] \
           #          = Opt_Result['SOC_TES'][Opt_Result.index[0]]                	                                   
           # Result_HeatFore_End['CHP th'][Result_Heat_End.index[timestep]] \
           #          = Opt_Result['P_CHP_th'][Opt_Result.index[0]]               	                                                        
                         
            # Thermal Storage                                 
            Result_TES_End['SOC TES'][Result_TES_End.index[timestep]] \
                     = CorrTerms['CorrTESSOC']             	                                   
            Result_TES_End['TES charging'][Result_TES_End.index[timestep]] \
                     = CorrTerms['CorrTESCh']             	                                   
            Result_TES_End['TES dis-charging'][Result_TES_End.index[timestep]] \
                     = CorrTerms['CorrTESDis']             	                                   
            Result_TES_End['TES too full'][Result_TES_End.index[timestep]] \
                     = CorrTerms['CorrTEStoofull']
        
            Result_TESFore_End['SOC TES'][Result_TES_End.index[timestep]] \
                     = Opt_Result['SOC_TES'][Opt_Result.index[timestep-loop]]               	                                   
            Result_TESFore_End['TES charging'][Result_TES_End.index[timestep]] \
                     = Opt_Result['P_TES_char'][Opt_Result.index[timestep-loop]]                	                                   
            Result_TESFore_End['TES dis-charging'][Result_TES_End.index[timestep]] \
                     = Opt_Result['P_TES_dis'][Opt_Result.index[timestep-loop]]                	                                   
            #CHP         
            Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]] \
                     = CorrTerms['CorrCHPth']             	                                   
            Result_CHP_End['CHP el'][Result_CHP_End.index[timestep]] \
                     = CorrTerms['CorrCHPel']             	                                   
            Result_CHP_End['CHP Export'][Result_CHP_End.index[timestep]] \
                     = CorrTerms['CorrCHPExp']             	                                   
            Result_CHP_End['CHP load self'][Result_CHP_End.index[timestep]] \
                     = CorrTerms['CorrCHP2Load']             	                                   
            Result_CHP_End['CHP batt self'][Result_CHP_End.index[timestep]] \
                     = CorrTerms['CorrCHP2Batt']             	                                   
            Result_CHP_End['CHP on_off'][Result_CHP_End.index[timestep]] \
                     = CorrTerms['CorrCHPonoff']        
            Result_CHP_End['CHP Gas'][Result_CHP_End.index[timestep]] \
                     = CorrTerms['CorrCHPGas']             	                                   
              	                                         
            Result_CHPFore_End['CHP th'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_th'][Opt_Result.index[timestep-loop]]               	                                   
            Result_CHPFore_End['CHP el'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_el'][Opt_Result.index[timestep-loop]] 
            Result_CHPFore_End['CHP Export'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_el_exp'][Opt_Result.index[timestep-loop]]               	                                   
            Result_CHPFore_End['CHP load self'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP2load'][Opt_Result.index[timestep-loop]] 
            Result_CHPFore_End['CHP batt self'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP2batt'][Opt_Result.index[timestep-loop]] 
            Result_CHPFore_End['CHP on_off'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['b_CHP_on'][Opt_Result.index[timestep-loop]] 
         
            # -------- Calculate CHP2Qload and CHP2Qstor  ------------------------
            # ------------ FORE ----------------
            QProfileFore = LoadPeriodFore['QLoad1'][Result_CHP_End.index[timestep]]\
                             + LoadPeriodFore['QLoad2'][Result_CHP_End.index[timestep]]
          
            if Result_CHPFore_End['CHP th'][Result_CHP_End.index[timestep]]>0:
                QProfileFore = LoadPeriodFore['QLoad1'][Result_CHP_End.index[timestep]]\
                             + LoadPeriodFore['QLoad2'][Result_CHP_End.index[timestep]]
                if Result_CHPFore_End['CHP th'][Result_CHP_End.index[timestep]]\
                    > QProfileFore:
                    Result_CHPFore_End['CHP th2load'][Result_CHP_End.index[timestep]]\
                         = QProfileFore
                    Result_CHPFore_End['CHP th2TES'][Result_CHP_End.index[timestep]]\
                         = Result_CHPFore_End['CHP th'][Result_CHP_End.index[timestep]]\
                    - QProfileFore
                    
                elif Result_CHPFore_End['CHP th'][Result_CHP_End.index[timestep]]\
                    <= QProfileFore:
                    Result_CHPFore_End['CHP th2load'][Result_CHP_End.index[timestep]]\
                         = Result_CHPFore_End['CHP th'][Result_CHP_End.index[timestep]]
                    Result_CHPFore_End['CHP th2TES'][Result_CHP_End.index[timestep]]\
                         = 0
            QProfileReal = LoadPeriodReal['QLoad1'][Result_CHP_End.index[timestep]]\
                             + LoadPeriodReal['QLoad2'][Result_CHP_End.index[timestep]]
     
            # ------------ REAL ----------------
            if Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]>0:
                QProfileReal = LoadPeriodReal['QLoad1'][Result_CHP_End.index[timestep]]\
                             + LoadPeriodReal['QLoad2'][Result_CHP_End.index[timestep]]
                if Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]\
                    > QProfileReal:
                    Result_CHP_End['CHP th2load'][Result_CHP_End.index[timestep]]\
                         = QProfileReal
                    Result_CHP_End['CHP th2TES'][Result_CHP_End.index[timestep]]\
                         = Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]\
                    - QProfileReal
         
                elif Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]\
                    <= QProfileReal:
                    Result_CHP_End['CHP th2load'][Result_CHP_End.index[timestep]]\
                         = Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]
                    Result_CHP_End['CHP th2TES'][Result_CHP_End.index[timestep]]\
                         = 0
            #--------------------------------------------------------------------                         
            # -----------Calc AUX2Tes AUX2Load
            #--------------------------------------------------------------------                         
#            #if QProfileReal - Result_CHP_End['CHP th2load'][Result_CHP_End.index[timestep]]>0
#            # Real                             
#            Result_Heat_End['Aux Gas2Load'][Result_Heat_End.index[timestep]]\
#                        = QProfileReal - Result_CHP_End['CHP th2load'][Result_CHP_End.index[timestep]]
#            Result_Heat_End['Aux Gas2TES'][Result_Heat_End.index[timestep]]\
#                        = Result_Heat_End['Aux Gasbrenner'][Result_Heat_End.index[timestep]] \
#                        - Result_Heat_End['Aux Gas2Load'][Result_Heat_End.index[timestep]]
#            # Fore                        
#            Result_HeatFore_End['Aux Gas2Load'][Result_Heat_End.index[timestep]]\
#                        = QProfileFore - Result_CHPFore_End['CHP th2load'][Result_CHP_End.index[timestep]]
#            Result_HeatFore_End['Aux Gas2TES'][Result_Heat_End.index[timestep]]\
#                        = Result_HeatFore_End['Aux Gasbrenner'][Result_Heat_End.index[timestep]] \
#                        - Result_HeatFore_End['Aux Gas2Load'][Result_Heat_End.index[timestep]]            
            #--------------------------------------------------------------------                         

            # PV
            Result_PV_End['PV batt selfcon'][Result_PV_End.index[timestep]] \
                    = CorrTerms['CorrPV2Batt']
            Result_PV_End['PV load selfcon'][Result_PV_End.index[timestep]] \
                    = CorrTerms['CorrPV2Load']
            Result_PV_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = CorrTerms['CorrPVexp']       	                                   

            Result_PVFore_End['PV batt selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2batt'][Opt_Result.index[timestep-loop]]
            Result_PVFore_End['PV load selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2load'][Opt_Result.index[timestep-loop]]
            Result_PVFore_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_exp'][Opt_Result.index[timestep-loop]]
  

          
    if len(LoadPeriodFore)-PrHoBin < 0:
        print 'CompTime not possible!'
    else:
        t2 = ti.clock()
        CompTime['Computational Time'][timestep] = t2 - t1 
   # print 'MAIN CompTime', CompTime
    # -----------------------------------------------------------------            
    # ----- Figures and Plotting  -------------------------------------
    # -----------------------------------------------------------------
    if len(LoadPeriodFore)-PrHoBin < 0:
          print "Cplex crash!"
    else:
         Plotc = 3
         # nach modified script: Jan von Appen
         Plotc_back = pl.Plotting(Result_Grid_End, Result_BAT_End, Result_PV_End,\
         Result_CHP_End, Result_Heat_End, Result_TES_End, \
         PVavaPeriodReal, P_PV_max, P_Load_max, LoadPeriodReal, \
         Battery, Costs, start_date, end_date, Plotc, 'Real', maxx,\
         PrHoBin, INOUT_string) 
         
         Plotc = Plotc_back
         Plotc_back = pl.Plotting(Result_GridFore_End, Result_BATFore_End, Result_PVFore_End,\
         Result_CHPFore_End, Result_HeatFore_End, Result_TESFore_End, \
         PVavaPeriodFore, P_PV_max, P_Load_max, LoadPeriodFore, \
         Battery, Costs, start_date, end_date, Plotc, 'Fore', maxx,\
         PrHoBin, INOUT_string) 
         
#==============================================================================
#     Result_Grid_End.plot(title='Grid')
#     Result_BAT_End.plot(title='Battery')
#     Result_Heat_End.plot(title='Heat') 
#     Result_TES_End.plot(title='Thermal Storage') 
#    Result_CHP_End.plot(title='CHP')
#   
#      
#==============================================================================

    # -----------------------------------------------------------------            
    # ------ KPIs -----------------------------------------------------    
    # ----------------------------------------------------------------- 
    if len(LoadPeriodFore)-PrHoBin < 0:   
       kpi.Calc_KPI_dummy('Fore', 144, INOUT_string)
       kpi.Calc_KPI_dummy('Real', 144, INOUT_string)
    else:       
       kpi.Calc_KPI(Result_BATFore_End, Result_PVFore_End, Result_GridFore_End,\
       Result_CHPFore_End, Result_TESFore_End, Result_HeatFore_End,\
       LoadPeriodFore, PVavaPeriodFore, Costs, PrHoBin, maxx,Delta_t, \
       Battery, CHP, Auxilary, 'Fore', CompTime,INOUT_string, CO2)
       
       # with ad-hoc, with Real PV and Real Load
       kpi.Calc_KPI(Result_BAT_End, Result_PV_End, Result_Grid_End,\
       Result_CHP_End, Result_TES_End, Result_Heat_End,\
       LoadPeriodReal, PVavaPeriodReal, Costs, PrHoBin, maxx,Delta_t, \
       Battery, CHP, Auxilary, 'Real', CompTime,INOUT_string, CO2)    
    # -----------------------------------------------------------------            
    # ------- Save to File --------------------------------------
    # -----------------------------------------------------------------               
    Result_Grid_End.to_csv('RESULTS\Result_AdhocV_Real_Grid_'+INOUT_string+'.csv')   
    Result_PV_End.to_csv('RESULTS\Result_AdhocV_Real_PV_'+INOUT_string+'.csv')   
    Result_BAT_End.to_csv('RESULTS\Result_AdhocV_Real_BAT_'+INOUT_string+'.csv')    
    Result_CHP_End.to_csv('RESULTS\Result_AdhocV_Real_CHP_'+INOUT_string+'.csv')    
    Result_TES_End.to_csv('RESULTS\Result_AdhocV_Real_TES_'+INOUT_string+'.csv')    
    Result_Heat_End.to_csv('RESULTS\Result_AdhocV_Real_Heat_'+INOUT_string+'.csv')    
 
    Result_GridFore_End.to_csv('RESULTS\Result_AdhocV_Fore_Grid_'+INOUT_string+'.csv')   
    Result_PVFore_End.to_csv('RESULTS\Result_AdhocV_AdhocV_Fore_PV_'+INOUT_string+'.csv')   
    Result_BATFore_End.to_csv('RESULTS\Result_AdhocV_Fore_BAT_'+INOUT_string+'.csv')    
    Result_CHPFore_End.to_csv('RESULTS\Result_AdhocV_Fore_CHP_'+INOUT_string+'.csv')    
    Result_TESFore_End.to_csv('RESULTS\Result_AdhocV_Fore_TES_'+INOUT_string+'.csv')    
    Result_HeatFore_End.to_csv('RESULTS\Result_AdhocV_Fore_Heat_'+INOUT_string+'.csv')    
 
    print "The End!"
    return 0
    
if __name__ == '__main__':
    Sensitivity()    
 #   ana.Analyse_Horizon()