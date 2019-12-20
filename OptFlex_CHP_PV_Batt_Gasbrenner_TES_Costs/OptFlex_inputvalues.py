# -*- coding: utf-8 -*
"""
Created on Thu May 07 12:44:54 2015
Überarbeitet und Validiert von Tkneiske Sep2015
CHPPV++
@author: tcantillO; tkneiske
"""

import numpy as np
#import scipy as sci
import scipy.io as sio
import matplotlib.pyplot as plt
import pandas as pd
import OptFlex_MPC as main
#import os


def inputvaluesDefault_MFH(Delta_t, TimeStepSize,year_stamps):          
 
     # ---------------------------------------------    
     # Battery 
     # ---------------------------------------------    
     Cap_batt =12./100.*60. #[kWh]  # Use 20% to 80% of total capacity 
     # Battery inverter 3-Phase SI 6.0H 6kVA. From datasheet
     P_batt_char_max = 3.3# [kW]
     P_batt_dis_max = 3.3#[kW]  
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
     SOC_batt_max = 100
     SOC_batt_min = 0
     SOC_batt_ini = 0.5#50
     Battery = pd.Series([eta_batt_sd,eta_batt_char,eta_batt_dis ,K_batt, P_batt_char_max ,\
     P_batt_dis_max,SOC_batt_ini, Cap_batt, SOC_batt_max, SOC_batt_min], \
     index=['eta_batt_sd','eta_batt_char','eta_batt_dis' ,'K_batt', 'P_batt_char_max' ,\
     'P_batt_dis_max','SOC_batt_ini', 'Cap_batt', 'SOC_batt_max', 'SOC_batt_min'])
     print '----------------------------'     
     print '     Battery parameter:'
     print '----------------------------'     
     print Battery
                            
     # ---------------------------------------------    
     #  Auxilary Gasbrenner
     # ---------------------------------------------    
     eta_aux = 1
     P_aux_th_min = 2.4
     P_aux_th_max = 50 # 14.3# [kWth] # musst be big enough
     Auxilary = pd.Series([eta_aux, P_aux_th_min, P_aux_th_max],\
     index=['eta_aux', 'P_aux_th_min', 'P_aux_th_max'])
     print '----------------------------'     
     print '     Auxilary  parameter:'
     print '----------------------------'     
     print Auxilary

     # ---------------------------------------------    
     # Thermal Energy Storage
     # ---------------------------------------------    
     Vol_S = 500# 500 volume of the storage in [Liter]
     Vol_S = Vol_S/float(1000)# volumen of the storage in [m^3] 
     #NOTE: float is need for a float output in divisions (not integer)
     delta_T_S = 20# Temperature change in storage in [K] (see Thomas 2007 and TU Dortmund)
     Water_c = 4.18/float(3600)# water heat capacity in [kWh/(kg*K)]
     Water_dens = 990# Water density [kg/m^3]
     Cap_TES = Vol_S*Water_dens*Water_c*delta_T_S# Capacity of the storage in [kWh] 
     SOC_TES_max = 100# T_upp = 80 °C & T_dhw = 60 °C
     SOC_TES_min = 0# T_upp = 60 °C & T_dhw = 60 °C
     #Start always with maximum capacity
     SOC_TES_ini = 0.5#50
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
     print '----------------------------'     
     print '  Thermal Storage Parameter:'
     print '----------------------------'     
     print ThermalStorage

     
     # ---------------------------------------------    
     #    CHP 
     # ---------------------------------------------    
#==============================================================================
#      ramp_CHP = (18.74 - 10.95)/(5.88-4.75)# [kW_fuel/min] What does this do?         
#      ramp_CHP = ramp_CHP*Delta_t#This goes to Pyomo
# #    Create scalar parameter for Pyomo Simulation
# #    Np_hrs = 12
# #    Np = Np_hrs*6# Prediction horizon in 10 min interval 
#      # ---------------------------------------------    
#      # 13.03.2015
#      # Considering also Control horizon Nc
#      # ---------------------------------------------    
#      Nc_hrs = 6
#      Nc = Nc_hrs*6 # Control horizon in 10 min interval
     P_CHP_gas_ini = 0     
     P_CHP_el_min = 1.5 # 1.5# P_el_min in [kW] according to datasheet ecoPower 3.0
     P_CHP_el_max = 4.7#  3.0
     eta_CHP_el = 0.263
     eta_CHP_th = 0.657# This value has to be saved
     b_CHP_on_ini = 0
     b_CHP_ini_1 = 0
     b_CHP_ini_2 = 0
     b_CHP_ini_3 = 0

     # Min. operation time for CHP
     #model.T_CHP_on = RangeSet(1,T_CHP_on[0])
     # At least 3 time steps
     #model.T_CHP_on = Param(model.I, initialize = 3)
     T_CHP_on = 3;  # 30 min
     T_CHP_off = 3; # 30 min
     
     CHP = pd.Series([P_CHP_gas_ini, P_CHP_el_min, P_CHP_el_max,\
     eta_CHP_el, eta_CHP_th, b_CHP_on_ini, b_CHP_ini_1,b_CHP_ini_2,b_CHP_ini_3, T_CHP_on, T_CHP_off],\
     index=['P_CHP_gas_ini', 'P_CHP_el_min', 'P_CHP_el_max',\
     'eta_CHP_el', 'eta_CHP_th', 'b_CHP_on_ini', 'b_CHP_ini_1','b_CHP_ini_2',\
     'b_CHP_ini_3', 'T_CHP_on', 'T_CHP_off'])

     print '----------------------------'     
     print '       CHP:'
     print '----------------------------'     
     print CHP

     # ---------------------------------------------    
     #       Kosten 
     # ---------------------------------------------    
     # Parameter for the cost function have to be in vector form
     #28.01.2015
     # PV Feed-in Tariff in Germany for 2015
     # Inbetriebnahme im Januar 205 - Dachanlage auf Wohngebäuden - bis 10 kWp
     # Einspeisevergütung = 12.56 Cent/kWh = 0.1256 EUR/kWh
     C_PV_FIT = 0.1256
     # C_PV_FIT = 0;#17.02.2015 Experiment no FI14.03.2011 22:20T
