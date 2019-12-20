# -*- coding: utf-8 -*-
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
28.06.17 delete CHP

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
#from copy import deepcopy

def MPC():
    plt.close("all")

    #-----------------------------------------------
    # ---------------  INPUT DATA  -----------------   
    #-----------------------------------------------
    Delta_t = 10 # 10 min bins
    start_date = '3/2/2013'    
    end_date = '3/3/2013'
    date_year = '1/1/2013'
    PrHoBin = 72;      
    #-----------------------------------------------
    
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print '%                                                  %'
    print '%         Optimierung von CHP, TES, GASboiler      %'     
    print '%         PV, Battery nach KOSTEN         %'     
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
 #   PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max, Battery, Auxilary, ThermalStorage, \
 #   Costs, EHeater = ipv.inputvalues_VDE_EFH(Delta_t, TimeStepSize,year_stamps)
  
#    if inputFile == "VDE":                    
    PVava_TOT_df, P_PV_max,P_Load_max, LoadAll_TOT_df, Battery, Auxilary, ThermalStorage, \
    Costs = ipv.inputvalues_VDE_EFH(Delta_t, TimeStepSize,year_stamps)
#EHeater        
#    elif inputFile == "LPG":
#        PVava_TOT_df, P_PV_max,P_Load_max, LoadAll_TOT_df, Battery, Costs \
#        = ipv.inputvalues_LPG_EFH(Delta_t, TimeStepSize,year_stamps)
#    else:
#        print ("ERROR ---- inputFile in Main is not correct")
   

    # -------------------------------------------------------------------------
    # REAL VALUES 
    # -------------------------------------------------------------------------
    day_stamps_date = pd.date_range(start_date, periods=BIN, freq=TimeStepSize)          
    # ---- Load
    LoadPeriodReal = LoadAll_TOT_df[start_date:end_date]
    # ---- PV
    PVavaPeriodReal = PVava_TOT_df[start_date:end_date]
    
    # -------------------------------------------------------------------------
    # FORECAST  Values -- Tagespersistenz
    # -------------------------------------------------------------------------
    print 'Forecast-Method: Tagespersistenz.'
    # -- Use for Tagespersistenz
    day_stamps_fore = day_stamps_date - pd.DateOffset(days=1) # 1 Tag vorher
    date_fore = day_stamps_fore[0].strftime('%m/%d/%Y')
    date_fore_end = day_stamps_fore[BIN-1].strftime('%m/%d/%Y')
    #print date_fore, date_fore_end    
    # ----  Load
    LPF = LoadAll_TOT_df[date_fore:date_fore_end] 
    LoadPeriodFore =LPF.set_index(day_stamps_date) # Re-index

    # ----- PV 
    PVPF = PVava_TOT_df[date_fore:date_fore_end]
    PVavaPeriodFore = PVPF.set_index(day_stamps_date) # Re-index
    #print day_stamps_fore
    #print day_stamps_date
    
    # -------------------------------------------------------------------------        
    # --- Plot differenz Forecast-Real Values
    #PV_LOAD_R_F = pd.concat([PVavaPeriodReal-PVavaPeriodFore, 
    #                         LoadPeriodReal['ELoad']-LoadPeriodFore['ELoad']], axis=1)                          
    #PV_LOAD_R_F.plot(title="real-forecast")                            
  
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
    Result_TES_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['QLoad1']*2, \
                SOCTESEnd, PTEScharEnd, PTESdisEnd], axis=1)                      
    # Result_TES_End = pd.concat([-LoadPeriodReal['QLoad1'], \
    #             -LoadPeriodReal['QLoad2'],SOCTESEnd, PTEScharEnd, PTESdisEnd], axis=1)                      

 
    #Heat                            
    AuxEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Aux Gasbrenner'])                              
    EHeaterelEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['EHeater el'])                
    EHeaterthEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['EHeater th'])                
      
    Result_Heat_End = pd.concat([-LoadPeriodReal['QLoad1']*2,
                                 AuxEnd, EHeaterthEnd,EHeaterelEnd,
                                 PTESdisEnd, SOCTESEnd], axis=1)                                 	

    # ---------- PV ----------                       
    #PVEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV']) 
    PVselfconbattEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV batt selfcon']) 
    PVselfconloadEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV load selfcon']) 
    PVexportEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Grid export']) 
    PVsumEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Summe'])     
    Result_PV_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'],\
                                -EHeaterelEnd, \
                             PVselfconloadEnd,PVselfconbattEnd, PVexportEnd,PVsumEnd], axis=1)   
    # mit Forecast
