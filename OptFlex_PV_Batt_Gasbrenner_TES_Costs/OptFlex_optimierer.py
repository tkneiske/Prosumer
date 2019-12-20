# -*- coding: utf-8 -*
"""
Created on Fri Jan 09 11:58:21 2015
Checked by tkneiske Sept 2015

@author: dhidalgo, tkneiske

"""
 
from __future__ import division
#from coopr.pyomo import * 
#from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.core import Var
from pyomo.environ import *
from pyomo.dae import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def OptFlex_optimierer(horizon_stamps, PrHoBin,  \
Load,P_PV_max_mat, P_Load_max_mat, P_sh_th, P_dhw_th, P_PV_ava, Battery,\
Auxilary, ThermalStorage, Costs):
 #, EHeater):
    #02.02.2015
    # Create a solver
    opt = SolverFactory('cplex')
    model = AbstractModel() #Declare model of type Abstract
    #-----------------------------------------------------------------------
    # Prediction horizon 144 = 1 Tag, 72 = 12 Stunden 
    #-----------------------------------------------------------------------
    model.K = RangeSet(0, PrHoBin-1) # Maybe start with 0 or 1 ????
    #-----------------------------------------------------------------------
    Np = PrHoBin-1   # used with CHP on/off rule
    m = range(0, PrHoBin)  # used in Cost vectors
 
    # Creating dictionaries to initialize Param
    # For constants

    #-----------------------------------------------------------------------
    #  ------------- Battery --------------------
    #-----------------------------------------------------------------------
    eta_batt_sd = {1: Battery['eta_batt_sd']}
    eta_batt_char = {1 : Battery['eta_batt_char']}
    eta_batt_dis = {1 : Battery['eta_batt_dis']}
    K_batt = {1: Battery['K_batt']}
    P_batt_char_max = {1: Battery['P_batt_char_max']}
    P_batt_dis_max = {1: Battery['P_batt_dis_max']}
    SOC_batt_ini = {1: Battery['SOC_batt_ini']}
    SOC_batt_max =  {1:Battery['SOC_batt_max']}
    SOC_batt_min = {1: Battery['SOC_batt_min']}

    P_PV_max = {1: P_PV_max_mat}
    P_Load_max = {1: P_Load_max_mat}  
    #-----------------------------------------------------------------------
    #  -------------- Auxilary ---------------------
    #-----------------------------------------------------------------------
    eta_aux = {1: Auxilary['eta_aux']}
    P_aux_th_max = {1: Auxilary['P_aux_th_max']}
    P_aux_th_min = {1: Auxilary['P_aux_th_min']}
   
    #-----------------------------------------------------------------------
    #  -------------- Thermal Storage ---------------------
    #----------------------------------------------------------------------- 
    SOC_TES_ini = {1: ThermalStorage['SOC_TES_ini']}
    K_TES = {1: ThermalStorage['K_TES']}
    eta_TES_sd = {1: ThermalStorage['eta_TES_sd']}
    eta_TES_char = {1: ThermalStorage['eta_TES_char']}
    eta_TES_dis = {1: ThermalStorage['eta_TES_dis']}
    SOC_TES_max = {1: ThermalStorage['SOC_TES_max']}
    SOC_TES_min = {1: ThermalStorage['SOC_TES_min']}
    #-----------------------------------------------------------------------
    #  ------------------- Costs --------------------------------------------
    #-----------------------------------------------------------------------
    C_gas_ar = Costs['C_gas']*np.ones((Np,1))
    C_grid_el_ar = Costs['C_grid_el']*np.ones((Np,1))
#    C_CHP_FIT_ar = Costs['C_CHP_FIT']*np.ones((Np,1))
#    C_CHP_cs_ar = Costs['C_CHP_cs']*np.ones((Np,1))
#    C_CHP_ex_ar = Costs['C_CHP_ex']*np.ones((Np,1)) # [0 bis 71]
    C_PV_FIT_ar = Costs['C_PV_FIT']*np.ones((Np,1))
    C_PV_eig_ar = Costs['C_PV_eig']*np.ones((Np,1))
    
    C_gas = {i: C_gas_ar[i-1,0] for i in m};
    C_grid_el = {i: C_grid_el_ar[i-1,0] for i in m};
