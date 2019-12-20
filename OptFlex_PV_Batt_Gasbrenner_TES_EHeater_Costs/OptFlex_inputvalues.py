# -*- coding: utf-8 -*-
"""
Created on Thu May 07 12:44:54 2015
Überarbeitet und Validiert von Tkneiske Sep2015
26.10.2015 Output in csv-File 

@author: tcantillO; tkneiske
"""

import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import pandas as pd

def inputvalues_VDE_EFH(Delta_t,  TimeStepSize,year_stamps):          
 
     # ---------------------------------------------    
     # Load vector inserted by tkneiske Sep2015    
     # ---------------------------------------------    
     # --- INPUT File adds thermnal and DHW--- take half each --- please change!!!
     QLoad=sio.loadmat('../INPUT/EFH_'+TimeStepSize+'.mat')['QLoad']
     ELoad=sio.loadmat('../INPUT/EFH_'+TimeStepSize+'.mat')['ELoad']
     #----- same as pandas dataframe
     ELoad_df = pd.DataFrame(ELoad, index=year_stamps, columns=['ELoad'])
     QLoad1_df = pd.DataFrame(QLoad*0.5, index=year_stamps, columns=['QLoad1'])    
     QLoad2_df = pd.DataFrame(QLoad*0.5, index=year_stamps, columns=['QLoad2'])    
     LoadAll_TOT_df = pd.concat([ELoad_df, QLoad1_df, QLoad2_df], axis=1)
     #print (LoadAll_df['ELoad'].values
     P_Load_max=10
     # ---------------------------------------------     
     ######## there is no necessity to scale 
     # Scale PV profile
     #P_PV_ava_Tot = P_PV_ava_Tot*P_PV_max;
     # ---------------------------------------------     

     # ---------------------------------------------    
     # PV Profile    
     # ---------------------------------------------     
     # ------- Source: IWES roof 2013 10 min resolution, normalized to 1kWP, AC
     # ------------ 1day = 144
     P_PV_max = 3.2 #[kW]    # Normierung
     PV = np.load("../INPUT/PVAC2013Kassel_5clean.npy")  *  P_PV_max
     # --------------- convert to Pandas Dataframe with TimeIndex ------
     PV_TOT_df = pd.DataFrame(PV, index=year_stamps, columns=['PV 2013, Kassel, 10min'])
     
      
     # ---------------------------------------------    
     # Battery parameters according to Jan's simulatione For MFH
     # ---------------------------------------------    
     Cap_batt = 4 #[kWh]
 
     # Battery inverter 3-Phase SI 6.0H 6kVA. From datasheet
     P_batt_char_max = 3.3# [kW]
     P_batt_dis_max = 3.3#[kW]
     # ---------------------------------------------    
     # Experiment no Batt
     #P_batt_char_max = 0;# [kW] Has to be changed in Python
     #P_batt_dis_max = 0;#[kW]
     # PV-Inverter 1 X Tripower 9000 
     # ---------------------------------------------    

     # Taken from Aastha's Paper
     # 13.03.2015 self-discharge coefficient for Li-Ion battery
     # According to SYSPV-NS self-discharge is 3# per Month