#    Result_PV_End = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'],\
    #                          PVEnd, 
#                             PVselfconEnd, PVexportEnd,PVsumEnd], axis=1)   
    
    #Corrections for MPC                             
#==============================================================================
#     LoadKorrEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['Load Diff']) 
#     PVCorrEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV Diff']) 
#     CorrBatDissEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CorrBatDiss'])
#     CorrBattSOCEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CorrBatSOC'])
#     CorrGridImpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CorrGridImp'])
#     CorrPVexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CorrPVexp'])
#     CorrGridexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CorrGridexp'])
#     CorrPVscEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CorrPVsc'])        
#     Result_Corr_End = pd.concat([LoadKorrEnd, PVCorrEnd, CorrBatDissEnd,CorrBattSOCEnd,\
#                       CorrGridImpEnd, CorrPVexpEnd, CorrGridexpEnd, CorrPVscEnd])
# 
#==============================================================================
    # -------------------------------------------------------------------------
    # ------------  MPC Loop --------------------------------------------------    
    # -------------------------------------------------------------------------
    ELoadF = LoadPeriodFore['ELoad'].values  
    Q1LoadF = LoadPeriodFore['QLoad1'].values
    Q2LoadF = LoadPeriodFore['QLoad2'].values                       
    PVavaFore = PVavaPeriodFore['PV 2013, Kassel, 10min'].values #PV2013, Kassel, 10min
    #PVavaReal = PVavaPeriodFore['PV 2013, Kassel, 10min'].values #PV2013, Kassel, 10min
    
    maxx = len(LoadPeriodFore)-PrHoBin
    if len(LoadPeriodFore)-PrHoBin < 0:
        print 'Prediction Horizon out of Range!!!'
    else:        
        maxx =  144
        for timestep in range(0, maxx):    
            print timestep, maxx
            # -----------------------------------------------------------------            
            # ------------------ Initialize for the next step ---------------------
            # -----------------------------------------------------------------            
            Load = {i: ELoadF[i+timestep] for i in PrHoBinRange}; 
            P_sh_th = {i: Q1LoadF[i+timestep] for i in PrHoBinRange};
            P_dhw_th = {i: Q2LoadF[i+timestep] for i in PrHoBinRange};
            P_PV_ava = {i: PVavaFore[i+timestep] for i in PrHoBinRange}; 
            # -----------------------------------------------------------------            
            # -------------------  Optimze ----------------------------------------    
            # -----------------------------------------------------------------                   	
            horizon_stamps = day_stamps_date[timestep:PrHoBin+timestep]
            Opt_Result=opt.OptFlex_optimierer(
                      horizon_stamps, PrHoBin,
                      Load, P_PV_max, P_Load_max, P_sh_th, P_dhw_th, P_PV_ava, Battery,
                      Auxilary,ThermalStorage, Costs)#, EHeater)

            # -----------------------------------------------------------------            
            # -----  Prepare Variable Results   -------------------------------
            # -----------------------------------------------------------------            
           
#==============================================================================
#             # --- Einzelplots ----Test Prediction Horizon --------------------
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
#                 
#             #if timestep==2 or timestep==max*0.5+1 or timestep==max-1:
#              #   Result_th_df.plot()
#==============================================================================
                
            # -----------------------------------------------------------------            
            # check and correct forecast schedule    
            # -----------------------------------------------------------------               