#    C_CHP_FIT = {i: C_CHP_FIT_ar[i-1,0] for i in m};
    C_PV_FIT = {i: C_PV_FIT_ar[i-1,0] for i in m};
    C_PV_eig = {i: C_PV_eig_ar[i-1,0] for i in m};
#    C_CHP_cs = {i: C_CHP_cs_ar[i-1,0] for i in m};
#    C_CHP_ex ={i: C_CHP_ex_ar[i-1,0] for i in m};
    #==============================================================================
    #     PARAMETER
    #==============================================================================
    model.I = RangeSet(1) # set I is related to scalar parameters 
#     #model.Np = Param(model.I, initialize = Np)
    # ----------- Battery ------------------
    model.eta_batt_sd = Param(model.I, initialize= eta_batt_sd)
    model.eta_batt_char = Param(model.I, initialize= eta_batt_char)
    model.eta_batt_dis = Param(model.I, initialize= eta_batt_dis)
    model.K_batt = Param(model.I, initialize= K_batt)
    model.P_batt_char_max = Param(model.I, initialize= P_batt_char_max)
    model.P_batt_dis_max = Param(model.I, initialize= P_batt_dis_max)
    model.SOC_batt_max = Param(model.I, initialize= SOC_batt_max)
    model.SOC_batt_min = Param(model.I, initialize= SOC_batt_min)
    model.SOC_batt_ini = Param(model.I, initialize = SOC_batt_ini)
    # ------------- Load -----------------------
    model.P_Load_max = Param(model.I, initialize = P_Load_max )
    model.P_Load = Param(model.K, initialize= Load)
    model.P_sh_th = Param(model.K, initialize= P_sh_th)
    model.P_dhw_th = Param(model.K, initialize= P_dhw_th)
    # --------------- PV ----------------------------------
    model.P_PV_ava = Param(model.K, initialize= P_PV_ava)
    model.P_PV_max = Param(model.I, initialize= P_PV_max )
    #---------------- Aux ----------------------------------
    model.eta_aux = Param(model.I, initialize= eta_aux)
    model.P_aux_th_max = Param(model.I, initialize= P_aux_th_max )
    model.P_aux_th_min = Param(model.I, initialize=P_aux_th_min)
#    model.P_PV_max = Param(model.I, initialize= P_PV_max)
    # ------------ EHeater ---------------------------------
#    model.eta_eheater = Param(model.I, initialize= eta_eheater)
#    model.P_eheater_min = Param(model.I, initialize= P_eheater_min)
#    model.P_eheater_max = Param(model.I, initialize= P_eheater_max)
    #   #va = {i_va: 0.0652 for i_va in range(1,Np_mat[0]+1)}   
    # ------------ Thermal Storage ------------------------
    model.K_TES = Param(model.I, initialize= K_TES)
    model.eta_TES_sd = Param(model.I, initialize= eta_TES_sd)
    model.eta_TES_char = Param(model.I, initialize= eta_TES_char)
    model.eta_TES_dis = Param(model.I, initialize= eta_TES_dis)
    model.SOC_TES_max = Param(model.I, initialize= SOC_TES_max)
    model.SOC_TES_min = Param(model.I, initialize= SOC_TES_min)
    model.SOC_TES_ini = Param(model.I, initialize = SOC_TES_ini)
    # -------------- Costs ----------------------------------------     
    model.C_gas = Param(model.K, initialize= C_gas)
    model.C_grid_el = Param(model.K, initialize= C_grid_el)
