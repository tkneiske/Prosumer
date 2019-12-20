# -*- coding: utf-8 -*
"""
Created on Tue Sep 15 21:21:28 2015
26.9 Ziel: CHP, TES, Battery, Gasboiler
CHP, PV, Battery Tes Gasboiler Kostenoptimal
12.10. PV ist auch implementiert !
       Forecast vom Vortag 
13.10. (einige) KPI und Plotting wie in OptIn implementiert       
23.10. Unterscheidung des Eigenverbrauchs in load and bat für PV und CHP
26.10. Jahressimulation implementiert
26.10. Ausgabe in csv Files 
18.5.16 Ausgabe InputParameter    
23.5.16 Replace np.zeros with np.zeros  --> Rückgängig sonst CHP Fehler!
24.5.16 Sensitiviy() hinzugefügt + mehr KPI für Analysis()
1.6.16 add InChoice
Sep.2016 Add CO2 Wert

@author: tkneiske
"""
import OptFlex_inputvalues as ipv
import OptFlex_optimierer as opt
import matplotlib.pyplot as plt
import OptFlex_plotting as pl
#import OptFlex_perfektePrognose as pp ** Funktioniert noch nicht**
import seaborn
import pandas as pd
import numpy as np
import OptFlex_KPIs as kpi
import time as ti
#from copy import deepcopy
#import OptFlex_forecast as fore
import os
from copy import deepcopy

def Sensitivity():
    #Haushalt = ['EFH','MFH']    
    #Haushalt = ['MFH']    # add values and InputFiles TMK 3.6.16
    Haushalt = ['EFH']       
    
    #Nachbar = ['NachbarOn','NachbarOff']    
    #Nachbar = ['NachbarOn']    # für VDE EFH only !!!
    Nachbar = ['NachbarOff']    
    
    #TimeSeriesIn = ['VDE', 'LPG']    
    #TimeSeriesIn = ['VDE']   
    #TimeSeriesIn = ['LPG']   
    TimeSeriesIn = ['LPG_Lab']   
     
    #InChoice = ['Default','ohneFIT']     
    InChoice = ['Default']    
    #InChoice = ['ohneFIT']    
        
    # LO Load - Verbrauch - El Price
    #IncentiveLO = ['LOoff','LOon','LOart']
    #IncentiveLO = ['LOon']    
    IncentiveLO = ['LOoff']       
    #IncentiveLO = ['LOart']       
    
    # ER ERzeugung - Feed-In Tariff
    #IncentiveER = ['ERoff','ERon','ERart']
    #IncentiveER = ['ERon']    
    IncentiveER = ['ERoff']       
    #IncentiveER = ['ERart']       
    
     
    #Abregelung = ['ABon']         
    Abregelung = ['ABoff']     
     
    # Nur Perfekt möglich - keine Prognose implementiert !!! 
    fore_method = ['Perfekt']   
    
    #Horizon = [2, 15, 36, 72, 144] 
    Horizon = [36]
    #Horizon = [72]    
    
    #Saison = ['Winter','Sommer','Uebergang']    
    #Saison = ['Winter','Sommer']       
    #Saison = ['Winter']    
    #Saison = ['Sommer']
    Saison = ['Uebergang']
    #Saison = ['all']
    
    for e in range (0, len(IncentiveLO)):   
     for m in range(0, len(Nachbar)):   
      for f in range (0, len(IncentiveER)):   
       for g in range (0, len(Haushalt)):
        for h in range(0, len(TimeSeriesIn)):  
         #datachoice = TimeSeriesIn[h]
         for l in range(0, len(InChoice)):
          for k in range(0, len(fore_method)):
           forem = fore_method[k] 
           for j in range(0, len(Saison)):       
            Season = Saison[j]         
            for i in range(0, len(Horizon)):        
                PrHoBin = Horizon[i]  #72;        
                print PrHoBin, Season
                MPC(Nachbar[m], PrHoBin, Season, forem, InChoice[l], TimeSeriesIn[h], Haushalt[g], IncentiveLO[e],IncentiveER[f], Abregelung[0])   
    return 0
    
