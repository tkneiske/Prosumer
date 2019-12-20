# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 21:21:28 2015
26.10.2015 Prepare for Jahressimulations
26.10.2015 Output in csv-File 

@author: tkneiske
"""
import OptFlex_inputvalues as ipv
import OptFlex_KPIs as kpi
import OptFlex_optimierer as opt
import OptFlex_nachregelung as cor
import OptFlex_plotting as pl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#from copy import deepcopy

#==============================================================================
# Check for use later 
#from datetime import date
#from dateutil.relativedelta import relativedelta
# 
# one_day = date.today() + relativedelta (days =+ 1)
# one_month = date.today() + relativedelta( months =+ 1 )
#==============================================================================

def MPC():
    plt.close("all")

    #-----------------------------------------------
    # ---------------  INPUT DATA  -----------------   
    #-----------------------------------------------
    Delta_t = 10 # 10 min bins
    start_date = '8/2/2013'    
    end_date = '8/3/2013'
    date_year = '1/1/2013'
    PrHoBin = 72  #72;     # Prediction Horizon 
    #inputFile = "LPG"  # Load Profile IWES
    inputFile = "VDE"  # Load Profile VDE
    #-----------------------------------------------
    
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print '%                                                  %'
    print '%         Optimierung von PV-Battery   Microgrid   %'     
    print '%                        28.4.2017                 %'
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
    if inputFile == "VDE":                    
        PVava_TOT_df, P_PV_max,P_Load_max, LoadAll_TOT_df, Battery, Costs \
        = ipv.inputvalues_VDE_EFH(Delta_t, TimeStepSize,year_stamps)
    elif inputFile == "LPG":
        PVava_TOT_df, P_PV_max,P_Load_max, LoadAll_TOT_df, Battery, Costs \
        = ipv.inputvalues_LPG_EFH(Delta_t, TimeStepSize,year_stamps)
    else:
        print ("ERROR ---- inputFile in Main is not correct")
   
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
    day_stamps_fore = day_stamps_date - pd.DateOffset(days=1) 
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
    
    
    # -------------------------------------------------
    #  Prepare Output and Results Dataframes    
    # -------------------------------------------------
    SOCbatEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['SOC battery']) 
    PbattcharEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Battery charging']) 
    PbattdisEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Battery dis-charging']) 
#    Result_BAT_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'], 
#                            SOCbatEnd, PbattcharEnd, PbattdisEnd], axis=1)                      
    Result_BAT_End = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'], 
                            SOCbatEnd, PbattcharEnd, PbattdisEnd], axis=1)                      
        
    GridImpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Grid Import'])
    GridExpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Grid Export'])    
    Result_Grid_End = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'], 
                            GridImpEnd, GridExpEnd], axis=1)
#    Result_Grid_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'], 
#                            GridImpEnd, GridExpEnd], axis=1)
                            
    #PVEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV']) 
   # PVselfconEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV selfcon']) 
    PVselfconbattEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV batt selfcon']) 
    PVselfconloadEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV load selfcon']) 
    PVexportEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Grid export']) 
    Result_PV_End = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'],\
#                             PVEnd, 
                             PVselfconbattEnd,PVselfconloadEnd, PVexportEnd], axis=1)   
#    Result_PV_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'],\
                                #      PVEnd, 
#                             PVselfconEnd, PVexportEnd], axis=1)   
                             
    #Corrections for MPC                             
    LoadKorrEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Load Diff']) 
    PVCorrEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Diff']) 
    CorrBatDissEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrBatDiss'])
    CorrBattSOCEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrBatSOC'])
    CorrGridImpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrGridImp'])
    CorrPVexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrPVexp'])
    CorrGridexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrGridexp'])
    CorrPVscEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrPVsc'])        
    Result_Corr_End = pd.concat([LoadKorrEnd, PVCorrEnd, CorrBatDissEnd,CorrBattSOCEnd,\
                      CorrGridImpEnd, CorrPVexpEnd, CorrGridexpEnd, CorrPVscEnd])
    # -------------------------------------------------------------------------
    # ------------  MPC Loop --------------------------------------------------    
    # -------------------------------------------------------------------------
    ELoadF = LoadPeriodFore['ELoad'].values  
    Q1LoadF = LoadPeriodFore['QLoad1'].values
    Q2LoadF = LoadPeriodFore['QLoad2'].values                       
    PVavaFore = PVavaPeriodFore['PV 2013, Kassel, 10min'].values #PV2013, Kassel, 10min
    #PVavaReal = PVavaPeriodFore['PV 2013, Kassel, 10min'].values #PV2013, Kassel, 10min
    
    maxx = len(PVavaPeriodFore)-PrHoBin
    if len(PVavaPeriodFore)-PrHoBin < 0:
        print 'Prediction Horizon out of Range!!!'
    else:        
      #  maxx = 144  # uncomment for 1 day only
        for timestep in range(0, maxx):    
            print timestep, maxx, BIN#, [Result_Corr_End.index[timestep]]
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
                       horizon_stamps, PrHoBin, P_PV_ava, P_PV_max, P_Load_max,\
                       Load, P_sh_th, P_dhw_th,Battery, Costs)

            # -----------------------------------------------------------------            
            # -----  Prepare Variable Results   -------------------------------
            # -----------------------------------------------------------------            
           
#==============================================================================
#           # --- Einzelplots ----Test Prediction Horizon --------------------
#             Result_df = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'], 
#                                    -Opt_Result['P_Grid_import'], 
#                                    Opt_Result['P_Grid_export'],
#                                    Opt_Result['SOC_batt']/50,
#                                    -Opt_Result['P_batt_dis'],
#                                   # Opt_Result['P_batt_char'],\
#                                   # -Opt_Result['P_PV_exp'],
#                                    -Opt_Result['P_PV2load']], axis=1)
#            if timestep==1 or timestep==maxx*0.5 or timestep==maxx-1:
#                 Result_df.plot()
#                 #print Opt_Result['P_PV']
# 
#==============================================================================
            # -----------------------------------------------------------------            
            # check and correct forecast schedule    
            # -----------------------------------------------------------------               
            #CorrTerms = cor.Correct_MPC(Opt_Result, PVavaPeriodReal, PVavaPeriodFore,
            #                            LoadPeriodReal, LoadPeriodFore, Battery)
            CorrTerms = cor.Correct_MPC_dummy(Opt_Result, PVavaPeriodReal, PVavaPeriodFore,
                                        LoadPeriodReal, LoadPeriodFore, Battery)                            
            # Correction after MPC
            Result_Corr_End['Load Diff'][Result_Corr_End.index[timestep]] = CorrTerms['LoadDiff']
            Result_Corr_End['PV Diff'][Result_Corr_End.index[timestep]] = CorrTerms['PVDiff']
            #Result_Corr_End['Battery diss'][Result_PV_End.index[timestep]] = CorrTerms['BatDiss']
            Result_Corr_End['CorrBatDiss'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrBatDiss']
            Result_Corr_End['CorrBatSOC'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrBatSOC']
            Result_Corr_End['CorrGridImp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrGridImp']
            Result_Corr_End['CorrGridexp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrGridexp']
            Result_Corr_End['CorrPVexp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrPVexp']
            Result_Corr_End['CorrPVsc'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrPVsc']
       

            # -----------------------------------------------------------------            
            # ------------------ Initialize for the next step -----------------
            # -----------------------------------------------------------------            
            Battery['SOC_batt_ini'] = Opt_Result['SOC_batt'][Opt_Result.index[0]]\
                          +CorrTerms['CorrBatSOC']
           
            # --- Gesamtergebnis -------- Variablen --------------------------
            # Battery                                 
            Result_BAT_End['SOC battery'][Result_BAT_End.index[timestep]] \
                      = (Opt_Result['SOC_batt'][Opt_Result.index[0]]\
                          +CorrTerms['CorrBatSOC'])                      
            Result_BAT_End['Battery charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_char'][Opt_Result.index[0]]\
                         +CorrTerms['CorrBatChar']
            Result_BAT_End['Battery dis-charging'][Result_BAT_End.index[timestep]] \
                     = (Opt_Result['P_batt_dis'][Opt_Result.index[0]]\
                         +CorrTerms['CorrBatDiss'])
                         
            # PV               	                                            
            Result_PV_End['PV batt selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2batt'][Opt_Result.index[0]]
            Result_PV_End['PV load selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2load'][Opt_Result.index[0]]
            Result_PV_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_exp'][Opt_Result.index[0]]\
                          +CorrTerms['CorrPVexp']
                            
            # Grid
            Result_Grid_End['Grid Import'][Result_Grid_End.index[timestep]] \
                    = (Opt_Result['P_Grid_import'][Opt_Result.index[0]]\
                          +CorrTerms['CorrGridImp'])
            Result_Grid_End['Grid Export'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_export'][Opt_Result.index[0]]\
                          +CorrTerms['CorrGridexp']
            #----------------------------


    # -----------------------------------------------------------------            
    # ----- File Output  -------------------------------------
    # -----------------------------------------------------------------                  
    #Result_df = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'],\
    #Result_Grid_End, Result_BAT_End, Result_PV_End])
    #d = pd.HDFStore('Result_PV_Battery_OptFlex.h5')
    #d.close()
    # -----------------------------------------------------------------            
    # ----- Figures and Plotting  -------------------------------------
    # -----------------------------------------------------------------
#==============================================================================
#     Result_Grid_End.plot(title='Grid')
#     Result_BAT_End.plot(title='Battery')
#     Result_PV_End.plot(title='PV')
#     Result_Corr_End.plot(title='Correction')          
#==============================================================================
    # ---------- Plotting nach Jan --------------------------------------     
    pl.Plotting(Result_Grid_End, Result_BAT_End, Result_PV_End,\
    PVavaPeriodReal,PVavaPeriodFore, P_PV_max, P_Load_max, LoadPeriodReal, \
    LoadPeriodFore, Battery, Costs, start_date, end_date, maxx) 
    
    # -----------------------------------------------------------------            
    # ------ KPIs -----------------------------------------------------    
    # -----------------------------------------------------------------            
    kpi.Calc_KPI(Result_BAT_End, Result_PV_End, Result_Grid_End,\
    LoadPeriodReal, PVavaPeriodFore, Costs, PrHoBin, maxx, Battery, Delta_t)
   
    Result_Grid_End.to_csv('Results\Kosten_Result_Grid_End.csv')   
    Result_PV_End.to_csv('Results\Kosten_Result_PV_End.csv')   
    Result_BAT_End.to_csv('Results\Kosten_Results_BAT_End.csv')    
    
    
    print "The End!"
    return 0

    
if __name__ == '__main__':
    	MPC()        