#    model.C_CHP_FIT = Param(model.K, initialize= C_CHP_FIT)
#    model.C_CHP_cs = Param(model.K, initialize= C_CHP_cs)
#    model.C_CHP_ex = Param(model.K, initialize= C_CHP_ex)
    model.C_PV_FIT = Param(model.K, initialize= C_PV_FIT)
    model.C_PV_eig = Param(model.K, initialize= C_PV_eig)
    
    # -------------------------------------------------------------------------
    # Continuos VARIABLES
    # --------------------------------------------------------------------------
    # 10.02.2015     
    # Boundaries for P_PV_sc: 0 <= P_PV_sc <= P_Load_max + P_eboiler_max + P_batt_char_max    
    #----------------------- PV ---------------------------------------  
   # model.P_PV_sc = Var(model.K, domain=NonNegativeReals, bounds = (0, 100))
    model.P_PV2load = Var(model.K, domain=NonNegativeReals, bounds = (0, 100))
    model.P_PV2batt = Var(model.K, domain=NonNegativeReals, bounds = (0, 100))
  #  model.P_PV2Eheater = Var(model.K, domain=NonNegativeReals, bounds = (0, 100))
    model.P_PV_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,100))
    #-------------------------- Grid ------------------------------
    model.P_grid_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,150))
    model.P_grid_imp = Var(model.K, initialize=10, domain=NonNegativeReals, bounds = (0, 150) )
    # --------------------------- Battery -----------------------
    model.SOC_batt = Var(model.K, domain=NonNegativeReals, bounds=(0,1000))
    model.P_batt_char = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
    model.P_batt_dis = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
    model.b_batt = Var(model.K, initialize=1, domain=Binary) # Laden = 1, Entladen = 0
    model.P_batt2Load = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
 #   model.P_batt2Eheater = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
    # ------------------ Auxilary Gaskessel--------------------------------
    model.P_aux_th = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
    model.P_aux_gas = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
    model.b_aux = Var(model.K, domain=Binary)
    # ----------------  Thermal Storage -----------------------------------
    #???? model.SOC_batt_term = Var(domain=NonNegativeReals, bounds = (0,100))        
    model.P_TES_char = Var(model.K, domain=NonNegativeReals, bounds=(0,100))
    model.P_TES_dis = Var(model.K, domain=NonNegativeReals, bounds= (0,100))
    model.SOC_TES = Var(model.K, domain=NonNegativeReals, bounds=(0,1000))
    # ------------------ EHeater -------------------------------------------
 #   model.P_eheater_el = Var(model.K, domain=NonNegativeReals, bounds =(0,200))
 #   model.P_eheater_th = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
 #   model.b_eheater = Var(model.K, domain=Binary)
# --------------------------------------------------------------------------
#                  OBJECTIVE 
# --------------------------------------------------------------------------

       
    def obj_expression(model):
        # Operational costs
        return sum(model.C_gas[k]*model.P_aux_gas[k] for k in model.K) +\
               sum(model.C_grid_el[k]*model.P_grid_imp[k] for k in model.K) -\
               sum(model.C_PV_FIT[k]*model.P_PV_exp[k] for k in model.K)# -\
                #sum(model.C_gas[k]*(model.P_aux_gas[k]+model.P_CHP_gas[k]) for k in model.K) +\
                #sum(model.C_CHP_FIT[k]*model.P_CHP_el_exp[k] for k in model.K) -\
                #sum(model.C_CHP_ex[k]*model.P_CHP_el_sc[k] for k in model.K) +\
                #sum(model.C_CHP_cs[k]*model.b_CHP_up[k] for k in model.K) +\
                #0.5*model.SOC_batt_term    
       
    #model.OBJ = Objective(rule=obj_expression, sense=max)
    model.OBJ = Objective(rule=obj_expression) #min
 
     # --------------------------------------------------------------------------
     #              CONSTRAINTS
     # --------------------------------------------------------------------------
     
    # ---------- Electrical ----     
    # Equation (2)  now eq (3) Energyconservation (or Powerconservation?)
    def ele_balance_constraint_rule(model,k):
         return model.P_Load[k] - model.P_grid_imp[k] \
             + model.P_grid_exp[k] - model.P_PV_ava[k] \
             + model.P_batt_char[k] - model.P_batt_dis[k] == 0
    model.ele_balance_constraint = \
    Constraint(model.K, rule=ele_balance_constraint_rule)
  
#    def ele_balance_constraint_rule(model,k):
#         return model.P_Load[k] - model.P_grid_imp[k]\
#             + model.P_grid_exp[k] - model.P_PV_ava[k]  \
#             + model.P_batt_char[k] - model.P_batt_dis[k]\
#             + model.P_eheater_el[k] == 0
#    model.ele_balance_constraint = \
#    Constraint(model.K, rule=ele_balance_constraint_rule)  
  
    # ------------- Thermal -----    
    # Equation (22)    
    def th_balance_constraint_rule(model,k):
        return model.P_sh_th[k] + model.P_dhw_th[k] -  model.P_aux_th[k] \
                + model.P_TES_char[k] - model.P_TES_dis[k]  == 0         
    model.th_balance_constraint = \
    Constraint(model.K, rule=th_balance_constraint_rule)