#     C_PV_FIT = C_PV_FIT*np.ones((Np,1))
     # ---------------------------------------------    
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
     C_CHP_FIT = (C_KWK_Index + C_KWK_Zus + C_KWK_Netznutz)
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
     
     Costs = pd.Series([C_PV_FIT, C_CHP_FIT, C_CHP_ex, C_gas, C_grid_el, C_CHP_cs],\
     index = ['C_PV_FIT','C_CHP_FIT', 'C_CHP_ex', 'C_gas', 'C_grid_el', 'C_CHP_cs'])
     print '----------------------------'     
     print '       Kosten:'
     print '----------------------------'      
     print Costs    
     
     # ---------------------------------------------    
      #       CO2 Emission Koeffizienten nach  climate change 2016
     # ---------------------------------------------    
     CO2_gas = 201   #  g-kWh^-1
     #deutscher Strommix 2015 
     CO2_grid = 587   #g-kWh^-1
     CO2_PV = 0 # g-kWh^-1
                   
     CO2 = pd.Series([CO2_gas,CO2_grid, CO2_PV],\
     index = ['CO2_gas','CO2_grid', 'CO2_PV'])
     print '----------------------------------'     
     print '       Co2 Emissionskoeffizienten:'
     print '----------------------------------'      
     print CO2         
     
     Battery.to_csv('OUTPUT\ParameterBattery_Default_MFH.csv')                        
     Costs.to_csv('OUTPUT\ParameterCosts_Default_MFH.csv')                                        
     CHP.to_csv('OUTPUT\ParameterCHP_Default_MFH.csv')      
     Auxilary.to_csv('OUTPUT\ParameterAux_Default_MFH.csv')   
     ThermalStorage.to_csv('OUTPUT\ParameterTES_Default_MFH.csv')        
     CO2.to_csv('OUTPUT\ParameterCO2_Default_MFH.csv')        

     return  Battery, Auxilary, ThermalStorage, CHP, Costs, CO2

        
def inputvaluesOHNE_Verg_MFH(Delta_t, TimeStepSize,year_stamps):          
   
     # ---------------------------------------------    
     # Battery      parameters according to Jan's simulatione For MFH (Diego)
     # ---------------------------------------------    
     Cap_batt =12./100.*60. #[kWh]  # Use 20% to 80% of total capacity
     # Battery inverter 3-Phase SI 6.0H 6kVA. From datasheet
     P_batt_char_max = 3.3# [kW]
     P_batt_dis_max = 3.3#[kW]  
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
     SOC_batt_max = 100
     SOC_batt_min = 0
     SOC_batt_ini = 0.5#50
     Battery = pd.Series([eta_batt_sd,eta_batt_char,eta_batt_dis ,K_batt, P_batt_char_max ,\
     P_batt_dis_max,SOC_batt_ini, Cap_batt, SOC_batt_max, SOC_batt_min], \
     index=['eta_batt_sd','eta_batt_char','eta_batt_dis' ,'K_batt', 'P_batt_char_max' ,\
     'P_batt_dis_max','SOC_batt_ini', 'Cap_batt', 'SOC_batt_max', 'SOC_batt_min'])
     print '----------------------------'     
     print '     Battery parameter:'
     print '----------------------------'     
     print Battery
                            
     # ---------------------------------------------    
     #  Auxiliry Gasbrenner
     # ---------------------------------------------    
     eta_aux = 1
     P_aux_th_min = 2.4
     P_aux_th_max = 50 # 14.3# [kWth] # musst be big enough
     Auxilary = pd.Series([eta_aux, P_aux_th_min, P_aux_th_max],\
     index=['eta_aux', 'P_aux_th_min', 'P_aux_th_max'])
     print '----------------------------'     
     print '     Auxilary  parameter:'
     print '----------------------------'     
     print Auxilary

     # ---------------------------------------------    
     # Parameter for the Thermal Energy Storage
     # ---------------------------------------------    
     Vol_S = 500# volume of the storage in [Liter]
     Vol_S = Vol_S/float(1000)# volumen of the storage in [m^3] 
     #NOTE: float is need for a float output in divisions (not integer)
     delta_T_S = 20# Temperature change in storage in [K] (see Thomas 2007 and TU Dortmund)
     Water_c = 4.18/float(3600)# water heat capacity in [kWh/(kg*K)]
     Water_dens = 990# Water density [kg/m^3]
     Cap_TES = Vol_S*Water_dens*Water_c*delta_T_S# Capacity of the storage in [kWh] 
     SOC_TES_max = 100# T_upp = 80 °C & T_dhw = 60 °C
     SOC_TES_min = 0# T_upp = 60 °C & T_dhw = 60 °C
     #Start always with maximum capacity
     SOC_TES_ini = 0.5#50
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
     print '----------------------------'     
     print '  Thermal Storage Parameter:'
     print '----------------------------'     
     print ThermalStorage

     
     # ---------------------------------------------    
     #    CHP 
     # ---------------------------------------------    
#==============================================================================
#      ramp_CHP = (18.74 - 10.95)/(5.88-4.75)# [kW_fuel/min] What does this do?         
#      ramp_CHP = ramp_CHP*Delta_t#This goes to Pyomo
# #    Create scalar parameter for Pyomo Simulation
# #    Np_hrs = 12
# #    Np = Np_hrs*6# Prediction horizon in 10 min interval 
#      # ---------------------------------------------    
#      # 13.03.2015
#      # Considering also Control horizon Nc
#      # ---------------------------------------------    
#      Nc_hrs = 6
#      Nc = Nc_hrs*6 # Control horizon in 10 min interval
     P_CHP_gas_ini = 0     
     P_CHP_el_min = 1.5 # 1.5# P_el_min in [kW] according to datasheet ecoPower 3.0
     P_CHP_el_max = 4.7#  3.0
     eta_CHP_el = 0.263
     eta_CHP_th = 0.657# This value has to be saved
     b_CHP_on_ini = 0
     b_CHP_ini_1 = 0
     b_CHP_ini_2 = 0
     b_CHP_ini_3 = 0

     # Min. operation time for CHP
     #model.T_CHP_on = RangeSet(1,T_CHP_on[0])
     # At least 3 time steps
     #model.T_CHP_on = Param(model.I, initialize = 3)
     T_CHP_on = 3;  # 30 min
     T_CHP_off = 3; # 30 min
     
     CHP = pd.Series([P_CHP_gas_ini, P_CHP_el_min, P_CHP_el_max,\
     eta_CHP_el, eta_CHP_th, b_CHP_on_ini, b_CHP_ini_1,b_CHP_ini_2,b_CHP_ini_3, T_CHP_on, T_CHP_off],\
     index=['P_CHP_gas_ini', 'P_CHP_el_min', 'P_CHP_el_max',\
     'eta_CHP_el', 'eta_CHP_th', 'b_CHP_on_ini', 'b_CHP_ini_1','b_CHP_ini_2',\
     'b_CHP_ini_3', 'T_CHP_on', 'T_CHP_off'])

     print '----------------------------'     
     print '       CHP:'
     print '----------------------------'     
     print CHP

     # ---------------------------------------------    
     #       Kosten 
     # ---------------------------------------------    
     # Parameter for the cost function have to be in vector form
     #28.01.2015
     # PV Feed-in Tariff in Germany for 2015
     # Inbetriebnahme im Januar 205 - Dachanlage auf Wohngebäuden - bis 10 kWp
     # Einspeisevergütung = 12.56 Cent/kWh = 0.1256 EUR/kWh
     C_PV_FIT = 0
 
