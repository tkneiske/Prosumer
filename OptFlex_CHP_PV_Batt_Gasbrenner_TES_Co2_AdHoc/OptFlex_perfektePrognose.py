# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 00:45:38 2015

@author: tkneiske
"""

import pandas as pd
import OptFlex_inputvalues as ipv
import OptFlex_optimierer as opt
import matplotlib.pyplot as plt
import OptFlex_plotting as pl
import seaborn
import pandas as pd
import numpy as np
import OptFlex_KPIs as kpi

def PerfektePrognose(PVavaPeriodReal,
        LoadPeriodReal, date):
            
            
            
    # -------------------------------------------------------------------------
    # Prepare Input
    # -------------------------------------------------------------------------    
    PrHoBin = 72  #72;
    #numberOfdays = 7
    numberOfdays = 2
    Delta_t = 10
    PVava_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max, Battery, Auxilary, ThermalStorage, \
    date_year = '1/1/2013'
    CHP, Costs = ipv.inputvaluesEFH(Delta_t, date_year)
    PrHoBinRange = range(0, PrHoBin)  # PredHorizonBin
    #horizon_stamps = pd.date_range(date, periods=PrHoBin, freq='10min')   
    #BIN = 144 #- for one day with 10min resolution
    BIN = 144*numberOfdays   
    day_stamps = pd.date_range(date, periods=BIN, freq='10min')  
    ELoadR = LoadPeriodReal['ELoad'].values  
    Q1LoadR = LoadPeriodReal['QLoad1'].values
    Q2LoadR = LoadPeriodReal['QLoad2'].values   
    PVavaReal = PVavaPeriodReal['PV 2013, Kassel, 10min'].values #PV2013, Kassel, 10min

    # -------------------------------------------------------------------------
    # Prepare: Ausgabe Dataframes
    # -------------------------------------------------------------------------
    #BAT    
    SOCbatEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['SOC battery']) 
    PbattcharEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['Battery charging']) 
    PbattdisEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['Battery dis-charging']) 
    Result_BAT_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['ELoad'], 
                            SOCbatEnd, PbattcharEnd, PbattdisEnd], axis=1)                      
    #Grid    
    GridImpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['Grid Import'])
    GridExpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['Grid Export'])    
    Result_Grid_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['ELoad'], 
                            GridImpEnd, GridExpEnd], axis=1)
    #TES                                         
    SOCTESEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['SOC TES']) 
    PTEScharEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['TES charging']) 
    PTESdisEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['TES dis-charging']) 
    Result_TES_End = pd.concat([PVavaPeriodReal,-LoadPeriodReal['QLoad1']*2, \
                SOCTESEnd, PTEScharEnd, PTESdisEnd], axis=1)                      
    # Result_TES_End = pd.concat([-LoadPeriodReal['QLoad1'], \
    #             -LoadPeriodReal['QLoad2'],SOCTESEnd, PTEScharEnd, PTESdisEnd], axis=1)                      

    #CHP
    CHPelEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CHP el'])                              
    CHPthEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CHP th'])                              
    CHPscEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CHP self'])                              
    CHPexpEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['CHP Export'])                              
    Result_CHP_End = pd.concat([-LoadPeriodReal['ELoad'], -LoadPeriodReal['QLoad1']*2,\
                            CHPelEnd, CHPthEnd, CHPscEnd, CHPexpEnd], axis=1)                      
    #Heat                            
    AuxEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['Aux Gasbrenner'])                              
    Result_Heat_End = pd.concat([-LoadPeriodReal['QLoad1']*2,
                                 AuxEnd, CHPthEnd,
                                 PTESdisEnd, SOCTESEnd], axis=1)                                 	
    #Result_Heat_End = pd.concat([-LoadPeriodReal['QLoad1'], -LoadPeriodReal['QLoad2'],
    #                             AuxEnd], axis=1)

    # ---------- PV ----------                       
    #PVEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV']) 
    PVselfconEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV selfcon']) 
    PVexportEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV Grid export']) 
    PVsumEnd = pd.DataFrame(np.zeros(BIN), index=day_stamps, columns=['PV Summe'])     
    Result_PV_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'],\
    #                             PVEnd, 
                             PVselfconEnd, PVexportEnd,PVsumEnd], axis=1)   
    # mit Forecast
    Result_PV_End = pd.concat([PVavaPeriodReal, -LoadPeriodReal['ELoad'],\
    #                          PVEnd, 
                             PVselfconEnd, PVexportEnd,PVsumEnd], axis=1)   
    # ohne Forecast    
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
    maxx = len(LoadPeriodReal)-PrHoBin
    if len(LoadPeriodReal)-PrHoBin < 0:
        print 'Prediction Horizon out of Range!!!'
    else:        
        maxx = 10
        for timestep in range(0, maxx):    
            print timestep
            # -----------------------------------------------------------------            
            # ------------------ Initialize for the next step ---------------------
            # -----------------------------------------------------------------            
            Load = {i: ELoadR[i+timestep] for i in PrHoBinRange}; 
            P_sh_th = {i: Q1LoadR[i+timestep] for i in PrHoBinRange};
            P_dhw_th = {i: Q2LoadR[i+timestep] for i in PrHoBinRange};
            P_PV_ava = {i: PVavaReal[i+timestep] for i in PrHoBinRange}; 
            # -----------------------------------------------------------------            
            # -------------------  Optimze ----------------------------------------    
            # -----------------------------------------------------------------                   	
            horizon_stamps = day_stamps[timestep:PrHoBin+timestep]
            Opt_Result=opt.OptFlex_optimierer(
                       horizon_stamps, PrHoBin,
                       Load, P_PV_max, P_Load_max, P_sh_th, P_dhw_th, P_PV_ava, Battery,
                       Auxilary, \
                       ThermalStorage, CHP, Costs)

            # -----------------------------------------------------------------            
            # -----  Prepare Variable Results   -------------------------------
            # -----------------------------------------------------------------            
           
            # --- Einzelplots ----Test Prediction Horizon --------------------
            Result_el_df = pd.concat([-LoadPeriodReal['ELoad'], 
                                   -Opt_Result['P_Grid_import'], 
                                    Opt_Result['P_Grid_export'],
                                    Opt_Result['SOC_batt'],
                                   -Opt_Result['P_batt_dis'],
                                    Opt_Result['P_batt_char'],             
                                    #Opt_Result['P_CHP_el_sc'],
                                   -Opt_Result['P_CHP_el'], 
                                   -Opt_Result['P_CHP_el_exp'], ],axis=1)                                   
            Result_th_df = pd.concat([-LoadPeriodReal['QLoad1']*2,
                                   -Opt_Result['P_aux_th'],
                                   -Opt_Result['P_TES_dis'],
                                    Opt_Result['P_TES_char'],
                                    Opt_Result['SOC_TES'],
                                    Opt_Result['P_CHP_th'],
                                     ],axis=1) 
            Result_PV_Grid = pd.concat([-PVavaPeriodReal['PV 2013, Kassel, 10min'],
                                   -LoadPeriodReal['ELoad'],
                                   -Opt_Result['P_Grid_import'], 
                                    Opt_Result['P_Grid_export'],
                                    Opt_Result['P_PV_exp'],
                                    Opt_Result['P_CHP_el_exp'], ],axis=1)                        
#==============================================================================
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
#==============================================================================
            #if timestep==2 or timestep==max*0.5+1 or timestep==max-1:
             #   Result_th_df.plot()
                
                
            # -----------------------------------------------------------------            
            # ----------------Re-Initialize SOC for the next step -----------------
            # -----------------------------------------------------------------            
            Battery['SOC_batt_ini'] = Opt_Result['SOC_batt'][Opt_Result.index[1]] 
            ThermalStorage['SOC_TES_ini'] = Opt_Result['SOC_TES'][Opt_Result.index[1]]            
            CHP['b_CHP_on_ini'] = Opt_Result['b_CHP_on'][Opt_Result.index[1]]
         
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
            Result_Heat_End['Aux Gasbrenner'][Result_Heat_End.index[timestep]] \
                    = Opt_Result['P_aux_th'][Opt_Result.index[0]]                	                                                                                          
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
            Result_CHP_End['CHP self'][Result_CHP_End.index[timestep]] \
                     = Opt_Result['P_CHP_el_sc'][Opt_Result.index[0]] 
            # PV
            #Result_PV_End['PV'][Result_PV_End.index[timestep]] \
            #        = Opt_Result['P_PV'][Opt_Result.index[0]]                	                                            
            Result_PV_End['PV selfcon'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_sc'][Opt_Result.index[0]]
         #                 +CorrTerms['CorrPVsc']                	                                            
            Result_PV_End['PV Grid export'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_exp'][Opt_Result.index[0]]
         #                 +CorrTerms['CorrPVexp']
            Result_PV_End['PV Summe'][Result_PV_End.index[timestep]] \
                    = Opt_Result['P_PV_exp'][Opt_Result.index[0]]+\
                      Opt_Result['P_PV_sc'][Opt_Result.index[0]]
         #                 +CorrTerms['CorrPVexp']+\
         #                +CorrTerms['CorrPVsc']                	                                            

    return Result_PV_End, Result_CHP_End, Result_TES_End, Result_Heat_End,\
        Result_Grid_End, Result_BAT_End