#    def th_balance_constraint_rule(model,k):
#        return model.P_sh_th[k] + model.P_dhw_th[k] -  model.P_aux_th[k] \
#                + model.P_TES_char[k] - model.P_TES_dis[k] \
#                - model.P_eheater_th[k]  == 0         
#    model.th_balance_constraint = \
#    Constraint(model.K, rule=th_balance_constraint_rule)
  # --------------------------------------------------------------------------
    # Self Consumption    
    # --------------------------------------------------------------------------

#==============================================================================
# ------------ ALT MIT PV_PC -------------------------------
#
#      # Equation (3)  now eq. (4) Self-consumption, what can self-consume the produced energy
#     def PV_selfcons1_rule(model,k):
#          return model.P_PV_sc[k] <= model.P_Load[k] + model.P_batt_char[k] 
#           # 16.02.2015 Test_ CHP_sc as a variable in this constraint
#     model.PV_selfcons1 = \
#     Constraint(model.K, rule=PV_selfcons1_rule)
#       
#     #     Self-consumption, limit for PV_SC by produced PV Power, now eq(4)
#     def PV_selfcons2_rule(model,k):
#         return model.P_PV_sc[k] <= model.P_PV_ava[k]        
#     model.PV_selfcons2 = \
#     Constraint(model.K, rule=PV_selfcons2_rule)
# 
#     # Equation (4) , now eq (5)
#     def PV_Export_rule(model,k):
#         return model.P_PV_exp[k] == model.P_PV_ava[k] - model.P_PV_sc[k]    
#     model.PV_Export = \
#     Constraint(model.K, rule=PV_Export_rule)
# 
#==============================================================================
    #load
    def PV_selfcons1load_rule(model,k):
         return model.P_PV2load[k] <= model.P_Load[k] 
    model.PV_selfcons1load = \
    Constraint(model.K, rule=PV_selfcons1load_rule)
 
    def PV_selfcons2load_rule(model,k):
        return model.P_PV2load[k] <= model.P_PV_ava[k]        
    model.PV_selfcons2load = \
    Constraint(model.K, rule=PV_selfcons2load_rule)
    # Eheater
#    def PV_selfcons1Eheater_rule(model,k):
#        return model.P_PV2Eheater[k] <= model.P_eheater_el[k] 
#    model.PV_selfcons1Eheater = \
#    Constraint(model.K, rule=PV_selfcons1Eheater_rule)

#    def PV_selfcons2Eheater_rule(model,k):
#        #return model.P_PV2load[k] + model.P_PV2eheater_el[k]<= model.P_PV_ava[k]        
#        return model.P_PV2Eheater[k] <= model.P_PV_ava[k]        
#    model.PV_selfcons2Eheater = \
#    Constraint(model.K, rule=PV_selfcons2Eheater_rule)
       
    # Batt
    def PV_selfcons1batt_rule(model,k):
        #return model.P_PV2load[k] + model.P_PV2eheater_el[k]<= model.P_PV_ava[k]     
         return model.P_PV2batt[k] == model.P_batt_char[k] 
          # 16.02.2015 Test_ CHP_sc as a variable in this constraint
    model.PV_selfcons1batt = \
    Constraint(model.K, rule=PV_selfcons1batt_rule)
 
    def PV_selfcons2batt_rule(model,k):
        return model.P_PV2batt[k] <= model.P_PV_ava[k]        
    model.PV_selfcons2batt = \
    Constraint(model.K, rule=PV_selfcons2batt_rule)
    
    # Export
    def PV_Export1_rule(model,k):
        return model.P_PV_exp[k] == P_PV_ava[k] - model.P_PV2load[k] -  model.P_PV2batt[k]
    model.PV_Export1 = \
    Constraint(model.K, rule=PV_Export1_rule)

    def PV_Export2_rule(model, k):
        return model.P_PV_exp[k] <= model.P_grid_exp[k]
    model.PV_Export2 = \
    Constraint(model.K, rule=PV_Export2_rule)
