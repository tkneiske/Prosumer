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



def MPC():
    plt.close("all")

    #-----------------------------------------------
    # ---------------  INPUT DATA  -----------------   
    #-----------------------------------------------
    Delta_t = 10 # 10 min bins
    start_date = '8/3/2013'    
    end_date = '8/4/2013'
    date_year = '1/1/2013'
    PrHoBin = 72  #72;      
    #-----------------------------------------------
    
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print '%                                                  %'
    print '%         Optimierung von PV-Battery nach Microgrid%'     
    print '%                          plus adhoc              %'
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
    PVava_TOT_df, P_PV_max,P_Load_max, LoadAll_TOT_df, Battery, Costs \
    = ipv.inputvaluesEFH(Delta_t, TimeStepSize,year_stamps)
   
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
    # PV_LOAD_R_F.plot(title="real-forecast")                            
    
    
    # -------------------------------------------------
    #  Prepare Output and Results Dataframes    
    # -------------------------------------------------
    SOCbatEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['SOC battery']) 
    PbattcharEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Battery charging']) 
    PbattdisEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Battery dis-charging']) 
        
    GridImpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Grid Import'])
    GridExpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Grid Export'])    
                            
    #PVEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV']) 
   # PVselfconEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV selfcon']) 
    PVselfconbattEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV batt selfcon']) 
    PVselfconloadEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV load selfcon']) 
    PVexportEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Grid export']) 

    #Corrections for MPC                             
    #LoadKorrEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['Load Diff']) 
    #PVCorrEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['PV Diff']) 
    CorrBatDissEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrBattDis'])
    CorrBatChEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrBattCh'])
    CorrBattSOCEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrBatSOC'])
    CorrGridImpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrGridImp'])
    CorrPVexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrPVexp'])
    CorrGridexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrGridExp'])
    CorrPV2BattEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrPV2Batt'])        
    CorrPV2LoadEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps_date, columns=['CorrPV2Load'])        
                             
    # PV-Load-Forecast Values    
    Result_GridFore_End = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'], 
                             GridImpEnd, GridExpEnd], axis=1)
    Result_BATFore_End = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'], 
                             SOCbatEnd, PbattcharEnd, PbattdisEnd], axis=1)                      
    Result_PVFore_End = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'],\
# #                             PVEnd, 
                              PVselfconbattEnd,PVselfconloadEnd, PVexportEnd], axis=1) 
    # PV-Load Real Values                                     
    Result_BAT_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'], 
                            SOCbatEnd, PbattcharEnd, PbattdisEnd], axis=1)                      
    Result_Grid_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'], 
                            GridImpEnd, GridExpEnd], axis=1)
    Result_PV_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'],\
                               #      PVEnd, 
                             PVselfconbattEnd,PVselfconloadEnd, PVexportEnd], axis=1)   
    Result_Corr_End = pd.concat([CorrBatDissEnd,CorrBattSOCEnd,\
                      CorrGridImpEnd, CorrPVexpEnd, CorrGridexpEnd, CorrPV2BattEnd, \
                      CorrPV2LoadEnd, CorrBatChEnd])
 
 
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
    
    maxx = len(PVavaPeriodFore)-PrHoBin
    if len(PVavaPeriodFore)-PrHoBin < 0:
        print 'Prediction Horizon out of Range!!!'
    else:        
       # maxx = 10
        
        for timestep in range(0, maxx):    
            print timestep, maxx, [Result_Corr_End.index[timestep]]
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
           
          # --- Einzelplots ----Test Prediction Horizon --------------------
            Result_df = pd.concat([PVavaPeriodFore, -LoadPeriodFore['ELoad'], 
            #Result_df = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'], 
                                   -Opt_Result['P_Grid_import'], 
                                   Opt_Result['P_Grid_export'],
                                   Opt_Result['SOC_batt']/50,
                                   -Opt_Result['P_batt_dis'],
                                  # Opt_Result['P_batt_char'],\
                                  # -Opt_Result['P_PV_exp'],
                                   -Opt_Result['P_PV2load']], axis=1)
           # if timestep==1 or timestep==maxx*0.5 or timestep==maxx-1:
           #     Result_df.plot()
                #print Opt_Result['P_PV']

             
            # --- Gesamtergebnis -------- Variablen --------------------------
            # Battery                                 
            Result_BAT_End['SOC battery'][Result_BAT_End.index[timestep]] \
                      = Opt_Result['SOC_batt'][Opt_Result.index[0]]
            Result_BAT_End['Battery charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_char'][Opt_Result.index[0]]                        
            Result_BAT_End['Battery dis-charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_dis'][Opt_Result.index[0]]
                         
                         
            # PV               	                                            
            Result_PV_End['PV batt selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2batt'][Opt_Result.index[0]]
            Result_PV_End['PV load selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2load'][Opt_Result.index[0]]
            Result_PV_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_exp'][Opt_Result.index[0]]
                          
                            
            # Grid
            Result_Grid_End['Grid Import'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_import'][Opt_Result.index[0]]
            Result_Grid_End['Grid Export'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_export'][Opt_Result.index[0]]
            #----------------------------
        
            # -----------------------------------------------------------------            
            # check and correct forecast schedule    
            # -----------------------------------------------------------------               
            CorrTerms = cor.AdHoc_MPC(Result_BAT_End, Result_PV_End,\
            Result_Grid_End, PVavaPeriodFore['PV 2013, Kassel, 10min'], PVavaReal[timestep],\
            LoadPeriodFore['ELoad'], timestep, Battery, \
                ELoadR[timestep], Q1LoadR[timestep], Q2LoadR[timestep])
            #CorrTerms = cor.Correct_MPC_dummy(Opt_Result, PVavaPeriodReal, PVavaPeriodFore,
            #                            LoadPeriodReal, LoadPeriodFore, Battery)                            
            
            # Correction after MPC
            
            Result_Corr_End['CorrBattDis'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrBattDis']
            Result_Corr_End['CorrBattCh'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrBattCh']
            Result_Corr_End['CorrBatSOC'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrBatSOC']
            Result_Corr_End['CorrGridImp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrGridImp']
            Result_Corr_End['CorrGridExp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrGridExp']
            Result_Corr_End['CorrPVexp'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrPVexp']
            Result_Corr_End['CorrPV2Batt'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrPV2Batt']                                        
            Result_Corr_End['CorrPV2Load'][Result_Corr_End.index[timestep]] \
                     = CorrTerms['CorrPV2Load']                                        
                     
                                 
            # -----------------------------------------------------------------            
            # ------------------ Initialize for the next step -----------------
            # -----------------------------------------------------------------            
            Battery['SOC_batt_ini'] = CorrTerms['CorrBatSOC']    
                                      
            # --- Gesamtergebnis -------- Variablen --------------------------
            # Battery                                 
            Result_BAT_End['SOC battery'][Result_BAT_End.index[timestep]] \
                      = CorrTerms['CorrBatSOC']                      
            Result_BAT_End['Battery charging'][Result_BAT_End.index[timestep]] \
                     = CorrTerms['CorrBattCh']
            Result_BAT_End['Battery dis-charging'][Result_BAT_End.index[timestep]] \
                     = CorrTerms['CorrBattDis']
                                 
            Result_BATFore_End['SOC battery'][Result_BAT_End.index[timestep]] \
                      = Opt_Result['SOC_batt'][Opt_Result.index[0]]                    
            Result_BATFore_End['Battery charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_char'][Opt_Result.index[0]]                        
            Result_BATFore_End['Battery dis-charging'][Result_BAT_End.index[timestep]] \
                     = Opt_Result['P_batt_dis'][Opt_Result.index[0]]
                         
                         
            # PV               	                                            
            Result_PV_End['PV batt selfcon'][Result_PV_End.index[timestep]] \
                    = CorrTerms['CorrPV2Batt']
            Result_PV_End['PV load selfcon'][Result_PV_End.index[timestep]] \
                    = CorrTerms['CorrPV2Load']
            Result_PV_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = CorrTerms['CorrPVexp']
 
            Result_PVFore_End['PV batt selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2batt'][Opt_Result.index[0]]
            Result_PVFore_End['PV load selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV2load'][Opt_Result.index[0]]
            Result_PVFore_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_exp'][Opt_Result.index[0]]
                          
                            
            # Grid
            Result_Grid_End['Grid Import'][Result_Grid_End.index[timestep]] \
                    = CorrTerms['CorrGridImp']
            Result_Grid_End['Grid Export'][Result_Grid_End.index[timestep]] \
                    = CorrTerms['CorrGridExp']
            
            Result_GridFore_End['Grid Import'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_import'][Opt_Result.index[0]]                          
            Result_GridFore_End['Grid Export'][Result_Grid_End.index[timestep]] \
                    = Opt_Result['P_Grid_export'][Opt_Result.index[0]]                       
            #----------------------------

    # -----------------------------------------------------------------            
    # ----- Figures and Plotting  -------------------------------------
    # -----------------------------------------------------------------
#==============================================================================
# s
#==============================================================================
#==============================================================================
#     Result_GridFore_End.plot(title='Grid Forecast')
#     Result_BATFore_End.plot(title='Battery Forecast')
#     Result_PVFore_End.plot(title='PV Forecast')
#     
#     Result_Corr_End.plot(title='Correction')   
#    
#==============================================================================
    Plotc = 3
   # ---------- Plotting nach Jan --------------------------------------     
    Plotc_back = pl.Plotting(Result_Grid_End, Result_BAT_End, Result_PV_End,\
    PVavaPeriodReal, P_PV_max, P_Load_max, LoadPeriodReal, \
    Battery, Costs, start_date, end_date, Plotc, 'Real') 
    Plotc = Plotc_back
    Plotc_back = pl.Plotting(Result_GridFore_End, Result_BATFore_End, Result_PVFore_End,\
    PVavaPeriodFore, P_PV_max, P_Load_max, LoadPeriodFore, \
    Battery, Costs, start_date, end_date, Plotc, 'Fore') 
     

    # -----------------------------------------------------------------            
    # ------ KPIs -----------------------------------------------------    
    # -----------------------------------------------------------------            

    # without ad-hoc, Fahrplan only
    kpi.Calc_KPI(Result_BATFore_End, Result_PVFore_End, Result_GridFore_End,\
    LoadPeriodFore, PVavaPeriodFore, Costs, PrHoBin, maxx, Battery, Delta_t, 'Fore')
    
    # with ad-hoc, with Real PV and Real Load
    kpi.Calc_KPI(Result_BAT_End, Result_PV_End, Result_Grid_End,\
    LoadPeriodReal, PVavaPeriodReal, Costs, PrHoBin, maxx, Battery, Delta_t, 'Real')

    # -----------------------------------------------------------------            
    # ----- File Output  -------------------------------------
    # -----------------------------------------------------------------                  
    
    Result_Grid_End.to_csv('OUTPUT\Kosten_Result_Grid_End.csv')   
    Result_PV_End.to_csv('OUTPUT\Kosten_Result_PV_End.csv')   
    Result_BAT_End.to_csv('OUTPUT\Kosten_Results_BAT_End.csv')    
    Result_GridFore_End.to_csv('OUTPUT\Kosten_Result_GridFore_End.csv')   
    Result_PVFore_End.to_csv('OUTPUT\Kosten_Result_PVFore_End.csv')   
    Result_BATFore_End.to_csv('OUTPUT\Kosten_Results_BATFore_End.csv')    
    
    
    print "The End!"
    return 0

    
if __name__ == '__main__':
    	MPC()        