#     C_PV_FIT = C_PV_FIT*np.ones((Np,1))
     # ---------------------------------------------    
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
#     C_KWK_Index = 0.03482
     # KWK-Zuschlag (Stand Okt. 2014) = 5.41 Cent/kWh = 0.0541 EUR/kWh     
 #    C_KWK_Zus = 0.0541

     # vermiedene Netzkosten
     # In der Praxis werden 0.4 bis 1.5 Cent pro Kilowattstunde an vermiedenen
     # Netznutzungsentgelten vergütet
#     C_KWK_Netznutz = 0.005 
     C_CHP_FIT = 0#(C_KWK_Index + C_KWK_Zus + C_KWK_Netznutz)
     # For CHP self-consumption 
     C_CHP_ex = 0#C_KWK_Zus#*np.ones((Np,1));
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
     
     Costs = pd.Series([C_PV_FIT, C_CHP_FIT, C_CHP_ex, C_gas, C_grid_el, C_CHP_cs],\
     index = ['C_PV_FIT','C_CHP_FIT', 'C_CHP_ex', 'C_gas', 'C_grid_el', 'C_CHP_cs'])
     print '----------------------------'     
     print '       Kosten:'
     print '----------------------------'     
     print Costs    
     
    # ---------------------------------------------    
      #       CO2 Emission Koeffizienten nach  climate change 2016
     # ---------------------------------------------    
     CO2_gas = 201   #  g-kWh^-1
     #deutscher Strommix 2015 
     CO2_grid = 587   #g-kWh^-1
     CO2_PV = 0 # g-kWh^-1
     CO2_PV = 60 # 50-60 g-kWh^-1
                   
     CO2 = pd.Series([CO2_gas,CO2_grid, CO2_PV],\
     index = ['CO2_gas','CO2_grid', 'CO2_PV'])
     print '----------------------------------'     
     print '       Co2 Emissionskoeffizienten:'
     print '----------------------------------'      
     print CO2         
     
     Battery.to_csv('OUTPUT\ParameterBattery_Default_MFH.csv')                        
     Costs.to_csv('OUTPUT\ParameterCosts_Default_MFH.csv')                                        
     CHP.to_csv('OUTPUT\ParameterCHP_Default_MFH.csv')      
     Auxilary.to_csv('OUTPUT\ParameterAux_Default_MFH.csv')   
     ThermalStorage.to_csv('OUTPUT\ParameterTES_Default_MFH.csv')        
     CO2.to_csv('OUTPUT\ParameterCO2_Default_MFH.csv')        

     return  Battery, Auxilary, ThermalStorage, CHP, Costs, CO2

def inputvaluesDefault_EFH(Delta_t, TimeStepSize,year_stamps):          
 
     # ---------------------------------------------    
     # Battery 
     # ---------------------------------------------    
     Cap_batt =4./100.*60. #[kWh]  # Use 20% to 80% of total capacity 
     # Battery inverter 3-Phase SI 6.0H 6kVA. From datasheet
     P_batt_char_max = 3.3# [kW]
     P_batt_dis_max = 3.3#[kW]  
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
     SOC_batt_max = 100
     SOC_batt_min = 0 
     SOC_batt_ini = 0.5#50
     Battery = pd.Series([eta_batt_sd,eta_batt_char,eta_batt_dis ,K_batt, P_batt_char_max ,\
     P_batt_dis_max,SOC_batt_ini, Cap_batt, SOC_batt_max, SOC_batt_min], \
     index=['eta_batt_sd','eta_batt_char','eta_batt_dis' ,'K_batt', 'P_batt_char_max' ,\
     'P_batt_dis_max','SOC_batt_ini', 'Cap_batt', 'SOC_batt_max', 'SOC_batt_min'])
     print '----------------------------'     
     print '     Battery parameter:'
     print '----------------------------'     
     print Battery
                            
     # ---------------------------------------------    
     #  Auxiliry Gasbrenner
     # ---------------------------------------------    
     eta_aux = 1
     P_aux_th_min = 2.4
     P_aux_th_max = 50 # 14.3# [kWth] # musst be big enough
     
    
     Auxilary = pd.Series([eta_aux, P_aux_th_min, P_aux_th_max],\
     index=['eta_aux', 'P_aux_th_min', 'P_aux_th_max'])
     print '----------------------------'     
     print '     Auxilary  parameter:'
     print '----------------------------'     
     print Auxilary

     # ---------------------------------------------    
     # Thermal Energy Storage
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
     SOC_TES_ini = 0.5#50
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
     print '----------------------------'     
     print '  Thermal Storage Parameter:'
     print '----------------------------'     
     print ThermalStorage

     
     # ---------------------------------------------    
     #    CHP 
     # ---------------------------------------------    
#==============================================================================
#      ramp_CHP = (18.74 - 10.95)/(5.88-4.75)# [kW_fuel/min] What does this do?         
#      ramp_CHP = ramp_CHP*Delta_t#This goes to Pyomo
# #    Create scalar parameter for Pyomo Simulation
# #    Np_hrs = 12
# #    Np = Np_hrs*6# Prediction horizon in 10 min interval 
#      # ---------------------------------------------    
#      # 13.03.2015
#      # Considering also Control horizon Nc
#      # ---------------------------------------------    
#      Nc_hrs = 6
#      Nc = Nc_hrs*6 # Control horizon in 10 min interval
     P_CHP_gas_ini = 0     
     P_CHP_el_min = 0 # 1.5# P_el_min in [kW] according to datasheet ecoPower 3.0
     P_CHP_el_max = 1.0#  3.0
     eta_CHP_el = 0.263
     eta_CHP_th = 0.657# This value has to be saved
     b_CHP_on_ini = 0
     b_CHP_ini_1 = 0
     b_CHP_ini_2 = 0
     b_CHP_ini_3 = 0
     # Min. operation time for CHP
     #model.T_CHP_on = RangeSet(1,T_CHP_on[0])
     # At least 3 time steps
     #model.T_CHP_on = Param(model.I, initialize = 3)
     T_CHP_on = 3;  # 30 min
     T_CHP_off = 3; # 30 min
     
     CHP = pd.Series([P_CHP_gas_ini, P_CHP_el_min, P_CHP_el_max,\
     eta_CHP_el, eta_CHP_th, b_CHP_on_ini, b_CHP_ini_1,b_CHP_ini_2,b_CHP_ini_3, T_CHP_on, T_CHP_off],\
     index=['P_CHP_gas_ini', 'P_CHP_el_min', 'P_CHP_el_max',\
     'eta_CHP_el', 'eta_CHP_th', 'b_CHP_on_ini', 'b_CHP_ini_1','b_CHP_ini_2',\
     'b_CHP_ini_3', 'T_CHP_on', 'T_CHP_off'])

     print '----------------------------'     
     print '       CHP:'
     print '----------------------------'     
     print CHP

     # ---------------------------------------------    
     #       Kosten 
     # ---------------------------------------------    
     # Parameter for the cost function have to be in vector form
     #28.01.2015
     # PV Feed-in Tariff in Germany for 2015
     # Inbetriebnahme im Januar 205 - Dachanlage auf Wohngebäuden - bis 10 kWp
     # Einspeisevergütung = 12.56 Cent/kWh = 0.1256 EUR/kWh
     C_PV_FIT = 0.1256
     # C_PV_FIT = 0;#17.02.2015 Experiment no FI14.03.2011 22:20T