#     eta_batt_sd = 0.03
     eta_batt_sd = (1-0.03/(24*30*60/Delta_t))
     eta_batt_char = 0.9
     eta_batt_dis = 0.92
     
     # Battery capacity in [%] for timeBIN Delta_t
     K_batt = (Delta_t/float(60))/float(Cap_batt)*100
     #  ( convert to hour /   4 kWh  ) * convert to %
 
     #K_batt = 0;#Experiment no Batt
     SOC_batt_max = 100
     SOC_batt_min = 20
     # Start always with maximum capacity --- Warum??
     SOC_batt_ini = 50

         # ---------------------------------------------    
     #  Auxiliary Gasbrenner
     # ---------------------------------------------    
     eta_aux = 1
     P_aux_th_min = 2.4#2.4# 2.4
     P_aux_th_max = 25.#20#2014.3# [kWth]
     Auxilary = pd.Series([eta_aux, P_aux_th_min, P_aux_th_max],\
     index=['eta_aux', 'P_aux_th_min', 'P_aux_th_max'])
     print ('----------------------------'     )
     print ('     Auxilary  parameter:')
     print ('----------------------------'     )
     print (Auxilary)

     #  ---------------------------------------------    
     # Electrical Boiler (Heizstab ?) Diego:Arbitrary chosen
     # ---------------------------------------------    
     eta_eheater = 1
     P_eheater_min = 0#[kWth] ######11.05.2011 2
     P_eheater_max = 2#2 ######11.05.2011 6
     
     EHeater = pd.Series([eta_eheater, P_eheater_min, P_eheater_max],\
     index=['eta_eheater', 'P_eheater_min', 'P_eheater_max'])
     print ('----------------------------'     )
     print ('            EHeater:')
     print ('----------------------------'     )
     print (EHeater)

     # ---------------------------------------------    
     # Parameter for the Thermal Energy Storage
     # ---------------------------------------------    
     Vol_S = 300# volume of the storage in [Liter]
     Vol_S = Vol_S/float(1000)# volumen of the storage in [m^3] 
     #NOTE: float is need for a float output in divisions (not integer)
     delta_T_S = 20# Temperature change in storage in [K] (see Thomas 2007 and TU Dortmund)
     Water_c = 4.18/float(3600)# water heat capacity in [kWh/(kg*K)]
     Water_dens = 990# Water density [kg/m^3]
     Cap_TES = Vol_S*Water_dens*Water_c*delta_T_S# Capacity of the storage in [kWh] 
     SOC_TES_max = 100# T_upp = 80 °C & T_dhw = 60 °C
     SOC_TES_min = 0# T_upp = 60 °C & T_dhw = 60 °C
     #Start always with maximum capacity
     SOC_TES_ini = 10
     K_TES = ((Delta_t/float(60))/Cap_TES)*100
 
     # ---------------------------------------------    
     # According to Vaillant data-sheet stanby losses for TES are 
     # 300 liter: 1.9 kWh/24h
     # 500 liter: 2.6 kWh/24h
     # ---------------------------------------------    
     StandbyTES=1.9
     if Vol_S == 1.0:
         StandbyTES = 1.9/Cap_TES# kWh/d
     elif Vol_S == 0.5:
         StandbyTES = 2.6/Cap_TES # kWh/d
          
     eta_TES_sd = 1 - StandbyTES/(24*60/Delta_t)
     # Same as battery
     eta_TES_char = 0.9
     eta_TES_dis = 0.92
             
     ThermalStorage = pd.Series([Vol_S, delta_T_S, Water_c, Water_dens, Cap_TES,\
     SOC_TES_max, SOC_TES_min, SOC_TES_ini, K_TES, StandbyTES, eta_TES_sd, \
     eta_TES_char, eta_TES_dis], \
     index=['Vol_S', 'delta_T_S', 'Water_c', 'Water_dens', 'Cap_TES',\
     'SOC_TES_max', 'SOC_TES_min', 'SOC_TES_ini', 'K_TES', 'StandbyTES',\
     'eta_TES_sd', 'eta_TES_char', 'eta_TES_dis'])
     print ('----------------------------')
     print ('  Thermal Storage Parameter:')
     print ('----------------------------')
     print (ThermalStorage)
     
     Battery = pd.Series([eta_batt_sd,eta_batt_char,eta_batt_dis ,K_batt, P_batt_char_max ,\
     P_batt_dis_max,SOC_batt_ini, Cap_batt, SOC_batt_max, SOC_batt_min], \
     index=['eta_batt_sd','eta_batt_char','eta_batt_dis' ,'K_batt', 'P_batt_char_max' ,\
     'P_batt_dis_max','SOC_batt_ini', 'Cap_batt', 'SOC_batt_max', 'SOC_batt_min'])
     print ('----------------------------')
     print ('     Battery parameter:')
     print ('----------------------------')
     print (Battery)
     print ('----------------------------')
     print ('     Load and PV:           ')
     print ('----------------------------')
     print ('P_PV_max:', P_PV_max)
     print ('P_Load_max:', P_Load_max)
                                     
     # ---------------------------------------------    
     #       Kosten 
     # ---------------------------------------------                                            
    # Parameter for the cost function have to be in vector form
    #28.01.2015
    # PV Feed-in Tariff in Germany for 2015
    # Inbetriebnahme im Januar 205 - Dachanlage auf Wohngebäuden - bis 10 kWp
    # Einspeisevergütung = 12.56 Cent/kWh = 0.1256 EUR/kWh
    # ---------------------------------------------     
     C_PV_FIT = 0.1256
    # C_PV_FIT = 0;#17.02.2015 Experiment no FI14.03.2011 22:20T
     #C_PV_FIT = C_PV_FIT*np.ones((Np,1))
     C_PV_eig = 0
     # CHP Feed-in Tariff 
     # Nach KWK-Gesetz
     # EV_KWK = Üblicher Preis + KWK-Zuschlag + Vermiedene Netzkosten
     # Üblicher Preis: an der Leipziger Strombörse EEX erzielten
     # durchschnittlichen Preis des Baseload-Stroms des vorangegangenen Quartals
     # (KWK-Index)
     # ---------------------------------------------    
     # KWK-Index von Q4/204 für Einspeisung in Q1/2015 = 3.482 Cent/kWh =
     # 0.03482 EUR/kWh
     # ---------------------------------------------    
     C_KWK_Index = 0.03482
     # KWK-Zuschlag (Stand Okt. 2014) = 5.41 Cent/kWh = 0.0541 EUR/kWh     
     C_KWK_Zus = 0.0541
     # C_KWK_Zus = 0;#17.02.2015 Experiment no FIT  
     # vermiedene Netzkosten
     # In der Praxis werden 0.4 bis 1.5 Cent pro Kilowattstunde an vermiedenen
     # Netznutzungsentgelten vergütet
     C_KWK_Netznutz = 0.005 
     C_CHP_FIT = (C_KWK_Index + C_KWK_Zus + C_KWK_Netznutz)#
     # For CHP self-consumption 
     C_CHP_ex = C_KWK_Zus#*np.ones((Np,1));
     # C_CHP_FIT = 0;#Experiment no FIT
     #C_CHP_FIT = C_CHP_FIT# *np.ones((Np,1))
 
     # Verivox Verbraucherpreisindex Gas
     # Durchschnittlicher Heizgaspreis in Cent pro kWh (brutto) 2014
     # bei einem Jahresverbrauch von 20.000 kWh = 6.52 Cent/kWh = 0.0652 EUR/kWh
     C_gas = 0.0652#*np.ones((Np,1))
     # Verivox Verbraucherpreisindex Strom
     # Durchschnittlicher Haushaltsstrompreis in Cent pro kWh (brutto) 2014
     # bei einem Jahresverbrauch von 4.000 kWh = 28.38 Cent/kWh = 0.2838 EUR/kWh
     C_grid_el = 0.2838#*np.ones((Np,1))
     # Costs for cold start --> Input from Vaillant is required
     # here just an assumption 0.5 Cent/kWh = 0.005 EUR
     C_CHP_cs = 0.02#*np.ones((Np,1))
     
     Costs = pd.Series([C_CHP_FIT, C_CHP_ex, C_gas, C_grid_el, C_CHP_cs, C_PV_FIT, C_PV_eig],\
     index = ['C_CHP_FIT', 'C_CHP_ex', 'C_gas', 'C_grid_el', 'C_CHP_cs', 'C_PV_FIT', 'C_PV_eig'])
     print ('----------------------------')
     print ('       Kosten:')
     print ('----------------------------')
     print (Costs)

     PV_TOT_df.to_csv('Results\INPUTPV.csv')                        
     LoadAll_TOT_df.to_csv('Results\INPUTLoad.csv')                        
     Battery.to_csv('Results\ParameterBattery.csv') 
     Auxilary.to_csv('Results\Auxilary.csv')                       
     ThermalStorage.to_csv('Results\TES.csv')                       
     Costs.to_csv('Results\ParameterCosts.csv')                                        
                                     
     return PV_TOT_df, P_PV_max, P_Load_max, LoadAll_TOT_df, Battery, Auxilary,\
             ThermalStorage, EHeater, Costs
 