def MPC(Nachbar, PrHoBin, Season, fore_method, InputChoice,TimeSeriesIn,Haushalt, IncentiveLO, IncentiveER, Abregel):
    plt.close("all")

    #-----------------------------------------------
    # ---------------  INPUT DATA  -----------------   
    #-----------------------------------------------
    Delta_t = 10 # 10 min bins

    Saison = Season        
    if Saison == "Winter":
     #   start_date = '1/5/2013'    # th load 40,56 , el. laod 10,91
     #   end_date = '1/6/2013'
        start_date = '1/10/2013'    # th. load 85, el. Load 11,41
        end_date = '1/11/2013'
    elif Saison == "Uebergang":
       # start_date = '4/8/2013'     # th. load 85, el. Load 11,41
       # end_date = '4/9/2013'
        start_date = '3/26/2013'  # th Load 93, el. Load 10,9   
        end_date = '3/27/2013'
       # start_date = '4/17/2013'    
       # end_date = '4/18/2013'
       # start_date = '4/19/2013'    # th. Load 40,6 ,  el. Load 10,9
       # end_date = '4/20/2013'
    elif Saison == "Sommer":
        #start_date = '8/4/2013'    
        #end_date = '8/5/2013'
        start_date = '8/11/2013'    
        end_date = '8/12/2013'
   # elif Saison == "Sommer":
    #    start_date = '7/11/2013'  #  peak shaving, 60% analyse
    #    end_date = '7/12/2013'       # 2,31/9.86
    elif Saison == "all":
       # start_date = '4/1/2013'    
       # end_date = '12/30/2013'   
        start_date = '1/2/2013'    
        end_date = '12/30/2013'   
    else:
        print "Fehler in Saison-Auswahl"
    
    INOUT_string = str(PrHoBin/6.)+'_'+Saison+'_'+fore_method+'_'+InputChoice+'_'\
        +TimeSeriesIn+'_'+Haushalt+'_'+ IncentiveLO+'_'+ IncentiveER+'_'+Abregel+'_'+Nachbar
    
    if Saison == 'Uebergang' and PrHoBin > 143:
        PrHoBin = 1000000
        INOUT_string = str(144/6.)+'_'+Saison+'_'+fore_method+'_'+InputChoice+'_'\
            +TimeSeriesIn+'_'+Haushalt+'_'+ IncentiveLO+'_'+ IncentiveER+'_'+Abregel+'_'+Nachbar
            
      
    date_year = '1/1/2013'
    #-----------------------------------------------
    
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print '%                                                  %'
    print '%         Optimierung von CHP, TES, GASboiler      %'     
    print '%       PV, Battery nach KOSTEN, Perfekte Prognose %'     
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
    #print os.getcwd() # Prints the working directory

                    
    # -------------------------------------------------------------------------
    # Get Input Parameter
    # -------------------------------------------------------------------------      
    #    PV und Lastzeitreihen
    if Haushalt == 'EFH':                      
        if TimeSeriesIn == 'VDE':
            PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                        ipv.Input_PV_Load_VDE_EFH(Delta_t, TimeStepSize,year_stamps, Nachbar)
        elif TimeSeriesIn == 'LPG':
                        PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                        ipv.Input_PV_Load_LPG_EFH(Delta_t, TimeStepSize,year_stamps)
        elif TimeSeriesIn == 'LPG_Lab':
                        PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                        ipv.Input_PV_Load_LPG_Lab(Delta_t, TimeStepSize,year_stamps)
        else:# default ist VDE  
             print 'ERROR - TimeSeriesIN EFH'
                          #  PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                          #  ipv.Input_PV_Load_VDE_EFH(Delta_t, TimeStepSize,year_stamps)
                    
                    # Components
        if InputChoice == 'Default' and TimeSeriesIn =="LPG_Lab":                    
                        Battery, Auxilary, ThermalStorage, \
                        CHP, Costs, CO2 = ipv.inputvaluesDefault_EFH_Lab(Delta_t, TimeStepSize,year_stamps)
        elif InputChoice == 'Default':                    
                        Battery, Auxilary, ThermalStorage, \
                        CHP, Costs, CO2 = ipv.inputvaluesDefault_EFH(Delta_t, TimeStepSize,year_stamps)
        elif InputChoice == 'ohneFIT':
                        Battery, Auxilary, ThermalStorage, \
                        CHP, Costs, CO2 = ipv.inputvaluesOHNE_Verg_EFH(Delta_t, TimeStepSize,year_stamps)
        else: #default
                     #       Battery, Auxilary, ThermalStorage, \
                     #       CHP, Costs = ipv.inputvaluesDefault_EFH(Delta_t, TimeStepSize,year_stamps)
                       print 'ERROR - InChoice EFH'
                       
    elif Haushalt == 'MFH':
        if TimeSeriesIn == 'VDE': # will not be implemented
            PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                        ipv.Input_PV_Load_VDE_MFH(Delta_t, TimeStepSize,year_stamps)
        elif TimeSeriesIn == 'LPG':
                        PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                        ipv.Input_PV_Load_LPG_MFH(Delta_t, TimeStepSize,year_stamps)
        else:# default ist VDE  
                        #    PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max = \
                        #    ipv.Input_PV_Load_VDE_MFH(Delta_t, TimeStepSize,year_stamps)
                        print 'ERROR - InChoice MFH'
                    # Components
        if InputChoice == 'Default':                    
                        Battery, Auxilary, ThermalStorage, \
                        CHP, Costs, CO2 = ipv.inputvaluesDefault_MFH(Delta_t, TimeStepSize,year_stamps)
        elif InputChoice == 'ohneFIT':
                            Battery, Auxilary, ThermalStorage, \
                            CHP, Costs, CO2 = ipv.inputvaluesOHNE_Verg_MFH(Delta_t, TimeStepSize,year_stamps)
        else: #default
                #            Battery, Auxilary, ThermalStorage, \
                #            CHP, Costs = ipv.inputvaluesDefault_MFH(Delta_t, TimeStepSize,year_stamps)
                    print 'ERROR - TimeSeriesIN MFH'
    else: #(default)                                   
         print 'ERROR - Haushalt '    
                         
    day_stamps_date = pd.date_range(start_date, periods=BIN, freq=TimeStepSize)          
                         
    # -------------------------------------------------------------------------
    #  Preiszeitreihe als Dataframe   EPEX und PV Vergütung
    # -------------------------------------------------------------------------
    if IncentiveLO == 'LOoff':   
        PreisProfilLO = Costs['C_grid_el']*pd.DataFrame(np.ones(BIN), index=day_stamps_date)
    elif IncentiveLO == 'LOon' :
        PreisProfilLO = ipv.PreisProfile(Delta_t, TimeStepSize,year_stamps,date_year)
    elif IncentiveLO == 'LOart':
        PreisProfilLO = Costs['C_grid_el'] * ipv.ArtPreisProfileLO(Delta_t, TimeStepSize,year_stamps,date_year, year_bins)
    else: #PreisProfil = pd.DataFrame(Costs['C_grid_el']*np.ones(BIN))
        print 'ERROR - Incentive'
       
    if IncentiveER == 'ERoff':
        PreisProfilER = Costs['C_PV_FIT']*pd.DataFrame(np.ones(BIN), index=day_stamps_date)                
    elif IncentiveER == 'ERart':
        PreisProfilER = Costs['C_PV_FIT'] *ipv.ArtPreisProfileER(Delta_t, TimeStepSize,year_stamps,date_year, year_bins)
    elif IncentiveER == 'ERon':
        PreisProfilER = ipv.PreisProfile(Delta_t, TimeStepSize,year_stamps,date_year)
    else: #PreisProfil = pd.DataFrame(Costs['C_grid_el']*np.ones(BIN))
        print 'ERROR - Incentive'
        
    print start_date, end_date
    PreisPlotER = PreisProfilER[start_date:end_date]
    PreisPlotLO = PreisProfilLO[start_date:end_date]
    PreisProfilER.plot()
    PreisProfilLO.plot()
    
    if IncentiveER == 'ERoff' or IncentiveLO == 'LOoff':
        print ("No time dependent prices used")
    else:   
        PreisPlotLO.plot(title='Strompreis')
        PreisPlotER.plot(title='Feed-In Tarif')
    #print PreisProfil.values              
    PreisPlotER.to_csv('RESULTS\Result_Opti_Fore_PreisProfil_ER_'+INOUT_string+'_10.csv')    
    PreisPlotLO.to_csv('RESULTS\Result_Opti_Fore_PreisProfil_LO_'+INOUT_string+'_10.csv')    
    
    # -------------------------------------------------------------------------
                         
                         
    # -------------------------------------------------------------------------
    # REAL VALUES ---------PREPARE for TWO Identical Days !!!!!! Tanja 25.6.2018
    # -------------------------------------------------------------------------
    # ---- Load
    LoadTestOrig = LoadAll_TOT_df[start_date:end_date]
    LoadTest = deepcopy(LoadTestOrig[:144])                         
    LoadPeriodReal = LoadTest.append(LoadTest)
   #print LoadPeriodReal
    LoadPeriodReal.index = LoadTestOrig.index
    # ---- PV
    PVTestOrig = PVava_TOT_df[start_date:end_date]
    PVTest = deepcopy(PVTestOrig[:144])
    PVavaPeriodReal = PVTest.append(PVTest)
    PVavaPeriodReal.index = PVTestOrig.index
    # -------------------------------------------------------------------------
    # for comparison use may be forecast values from AdHoc and AdHocV
    # -------------------------------------------------------------------------    