#     C_PV_FIT = C_PV_FIT*np.ones((Np,1))
     # ---------------------------------------------    
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
     C_CHP_FIT = (C_KWK_Index + C_KWK_Zus + C_KWK_Netznutz)
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
     
     Costs = pd.Series([C_PV_FIT, C_CHP_FIT, C_CHP_ex, C_gas, C_grid_el, C_CHP_cs],\
     index = ['C_PV_FIT','C_CHP_FIT', 'C_CHP_ex', 'C_gas', 'C_grid_el', 'C_CHP_cs'])
     print '----------------------------'     
     print '       Kosten:'
     print '----------------------------'      
     print Costs    
     # ---------------------------------------------    
      #       CO2 Emission Koeffizienten nach  climate change 2016
     # ---------------------------------------------    
     CO2_gas = 201   #  g-kWh^-1
     #deutscher Strommix 2015 
     CO2_grid = 587   #g-kWh^-1
     CO2_PV = 0 # g-kWh^-1
     CO2_PV = 60 # 50-60 g-kWh^-1
                   
     CO2 = pd.Series([CO2_gas,CO2_grid, CO2_PV],\
     index = ['CO2_gas','CO2_grid', 'CO2_PV'])
     print '----------------------------------'     
     print '       Co2 Emissionskoeffizienten:'
     print '----------------------------------'      
     print CO2         
     
  
     Battery.to_csv('OUTPUT\ParameterBattery_EFH_default.csv')                        
     Costs.to_csv('OUTPUT\ParameterCosts_EFH_default.csv')                                        
     CHP.to_csv('OUTPUT\ParameterCHP_EFH_default.csv')      
     Auxilary.to_csv('OUTPUT\ParameterAux_EFH_default.csv')   
     ThermalStorage.to_csv('OUTPUT\ParameterTES_EFH_default.csv')        
     CO2.to_csv('OUTPUT\ParameterCO2_Default_EFH.csv')        

     return  Battery, Auxilary, ThermalStorage, CHP, Costs, CO2

def inputvaluesDefault_EFH_Lab(Delta_t, TimeStepSize,year_stamps):          
 
     # ---------------------------------------------    
     # Battery 
     # ---------------------------------------------    
     Cap_batt = 6.3#100.*80.# --> 5.04 kWh
     # Battery inverter 3-Phase SI 6.0H 6kVA. From datasheet
     P_batt_char_max = 3.3# [kW]
     P_batt_dis_max = 3.3#[kW]  
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
     SOC_batt_max = 100
     SOC_batt_min = 20 
     SOC_batt_ini = 100 #0.5#50
     Battery = pd.Series([eta_batt_sd,eta_batt_char,eta_batt_dis ,K_batt, P_batt_char_max ,\
     P_batt_dis_max,SOC_batt_ini, Cap_batt, SOC_batt_max, SOC_batt_min], \
     index=['eta_batt_sd','eta_batt_char','eta_batt_dis' ,'K_batt', 'P_batt_char_max' ,\
     'P_batt_dis_max','SOC_batt_ini', 'Cap_batt', 'SOC_batt_max', 'SOC_batt_min'])
     print '----------------------------'     
     print '----------------------------'     
     print ' ------ LABOR ----------------'
     print '----------------------------'     
     print '----------------------------'     
     print '     Battery parameter:'
     print '----------------------------'     
     print Battery
                            
     # ---------------------------------------------    
     #  Auxiliry Gasbrenner
     # ---------------------------------------------    
     eta_aux = 1
     #--->P_aux_th_min = 2.4
     #--->P_aux_th_max = 50 # 14.3# [kWth] # musst be big enough
     
     #-------LABOR--------
     #P_aux_th_min = 20.     
     P_aux_th_min = 0.
     P_aux_th_max = 30. # 14.3# [kWth] # musst be big enough
    
     Auxilary = pd.Series([eta_aux, P_aux_th_min, P_aux_th_max],\
     index=['eta_aux', 'P_aux_th_min', 'P_aux_th_max'])
     print '----------------------------'     
     print '     Auxilary  parameter:'
     print '----------------------------'     
     print Auxilary

     # ---------------------------------------------    
     # Thermal Energy Storage
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
     SOC_TES_ini = 100#0.5#50
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
     print '----------------------------'     
     print '  Thermal Storage Parameter:'
     print '----------------------------'     
     print ThermalStorage

     
     # ---------------------------------------------    
     #    CHP 
     # ---------------------------------------------    
#==============================================================================
#      ramp_CHP = (18.74 - 10.95)/(5.88-4.75)# [kW_fuel/min] What does this do?         
#      ramp_CHP = ramp_CHP*Delta_t#This goes to Pyomo
# #    Create scalar parameter for Pyomo Simulation
# #    Np_hrs = 12
# #    Np = Np_hrs*6# Prediction horizon in 10 min interval 
#      # ---------------------------------------------    
#      # 13.03.2015
#      # Considering also Control horizon Nc
#      # ---------------------------------------------    
#      Nc_hrs = 6
#      Nc = Nc_hrs*6 # Control horizon in 10 min interval
     P_CHP_gas_ini = 0     
     P_CHP_el_min = 0 # 1.5# P_el_min in [kW] according to datasheet ecoPower 3.0
     P_CHP_el_max = 1.0#  3.0
     eta_CHP_el = 0.263
     eta_CHP_th = 0.657# This value has to be saved
     b_CHP_on_ini = 0
     b_CHP_ini_1 = 0
     b_CHP_ini_2 = 0
     b_CHP_ini_3 = 0
     # Min. operation time for CHP
     #model.T_CHP_on = RangeSet(1,T_CHP_on[0])
     # At least 3 time steps
     #model.T_CHP_on = Param(model.I, initialize = 3)
     T_CHP_on = 3;  # 30 min
     T_CHP_off = 3; # 30 min
     
     CHP = pd.Series([P_CHP_gas_ini, P_CHP_el_min, P_CHP_el_max,\
     eta_CHP_el, eta_CHP_th, b_CHP_on_ini, b_CHP_ini_1,b_CHP_ini_2,b_CHP_ini_3, T_CHP_on, T_CHP_off],\
     index=['P_CHP_gas_ini', 'P_CHP_el_min', 'P_CHP_el_max',\
     'eta_CHP_el', 'eta_CHP_th', 'b_CHP_on_ini', 'b_CHP_ini_1','b_CHP_ini_2',\
     'b_CHP_ini_3', 'T_CHP_on', 'T_CHP_off'])

     print '----------------------------'     
     print '       CHP:'
     print '----------------------------'     
     print CHP

     # ---------------------------------------------    
     #       Kosten 
     # ---------------------------------------------    
     # Parameter for the cost function have to be in vector form
     #28.01.2015
     # PV Feed-in Tariff in Germany for 2015
     # Inbetriebnahme im Januar 205 - Dachanlage auf Wohngebäuden - bis 10 kWp
     # Einspeisevergütung = 12.56 Cent/kWh = 0.1256 EUR/kWh
     C_PV_FIT = 0.1256
     # C_PV_FIT = 0;#17.02.2015 Experiment no FI14.03.2011 22:20T