def inputvalues_LPG_EFH(Delta_t,  TimeStepSize,year_stamps):          
 
     print (" Use PV and Load from LPG ! ")
     #-------------------------------------------------  
     # SIMONS- StromWärmelastgenerator Mai 2017
     #-------------------------------------------------  
     Q_DHWLoad_SD = pd.read_pickle("../INPUT/dhw_SFH_Kassel_1970_14")     #df
     Q_SHLoad_SD = pd.read_pickle("../INPUT/sh_SFH_Kassel_1970_14")     #tuple
     E_Load_SD = pd.read_pickle("../INPUT/el_SFH_Kassel_1970_14")     #array-tuples
     print (Q_SHLoad_SD[0].shape)
 
     # ---- Running mean zur Beachtung der Trägheit des Gebäudes
     #N = 1  # Durchschnittszeitraum für Heizmittelwert
     #print (Q_DHWLoad_SD #[kW Durchschnitt pro 10 min bins]
     QLoad1_df = Q_DHWLoad_SD
     QLoad2_df = Q_SHLoad_SD[0]
     #QLoad2_df = running_mean(Q_SHLoad_SD[0].values, N)            running average
     #QLoad2_df = QLoad2_df.set_index(Q_SHLoad_SD[0].index)         Anpassung Indizes
  
     QLoad1_df.columns=['QLoad1']  
     QLoad2_df.columns=['QLoad2']
     #print (Q_SHLoad_SD[0] #[kW Durchschnitt pro 10 min bins]
     ELoad_SD = np.mean(E_Load_SD[0].reshape(-1,10),axis = 1)
     ELoad_df = pd.DataFrame(ELoad_SD, index=year_stamps, columns=['ELoad'])
          
     LoadAll_TOT_df = pd.concat([ELoad_df, QLoad1_df, QLoad2_df], axis=1)
     
     P_Load_max=10
     # ---------------------------------------------     
     ######## there is no necessity to scale 
     # Scale PV profile
     #P_PV_ava_Tot = P_PV_ava_Tot*P_PV_max;
     # ---------------------------------------------     
     
     # ---------------------------------------------    
     # PV Profile    
     # ---------------------------------------------     
     # ------- Source: IWES roof 2013 10 min resolution, normalized to 1kWP, AC
     # ------------ 1day = 144
     P_PV_max = 3.2 #[kW]    # Normierung
     PV = np.load("../INPUT/PVAC2013Kassel_5clean.npy")  *  P_PV_max
     # --------------- convert to Pandas Dataframe with TimeIndex ------
     PV_TOT_df = pd.DataFrame(PV, index=year_stamps, columns=['PV 2013, Kassel, 10min'])
     
      
     # ---------------------------------------------    
     # Battery parameters according to Jan's simulatione For MFH
     # ---------------------------------------------    
     Cap_batt = 4 #[kWh]
 
     # Battery inverter 3-Phase SI 6.0H 6kVA. From datasheet
     P_batt_char_max = 3.3# [kW]
     P_batt_dis_max = 3.3#[kW]
     # ---------------------------------------------    
     # Experiment no Batt
     #P_batt_char_max = 0;# [kW] Has to be changed in Python
     #P_batt_dis_max = 0;#[kW]
     # PV-Inverter 1 X Tripower 9000 
     # ---------------------------------------------    

     # Taken from Aastha's Paper
     # 13.03.2015 self-discharge coefficient for Li-Ion battery
     # According to SYSPV-NS self-discharge is 3# per Month
