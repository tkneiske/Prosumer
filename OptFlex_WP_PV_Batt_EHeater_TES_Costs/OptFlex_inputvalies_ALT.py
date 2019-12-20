# -*- coding: utf-8 -*
"""
Created on Thu May 07 12:44:54 2015
Überarbeitet und Validiert von Tkneiske Sep2015
CHPPV ++
@author: tcantillO; tkneiske
"""

import numpy as np
#import scipy as sci
import scipy.io as sio
import matplotlib.pyplot as plt
import pandas as pd

def inputvaluesEFH(Delta_t, TimeStepSize,year_stamps):          
     # ---------------------------------------------    
     # Load vector inserted by tkneiske Sep2015    
     # ---------------------------------------------    
     # --- INPUT File adds thermnal and DHW--- take half each --- please change!!!
     QLoad=sio.loadmat('INPUT/EFH_'+TimeStepSize+'.mat')['QLoad']
     ELoad=sio.loadmat('INPUT/EFH_'+TimeStepSize+'.mat')['ELoad'] 
     #----- same as pandas dataframe
     ELoad_df = pd.DataFrame(ELoad, index=year_stamps, columns=['ELoad'])
     QLoad1_df = pd.DataFrame(QLoad*0.5, index=year_stamps, columns=['QLoad1'])    
     QLoad2_df = pd.DataFrame(QLoad*0.5, index=year_stamps, columns=['QLoad2'])    
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
   
    
     # ---------------------------------------------    
     # Battery parameters according to Jan's simulatione For MFH (Diego)
     # ---------------------------------------------    
     Cap_batt = 4/100.*60. #[kWh]  # Use 20% to 80% of total capacity
 
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
     SOC_batt_ini = 50

     Battery = pd.Series([eta_batt_sd,eta_batt_char,eta_batt_dis ,K_batt, P_batt_char_max ,\
     P_batt_dis_max,SOC_batt_ini, Cap_batt, SOC_batt_max, SOC_batt_min], \
     index=['eta_batt_sd','eta_batt_char','eta_batt_dis' ,'K_batt', 'P_batt_char_max' ,\
     'P_batt_dis_max','SOC_batt_ini', 'Cap_batt', 'SOC_batt_max', 'SOC_batt_min'])
     print '----------------------------'     
     print '     Battery parameter:'
     print '----------------------------'     
     print Battery
                            
     # ---------------------------------------------    
     #  Auxiliary Gasbrenner
     # ---------------------------------------------    
     eta_aux = 1
     P_aux_th_min = 2.4#2.4# 2.4
     P_aux_th_max = 25.#20#2014.3# [kWth]
     Auxilary = pd.Series([eta_aux, P_aux_th_min, P_aux_th_max],\
     index=['eta_aux', 'P_aux_th_min', 'P_aux_th_max'])
     print '----------------------------'     
     print '     Auxilary  parameter:'
     print '----------------------------'     
     print Auxilary

     #  ---------------------------------------------    
     # Electrical Boiler (Heizstab ?) Diego:Arbitrary chosen
     # ---------------------------------------------    
     eta_eheater = 1
     P_eheater_min = 0#[kWth] ######11.05.2011 2
     P_eheater_max = 2#2 ######11.05.2011 6
     
     EHeater = pd.Series([eta_eheater, P_eheater_min, P_eheater_max],\
     index=['eta_eheater', 'P_eheater_min', 'P_eheater_max'])
     print '----------------------------'     
     print '            EHeater:'
     print '----------------------------'     
     print EHeater

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
     SOC_TES_ini = 50
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
     
     Costs = pd.Series([C_PV_FIT, C_gas, C_grid_el],\
     index = ['C_PV_FIT', 'C_gas', 'C_grid_el'])
     print '----------------------------'     
     print '       Kosten:'
     print '----------------------------'     
     print Costs    
     
     return PV_TOT_df, LoadAll_TOT_df, P_Load_max, P_PV_max, Battery, Auxilary,\
             ThermalStorage, Costs, EHeater

        
        