#==============================================================================
#     def PV_rule(model,k):
#         return model.P_PV[k] <= model.P_PV_ava[k]    
#     model.PV_rule = \
#     Constraint(model.K, rule=PV_rule)     
#==============================================================================

#------------------------------------------------------------------------------
# ------------------    Battery model -----------------------------------------
#------------------------------------------------------------------------------
    
    # ------------------------------------
    #  ---------   SOC    ----------------
    # ------------------------------------
    # Equation (14) --> (now Diegos Doku eq 15) 
    def Battery_rule(model,k):
         if k == 0:
             return model.SOC_batt[k] - (model.P_batt_char[k]*model.eta_batt_char[1] - \
             model.P_batt_dis[k]/model.eta_batt_dis[1])*model.K_batt[1] == \
             model.SOC_batt_ini[1]#*model.eta_batt_sd[1] 
             #return model.SOC_batt_ini[1]
         else: 
             return model.SOC_batt[k] -  (model.P_batt_char[k]*model.eta_batt_char[1] - \
             model.P_batt_dis[k]/model.eta_batt_dis[1])*model.K_batt[1] == \
             model.SOC_batt[k-1]*model.eta_batt_sd[1]         
           #  return model.SOC_batt[k] 
    model.Battery = \
    Constraint(model.K, rule=Battery_rule)
   
    # Lower Limit SOC    now eq (16)
    def Battery_SOC1_rule(model,k):
          return model.SOC_batt[k] >= model.SOC_batt_min[1] 
    model.Battery_SOC1 = \
    Constraint(model.K, rule=Battery_SOC1_rule)
    # Upper limit SOC      now eq (16)
    def Battery_SOC2_rule(model,k):
         return model.SOC_batt[k] <= model.SOC_batt_max[1]     
    model.Battery_SOC2 = \
    Constraint(model.K, rule=Battery_SOC2_rule)
  
    # ------------------------------------
    # Equation (15a) -------  BATTERY DISCHARGING ------------
    # ------------------------------------
    def Battery_Dis1_rule (model,k):
        return model.P_batt_dis[k] >= 0     
    model.Battery_Dis1 = \
    Constraint(model.K, rule=Battery_Dis1_rule)
      
    # Equation (15b) ----  if b_batt = 0 ---> Discharging  --- npw eq (17)
    def Battery_Dis2_rule (model,k):
       return model.P_batt_dis[k] <= model.P_batt_dis_max[1]*(1 - model.b_batt[k])     
    model.Battery_Dis2 = \
    Constraint(model.K, rule=Battery_Dis2_rule)
  
    # ------------------------------------
    # Equation (16a)  ------- BATTERY CHARGING ------------------
    # ------------------------------------
    def Battery_Char1_rule (model,k):
         return model.P_batt_char[k] >= 0      
    model.Battery_Char1 = \
    Constraint(model.K, rule=Battery_Char1_rule)
      
    # Equation (16b) ------- if b_batt = 1 ---> Charging ---- now eq (18)
    def Battery_Char2_rule (model,k):
        return model.P_batt_char[k] <= model.P_batt_char_max[1]*(model.b_batt[k]) 
    model.Battery_Char2 = \
    Constraint(model.K, rule=Battery_Char2_rule)