#     C_PV_FIT = C_PV_FIT*np.ones((Np,1))
     # ---------------------------------------------    
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
     C_CHP_FIT = (C_KWK_Index + C_KWK_Zus + C_KWK_Netznutz)
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
     
     Costs = pd.Series([C_PV_FIT, C_CHP_FIT, C_CHP_ex, C_gas, C_grid_el, C_CHP_cs],\
     index = ['C_PV_FIT','C_CHP_FIT', 'C_CHP_ex', 'C_gas', 'C_grid_el', 'C_CHP_cs'])
     print '----------------------------'     
     print '       Kosten:'
     print '----------------------------'      
     print Costs    
     # ---------------------------------------------    
      #       CO2 Emission Koeffizienten nach  climate change 2016
     # ---------------------------------------------    
     CO2_gas = 201   #  g-kWh^-1
     #deutscher Strommix 2015 
     CO2_grid = 587   #g-kWh^-1
     CO2_PV = 0 # g-kWh^-1
     CO2_PV = 60 # 50-60 g-kWh^-1
                   
     CO2 = pd.Series([CO2_gas,CO2_grid, CO2_PV],\
     index = ['CO2_gas','CO2_grid', 'CO2_PV'])
     print '----------------------------------'     
     print '       Co2 Emissionskoeffizienten:'
     print '----------------------------------'      
     print CO2         
     
  
     Battery.to_csv('OUTPUT\ParameterBattery_EFH_default.csv')                        
     Costs.to_csv('OUTPUT\ParameterCosts_EFH_default.csv')                                        
     CHP.to_csv('OUTPUT\ParameterCHP_EFH_default.csv')      
     Auxilary.to_csv('OUTPUT\ParameterAux_EFH_default.csv')   
     ThermalStorage.to_csv('OUTPUT\ParameterTES_EFH_default.csv')        
     CO2.to_csv('OUTPUT\ParameterCO2_Default_EFH.csv')        

     return  Battery, Auxilary, ThermalStorage, CHP, Costs, CO2       
def inputvaluesOHNE_Verg_EFH(Delta_t, TimeStepSize,year_stamps):          
   
     # ---------------------------------------------    
     # Battery      parameters according to Jan's simulatione For MFH (Diego)
     # ---------------------------------------------    
     Cap_batt =4./100.*60. #[kWh]  # Use 20% to 80% of total capacity
     # Battery inverter 3-Phase SI 6.0H 6kVA. From datasheet
     P_batt_char_max = 3.3# [kW]
     P_batt_dis_max = 3.3#[kW]  
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
     SOC_batt_max = 100
     SOC_batt_min = 0
     SOC_batt_ini = 0.5#50
     Battery = pd.Series([eta_batt_sd,eta_batt_char,eta_batt_dis ,K_batt, P_batt_char_max ,\
     P_batt_dis_max,SOC_batt_ini, Cap_batt, SOC_batt_max, SOC_batt_min], \
     index=['eta_batt_sd','eta_batt_char','eta_batt_dis' ,'K_batt', 'P_batt_char_max' ,\
     'P_batt_dis_max','SOC_batt_ini', 'Cap_batt', 'SOC_batt_max', 'SOC_batt_min'])
     print '----------------------------'     
     print '     Battery parameter:'
     print '----------------------------'     
     print Battery
                            
     # ---------------------------------------------    
     #  Auxiliry Gasbrenner
     # ---------------------------------------------    
     eta_aux = 1
     P_aux_th_min = 2.4
     P_aux_th_max = 50 # 14.3# [kWth] # musst be big enough
     Auxilary = pd.Series([eta_aux, P_aux_th_min, P_aux_th_max],\
     index=['eta_aux', 'P_aux_th_min', 'P_aux_th_max'])
     print '----------------------------'     
     print '     Auxilary  parameter:'
     print '----------------------------'     
     print Auxilary

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
     SOC_TES_ini = 0.5#50
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
     print '----------------------------'     
     print '  Thermal Storage Parameter:'
     print '----------------------------'     
     print ThermalStorage

     
     # ---------------------------------------------    
     #    CHP 
     # ---------------------------------------------    
#==============================================================================
#      ramp_CHP = (18.74 - 10.95)/(5.88-4.75)# [kW_fuel/min] What does this do?         
#      ramp_CHP = ramp_CHP*Delta_t#This goes to Pyomo
# #    Create scalar parameter for Pyomo Simulation
# #    Np_hrs = 12
# #    Np = Np_hrs*6# Prediction horizon in 10 min interval 
#      # ---------------------------------------------    
#      # 13.03.2015
#      # Considering also Control horizon Nc
#      # ---------------------------------------------    
#      Nc_hrs = 6
#      Nc = Nc_hrs*6 # Control horizon in 10 min interval
     P_CHP_gas_ini = 0     
     P_CHP_el_min = 0 # 1.5# P_el_min in [kW] according to datasheet ecoPower 3.0
     P_CHP_el_max = 1.0#  3.0
     eta_CHP_el = 0.263
     eta_CHP_th = 0.657# This value has to be saved
     b_CHP_on_ini = 0
     b_CHP_ini_1 = 0
     b_CHP_ini_2 = 0
     b_CHP_ini_3 = 0
     # Min. operation time for CHP
     #model.T_CHP_on = RangeSet(1,T_CHP_on[0])
     # At least 3 time steps
     #model.T_CHP_on = Param(model.I, initialize = 3)
     T_CHP_on = 3;  # 30 min
     T_CHP_off = 3; # 30 min
     
     CHP = pd.Series([P_CHP_gas_ini, P_CHP_el_min, P_CHP_el_max,\
     eta_CHP_el, eta_CHP_th, b_CHP_on_ini, b_CHP_ini_1,b_CHP_ini_2,b_CHP_ini_3, T_CHP_on, T_CHP_off],\
     index=['P_CHP_gas_ini', 'P_CHP_el_min', 'P_CHP_el_max',\
     'eta_CHP_el', 'eta_CHP_th', 'b_CHP_on_ini', 'b_CHP_ini_1','b_CHP_ini_2',\
     'b_CHP_ini_3', 'T_CHP_on', 'T_CHP_off'])

     print '----------------------------'     
     print '       CHP:'
     print '----------------------------'     
     print CHP

     # ---------------------------------------------    
     #       Kosten 
     # ---------------------------------------------    
     # Parameter for the cost function have to be in vector form
     #28.01.2015
     # PV Feed-in Tariff in Germany for 2015
     # Inbetriebnahme im Januar 205 - Dachanlage auf Wohngebäuden - bis 10 kWp
     # Einspeisevergütung = 12.56 Cent/kWh = 0.1256 EUR/kWh
     C_PV_FIT = 0
 