#    if fore_method == 'Persistenz':
#        LoadPeriodReal = fore.TagesPersistenz(LoadAll_TOT_df, day_stamps_date, BIN)#
#        PVavaPeriodReal = fore.TagesPersistenz(PVava_TOT_df, day_stamps_date, BIN)
#    elif fore_method == 'Mittel':
#        LoadPeriodReal = fore.DreiTageRunAverage(LoadAll_TOT_df, day_stamps_date, BIN)
#        PVavaPeriodReal = fore.DreiTageRunAverage(PVava_TOT_df, day_stamps_date, BIN)
#    elif fore_method == 'Perfekt':
#        LoadPeriodReal = fore.TagesPersistenz(LoadAll_TOT_df, day_stamps_date, BIN)#
#        PVavaPeriodReal = fore.TagesPersistenz(PVava_TOT_df, day_stamps_date, BIN)
#    else: 
#        print "ERROR: Forcast Method not correct !" 
    # -------------------------------------------------------------------------
    # FORECAST  Values 
    # -------------------------------------------------------------------------
    LoadPeriodFore = LoadPeriodReal
    LoadPeriodFore.plot(title='Load')
    PVavaPeriodFore = PVavaPeriodReal
    PVavaPeriodFore.plot(title='PV')
    # not implemented ! see OptFlex - AdHoc und AdhocV
       
    # -------------------------------------------------------------------------
    # Prepare: Ausgabe Dataframes
    # -------------------------------------------------------------------------
    #BAT    
    SOCbatEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['SOC battery']) 
    PbattcharEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Battery charging']) 
    PbattdisEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Battery dis-charging']) 
    Result_BAT_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['ELoad'], 
                            SOCbatEnd, PbattcharEnd, PbattdisEnd], axis=1)                      
    #Grid    
    GridImpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Grid Import'])
    GridExpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Grid Export'])    
    Result_Grid_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['ELoad'], 
                            GridImpEnd, GridExpEnd], axis=1)
    #TES                                         
    SOCTESEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['SOC TES']) 
    PTEScharEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['TES charging']) 
    PTESdisEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['TES dis-charging']) 
    Result_TES_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['QLoad1']-LoadPeriodReal['QLoad2'], \
                SOCTESEnd, PTEScharEnd, PTESdisEnd], axis=1)                      
    # Result_TES_End = pd.concat([-LoadPeriodReal['QLoad1'], \
    #             -LoadPeriodReal['QLoad2'],SOCTESEnd, PTEScharEnd, PTESdisEnd], axis=1)                      
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
    Result_CHP_End = pd.concat([-LoadPeriodReal['ELoad'], -LoadPeriodReal['QLoad1']-LoadPeriodReal['QLoad2'],\
                            CHPelEnd, CHPthEnd, CHPscloadEnd,CHPscbattEnd, CHPexpEnd,\
                            CHPonoffEnd, CHPGas, CHP2QLoad ,CHP2TES], axis=1)                      
    #Heat                            
    AuxEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Aux Gasbrenner'])                              
    AuxGasEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Aux Gas'])                              
    Result_Heat_End = pd.concat([-LoadPeriodReal['QLoad1']-LoadPeriodReal['QLoad2'],
                                 AuxEnd, CHPthEnd,
                                 PTESdisEnd, SOCTESEnd, AuxGasEnd], axis=1)                                 	

    # ---------- PV ----------                       
    PVselfconbattEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV batt selfcon']) 
    PVselfconloadEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV load selfcon']) 
    PVexportEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Grid export']) 
    PVsumEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Summe'])     
    Result_PV_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'],\
                PVselfconloadEnd,PVselfconbattEnd, PVexportEnd,PVsumEnd], axis=1)   
    
    # ----  Corrections for MPC                             
    # Not implemente !
    
    # -------------------------------------------------------------------------
    # ------------  MPC Loop --------------------------------------------------    
    # -------------------------------------------------------------------------
    ELoadF = LoadPeriodFore['ELoad'].values  
    Q1LoadF = LoadPeriodFore['QLoad1'].values
    Q2LoadF = LoadPeriodFore['QLoad2'].values                       
    PVavaFore = PVavaPeriodFore['PV 2013, Kassel, 10min'].values #PV2013, Kassel, 10min
    PPER = PreisProfilER[0].values
    PPLO = PreisProfilLO[0].values
  
    
    maxx = len(LoadPeriodFore)-PrHoBin
    t1 = ti.clock()    
    if len(LoadPeriodFore)-PrHoBin < 0:
        print 'Prediction Horizon out of Range!!!'
        #if something is wrong, do not optimize
        # dummy is providing default dataframes as results
        Opt_Result = opt.OptFlex_optimierer_dummy(day_stamps_date,BIN)
    else:        
        minn = 0
        #
        maxx = 144
        #maxx = 77
        for timestep in range(minn, maxx):
            print [Result_PV_End.index[timestep]]
            print PrHoBin, timestep, maxx, Saison, fore_method, InputChoice,\
                    TimeSeriesIn,Haushalt,IncentiveLO, IncentiveER, Abregel, Nachbar
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
            # -------------------  Optimze ----------------------------------------    Opt_Result['b_CHP_on'][Opt_Result.index[0]]
            # -----------------------------------------------------------------                   	