#------------------------------------------------------------------------------
# ------------------    Grid model -----------------------------------------
#------------------------------------------------------------------------------

    # Grid exchange --- now eq.21
    def Grid_exp_rule(model,k):
       return model.P_grid_exp[k] == model.P_PV_exp[k]   
    model.Grid_exp = \
    Constraint(model.K, rule=Grid_exp_rule)
     
    # Equation (20a) --- Grid export -- now eq.22
    def Grid_exp_batt1_rule(model,k):
        return model.P_grid_exp[k] >= 0
    model.Grid_exp_batt1 = \
    Constraint(model.K, rule=Grid_exp_batt1_rule)
     
    # Equation (20b) --- now eq.22 ---Grid export --- Netzeinspeisung maximal PV Erzeugung
    def Grid_exp_batt2_rule(model,k):
        #return model.P_grid_exp[k] - (model.P_CHP_el_max[1] + model.P_PV_max[1])*model.b_batt[k] <= 0 
        #return model.P_grid_exp[k] - (model.P_CHP_el_max[1] + model.P_PV_max[1]) <= 0
        return model.P_grid_exp[k] - model.P_PV_max[1] <= 0
    model.Grid_exp_batt2 = \
    Constraint(model.K, rule=Grid_exp_batt2_rule)
    
    # Equation (21a)  --- Grid import --- now eq.23
    def Grid_imp_batt1_rule(model,k):
        return model.P_grid_imp[k] >= 0
    model.Grid_imp_batt1 = \
    Constraint(model.K, rule=Grid_imp_batt1_rule)  

    # Equation (21b) --- Grid import --- now eq.23 --- no grid import for battery
    def Grid_imp_batt2_rule(model,k):
    #    return model.P_grid_imp[k] -(model.P_Load[k] + model.P_eboiler_max[1])* \
    #    (1-model.b_batt[k]) <= 0
       return model.P_grid_imp[k] - (model.P_Load_max[1])*\
       (1-model.b_batt[k]) <= 0
    model.Grid_imp_batt2 = \
    Constraint(model.K, rule=Grid_imp_batt2_rule)
#------------------------------------------------------------------------------
# ------------------   Aux Gasbrenner -----------------------------------------
#------------------------------------------------------------------------------

     # Equation(27a)
    def Aux_Modulation1_rule(model,k):
        return model.P_aux_th[k] <= model.P_aux_th_max[1]*model.b_aux[k]
    model.Aux_Modulation1 = \
    Constraint(model.K, rule=Aux_Modulation1_rule)
 
    # Equation(27b)
    def Aux_Modulation2_rule(model,k):
        return model.P_aux_th[k] >= model.P_aux_th_min[1]*model.b_aux[k]     
    model.Aux_Modulation2 = \
    Constraint(model.K, rule=Aux_Modulation2_rule)
     
    # Equation(28)
    def Aux_Performance_rule(model,k):
        return model.P_aux_gas[k] == model.P_aux_th[k]/model.eta_aux[1]   
    model.Aux_Performance = \
    Constraint(model.K, rule=Aux_Performance_rule)
 
#------------------------------------------------------------------------------
# ------------------   EHeater  -----------------------------------------
#------------------------------------------------------------------------------
     # Equation (17)
     # 07.05.2015
     # Modulation for eheater
#    def Eheater_Modulation1_rule(model,k):
#        return model.P_eheater_th[k] <= model.P_eheater_max[1]*model.b_eheater[k]         
#    model.Eheater_Modulation1 = \
#    Constraint(model.K, rule=Eheater_Modulation1_rule)
 
#    def Eheater_Modulation2_rule(model,k):
#        return model.P_eheater_th[k] >= model.P_eheater_min[1]*model.b_eheater[k]         
#    model.Eheater_Modulation2 = \
#    Constraint(model.K, rule=Eheater_Modulation2_rule)
     
#    def Eheater_Performance_rule (model,k):
#        return model.P_eheater_el[k] == model.P_eheater_th[k]/model.eta_eheater[1]     
#    model.Eheater_Performance = \
#    Constraint(model.K, rule=Eheater_Performance_rule)

    
#------------------------------------------------------------------------------
# ------------------    Thermal Storage ----------------------------------------
#------------------------------------------------------------------------------
    # Equation (24)
    def TES_rule(model,k):
        if k == 0:
            return model.SOC_TES[k]  - (model.P_TES_char[k]*model.eta_TES_char[1] - \
                    model.P_TES_dis[k]/model.eta_TES_dis[1])*model.K_TES[1]== \
                    model.SOC_TES_ini[1]#*model.eta_TES_sd[1] 
        else: 
            return model.SOC_TES[k] - (model.P_TES_char[k]*model.eta_TES_char[1] - \
                    model.P_TES_dis[k]/model.eta_TES_dis[1])*model.K_TES[1] == \
                    model.SOC_TES[k-1]*model.eta_TES_sd[1]                     
    model.TES = \
    Constraint(model.K, rule=TES_rule)
    
    def TES_SOC1_rule(model,k):
        return model.SOC_TES[k] >= model.SOC_TES_min[1]     
    model.TES_SOC1 = \
    Constraint(model.K, rule=TES_SOC1_rule)
    
    def TES_SOC2_rule(model,k):
        return model.SOC_TES[k] <= model.SOC_TES_max[1]     
    model.TES_SOC2 = \
    Constraint(model.K, rule=TES_SOC2_rule)
 
     # Equation (25)  ------- Jede Heatsource geht auf den Thermal Storage
    def TES_char_rule(model,k):
       return model.P_TES_char[k]   \
       - model.P_aux_th[k] == 0  