#==============================================================================
#             CorrTerms = cor.Correct_MPC(Opt_Result, PVavaPeriodReal, PVavaPeriodFore,
#                                         LoadPeriodReal, LoadPeriodFore, Battery)
#             #CorrTerms = cor.Correct_MPC_dummy(Opt_Result, PVavaPeriodReal, PVavaPeriodFore,
#             #                            LoadPeriodReal, LoadPeriodFore, Battery)                                                
#==============================================================================
                
            # -----------------------------------------------------------------            
            # ----------------Re-Initialize SOC for the next step -----------------
            # -----------------------------------------------------------------            
            Battery['SOC_batt_ini'] = Opt_Result['SOC_batt'][Opt_Result.index[0]] 
            ThermalStorage['SOC_TES_ini'] = Opt_Result['SOC_TES'][Opt_Result.index[0]]  
       #     print " ------------>  SOC"
       #     print Opt_Result['SOC_batt'] 
       #     print Battery['SOC_batt_ini'], ThermalStorage['SOC_TES_ini']             
         
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
            # Aux Gasbrenner & EHeater
            Result_Heat_End['Aux Gasbrenner'][Result_Heat_End.index[timestep]] \
                    = Opt_Result['P_aux_th'][Opt_Result.index[0]]                	                                                                                          
            Result_Heat_End['TES dis-charging'][Result_Heat_End.index[timestep]] \
                     = Opt_Result['P_TES_dis'][Opt_Result.index[0]]                	                                   
            Result_Heat_End['SOC TES'][Result_Heat_End.index[timestep]] \
                     = Opt_Result['SOC_TES'][Opt_Result.index[0]]                	                                   
#            Result_Heat_End['EHeater th'][Result_Heat_End.index[timestep]] \
#                     = Opt_Result['P_eheater_th'][Opt_Result.index[0]]               	                                                        
#            Result_Heat_End['EHeater el'][Result_Heat_End.index[timestep]] \
#                     = Opt_Result['P_eheater_el'][Opt_Result.index[0]]               	                                                        
            # Thermal Storage                                 
            Result_TES_End['SOC TES'][Result_TES_End.index[timestep]] \
                     = Opt_Result['SOC_TES'][Opt_Result.index[0]]               	                                   
            Result_TES_End['TES charging'][Result_TES_End.index[timestep]] \
                     = Opt_Result['P_TES_char'][Opt_Result.index[0]]                	                                   
            Result_TES_End['TES dis-charging'][Result_TES_End.index[timestep]] \
                     = Opt_Result['P_TES_dis'][Opt_Result.index[0]]                	                                   
         
                     
            # PV
            #Result_PV_End['PV'][Result_PV_End.index[timestep]] \
            #        = Opt_Result['P_PV'][Opt_Result.index[0]]                	                                            
            Result_PV_End['PV batt selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2batt'][Opt_Result.index[0]]
            Result_PV_End['PV load selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2load'][Opt_Result.index[0]]
            Result_PV_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_exp'][Opt_Result.index[0]]
         #                 +CorrTerms['CorrPVexp']
         #                 +CorrTerms['CorrPVexp']+\
         #                +CorrTerms['CorrPVsc']                	                                            
    
    
    
    

    # -----------------------------------------------------------------            
    # ----- Figures and Plotting  -------------------------------------
    # -----------------------------------------------------------------
    # nach modified script: Jan von Appen
    Plotc = 3
    # nach modified script: Jan von Appen
    Plotc_back = pl.Plotting(Result_Grid_End, Result_BAT_End, Result_PV_End,\
    Result_Heat_End, Result_TES_End, \
    PVavaPeriodFore, P_PV_max, P_Load_max, LoadPeriodFore, \
    Battery, Costs, start_date, end_date, Plotc, 'Fore', maxx)
    #Battery, Costs, EHeater, start_date, end_date, Plotc, 'Fore', maxx)
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
    print 'KPI_END are calculated with Forecast values !!!'    
       # without ad-hoc, Fahrplan only
    kpi.Calc_KPI(Result_BAT_End, Result_PV_End, Result_Grid_End,\
    Result_TES_End, Result_Heat_End,\
    LoadPeriodFore, PVavaPeriodFore, Costs, PrHoBin, maxx,Delta_t, \
    Battery, Auxilary,'Fore')
    #Battery, Auxilary, EHeater,'Fore')
    # -----------------------------------------------------------------            
    # ------- Save to File --------------------------------------
    # -----------------------------------------------------------------               
    Result_Grid_End.to_csv('Results\Kosten_Result_Grid_End.csv')   
    Result_PV_End.to_csv('Results\Kosten_Result_PV_End.csv')   
    Result_BAT_End.to_csv('Results\Kosten_Results_BAT_End.csv')    
    Result_TES_End.to_csv('Results\Kosten_Results_TES_End.csv')    
    Result_Heat_End.to_csv('Results\Kosten_Results_Heat_End.csv')    
 
    print "The End!"
    return 0
    
if __name__ == '__main__':
    	MPC()        