#     C_PV_FIT = C_PV_FIT*np.ones((Np,1))
     # ---------------------------------------------    
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
#     C_KWK_Index = 0.03482
     # KWK-Zuschlag (Stand Okt. 2014) = 5.41 Cent/kWh = 0.0541 EUR/kWh     
 #    C_KWK_Zus = 0.0541

     # vermiedene Netzkosten
     # In der Praxis werden 0.4 bis 1.5 Cent pro Kilowattstunde an vermiedenen
     # Netznutzungsentgelten vergütet
#     C_KWK_Netznutz = 0.005 
     C_CHP_FIT = 0#(C_KWK_Index + C_KWK_Zus + C_KWK_Netznutz)
     # For CHP self-consumption 
     C_CHP_ex = 0#C_KWK_Zus#*np.ones((Np,1));
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
     
     Costs = pd.Series([C_PV_FIT, C_CHP_FIT, C_CHP_ex, C_gas, C_grid_el, C_CHP_cs],\
     index = ['C_PV_FIT','C_CHP_FIT', 'C_CHP_ex', 'C_gas', 'C_grid_el', 'C_CHP_cs'])
     print '----------------------------'     
     print '       Kosten:'
     print '----------------------------'     
     print Costs    
     
     # ---------------------------------------------    
      #       CO2 Emission Koeffizienten nach  climate change 2016
     # ---------------------------------------------    
     CO2_gas = 201   #  g-kWh^-1
     #deutscher Strommix 2015 
     CO2_grid = 587   #g-kWh^-1
     CO2_PV = 0 # g-kWh^-1
                   
     CO2 = pd.Series([CO2_gas,CO2_grid, CO2_PV],\
     index = ['CO2_gas','CO2_grid', 'CO2_PV'])
     print '----------------------------------'     
     print '       Co2 Emissionskoeffizienten:'
     print '----------------------------------'      
     print CO2         
    
     Battery.to_csv('OUTPUT\ParameterBattery_ohneFIT_EFH.csv')                        
     Costs.to_csv('OUTPUT\ParameterCosts_ohneFIT_EFH.csv')                                        
     CHP.to_csv('OUTPUT\ParameterCHP_ohneFIT_EFH.csv')      
     Auxilary.to_csv('OUTPUT\ParameterAux_ohneFIT_EFH.csv')   
     ThermalStorage.to_csv('OUTPUT\ParameterTES_ohneFIT_EFH.csv')        
     CO2.to_csv('OUTPUT\ParameterCO2_Default_EFH.csv')        

     return  Battery, Auxilary, ThermalStorage, CHP, Costs, CO2


def Input_PV_Load_VDE_MFH(Delta_t, TimeStepSize,year_stamps):
     print " Use PV and Load from VDE Norm ! "
    
     # ---------------------------------------------    
     # Load vector inserted by tkneiske Sep2015    
     # ---------------------------------------------    

     # ---- READ Datafiles VDI Simon drauz, 10.08.2016 TMK   
     LoadHDFstore = pd.HDFStore("INPUT/energy_demand_VDI4655_MFH_2013_Kassel_57157.92kWh.hdf5")
     #Load_DF = LoadHDFstore.energy_demand # 15 min resolution
     Load_DF_res = LoadHDFstore.energy_demand_resample        
     LoadHDFstore.close
     
     #Load_DF.plot(title = "MFH energy demand")
     #Load_DF_res.plot(title = "MFH energy demand reample")
     ELoad_df = Load_DF_res["W_TT_t"] 
     QLoad1_df = Load_DF_res['Q_DHW_TT_t']
     QLoad2_df = Load_DF_res['Q_SH_TT_t']
  
     LoadAll_TOT_df = pd.concat([ELoad_df, QLoad1_df, QLoad2_df], axis=1)
     LoadAll_TOT_df.columns=["ELoad", "QLoad1", "QLoad2"]
         
     P_Load_max=10
     print '----------------------------'     
     print '     Load and PV:           '
     print '----------------------------'     
     print 'P_Load_max:', P_Load_max
     
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
     P_PV_max = 12 #[kW]    # Normierung
     PV = np.load("INPUT/PVAC2013Kassel_5clean.npy")  *  P_PV_max
     # --------------- convert to Pandas Dataframe with TimeIndex ------
     PV_TOT_df = pd.DataFrame(PV, index=year_stamps, columns=['PV 2013, Kassel, 10min'])
     print 'P_PV_max:', P_PV_max
     
     PV_TOT_df.to_csv('OUTPUT\INPUTPV_Kassel2013_MFH.csv')                        
     LoadAll_TOT_df.to_csv('OUTPUT\INPUTLoad_VDI4655_MFH.csv')                        
          
     return PV_TOT_df, LoadAll_TOT_df ,P_Load_max, P_PV_max,   


def Input_PV_Load_LPG_MFH(Delta_t, TimeStepSize,year_stamps):
     
     print " Use PV and Load from LPG ! "
     #-------------------------------------------------  
     # SIMONS- StromWärmelastgenerator Mai 2017
     #-------------------------------------------------  
     Q_DHWLoad_SD = pd.read_pickle("INPUT/dhw_MFH_Kassel_1980_14")     #df
     Q_SHLoad_SD = pd.read_pickle("INPUT/sh_MFH_Kassel_1980_14")     #tuple
     E_Load_SD = pd.read_pickle("INPUT/el_MFH_Kassel_1980_14")     #array-tuples            
     print Q_SHLoad_SD[0].shape
 

     # ---- Running mean zur Beachtung der Trägheit des Gebäudes
     #N = 1  # Durchschnittszeitraum für Heizmittelwert
     #print Q_DHWLoad_SD #[kW Durchschnitt pro 10 min bins]
     QLoad1_df = Q_DHWLoad_SD
     QLoad2_df = Q_SHLoad_SD[0]
     #QLoad2_df = running_mean(Q_SHLoad_SD[0].values, N)            running average
     #QLoad2_df = QLoad2_df.set_index(Q_SHLoad_SD[0].index)         Anpassung Indizes
  
     QLoad1_df.columns=['QLoad1']  
     QLoad2_df.columns=['QLoad2']
     #print Q_SHLoad_SD[0] #[kW Durchschnitt pro 10 min bins]
     ELoad_SD = np.mean(E_Load_SD[0].reshape(-1,10),axis = 1)
     ELoad_df = pd.DataFrame(ELoad_SD, index=year_stamps, columns=['ELoad'])
         
     LoadAll_TOT_df = pd.concat([ELoad_df, QLoad1_df, QLoad2_df], axis=1)
     
     P_Load_max=10
     print '----------------------------'     
     print '     Load and PV:           '
     print '----------------------------'     
     print 'P_Load_max:', P_Load_max
     
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
     P_PV_max = 12 #[kW]    # Normierung
     PV = np.load("INPUT/PVAC2013Kassel_5clean.npy")  *  P_PV_max
     # --------------- convert to Pandas Dataframe with TimeIndex ------
     PV_TOT_df = pd.DataFrame(PV, index=year_stamps, columns=['PV 2013, Kassel, 10min'])
     print 'P_PV_max:', P_PV_max
     
     PV_TOT_df.to_csv('OUTPUT\INPUTPV_Kassel2013_MFH.csv')                        
     LoadAll_TOT_df.to_csv('OUTPUT\INPUTLoad_LPG_MFH.csv')                        
          
     return PV_TOT_df, LoadAll_TOT_df ,P_Load_max, P_PV_max,   