#       - model.P_eheater_th[k]== 0  
#       return model.P_TES_char[k]  - model.P_aux_th[k] - model.P_eboiler_th[k] \
#       - model.P_CHP_th[k] == 0  
    model.TES_char = \
    Constraint(model.K, rule=TES_char_rule)

    # Equation (26) ---------- Storage Bedient immer die Wärmelasten
    def TES_dis_rule(model,k):
        return model.P_TES_dis[k] == model.P_sh_th[k]  + \
        model.P_dhw_th[k]
    model.TES_dis = \
    Constraint(model.K, rule=TES_dis_rule)
        
    # --------------------------------------------------------------------------
    #        Create a model instance and optimize
    # --------------------------------------------------------------------------
    instance = model.create_instance()  
    results = opt.solve(instance, tee=False)
    #results.write()    
 
    # --------------------------------------------------------------------------
    #           Prepare results
    # --------------------------------------------------------------------------   
    instance.solutions.load_from(results)
    
    # --------------------------- Grid -----------------------
    P_grid_imp_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_grid_imp')
    for i in range(0, PrHoBin):
        P_grid_imp_res[i] = varobject[(i)].value
        #print P_grid_imp_res
    P_grid_imp_res_df = pd.DataFrame(
                        P_grid_imp_res, index=horizon_stamps, columns=['P_Grid_import'])
                        
    P_grid_exp_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_grid_exp')
    for i in range(0, PrHoBin):
        P_grid_exp_res[i] = varobject[(i)].value
        #print P_grid_imp_res
    P_grid_exp_res_df = pd.DataFrame(
                        P_grid_exp_res, index=horizon_stamps, columns=['P_Grid_export'])

    # --------------------------- Battery -----------------------    
    SOC_batt_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'SOC_batt')
    for i in range(0, PrHoBin):
        SOC_batt_res[i] = varobject[(i)].value
    SOC_batt_res_df = pd.DataFrame(
                        SOC_batt_res, index=horizon_stamps, columns=['SOC_batt'])

    P_batt_char_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_batt_char')
    for i in range(0, PrHoBin):
        P_batt_char_res[i] = varobject[(i)].value
    P_batt_char_res_df = pd.DataFrame(
                        P_batt_char_res, index=horizon_stamps, columns=['P_batt_char'])

    P_batt_dis_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_batt_dis')
    for i in range(0, PrHoBin):
        P_batt_dis_res[i] = varobject[(i)].value
    P_batt_dis_res_df = pd.DataFrame(
                        P_batt_dis_res, index=horizon_stamps, columns=['P_batt_dis'])

#==============================================================================
#     On_Off_batt = np.zeros(PrHoBin)
#     varobject = getattr(instance, 'b_batt')
#     for i in range(0, PrHoBin):
#         On_Off_batt[i] = varobject[(i)].value
#     On_Off_batt_df = pd.DataFrame(
#                         On_Off_batt, index=horizon_stamps, columns=['b_batt'])
#==============================================================================

    # --------------------------- PV -----------------------    
    P_PV_exp_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_PV_exp')
    for i in range(0, PrHoBin):
        P_PV_exp_res[i] = varobject[(i)].value
    P_PV_exp_res_df = pd.DataFrame(
                        P_PV_exp_res, index=horizon_stamps, columns=['P_PV_exp'])

#==============================================================================
#     P_PV_sc_res = np.zeros(PrHoBin)
#     varobject = getattr(instance, 'P_PV_sc')
#     for i in range(0, PrHoBin):
#         P_PV_sc_res[i] = varobject[(i)].value
#     P_PV_sc_res_df = pd.DataFrame(
#                         P_PV_sc_res, index=horizon_stamps, columns=['P_PV_sc'])
# 
#==============================================================================
    P_PV2batt_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_PV2batt')
    for i in range(0, PrHoBin):
        P_PV2batt_res[i] = varobject[(i)].value
    P_PV2batt_res_df = pd.DataFrame(
                        P_PV2batt_res, index=horizon_stamps, columns=['P_PV2batt'])    
 