def inputvaluesMFH(Delta_t):    
     
    #day_stamps = pd.date_range('01/01/2013', '01/01/2014', freq='10min')  
    year_stamps = pd.date_range('01/01/2013', periods=52560, freq='10min')  
    print year_stamps
    # ---------------------------------------------    
    # Load vector inserted by tkneiske Sep2015    
    # ---------------------------------------------    
    #ph=sci.io.loadmat('INPUT\VDI_MFH_10.mat') 
    #Load_cop = ph['VDI_EFH']
    #QLoad['QProfil']=sio.loadmat('INPUT/EFH_'+TimeStepSize+'.mat')['QLoad']
    #ELoad['EProfil']=sio.loadmat('INPUT/EFH_'+TimeStepSize+'.mat')['ELoad']
    Load_cop = 1
    P_dhw_th = 1
    P_sh_th = 1
    print 'Old Old Old Do NOT use !!!!'           


    # ---------------------------------------------    
    # PV Profile    
    # ---------------------------------------------     
    # --------> OLD from DIEGO ---------> P_PV_ava=P_PV_avacop[cont:Np+(cont)];
    # --------> OLD from DIEGO ---------> PV generation for prediction horizont#
    # --------> OLD from DIEGO ---------> PV = ph['INTPUT\PVV']
    # --------> OLD from DIEGO ---------> PVcut = PV[1:145,0]
    # --------> OLD from DIEGO ---------> plt.plot(PVcut)   
    # ------- Source: IWES roof 2013 10 min resolution, normalized to 1kWP, AC
    # ------------ 1day = 144
    PV = np.load("INPUT/PVAC2013Kassel_5clean.npy") 
    # --------------- convert to Pandas Dataframe with TimeIndex ------
    PV_df = pd.DataFrame(PV, index=year_stamps, columns=['PV 2013, Kassel, 10min'])
    PV_day = PV_df['6/1/2013'] # 144
    P_PV_ava = PV_day.values
    #print PV_day    # nparray length 144. 1 day
    print P_PV_ava
    # ---------------- Testplotting----------------------
    #plt.figur
    #plt.plot(PV)
    #plt.plot(year_stamps,PV)
    #print len(PV) = 52560  = 6*24*365
    #PV_df.plot()
    PV_day.plot()
    
    
    
    # ---------------------------------------------     
    # ???
    # ---------------------------------------------     
    ramp_CHP = (18.74 - 10.95)/(5.88-4.75)# [kW_fuel/min] What does this do?
    ramp_CHP = ramp_CHP*Delta_t#This goes to Pyomo
    P_CHP_gas_ini = 0

    # ---------------------------------------------     
    # PV and Battery parameters according to Jan's simulatione
    # For MFH
    # ---------------------------------------------     
    Cap_batt = 12# [kWh]

    # ---------------------------------------------     
    # Battery inverter 3-Phase SI 6.0H 6kVA. From datasheet
    # ---------------------------------------------     
    P_batt_char_max = 6# [kW]
    P_batt_dis_max = 6#[kW]

    # ---------------------------------------------     
    # Experiment no Batt
    #         P_batt_char_max = 0;# [kW] Has to be changed in Python
    #         P_batt_dis_max = 0;#[kW]
    # PV-Inverter 1 X Tripower 9000 
    # ---------------------------------------------     
    P_PV_max = 9#[kW]

    # ---------------------------------------------     
    # Create scalar parameter for Pyomo Simulation
    # ---------------------------------------------     
    Np_hrs = 12
    Np = Np_hrs*6# Prediction horizon in 10 min interval

    # ---------------------------------------------     
    # 13.03.2015
    # Considering also Control horizon Nc
    # ---------------------------------------------     
    Nc_hrs = 6
    Nc = Nc_hrs*6 # Control horizon in 10 min interval
    P_CHP_el_min = 1.5# P_el_min in [kW] according to datasheet
    P_CHP_el_max = 4.7
    eta_CHP_el = 0.23
    eta_CHP_th = 0.67# This value has to be saved
    b_CHP_on_ini = 0


    # Taken from Aastha's Paper
    # ---------------------------------------------     
    # 13.03.2015 self-discharge coefficient for Li-Ion battery
    # According to SYSPV-NS self-discharge is 3# per Month
    # ---------------------------------------------     
    eta_batt_sd = 0.03
    eta_batt_sd = (1-0.03/(24*30*60/Delta_t))

    eta_batt_char = 0.9
    eta_batt_dis = 0.92
    K_batt = (Delta_t/float(60))/float(Cap_batt)*100
        # K_batt = 0;#Experiment no Batt
    SOC_batt_max = 100
    SOC_batt_min = 20
    SOC_batt_ini = 50
    #         SOC_batt_ini = 0 #Experiment no Batt

    # ---------------------------------------------     
    # Arbitrary chosen
    # ---------------------------------------------     
    eta_boiler = 0.9 ####CHANGE
    P_eboiler_max = 21.4#[kWth]
    P_eboiler_min = 3.8         
    #         P_eboiler_max =0#[kWth] #No boiler experiment
    #         P_eboiler_min = 0 #No boiler experiment
    eta_aux = 0.9
    P_aux_th_min = 3.8
    P_aux_th_max = 21.4# [kWth]

    # ---------------------------------------------     
    # Parameter for the cost function have to be in vector form
    #28.01.2015
    # PV Feed-in Tariff in Germany for 2015
    # Inbetriebnahme im Januar 205 - Dachanlage auf Wohngebäuden - bis 10 kWp
    # Einspeisevergütung = 12.56 Cent/kWh = 0.1256 EUR/kWh
    # ---------------------------------------------     
    C_PV_FIT = 0.1256
    # C_PV_FIT = 0;#17.02.2015 Experiment no FI14.03.2011 22:20T
    C_PV_FIT = C_PV_FIT#*np.ones((Np,1))

    # ---------------------------------------------     
    # ---------------------------------------------     
    # CHP Feed-in Tariff 
    # Nach KWK-Gesetz
    # EV_KWK = Üblicher Preis + KWK-Zuschlag + Vermiedene Netzkosten
    # ---------------------------------------------     
    # ---------------------------------------------     

    # ---------------------------------------------     
    # Üblicher Preis: an der Leipziger Strombörse EEX erzielten
    # durchschnittlichen Preis des Baseload-Stroms des vorangegangenen Quartals
    # (KWK-Index)
    # KWK-Index von Q4/204 für Einspeisung in Q1/2015 = 3.482 Cent/kWh =
    # 0.03482 EUR/kWh
    # ---------------------------------------------     
    C_KWK_Index = 0.03482

    # ---------------------------------------------     
    # KWK-Zuschlag (Stand Okt. 2014) = 5.41 Cent/kWh = 0.0541 EUR/kWh
    # ---------------------------------------------     
    C_KWK_Zus = 0.0541
    # C_KWK_Zus = 0;#17.02.2015 Experiment no FIT
    
    # ---------------------------------------------     
    # For CHP self-consumption in the objective function
    # ---------------------------------------------     
    C_CHP_ex = C_KWK_Zus#*np.ones((Np,1));

    # ---------------------------------------------     
    # vermiedene Netzkosten
    # In der Praxis werden 0.4 bis 1.5 Cent pro Kilowattstunde an vermiedenen
    # Netznutzungsentgelten vergütet
    # ---------------------------------------------     
    C_KWK_Netznutz = 0.005
    
    C_CHP_FIT = (C_KWK_Index + C_KWK_Zus + C_KWK_Netznutz)
    # C_CHP_FIT = 0;#Experiment no FIT
    C_CHP_FIT = C_CHP_FIT #*np.ones((Np,1))

    # ---------------------------------------------     
    # Verivox Verbraucherpreisindex Gas
    # Durchschnittlicher Heizgaspreis in Cent pro kWh (brutto) 2014
    # bei einem Jahresverbrauch von 20.000 kWh = 6.52 Cent/kWh = 0.0652 EUR/kWh
    # ---------------------------------------------     
    C_gas = 0.0652#*np.ones((Np,1))

    # ---------------------------------------------     
    # Verivox Verbraucherpreisindex Strom
    # Durchschnittlicher Haushaltsstrompreis in Cent pro kWh (brutto) 2014
    # bei einem Jahresverbrauch von 4.000 kWh = 28.38 Cent/kWh = 0.2838 EUR/kWh
    # ---------------------------------------------     
    C_grid_el = 0.2838#*np.ones((Np,1))


    # ---------------------------------------------     
    # Costs for cold start --> Input from Vaillant is required
    # here just an assumption 0.5 Cent/kWh = 0.005 EUR
    # ---------------------------------------------     
    C_CHP_cs = 0.02#*np.ones((Np,1))

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
    SOC_TES_ini = 10
    K_TES = ((Delta_t/float(60))/Cap_TES)*100

    # ---------------------------------------------     
    # According to Vaillant data-sheet stanby losses for TES are 
    # 300 liter: 1.9 kWh/24h
    # 500 liter: 2.6 kWh/24h
    # ---------------------------------------------              
    if Vol_S == 0.3:
        StandbyTES = 1.9/Cap_TES# kWh/d
    elif Vol_S == 0.5:
        StandbyTES = 2.6/Cap_TES # kWh/d
         
    eta_TES_sd = 1 - StandbyTES/(24*60/Delta_t)
    
    # Same as battery
    eta_TES_char = 0.9
    eta_TES_dis = 0.92

   
    return  P_PV_ava, P_dhw_th, P_sh_th, Load_cop,P_eboiler_min,Cap_TES,Np,P_Load_max,eta_CHP_th,P_CHP_el_min, \
    P_CHP_el_max,eta_CHP_el,ramp_CHP,eta_batt_sd,eta_batt_char,eta_batt_dis , \
    K_batt ,P_batt_char_max ,P_batt_dis_max ,eta_boiler ,P_PV_max ,eta_aux , \
    C_gas ,C_grid_el ,C_CHP_FIT ,C_PV_FIT ,C_CHP_cs ,K_TES ,eta_TES_sd , \
    eta_TES_char ,eta_TES_dis ,P_aux_th_max ,P_aux_th_min ,P_eboiler_max , \
    SOC_batt_max ,SOC_batt_min ,SOC_TES_max ,SOC_TES_min ,C_CHP_ex ,P_CHP_gas_ini , \
    b_CHP_on_ini ,SOC_batt_ini,SOC_TES_ini,Cap_batt
        
if __name__ == '__main__':
    	main.MPC()     
   