def Input_PV_Load_VDE_EFH(Delta_t, TimeStepSize,year_stamps, Nachbar):
     print " Use PV and Load from VDE Norm ! "
    
     # ---------------------------------------------    
     # Load vector inserted by tkneiske Sep2015    
     # ---------------------------------------------    
     # --- INPUT File adds thermnal and DHW--- take half each --- please change!!!
#     QLoad=sio.loadmat('INPUT/EFH_'+TimeStepSize+'.mat')['QLoad']
#     ELoad=sio.loadmat('INPUT/EFH_'+TimeStepSize+'.mat')['ELoad'] 
#     #----- same as pandas dataframe
#     ELoad_df = pd.DataFrame(ELoad, index=year_stamps, columns=['ELoad'])
#     QLoad1_df = pd.DataFrame(QLoad*0.5, index=year_stamps, columns=['QLoad1'])    
#     QLoad2_df = pd.DataFrame(QLoad*0.5, index=year_stamps, columns=['QLoad2'])    
#    
     # ---- READ Datafiles VDI Simon drauz, 10.08.2016 TMK   
     LoadHDFstore = pd.HDFStore("INPUT/energy_demand_VDI4655_SFH_2013_Kassel_16506.0kWh.hdf5")
    #  print LoadHDFstore
     #Load_DF = LoadHDFstore.energy_demand # 1 min Resolution
     Load_DF_res = LoadHDFstore.energy_demand_resample        
     LoadHDFstore.close
     #----- same as pandas dataframe   
     ELoad_df = Load_DF_res["W_TT_t"] 
     QLoad1_df = Load_DF_res['Q_DHW_TT_t']
     QLoad2_df = Load_DF_res['Q_SH_TT_t']
     # Load_DF.plot(title = "EFH energy demand")
     #  Load_DF_res.plot(title = "EFH energy demand reample")       
         
     if Nachbar == 'NachbarOn':  # Näherung Nachbar == KWK Besitzer Tanja Sept.2016
         LoadAll_TOT_df = pd.concat([ELoad_df, QLoad1_df*2., QLoad2_df*2.], axis=1)
     elif Nachbar == 'NachbarOff':         
        LoadAll_TOT_df = pd.concat([ELoad_df, QLoad1_df, QLoad2_df], axis=1)
     else:
        print 'ERROR: Inputvalues, Nachbar falsch !!!'         
     LoadAll_TOT_df.columns=["ELoad", "QLoad1", "QLoad2"]
     P_Load_max=10
     print '----------------------------'     
     print '     Load and PV:           '
     print '----------------------------'     
     print 'P_Load_max:', P_Load_max
     
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
     PV = np.load("INPUT/PVAC2013Kassel_5clean.npy")  *  P_PV_max
     # --------------- convert to Pandas Dataframe with TimeIndex ------
     PV_TOT_df = pd.DataFrame(PV, index=year_stamps, columns=['PV 2013, Kassel, 10min'])
     print 'P_PV_max:', P_PV_max
     
     PV_TOT_df.to_csv('OUTPUT\INPUTPV_Kassel2013_EFH.csv')                        
     LoadAll_TOT_df.to_csv('OUTPUT\INPUTLoad_VDI4655_EFH.csv')                        
          
     return PV_TOT_df, LoadAll_TOT_df ,P_Load_max, P_PV_max,   


def Input_PV_Load_LPG_EFH(Delta_t, TimeStepSize,year_stamps):
     
     print " Use PV and Load from LPG ! "
     #-------------------------------------------------  
     # SIMONS- StromWärmelastgenerator Mai 2017
     #-------------------------------------------------  
     Q_DHWLoad_SD = pd.read_pickle("INPUT/dhw_SFH_Kassel_1970_14")     #df
     Q_SHLoad_SD = pd.read_pickle("INPUT/sh_SFH_Kassel_1970_14")     #tuple
     E_Load_SD = pd.read_pickle("INPUT/el_SFH_Kassel_1970_14")     #array-tuples            
  #   Q_DHWLoad_SD = pd.read_pickle("INPUT/dhw")     #df
  #   Q_SHLoad_SD = pd.read_pickle("INPUT/sh")     #tuple
  #   E_Load_SD = pd.read_pickle("INPUT/el")     #array-tuples            
  #   print Q_SHLoad_SD[0].shape
 
     # ---- Running mean zur Beachtung der Trägheit des Gebäudes
     #N = 1  # Durchschnittszeitraum für Heizmittelwert
     #print Q_DHWLoad_SD #[kW Durchschnitt pro 10 min bins]
     QLoad1_df = Q_DHWLoad_SD
     QLoad2_df = Q_SHLoad_SD[0]
     #QLoad2_df = running_mean(Q_SHLoad_SD[0].values, N)            running average
     #QLoad2_df = QLoad2_df.set_index(Q_SHLoad_SD[0].index)         Anpassung Indizes
  
     QLoad1_df.columns=['QLoad1']  
     QLoad2_df.columns=['QLoad2']
     #print Q_SHLoad_SD[0] #[kW Durchschnitt pro 10 min bins]
     ELoad_SD = np.mean(E_Load_SD[0].reshape(-1,10),axis = 1)
     ELoad_df = pd.DataFrame(ELoad_SD, index=year_stamps, columns=['ELoad'])
     
    
     
     LoadAll_TOT_df = pd.concat([ELoad_df, QLoad1_df, QLoad2_df], axis=1)
     
     P_Load_max=10
     print '----------------------------'     
     print '     Load and PV:           '
     print '----------------------------'     
     print 'P_Load_max:', P_Load_max
     
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
     PV = np.load("INPUT/PVAC2013Kassel_5clean.npy")  *  P_PV_max
     # --------------- convert to Pandas Dataframe with TimeIndex ------
     PV_TOT_df = pd.DataFrame(PV, index=year_stamps, columns=['PV 2013, Kassel, 10min'])
     print 'P_PV_max:', P_PV_max
     
     PV_TOT_df.to_csv('OUTPUT\INPUTPV_Kassel2013_EFH.csv')                        
     LoadAll_TOT_df.to_csv('OUTPUT\INPUTLoad_LPG_EFH.csv')                        
          
     return PV_TOT_df, LoadAll_TOT_df ,P_Load_max, P_PV_max,   