#    P_PV2Eheater_res = np.zeros(PrHoBin)
#    varobject = getattr(instance, 'P_PV2Eheater')
#    for i in range(0, PrHoBin):
#        P_PV2Eheater_res[i] = varobject[(i)].value
#    P_PV2Eheater_res_df = pd.DataFrame(
#                        P_PV2Eheater_res, index=horizon_stamps, columns=['P_PV2Eheater'])                        
                       
    P_PV2load_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_PV2load')
    for i in range(0, PrHoBin):
        P_PV2load_res[i] = varobject[(i)].value
    P_PV2load_res_df = pd.DataFrame(
                        P_PV2load_res, index=horizon_stamps, columns=['P_PV2load'])

    # ----------------------- Auxilary Gasbrenner ------------   
    P_aux_th_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_aux_th')
    for i in range(0, PrHoBin):
        P_aux_th_res[i] = varobject[(i)].value
    P_aux_th_res_df = pd.DataFrame(
                        P_aux_th_res, index=horizon_stamps, columns=['P_aux_th'])

    P_aux_gas_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_aux_gas')
    for i in range(0, PrHoBin):
        P_aux_gas_res[i] = varobject[(i)].value
    P_aux_gas_res_df = pd.DataFrame(
                        P_aux_gas_res, index=horizon_stamps, columns=['P_aux_gas'])
    
    # -------------------------Thermal Storage -----------------------    
    SOC_TES_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'SOC_TES')
    for i in range(0, PrHoBin):
        SOC_TES_res[i] = varobject[(i)].value
    SOC_TES_res_df = pd.DataFrame(
                        SOC_TES_res, index=horizon_stamps, columns=['SOC_TES'])

    P_TES_char_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_TES_char')
    for i in range(0, PrHoBin):
        P_TES_char_res[i] = varobject[(i)].value
    P_TES_char_res_df = pd.DataFrame(
                        P_TES_char_res, index=horizon_stamps, columns=['P_TES_char'])

    P_TES_dis_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_TES_dis')
    for i in range(0, PrHoBin):
        P_TES_dis_res[i] = varobject[(i)].value
    P_TES_dis_res_df = pd.DataFrame(
                        P_TES_dis_res, index=horizon_stamps, columns=['P_TES_dis'])

      # -------------------------  Eheater --- Heizstab ---------------------    
#    P_eheater_el_res = np.zeros(PrHoBin)
#    varobject = getattr(instance, 'P_eheater_el')
#    for i in range(0, PrHoBin):
#        P_eheater_el_res[i] = varobject[(i)].value
#    P_eheater_el_res_df = pd.DataFrame(
#                        P_eheater_el_res, index=horizon_stamps, columns=['P_eheater_el'])
    
#    P_eheater_th_res = np.zeros(PrHoBin)
#    varobject = getattr(instance, 'P_eheater_th')
#    for i in range(0, PrHoBin):
#        P_eheater_th_res[i] = varobject[(i)].value
#    P_eheater_th_res_df = pd.DataFrame(
#                        P_eheater_th_res, index=horizon_stamps, columns=['P_eheater_th'])
#-----------------------------------------------------------------------------
    OptResult = pd.concat([P_grid_imp_res_df,P_grid_exp_res_df, \
    P_PV2batt_res_df,P_PV2load_res_df, P_PV_exp_res_df,\
    SOC_batt_res_df, P_batt_dis_res_df, P_batt_char_res_df,\
    SOC_TES_res_df, P_TES_dis_res_df, P_TES_char_res_df,\
    P_aux_th_res_df, P_aux_gas_res_df \
    ], axis=1)   
    #,P_PV2Eheater_res_df
#    P_eheater_th_res_df, P_eheater_el_res_df\
    #print P_PV_exp_res_df, P_PV_sc_res_df
    return OptResult
   
if __name__ == '__main__':
    plt.close("all")
    

    print "I am just a poor Optimizer without any idea of running.\
    Please ask my friend OptFlex_MPC!"
   