#==============================================================================
            horizon_stamps = day_stamps_date[timestep:PrHoBin+timestep]
            Opt_Result=opt.OptFlex_optimierer(
                       horizon_stamps, PrHoBin,
                       Load, P_PV_max, P_Load_max, P_sh_th, P_dhw_th, P_PV_ava, Battery,
                       Auxilary, ThermalStorage, CHP, Costs, CO2, PreisProfilER_cut, PreisProfilLO_cut, Abregel)
            #print Opt_Result.ix[0]
            # --- Einzelplots ----Test Prediction Horizon --------------------
#==============================================================================
#             Result_el_df = pd.concat([-LoadPeriodFore['ELoad'], 
#                                    -Opt_Result['P_Grid_import'], 
#                                     Opt_Result['P_Grid_export'],
#                                     Opt_Result['SOC_batt']/50,
#                                    -Opt_Result['P_batt_dis'],
#                                     Opt_Result['P_batt_char'],             
#                                    -Opt_Result['P_CHP2load'],
#                                    -Opt_Result['P_CHP_el'], 
#                                    -Opt_Result['P_CHP_el_exp'], ],axis=1)                                   
#             Result_th_df = pd.concat([-LoadPeriodFore['QLoad1']*2,
#                                    -Opt_Result['P_aux_th'],
#                                    -Opt_Result['P_TES_dis'],
#                                     Opt_Result['P_TES_char'],
#                                     Opt_Result['SOC_TES']/50,
#                                     Opt_Result['P_CHP_th'],
#                                     Opt_Result['b_CHP_on'],         
#                                      ],axis=1) 
#             Result_PV_Grid = pd.concat([-PVavaPeriodFore['PV 2013, Kassel, 10min'],
#                                    -LoadPeriodReal['ELoad'],
#                                    -Opt_Result['P_Grid_import'], 
#                                     Opt_Result['P_Grid_export'],
#                                     Opt_Result['P_PV_exp'],
#                                     Opt_Result['P_CHP_el_exp'], ],axis=1)                        
#             if timestep==1 or timestep==maxx*0.5 or timestep==maxx-1:
#                 #plt.figure(title=')                         
#                 Result_el_df.plot(title='elek')              
#                 #plt.figure()                                                            
#                 Result_th_df.plot(title='therm')
#                 Result_PV_Grid.plot(title='PV_Grid')
#             if timestep==38:
#                 Result_el_df.plot(title='elek')              
#                 Result_th_df.plot(title='therm')
#                 Result_PV_Grid.plot(title='PV_Grid')
#==============================================================================
                
            #if timestep==2 or timestep==max*0.5+1 or timestep==max-1:
             #   Result_th_df.plot()
                
            # -----------------------------------------------------------------            
            # check and correct forecast schedule    
            # -----------------------------------------------------------------               
            #  not implemented                 
                
            
            # -----------------------------------------------------------------            
            # --- Sammle Eintröge[0] für Gesamtergebnis -----------------------
            # -----------------------------------------------------------------            
            # Battery                                 
            Result_BAT_End['SOC battery'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['SOC_batt'][Opt_Result.index[0]]               	                                   
            Result_BAT_End['Battery charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_char'][Opt_Result.index[0]]                	                                   
            Result_BAT_End['Battery dis-charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_dis'][Opt_Result.index[0]]                	                                   
            # Grid
            Result_Grid_End['Grid Import'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_import'][Opt_Result.index[0]]                	                                   
            Result_Grid_End['Grid Export'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_export'][Opt_Result.index[0]]                	                                   
            # Aux Gasbrenner
            if Opt_Result['P_aux_th'][Opt_Result.index[0]] >= 1e-4:
                Result_Heat_End['Aux Gasbrenner'][Result_Heat_End.index[timestep]] \
                    = Opt_Result['P_aux_th'][Opt_Result.index[0]]                	                                                                                          
                Result_Heat_End['Aux Gas'][Result_Heat_End.index[timestep]] \
                    = Opt_Result['P_aux_gas'][Opt_Result.index[0]]                	                                                                                          
            elif Opt_Result['P_aux_th'][Opt_Result.index[0]] < 1e-4:                     
                Result_Heat_End['Aux Gasbrenner'][Result_Heat_End.index[timestep]] \
                    = 0
                Result_Heat_End['Aux Gas'][Result_Heat_End.index[timestep]] \
                    = 0
            else:
                print "Error -- Aux-Value out of range !!!"
            Result_Heat_End['TES dis-charging'][Result_Heat_End.index[timestep]] \
                     = Opt_Result['P_TES_dis'][Opt_Result.index[0]]                	                                   
            Result_Heat_End['SOC TES'][Result_Heat_End.index[timestep]] \
                     = Opt_Result['SOC_TES'][Opt_Result.index[0]]                	                                   
            Result_Heat_End['CHP th'][Result_Heat_End.index[timestep]] \
                     = Opt_Result['P_CHP_th'][Opt_Result.index[0]]               	                                                        
            # Thermal Storage                                 
            Result_TES_End['SOC TES'][Result_TES_End.index[timestep]] \
                     = Opt_Result['SOC_TES'][Opt_Result.index[0]]               	                                   
            Result_TES_End['TES charging'][Result_TES_End.index[timestep]] \
                     = Opt_Result['P_TES_char'][Opt_Result.index[0]]                	                                   
            Result_TES_End['TES dis-charging'][Result_TES_End.index[timestep]] \
                     = Opt_Result['P_TES_dis'][Opt_Result.index[0]]                	                                   
            #CHP         
            Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_th'][Opt_Result.index[0]]               	                                   
            Result_CHP_End['CHP el'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_el'][Opt_Result.index[0]] 
            Result_CHP_End['CHP Export'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_el_exp'][Opt_Result.index[0]]               	                                   
            Result_CHP_End['CHP load self'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP2load'][Opt_Result.index[0]] 
            Result_CHP_End['CHP batt self'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP2batt'][Opt_Result.index[0]] 
            Result_CHP_End['CHP Gas'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_gas'][Opt_Result.index[0]] 
            #-- see if-else below to avoid 1.0000000000000002 or 0.99999999999433 TMK 19.12.2016
            #Result_CHP_End['CHP on_off'][Result_CHP_End.index[timestep]] \
            #         = Opt_Result['b_CHP_on'][Opt_Result.index[0]] 
         
         
            
            # -----------------------------------------------------------------            
            # ----------------Re-Initialize SOC for the next step -----------------
            # -----------------------------------------------------------------            
            Battery['SOC_batt_ini'] = Opt_Result['SOC_batt'][Opt_Result.index[0]] 
            ThermalStorage['SOC_TES_ini'] = Opt_Result['SOC_TES'][Opt_Result.index[0]]
            if Opt_Result['b_CHP_on'][Opt_Result.index[0]] == 1 or Opt_Result['b_CHP_on'][Opt_Result.index[0]] == 0:
                CHP['b_CHP_on_ini'] = Opt_Result['b_CHP_on'][Opt_Result.index[0]]
                Result_CHP_End['CHP on_off'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['b_CHP_on'][Opt_Result.index[0]] 
            elif Opt_Result['b_CHP_on'][Opt_Result.index[0]]<1.1 and Opt_Result['b_CHP_on'][Opt_Result.index[0]]>0.9:
                CHP['b_CHP_on_ini'] = 1
                Result_CHP_End['CHP on_off'][Result_CHP_End.index[timestep]] = 1
            elif Opt_Result['b_CHP_on'][Opt_Result.index[0]]<0.1 and Opt_Result['b_CHP_on'][Opt_Result.index[0]]>-0.1:
                CHP['b_CHP_on_ini'] = 0
                Result_CHP_End['CHP on_off'][Result_CHP_End.index[timestep]] = 0
            else:
                print ("ERROR  -   CHP['b_CHP_on_ini']", Opt_Result['b_CHP_on'][Opt_Result.index[0]])
                            
            
                
            CHP['b_CHP_ini_1'] = Result_CHP_End['CHP on_off'][Result_CHP_End.index[timestep-2]]
            CHP['b_CHP_ini_2'] = Result_CHP_End['CHP on_off'][Result_CHP_End.index[timestep-1]]
            CHP['b_CHP_ini_3'] = Result_CHP_End['CHP on_off'][Result_CHP_End.index[timestep]]
           # print ("Cost:2", CHP['b_CHP_on_ini'], CHP['b_CHP_ini_1'], CHP['b_CHP_ini_2'], CHP['b_CHP_ini_3'])
            # -------- Calculate CHP2Qload and CHP2Qstor  ------------------------
            # ------------ FORE only ----------------
            if Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]>0:
                QProfileFore = LoadPeriodFore['QLoad1'][Result_CHP_End.index[timestep]]\
                             + LoadPeriodFore['QLoad2'][Result_CHP_End.index[timestep]]
                if Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]\
                    > QProfileFore:
                    Result_CHP_End['CHP th2load'][Result_CHP_End.index[timestep]]\
                         = QProfileFore
                    Result_CHP_End['CHP th2TES'][Result_CHP_End.index[timestep]]\
                         = Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]\
                         - QProfileFore
                elif Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]\
                    <= QProfileFore:
                    Result_CHP_End['CHP th2load'][Result_CHP_End.index[timestep]]\
                         = Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]
                    Result_CHP_End['CHP th2TES'][Result_CHP_End.index[timestep]]\
                         = 0
            #----------------------------------------------------------------
#                         
#            if Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]>0:
#                QProfileReal = LoadPeriodReal['QLoad1'][Result_CHP_End.index[timestep]]\
#                             + LoadPeriodReal['QLoad2'][Result_CHP_End.index[timestep]]
#                if Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]\
#                    > QProfileReal:
#                    Result_CHP_End['CHP th2load'][Result_CHP_End.index[timestep]]\
#                         = QProfileReal
#                    Result_CHP_End['CHP th2TES'][Result_CHP_End.index[timestep]]\
#                         = Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]\
#                    - QProfileReal
#                elif Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]\
#                    <= QProfileReal:
#                    Result_CHP_End['CHP th2load'][Result_CHP_End.index[timestep]]\
#                         = Result_CHP_End['CHP th'][Result_CHP_End.index[timestep]]
#                    Result_CHP_End['CHP th2TES'][Result_CHP_End.index[timestep]]\
#                         = 0
#            #---------------------------------------------------------------------                          
                     
            # PV
            Result_PV_End['PV batt selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2batt'][Opt_Result.index[0]]
            Result_PV_End['PV load selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2load'][Opt_Result.index[0]]
            Result_PV_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_exp'][Opt_Result.index[0]]
   
    if len(LoadPeriodFore)-PrHoBin < 0:
        print 'CompTime not possible!'
    else:
        t2 = ti.clock()
        CompTime['Computational Time'][timestep] = t2 - t1 
        
 
    # -----------------------------------------------------------------            
    # ----- Figures and Plotting  -------------------------------------
    # -----------------------------------------------------------------
    if len(LoadPeriodFore)-PrHoBin < 0:
       print "Cplex crash"
    else:
     # nach modified script: Jan von Appen
       Plotc = 3
       # nach modified script: Jan von Appen
       Plotc_back = pl.Plotting(Result_Grid_End, Result_BAT_End, Result_PV_End,\
       Result_CHP_End, Result_Heat_End, Result_TES_End, \
       PVavaPeriodFore, P_PV_max, P_Load_max, LoadPeriodFore, \
       Battery, Costs, start_date, end_date, Plotc, 'Fore', maxx,\
       PrHoBin, INOUT_string)

#==============================================================================
#     Result_Grid_End.plot(title='Grid')
#     Result_BAT_End.plot(title='Battery')
#     Result_Heat_End.plot(title='Heat') 
#     Result_TES_End.plot(title='Thermal Storage') 
#     Result_CHP_End.plot(title='CHP')
#   
#      
#==============================================================================

    # -----------------------------------------------------------------            
    # ------ KPIs -----------------------------------------------------    
    # -----------------------------------------------------------------            
    if len(LoadPeriodFore)-PrHoBin < 0:
       print "Fehler! No plotting!"
       kpi.Calc_KPI_dummy('Fore', 144,CompTime, INOUT_string)
    else:
       kpi.Calc_KPI(Result_BAT_End, Result_PV_End, Result_Grid_End,\
       Result_CHP_End, Result_TES_End, Result_Heat_End,\
       LoadPeriodFore, PVavaPeriodFore, Costs, PrHoBin, maxx,Delta_t, \
       Battery, CHP, Auxilary, 'Fore', CompTime,INOUT_string,CO2)
    # -----------------------------------------------------------------            
    # ------- Save to File --------------------------------------
    # -----------------------------------------------------------------
    Result_Grid_End.to_csv('RESULTS\Result_Opti_Fore_Grid_'+INOUT_string+'_10.csv')   
    Result_PV_End.to_csv('RESULTS\Result_Opti_Fore_PV_'+INOUT_string+'_10.csv')   
    Result_BAT_End.to_csv('RESULTS\Result_Opti_Fore_BAT_'+INOUT_string+'_10.csv')    
    Result_CHP_End.to_csv('RESULTS\Result_Opti_Fore_CHP_'+INOUT_string+'_10.csv')    
    Result_TES_End.to_csv('RESULTS\Result_Opti_Fore_TES_'+INOUT_string+'_10.csv')    
    Result_Heat_End.to_csv('RESULTS\Result_Opti_Fore_Heat_'+INOUT_string+'_10.csv')    
    LoadPeriodFore.to_csv('RESULTS\Load_'+INOUT_string+'_10.csv') 
    print "The End!"
    return 0
    
if __name__ == '__main__':
    	Sensitivity()
  #     ana.Analyse_Horizon()  