#     eta_batt_sd = 0.03
     eta_batt_sd = (1-0.03/(24*30*60/Delta_t))
     eta_batt_char = 0.9
     eta_batt_dis = 0.92
     
     # Battery capacity in [%] for timeBIN Delta_t
     K_batt = (Delta_t/float(60))/float(Cap_batt)*100
     #  ( convert to hour /   4 kWh  ) * convert to %
 
     #K_batt = 0;#Experiment no Batt
     SOC_batt_max = 100
     SOC_batt_min = 20
     # Start always with maximum capacity --- Warum??
     SOC_batt_ini = 50

    
     Battery = pd.Series([eta_batt_sd,eta_batt_char,eta_batt_dis ,K_batt, P_batt_char_max ,\
     P_batt_dis_max,SOC_batt_ini, Cap_batt, SOC_batt_max, SOC_batt_min], \
     index=['eta_batt_sd','eta_batt_char','eta_batt_dis' ,'K_batt', 'P_batt_char_max' ,\
     'P_batt_dis_max','SOC_batt_ini', 'Cap_batt', 'SOC_batt_max', 'SOC_batt_min'])
     print ('----------------------------')
     print ('     Battery parameter:')
     print ('----------------------------')
     print (Battery)
     print ('----------------------------')
     print ('     Load and PV:           ')
     print ('----------------------------')
     print ('P_PV_max:', P_PV_max)
     print ('P_Load_max:', P_Load_max)
                                     
         # ---------------------------------------------    
     #       Kosten 
     # ---------------------------------------------                                            
    # Parameter for the cost function have to be in vector form
    #28.01.2015
    # PV Feed-in Tariff in Germany for 2015
    # Inbetriebnahme im Januar 205 - Dachanlage auf Wohngebäuden - bis 10 kWp
    # Einspeisevergütung = 12.56 Cent/kWh = 0.1256 EUR/kWh
    # ---------------------------------------------     
     C_PV_FIT = 0.1256
    # C_PV_FIT = 0;#17.02.2015 Experiment no FI14.03.2011 22:20T
     #C_PV_FIT = C_PV_FIT*np.ones((Np,1))
     C_PV_eig = 0
     # CHP Feed-in Tariff 
     # Nach KWK-Gesetz
     # EV_KWK = Üblicher Preis + KWK-Zuschlag + Vermiedene Netzkosten
     # Üblicher Preis: an der Leipziger Strombörse EEX erzielten
     # durchschnittlichen Preis des Baseload-Stroms des vorangegangenen Quartals
     # (KWK-Index)
     # ---------------------------------------------    
     # KWK-Index von Q4/204 für Einspeisung in Q1/2015 = 3.482 Cent/kWh =
     # 0.03482 EUR/kWh
     # ---------------------------------------------    
     C_KWK_Index = 0.03482
     # KWK-Zuschlag (Stand Okt. 2014) = 5.41 Cent/kWh = 0.0541 EUR/kWh     
     C_KWK_Zus = 0.0541
     # C_KWK_Zus = 0;#17.02.2015 Experiment no FIT  
     # vermiedene Netzkosten
     # In der Praxis werden 0.4 bis 1.5 Cent pro Kilowattstunde an vermiedenen
     # Netznutzungsentgelten vergütet
     C_KWK_Netznutz = 0.005 
     C_CHP_FIT = (C_KWK_Index + C_KWK_Zus + C_KWK_Netznutz)#
     # For CHP self-consumption 
     C_CHP_ex = C_KWK_Zus#*np.ones((Np,1));
     # C_CHP_FIT = 0;#Experiment no FIT
     #C_CHP_FIT = C_CHP_FIT# *np.ones((Np,1))
 
     # Verivox Verbraucherpreisindex Gas
     # Durchschnittlicher Heizgaspreis in Cent pro kWh (brutto) 2014
     # bei einem Jahresverbrauch von 20.000 kWh = 6.52 Cent/kWh = 0.0652 EUR/kWh
     C_gas = 0.0652#*np.ones((Np,1))
     # Verivox Verbraucherpreisindex Strom
     # Durchschnittlicher Haushaltsstrompreis in Cent pro kWh (brutto) 2014
     # bei einem Jahresverbrauch von 4.000 kWh = 28.38 Cent/kWh = 0.2838 EUR/kWh
     C_grid_el = 0.2838#*np.ones((Np,1))
     # Costs for cold start --> Input from Vaillant is required
     # here just an assumption 0.5 Cent/kWh = 0.005 EUR
     C_CHP_cs = 0.02#*np.ones((Np,1))
     
     Costs = pd.Series([C_CHP_FIT, C_CHP_ex, C_gas, C_grid_el, C_CHP_cs, C_PV_FIT, C_PV_eig],\
     index = ['C_CHP_FIT', 'C_CHP_ex', 'C_gas', 'C_grid_el', 'C_CHP_cs', 'C_PV_FIT', 'C_PV_eig'])
     print ('----------------------------'   )
     print ('       Kosten:')
     print ('----------------------------'    )
     print (Costs)

     PV_TOT_df.to_csv('Results\INPUTPV.csv')                        
     LoadAll_TOT_df.to_csv('Results\INPUTLoad.csv')                        
     Battery.to_csv('Results\ParameterBattery.csv')                        
     Costs.to_csv('Results\ParameterCosts.csv')                                        
                                     
     return PV_TOT_df, P_PV_max, P_Load_max, LoadAll_TOT_df, Battery, Costs
 
   