def Input_PV_Load_LPG_Lab(Delta_t, TimeStepSize,year_stamps):
     
     print " Use PV and Load from LPG LABOR! "
     #-------------------------------------------------  
     # SIMONS- StromWärmelastgenerator Mai 2017
     #-------------------------------------------------  
  #   Q_DHWLoad_SD = pd.read_pickle("INPUT/dhw_SFH_Kassel_1970_14")     #df
  #   Q_SHLoad_SD = pd.read_pickle("INPUT/sh_SFH_Kassel_1970_14")     #tuple
  #   E_Load_SD = pd.read_pickle("INPUT/el_SFH_Kassel_1970_14")     #array-tuples            
  #   Q_DHWLoad_SD = pd.read_pickle("INPUT/dhw")     #df
  #   Q_SHLoad_SD = pd.read_pickle("INPUT/sh")     #tuple
  #   E_Load_SD = pd.read_pickle("INPUT/el")     #array-tuples            
  #   print Q_SHLoad_SD[0].shape
          
          
     Q_DHWLoad_SD = pd.read_hdf("INPUT/20161202_data_SD.hdf5", "dhw")     
     Q_SHLoad_SD = pd.read_hdf("INPUT/20161202_data_SD.hdf5", "sh")     
     E_Load_SD = pd.read_hdf("INPUT/20161202_data_SD.hdf5", "el")     

     QLoad1_df = Q_DHWLoad_SD/1000.
     QLoad2_df = Q_SHLoad_SD/1000.
     ELoad_df = Seconds_to_Minutes(E_Load_SD)/1000.
       
       
  #   QLoad1_df.columns=['QLoad1']  
  #   print QLoad1_df
  #   QLoad2_df.columns=['QLoad2']
  #   ELoad_df.columns=['ELoad']
         
     LoadAll_TOT_df = pd.concat([ELoad_df, QLoad1_df, QLoad2_df], axis=1)
     LoadAll_TOT_df.columns = ['ELoad','QLoad1','QLoad2']  
     #print LoadAll_TOT_df
     
     P_Load_max=10
     print '----------------------------'     
     print '     Load and PV:           '
     print '----------------------------'     
     print 'P_Load_max:', P_Load_max
     
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
     P_PV_max = 4.0#5.# 3.2 #[kW]    # Normierung
     PV = np.load("INPUT/PVAC2013Kassel_5clean.npy")  *  P_PV_max
     # --------------- convert to Pandas Dataframe with TimeIndex ------
     PV_TOT_df = pd.DataFrame(PV, index=year_stamps, columns=['PV 2013, Kassel, 10min'])
     print 'P_PV_max:', P_PV_max
     
     PV_TOT_df.to_csv('OUTPUT\INPUTPV_Kassel2013_EFH.csv')                        
     LoadAll_TOT_df.to_csv('OUTPUT\INPUTLoad_LPG_EFH.csv')                        
          
     return PV_TOT_df, LoadAll_TOT_df ,P_Load_max, P_PV_max,   

def PreisProfile(Delta_t, TimeStepSize,year_stamps, date_year):      
     # ----------------------------------  EXEC Zeitreihe ----------------------------------------
     year = 2013 
     start = '1/1/2013'
     end = '12/31/2013 23:00'
     
     PriceProfil = pd.read_csv('INPUT\Spot'+str(year)+'_one.csv', header=None, delimiter=';')/1000
     #PriceProfil = pd.read_csv('INPUT\Spot'+str(year)+'_one.csv', header=None, delimiter=';').transpose()/1000
     #test = PriceProfil.reindex(index = range(0,len(PriceProfil)*4), method = 'ffill') 
     year_stamp_hour = pd.date_range(start, end, freq='h')  

     PriceProfil.index = year_stamp_hour    
    # PriceProfil_10min = (PriceProfil.reindex(index = year_stamps, method = 'ffill') + 0.15 ) * 1.19
     PriceProfil_10min = (PriceProfil.reindex(index = year_stamps, method = 'ffill')  + 0.15) * 1.19
         #         EXEX + weitere Steuern und Umlagen mal USt.
    # -----------------------------------------------------------------------------------------

     return PriceProfil_10min
  
def ArtPreisProfileLO(Delta_t, TimeStepSize,year_stamps, date_year, year_bins):      

     # -------------------------künstlich erzeugte Zeitreihe El. Prices-----------
     PriceProfile = pd.DataFrame(np.ones(year_bins), index=year_stamps)   
     year_stamps
     
    #-------------------  PV-Einspeisung ---------------     
     
     P=1
     PriceProfile[PriceProfile.index.hour<=4] = 1*P  # 0, -1
     PriceProfile[PriceProfile.index.hour>4] = 1*P  # 0, -1
     PriceProfile[PriceProfile.index.hour>10] = 2*P# 0, -1
     PriceProfile[PriceProfile.index.hour>14] = 2*P
     PriceProfile[PriceProfile.index.hour>16] = 1*P  # 0, -1
     PriceProfile[PriceProfile.index.hour>20] = 1*P  # 0, -1
             
             
     #print PriceProfile
    
     return PriceProfile

def ArtPreisProfileER(Delta_t, TimeStepSize,year_stamps, date_year, year_bins):      

     # -------------------------künstlich erzeugte Zeitreihe Feed-In Tariff -----------
     PriceProfile = pd.DataFrame(np.ones(year_bins), index=year_stamps)   
     year_stamps
     
    #-------------------  PV-Einspeisung ---------------     
     P=1
     #                                        verbreiterte Einspeisung- Peak reduction bei -1
     PriceProfile[PriceProfile.index.hour<=4] = 1*P  #1  1
     PriceProfile[PriceProfile.index.hour>4] = 1*P  # 1  1
     PriceProfile[PriceProfile.index.hour>9] = 1*P  # 1  1
     PriceProfile[PriceProfile.index.hour>10] = 0*P # 0-1
     PriceProfile[PriceProfile.index.hour>14] = 1*P  #1  1
     PriceProfile[PriceProfile.index.hour>16] = 1*P  #1  1
     PriceProfile[PriceProfile.index.hour>20] = 1*P  #1  1
             
     #print PriceProfile
    
     return PriceProfile

def running_mean(x, N):
     cumsum = np.cumsum(np.insert(x, 0, 0)) 
     print len(cumsum)
     a = (cumsum[N:] - cumsum[:-N]) / N 
     for i in range(N):
        c = (cumsum[N:] - cumsum[:-N]) / N 
        a = np.insert(a, 0, c[i])
     return pd.DataFrame(a[1:])   
                  
def Seconds_to_Minutes(DF_sec):
   # print len(DF_sec)
   # print DF_sec
    DF_min = DF_sec.el.resample('10min', how='sum')/600.
  #  print DF_min
    return DF_min
        
if __name__ == '__main__':  
        plt.close("all")
        print "I am just an Input-File !!!!" 
        
        #print "I am just a poor InputReader without any idea of running.\
    #Please ask my friend OptFlex_MPC!"
   