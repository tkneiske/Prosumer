# -*- coding: utf-8 -*
"""
Created on Fri Jan 09 11:58:21 2015
Checked by tkneiske Sept 2015

@author: dhidalgo, tkneiske

"""

# OPtFlex
# Validation of INEVES V1
 

# Notes: 
# 1. Object for investigation is one MFH with a ecopower 4.7 (modulated)
# 2. Electrical and thermal profiles are taken from VDI
# 3. A perfect forecast is assumed

from __future__ import division
from pyomo.opt import SolverFactory
from pyomo.core import Var
from pyomo.environ import *
from pyomo.dae import *
#import sys
#import csv
#import OptFlex_inputvalues as ipv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def OptFlex_optimierer(horizon_stamps, PrHoBin,  \
Load,P_PV_max_mat, P_Load_max_mat, P_sh_th, P_dhw_th, P_PV_ava, Battery,\
Auxilary, ThermalStorage, CHP, Costs, CO2,PreisProfilER, PreisProfilLO, Abregel):
    #02.02.2015
    # Create a solver
    opt = SolverFactory('cplex')
    # 15.05.2015
    # Solver Options
    #opt.options['timelimit'] =  9*60 + 50  # Maimale runtime
    #opt.options['mipgap']=0.001  #Genauigkeit    
    model = AbstractModel() #Declare model of type Abstract
    #-----------------------------------------------------------------------
    # Prediction horizon 144 = 1 Tag, 72 = 12 Stunden 
    #-----------------------------------------------------------------------
    model.K = RangeSet(0, PrHoBin-1) # Maybe start with 0 or 1 ????
    Np = PrHoBin-1   # used with CHP on/off rule
    m = range(0, PrHoBin)  # used in Cost vectors
    #-----------------------------------------------------------------------
    # Creating dictionaries to initialize Param
    P_Load_max = {1: P_Load_max_mat}  # Used where?
    P_PV_max = {1: P_PV_max_mat}
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
    #  -------------- CHP ---------------------
    #----------------------------------------------------------------------- 
    T_CHP_on = int(CHP['T_CHP_on'])
    T_CHP_off =  int(CHP['T_CHP_off'])
    P_CHP_el_min = {1: CHP['P_CHP_el_min']}
    P_CHP_el_max = {1: CHP['P_CHP_el_max']}
    eta_CHP_el = {1: CHP['eta_CHP_el']}
    eta_CHP_th={1: CHP['eta_CHP_th']}
    #P_CHP_gas_ini = {1: CHP['P_CHP_gas_ini']}
    b_CHP_on_ini = {1: CHP['b_CHP_on_ini']}
    b_CHP_ini_1 = {1: CHP['b_CHP_ini_1']}
    b_CHP_ini_2 = {1: CHP['b_CHP_ini_2']}
    b_CHP_ini_3 = {1: CHP['b_CHP_ini_3']}  
     # 30.01.2015 To be modified
     #    eta_CHP_th = {}
     #    eta_CHP_th[1] = eta_CHP_th_mat;
#     ramp_CHP = {1: CHP['ramp_CHP']}
   
          
#     # For vectors
#     m = range(1,Np_mat+1) # In Python range does not consider the last value
#     print m, Np_mat
    # 04.02.2015    
    # Initial values
    # set K is related to prediction horizon Np. Set K = k_i+j|k_i
    # for j=1:Np-1
    # where k_i is any arbitrary initial time     
    

    #-----------------------------------------------------------------------
    #  ------------------- Costs --------------------------------------------
    #-----------------------------------------------------------------------
    C_gas_ar = Costs['C_gas']*np.ones((Np,1))
    #C_grid_el_ar = Costs['C_grid_el']*np.ones((Np,1))
    C_CHP_FIT_ar = Costs['C_CHP_FIT']*np.ones((Np,1))
    C_CHP_cs_ar = Costs['C_CHP_cs']*np.ones((Np,1))
    C_CHP_ex_ar = Costs['C_CHP_ex']*np.ones((Np,1)) # [0 bis 71]
    #C_PV_FIT_ar = Costs['C_PV_FIT']*np.ones((Np,1))
    
    C_gas = {i: C_gas_ar[i-1,0] for i in m};
    #C_grid_el = {i: C_grid_el_ar[i-1,0] for i in m};
    C_CHP_FIT = {i: C_CHP_FIT_ar[i-1,0] for i in m};
    #C_PV_FIT = {i: C_PV_FIT_ar[i-1,0] for i in m};
    C_CHP_cs = {i: C_CHP_cs_ar[i-1,0] for i in m};
    C_CHP_ex ={i: C_CHP_ex_ar[i-1,0] for i in m};
    
    #-----------------------------------------------------------------------
    #  ------------------- CO2 --------------------------------------------
    #-----------------------------------------------------------------------
    CO2_gas_ar = CO2['CO2_gas']*np.ones((Np,1))
    CO2_grid_ar = CO2['CO2_grid']*np.ones((Np,1))
    CO2_PV_ar = CO2['CO2_PV']*np.ones((Np,1))
    
    CO2_gas = {i: CO2_gas_ar[i-1,0] for i in m};
    CO2_grid = {i: CO2_grid_ar[i-1,0] for i in m};
    CO2_PV = {i: CO2_PV_ar[i-1,0] for i in m};
        
   
    #==============================================================================
    #     PARAMETER
    #==============================================================================
    model.I = RangeSet(1) # set I is related to scalar parameters 
#     #model.Np = Param(model.I, initialize = Np) #CHP
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
    model.P_PV_max = Param(model.I, initialize= P_PV_max)
    #---------------- Aux ----------------------------------
    model.eta_aux = Param(model.I, initialize= eta_aux)
    model.P_aux_th_max = Param(model.I, initialize= P_aux_th_max )
    model.P_aux_th_min = Param(model.I, initialize=P_aux_th_min)
    # ------------ Thermal Storage ------------------------
    model.K_TES = Param(model.I, initialize= K_TES)
    model.eta_TES_sd = Param(model.I, initialize= eta_TES_sd)
    model.eta_TES_char = Param(model.I, initialize= eta_TES_char)
    model.eta_TES_dis = Param(model.I, initialize= eta_TES_dis)
    model.SOC_TES_max = Param(model.I, initialize= SOC_TES_max)
    model.SOC_TES_min = Param(model.I, initialize= SOC_TES_min)
    model.SOC_TES_ini = Param(model.I, initialize = SOC_TES_ini)
    # ----------------- CHP ------------------------------------
    model.T_CHP_on = Param(model.I, initialize = T_CHP_on)
    model.T_CHP_off = Param(model.I, initialize = T_CHP_off)
    model.P_CHP_el_min = Param(model.I, initialize = P_CHP_el_min)
    model.P_CHP_el_max = Param(model.I, initialize= P_CHP_el_max)
    model.eta_CHP_el = Param(model.I, initialize= eta_CHP_el)
    model.eta_CHP_th = Param(model.I, initialize = eta_CHP_th)
   # model.P_CHP_gas_ini = Param(model.I, initialize = P_CHP_gas_ini)
    model.b_CHP_on_ini = Param(model.I, initialize = b_CHP_on_ini)
    model.b_CHP_ini_1 = Param(model.I, initialize = b_CHP_ini_1) 
    model.b_CHP_ini_2 = Param(model.I, initialize = b_CHP_ini_2)
    model.b_CHP_ini_3 = Param(model.I, initialize = b_CHP_ini_3)
    #model.ramp_CHP = Param(model.I, initialize= ramp_CHP)
    # -------------- Costs ----------------------------------------     
    model.C_gas = Param(model.K, initialize= C_gas)
    #model.C_grid_el = Param(model.K, initialize= C_grid_el)
    model.C_grid_el = Param(model.K, initialize= PreisProfilLO)
    #model.C_PV_FIT = Param(model.K, initialize= C_PV_FIT)
    model.C_PV_FIT = Param(model.K, initialize= PreisProfilER)
    model.C_CHP_FIT = Param(model.K, initialize= C_CHP_FIT)
    #model.C_CHP_FIT = Param(model.K, initialize= PreisProfil)
    model.C_CHP_cs = Param(model.K, initialize= C_CHP_cs)
    model.C_CHP_ex = Param(model.K, initialize= C_CHP_ex)
    
#   #va = {i_va: 0.0652 for i_va in range(1,Np_mat[0]+1)}  
     
         
#     # 04.02.2015
#     # New parameter big-M
#     M_CHP_sc = P_Load_max + P_batt_char_max_mat + P_eboiler_max_mat 
#     # M_CHP_sc  = 10 + 6 + 21.4
#     model.M_sc = Param(model.I, initialize = M_CHP_sc)
#     
#     # 04.02.2015
#     # Min. operation time for CHP
#     #model.T_CHP_on = RangeSet(1,T_CHP_on[0])
#     # At least 3 time steps
#     #model.T_CHP_on = Param(model.I, initialize = 3)
#     T_CHP_on = 3;
#     T_CHP_off = 3;
#     # the next line declares decision variables indexed by the set J 
#     # Are all decision variables in INEVES nonnegatives?
#     # Create decision variables for each element in INEVES 
#     
#     # i.e. x = [P_batt_char(k) P_batt_dis(k) P_TES_char(k) P_TES_dis(k) 
#     # P_batt_char(k+1) P_batt_dis(k+1) P_TES_char(k+1) P_TES_dis(k+1)
#     # ... P_batt_char(k+Np-1) P_batt_dis(k+Np-1) P_TES_char(k+Np-1) 
#     # P_TES_dis(k+Np-1) b_CHP_on(k:k+Np-1) P_CHP_el(k:k+Np-1) P_CHP_el_sc(k:k+Np-1) P_CHP_el_exp(k:k+Np-1)
#     # P_PV(k:k+Np-1) P_PV_SC(k:k+Np-1) P_PV_exp(k:k+Np-1) 
#     # P_grid_exp(k:k+Np-1) P_grid_imp(k:k+Np-1) b_eboil(k:k+Np-1) 
#     # b_aux(k:k+Np-1) b_batt(k:k+Np-1)  b_CHP_up(k:k+Np-1)
#     # b_CHP_down(k:k+Np-1)]' 
#     
#     
#     # -------------------------------------------------------------------------
#     # Continuos VARIABLES
#     # --------------------------------------------------------------------------
    # 10.02.2015     
    # Boundaries for P_PV_sc: 0 <= P_PV_sc <= P_Load_max + P_eboiler_max + P_batt_char_max    
    #----------------------- PV ---------------------------------------  
 #   model.P_PV_sc = Var(model.K, domain=NonNegativeReals, bounds = (0, 100))
    model.P_PV2batt = Var(model.K, domain=NonNegativeReals, bounds = (0, 100))
    model.P_PV2load = Var(model.K, domain=NonNegativeReals, bounds = (0, 100))
    model.P_PV_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,100)) 
    #-------------------------- Grid ------------------------------
    model.P_grid_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,150))
    model.P_grid_imp = Var(model.K, initialize=10, domain=NonNegativeReals, bounds = (0, 150) )
    # --------------------------- Battery -----------------------
    model.SOC_batt = Var(model.K, domain=NonNegativeReals, bounds=(0,1000))
    model.P_batt_char = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
    model.P_batt_dis = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
    model.b_batt = Var(model.K, initialize=1, domain=Binary) # Laden = 1, Entladen = 0
    # ------------------ Auxilary Gaskessel--------------------------------
    model.P_aux_th = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
    model.P_aux_gas = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
    model.b_aux = Var(model.K, domain=Binary)
    # ----------------  Thermal Storage -----------------------------------
    #???? model.SOC_batt_term = Var(domain=NonNegativeReals, bounds = (0,100))        
    model.P_TES_char = Var(model.K, domain=NonNegativeReals, bounds=(0,100))
    model.P_TES_dis = Var(model.K, domain=NonNegativeReals, bounds= (0,100))
    model.SOC_TES = Var(model.K, domain=NonNegativeReals, bounds=(0,1000))
    # ------------------ CHP -----------------------------------------------
    model.P_CHP_el = Var(model.K, domain=NonNegativeReals, bounds=(0,50))
    # 10.02.2015    
    # Boundaries for P_CHP_el_sc: 0 <= P_CHP_el_sc <= P_Load_max + P_eboiler_max + P_batt_char_max
    #model.P_CHP_el_sc = Var(model.K, domain=NonNegativeReals, bounds = (0, 50))
    model.P_CHP2batt = Var(model.K, domain=NonNegativeReals, bounds = (0, 50))
    model.P_CHP2load = Var(model.K, domain=NonNegativeReals, bounds = (0, 50))
    model.P_CHP_el_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,50))
    # Boundaries for P_grid_imp: 0 <= P_grid_imp <= P_Load_max + P_eboiler_max
    model.P_CHP_gas = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
    model.P_CHP_th = Var(model.K, domain=NonNegativeReals, bounds=(0,130))
    model.b_CHP_on = Var(model.K, domain=Binary)
    model.b_CHP_up = Var(model.K, domain=Binary)
    model.b_CHP_down = Var(model.K, domain=Binary)
#==============================================================================
     
#     # big-M auxiliary binary variables
#     model.d1_CHP_sc = Var(model.K, domain=Binary)
#     model.d2_CHP_sc = Var(model.K, domain=Binary)
     

# --------------------------------------------------------------------------
#                  OBJECTIVE 
# --------------------------------------------------------------------------
     # Equation (1)
#     # 
#     # def obj_expression(model):
#     #    return model.C_gas*sum(model.P_CHP_gas[j] + model.P_aux_gas[j] for j in model.k)\
#     #    + model.C_grid_el*sum(model.P_grid_imp[j]  for j in model.k)\ 
#     #    - model.C_CHP_FIT*sum(model.P_CHP_exp[j] for j in model.k)\ 
#     #    - model.C_PV_FIT*sum(model.P_PV_FIT[j] for j in model.k)\
#     #    + model.C_CHP_cs*sum(model.b_CHP_up[j] for j in model.k) == 0
# 
    def obj_expression(model):        
        #Minimize grid_export - Eigenverbrauch 
        #return sum(model.P_grid_imp[k] for k in model.K)  #MIN
       # Minimize grid_import - Autarkie 
       # return sum(model.P_grid_exp[k] for k in model.K)  #MIN
       
       # Maximize selfconsumption - Eigenverbrauch  
       # return sum(model.P_PV_sc[k] for k in model.K) # MAX

       # Maximize selfconsumption - Eigenverbrauch- funktioniert nicht, warum ?
       #return sum(model.P_CHP_el_sc[k] for k in model.K) # MAX
       
       
    # Operational costs
#     def obj_expression(model):# stimmt das Tanja 16.6.18 PV_FIT
          return sum(model.C_gas[k]*(model.P_aux_gas[k]+model.P_CHP_gas[k]) for k in model.K)\
                  +sum(model.C_grid_el[k]*model.P_grid_imp[k] for k in model.K)\
                  -sum(model.C_CHP_FIT[k]*model.P_CHP_el_exp[k] for k in model.K)\
                  -sum(model.C_CHP_ex[k]*model.P_CHP2load[k] for k in model.K)\
                  -sum(model.C_CHP_ex[k]*model.P_CHP2batt[k] for k in model.K)\
                  -sum(model.C_PV_FIT[k]*model.P_PV_exp[k] for k in model.K)\
                  +sum(model.C_CHP_cs[k]*model.b_CHP_up[k] for k in model.K)\
#            
                  #+0.5*model.SOC_batt_term 
#==============================================================================
       


         #return sum(model.C_gas[k]*(model.P_CHP_gas[k]*model.P_aux_gas[k]) for k in model.K) +\
#         #        sum(model.C_grid_el[k]*model.P_grid_imp[k] for k in model.K) -\
#         #        sum(model.C_CHP_FIT[k]*model.P_CHP_el_exp[k] for k in model.K) -\
#         #        sum(model.C_PV_FIT[k]*model.P_PV_exp[k] for k in model.K) -\
#         #        sum(model.C_CHP_ex[k]*model.P_CHP_el_sc[k] for k in model.K) +\
#         #        sum(model.C_CHP_cs[k]*model.b_CHP_up[k] for k in model.K)        
#         # summation(model.C_gas,model.P_CHP_gas + model.P_aux_gas) +\
#         #summation(model.C_grid_el,model.P_grid_imp) -\
#         #summation(model.C_CHP_FIT,model.P_CHP_exp) -\
#         #summation(model.C_PV_FIT,model.P_PV_FIT) -\
#         #summation(model.C_CHP_ex,model.P_CHP_el_sc) +\
#         #summation(model.C_CHP_cs,model.b_CHP_up)
#     
 
  # model.OBJ = Objective(rule=obj_expression, sense=max)
    model.OBJ = Objective(rule=obj_expression)
 
    # --------------------------------------------------------------------------
    #              CONSTRAINTS
    # --------------------------------------------------------------------------

    # ---------------------------------------------------------------------
    # Energy balance    
    # ---------------------------------------------------------------------
     
    # ---------- Electrical ----     
     # Equation (2)  now eq (3) Energyconservation (or Powerconservation?)
    def ele_balance_constraint_rule(model,k):
         return model.P_Load[k] - model.P_grid_imp[k]\
             + model.P_PV_exp[k]+ model.P_CHP_el_exp[k] - model.P_PV_ava[k]  \
             + model.P_batt_char[k] - model.P_batt_dis[k]\
             - model.P_CHP_el[k]  == 0
    model.ele_balance_constraint = \
    Constraint(model.K, rule=ele_balance_constraint_rule)

    # ------------- Thermal -----    
    # Equation (22)    
    def th_balance_constraint_rule(model,k):
        return model.P_sh_th[k] + model.P_dhw_th[k] -  model.P_aux_th[k] \
                + model.P_TES_char[k] - model.P_TES_dis[k] \
                - model.P_CHP_th[k]  == 0         
    model.th_balance_constraint = \
    Constraint(model.K, rule=th_balance_constraint_rule)
     
    # --------------------------------------------------------------------------
    # PV Self Consumption    
    # --------------------------------------------------------------------------

#==============================================================================
#     # Equation (3)  now eq. (4) Self-consumption, what can self-consume the produced energy
#     def PV_selfcons1_rule(model,k):
#          return model.P_PV_sc[k] <= model.P_Load[k] + model.P_batt_char[k] \
#          - model.P_CHP_el_sc[k]
#           # 16.02.2015 Test_ CHP_sc as a variable in this constraint
#           #return model.P_PV_sc[k] <= model.P_Load[k] + model.P_batt_char[k] +\
#           #+ model.P_eboiler_el[k] - model.P_CHP_el_sc[k]
#     model.PV_selfcons1 = \
#     Constraint(model.K, rule=PV_selfcons1_rule)
#       
#     # Self-consumption, limit for PV_SC by produced PV Power, now eq(4)
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
    def PV_selfcons1load_rule(model,k):
         return model.P_PV2load[k] <= model.P_Load[k] 
    model.PV_selfcons1load = \
    Constraint(model.K, rule=PV_selfcons1load_rule)
  
    def PV_selfcons1batt_rule(model,k):
         return model.P_PV2batt[k] == model.P_batt_char[k] - model.P_CHP2batt[k]
          # 16.02.2015 Test_ CHP_sc as a variable in this constraint
    model.PV_selfcons1batt = \
    Constraint(model.K, rule=PV_selfcons1batt_rule)
      
    def PV_selfcons2load_rule(model,k):
        return model.P_PV2load[k] <= model.P_PV_ava[k]        
    model.PV_selfcons2load = \
    Constraint(model.K, rule=PV_selfcons2load_rule)
 
    def PV_selfcons2batt_rule(model,k):
        return model.P_PV2batt[k] <= model.P_PV_ava[k]        
    model.PV_selfcons2batt = \
    Constraint(model.K, rule=PV_selfcons2batt_rule)

    def PV_Export1_rule(model,k):
        return model.P_PV_exp[k] == P_PV_ava[k] - model.P_PV2load[k] -  model.P_PV2batt[k]
    model.PV_Export1 = \
    Constraint(model.K, rule=PV_Export1_rule)

    def PV_Export2_rule(model, k):
        return model.P_PV_exp[k] == model.P_grid_exp[k] - model.P_CHP_el_exp[k]
    model.PV_Export2 = \
    Constraint(model.K, rule=PV_Export2_rule) 

    
#  --------------- Abregelung von 50% PV peak--------------------------------              
    if Abregel == 'ABon':
        def PV_Export3_rule(model,k):
            return model.P_PV_exp[k] <= model.P_PV_max[1]*0.5
        model.PV_Export3 = \
        Constraint(model.K, rule=PV_Export3_rule)
            
    
    # --------------------------------------------------------------------------
    #   CHP Self-Consumption    
    # --------------------------------------------------------------------------
#==============================================================================
#     # Equation (5) now Equation (7)
#     def CHP_selfcons1_rule(model,k):
#         return model.P_CHP_el_sc[k] <= model.P_Load[k] + model.P_batt_char[k] \
#         - model.P_PV_sc[k]
#  #        return model.P_CHP_el_sc[k] <= model.P_Load[k] + model.P_batt_char[k] + \
#  #        + model.P_eboiler_el[k] - model.P_PV_sc[k]    
#     model.CHP_selfcons1 = \
#     Constraint(model.K, rule=CHP_selfcons1_rule)
# 
#     def CHP_selfcons2_rule(model,k):
#         return model.P_CHP_el_sc[k] <= model.P_CHP_el[k]    
#     model.CHP_selfcons2 = \
#     Constraint(model.K, rule=CHP_selfcons2_rule)
#  
#     # Equation (6) now Equation (8)
#     def CHP_Export_rule(model,k):
#         return model.P_CHP_el_exp[k] == model.P_CHP_el[k] - model.P_CHP_el_sc[k]     
#     model.CHP_Export = \
#     Constraint(model.K, rule=CHP_Export_rule)
# 
#==============================================================================
    def CHP_selfcons1load_rule(model,k):
         return model.P_CHP2load[k] <= model.P_Load[k] 
    model.CHP_selfcons1load = \
    Constraint(model.K, rule=CHP_selfcons1load_rule)
  
    def CHP_selfcons1batt_rule(model,k):
         return model.P_CHP2batt[k] == model.P_batt_char[k] - model.P_PV2batt[k] 
    model.CHP_selfcons1batt = \
    Constraint(model.K, rule=CHP_selfcons1batt_rule)
      
    def CHP_selfcons2load_rule(model,k):
        return model.P_CHP2load[k] <= model.P_CHP_el[k]        
    model.CHP_selfcons2load = \
    Constraint(model.K, rule=CHP_selfcons2load_rule)
 
    def CHP_selfcons2batt_rule(model,k):
        return model.P_CHP2batt[k] <= model.P_CHP_el[k]        
    model.CHP_selfcons2batt = \
    Constraint(model.K, rule=CHP_selfcons2batt_rule)

    def CHP_Export1_rule(model,k):
        return model.P_CHP_el_exp[k] == model.P_CHP_el[k] - model.P_CHP2load[k] -  model.P_CHP2batt[k]
    model.CHP_Export1 = \
    Constraint(model.K, rule=CHP_Export1_rule)

    def CHP_Export2_rule(model, k):
        return model.P_CHP_el_exp[k] == model.P_grid_exp[k]-model.P_PV_exp[k]
    model.CHP_Export2 = \
    Constraint(model.K, rule=CHP_Export2_rule) 
#==============================================================================
#     #def CHP_selfcons3_rule(model,k):
#     #    return model.P_CHP_el_sc[k] - (model.P_Load[k] + model.P_batt_char[k] + \
#     #    + model.P_eboiler_el[k] - model.P_PV_sc[k]) +\
#     #    model.M_sc[1]*(1-model.d1_CHP_sc[k]) >= 0   
#     #model.CHP_selfcons3 = \
#     #Constraint(model.K, rule=CHP_selfcons3_rule)
#  
#     #def CHP_selfcons4_rule(model,k):
#     #    return model.P_CHP_el_sc[k] - model.P_CHP_el[k] +\
#     #    model.M_sc[1]*(1-model.d2_CHP_sc[k]) >= 0    
#     #model.CHP_selfcons4 = \
#     #Constraint(model.K, rule=CHP_selfcons4_rule)
#  
#     #def CHP_selfcons5_rule(model,k):
#     #    return model.d1_CHP_sc[k] + model.d2_CHP_sc[k] >= 1     
#     #model.CHP_selfcons5 = \
#     #Constraint(model.K, rule=CHP_selfcons5_rule)
#==============================================================================
 
     
#     # Equation (7a)   PLEASE INSERT FOR MFH  ----  TMK-----
# #     if typeofsystem=='b': ##only modulate in MFH
# #         def CHP_Modulation1_rule(model,k):
# #             return model.b_CHP_on[k]*model.P_CHP_el_Pax[1] >= model.P_CHP_el[k]
# #         
# #         model.CHP_Modulation1 = \
# #        Constraint(model.K, rule=CHP_Modulation1_rule)
# #     
# #     # Equation (7b) 
# #         def CHP_Modulation2_rule(model,k):
# #             return model.b_CHP_on[k]*model.P_CHP_el_min[1] <= model.P_CHP_el[k]
# #     
# #         model.CHP_Modulation2 = \
# #         Constraint(model.K, rule=CHP_Modulation2_rule)
# #        
# #     else:
# #         def CHP_rule(model,k):
# #             return model.P_CHP_el[k] - model.P_CHP_el_max[1]*model.b_CHP_on[k] == 0
# #             
# #         model.CHP =\
# #         Constraint(model.K, rule=CHP_rule)
# #==============================================================================
  
    # --------------------------------------------------------------------------
    #   CHP 
    # --------------------------------------------------------------------------

    #-------------- CHP Performance ------------------     
    # Equation (8) now Equation (10)
    # Just steady state performance is considered

    # ------------------------ PERFORMANCE ------------------------------------
    def CHP_el_Performance_rule(model,k):
        return model.P_CHP_el[k] == model.P_CHP_gas[k]*model.eta_CHP_el[1]          
    model.CHP_el_Performance = \
    Constraint(model.K, rule=CHP_el_Performance_rule)

    # Equation (23) now Equation (25) -- Fehler in Doku /eta_th????
    def CHP_th_Performance_rule(model,k):
        return model.P_CHP_th[k] == model.P_CHP_gas[k]*model.eta_CHP_th[1]         
    model.CHP_th_Performance = \
    Constraint(model.K, rule=CHP_th_Performance_rule)     

    # ------------------------ ON/OFF -----------------------------------------

     # --- mit "==" ohne Modulation  just on/off  mit "<=" als Grenze 
    def CHP_rule(model,k):
        return model.P_CHP_el[k] - model.P_CHP_el_max[1]*model.b_CHP_on[k] == 0         
    model.CHP =\
    Constraint(model.K, rule=CHP_rule)
    
    def CHP2_rule(model,k):
        return model.P_CHP_el[k] >= model.P_CHP_el_min[1] *model.b_CHP_on[k]
    model.CHP2 = \
    Constraint(model.K, rule=CHP2_rule)

#==============================================================================
#    now Equation (9)
#     # ---- mit Modulation    wie Aux Boiler
#     def CHP_Modulation1_rule(model,k):
#        return model.P_CHP_el[k] <= model.P_CHP_el_max[1]*model.b_CHP_on[k]
#     model.CHP_Modulation1 = \
#     Constraint(model.K, rule=CHP_Modulation1_rule)
# 
#     def CHP_Modulation2_rule(model,k):
#        return model.P_CHP_el[k] >= model.P_CHP_el_min[1]*model.b_CHP_on[k]
#     model.CHP_Modulation2 = \
#     Constraint(model.K, rule=CHP_Modulation2_rule)
#==============================================================================
           # Equation (12) now Equation (11)

    def CHP_Up_Down1_rule(model,k):
        if k == 0:
  #            return model.b_CHP_on[k] - model.b_CHP_on_ini[1] <= model.b_CHP_up[k] - \
  #                    model.b_CHP_down[k] 
            return model.b_CHP_on[k] - model.b_CHP_on_ini[1] - model.b_CHP_up[k] + \
                    model.b_CHP_down[k] == 0 
        else: 
            #  return model.b_CHP_on[k]-model.b_CHP_on[k-1] <= model.b_CHP_up[k] - \
            # model.b_CHP_down[k] 
            return model.b_CHP_on[k]-model.b_CHP_on[k-1] - model.b_CHP_up[k] + \
                     model.b_CHP_down[k] == 0     
    model.CHP_Up_Down1 = \
    Constraint(model.K, rule=CHP_Up_Down1_rule)
  
     # Equation (13) now Equation (12)
    def CHP_Up_Down2_rule(model,k):
        return model.b_CHP_up[k] + model.b_CHP_down[k] <= 1    
    model.CHP_Up_Down2 = \
    Constraint(model.K, rule=CHP_Up_Down2_rule)
    
    def CHP_min_ON_rule(model,k):# only implemented for three steps Delta_T !!!TMK
        if (k==0):
            return model.b_CHP_ini_1[1]+model.b_CHP_ini_2[1]+model.b_CHP_ini_3[1] + T_CHP_on*model.b_CHP_up[k] <= 3
        elif (k==1):
            return model.b_CHP_ini_2[1]+model.b_CHP_ini_3[1]+model.b_CHP_on[k-1] + T_CHP_on*model.b_CHP_up[k] <= 3
        elif (k==2):
            return model.b_CHP_ini_3[1]+model.b_CHP_on[k-1]+model.b_CHP_on[k-2] + T_CHP_on*model.b_CHP_up[k] <= 3        
        t_on_range = range(k+1,min(k+T_CHP_on+1,Np))        
        return sum(model.b_CHP_on[i] for i in t_on_range) - T_CHP_on*model.b_CHP_up[k] >= 0
    model.CHP_min_ON = \
    Constraint(model.K, rule=CHP_min_ON_rule)

    def CHP_min_OFF_rule(model,k): #only implemented for three steps Delta_T !!!TMK
        if (k==0):
            return T_CHP_off - (model.b_CHP_ini_1[1]+model.b_CHP_ini_2[1]+model.b_CHP_ini_3[1]) + \
            T_CHP_off*model.b_CHP_down[k] <= 3
        elif (k==1):
            return T_CHP_off - (model.b_CHP_ini_2[1]+model.b_CHP_ini_3[1]+model.b_CHP_on[0]) + \
            T_CHP_off*model.b_CHP_down[k] <= 3
        elif (k==2):
            return T_CHP_off - (model.b_CHP_ini_3[1]+model.b_CHP_on[0]+model.b_CHP_on[1]) + \
            T_CHP_off*model.b_CHP_down[k] <= 3
        t_off_range = range(k+1,min(k+T_CHP_off+1,Np))        
        return T_CHP_off - sum(model.b_CHP_on[i] for i in t_off_range) - T_CHP_off*model.b_CHP_down[k] >= 0
    model.CHP_min_OFF = \
    Constraint(model.K, rule=CHP_min_OFF_rule)

 
     # Equation (9a)
     #    def CHP_Ramp1_rule(model,k):
     #        if k == 1:
     #            return model.P_CHP_gas[k] >= model.P_CHP_gas_ini[1] - model.ramp_CHP[1] 
     #        else:
     #            return model.P_CHP_gas[k-1] - model.P_CHP_gas[k] <=  model.ramp_CHP[1]  
     #    
     #    model.CHP_Ramp1 = \
     #    Constraint(model.K, rule=CHP_Ramp1_rule)
     #    
     #    # Equation (9b)  
     #    def CHP_Ramp2_rule(model,k):
     #        if k == 1:
     #            return model.P_CHP_gas[k] <= model.P_CHP_gas_ini[1] + model.ramp_CHP[1] 
     #        else:
     #            return model.P_CHP_gas[k] - model.P_CHP_gas[k-1] <=  model.ramp_CHP[1] 
     #    
     #    model.CHP_Ramp2 = \
     #    Constraint(model.K, rule=CHP_Ramp2_rule)
     
    
 

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
             model.SOC_batt_ini[1]*model.eta_batt_sd[1] 
         else: 
             return model.SOC_batt[k] -  (model.P_batt_char[k]*model.eta_batt_char[1] - \
             model.P_batt_dis[k]/model.eta_batt_dis[1])*model.K_batt[1] == \
             model.SOC_batt[k-1]*model.eta_batt_sd[1]         
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
#==============================================================================     
#    #09.02.2015    
#   #11.02.2015 Testing SOC_Terminal as decision variable    
#    def Battery_SOC_Terminal_rule(model):
#       #return model.SOC_batt[Np] >= 9 
#        return model.SOC_batt[Np] - model.SOC_batt_term >=0
#    #
#    model.Battery_SOC_Terminal = \
#    Constraint(rule=Battery_SOC_Terminal_rule)
#==============================================================================     

#------------------------------------------------------------------------------
# ------------------    Grid model -----------------------------------------
#------------------------------------------------------------------------------
    # Grid exchange --- now eq.21
    def Grid_exp_rule(model,k):
        return model.P_grid_exp[k] == model.P_CHP_el_exp[k] + model.P_PV_exp[k]
    model.Grid_exp = \
    Constraint(model.K, rule=Grid_exp_rule)
     
    # Equation (20a) --- Grid export -- now eq.22
    def Grid_exp_batt1_rule(model,k):
        return model.P_grid_exp[k] >= 0
    model.Grid_exp_batt1 = \
    Constraint(model.K, rule=Grid_exp_batt1_rule)
     
#==============================================================================
#     # Equation (20b) --- now eq.22 ---Grid export --- Netzeinspeisung maximal PV Erzeugung
#     def Grid_exp_batt2_rule(model,k):   
#         #return model.P_grid_exp[k] - (model.P_CHP_el_max[1])*model.b_batt[k] <= 0 
#         return model.P_grid_exp[k] - (model.P_CHP_el_max[1] + model.P_PV_max[1])*model.b_batt[k] <= 0 
#     model.Grid_exp_batt2 = \
#     Constraint(model.K, rule=Grid_exp_batt2_rule)
#==============================================================================
   
    # Equation (21a)  --- Grid import --- now eq.23
    def Grid_imp_batt1_rule(model,k):
        return model.P_grid_imp[k] >= 0
    model.Grid_imp_batt1 = \
    Constraint(model.K, rule=Grid_imp_batt1_rule)
    
    # Equation (21b) --- Grid import --- now eq.23 --- no grid import for battery
    def Grid_imp_batt2_rule(model,k):
       return model.P_grid_imp[k] - (model.P_Load_max[1] )*\
       (1-model.b_batt[k]) <= 0
#       return model.P_grid_imp[k] - (model.P_Load_max[1] + model.P_eboiler_max[1]))*\
#       (1-model.b_batt[k]) <= 0
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
# ------------------    Thermal Storage ----------------------------------------
#------------------------------------------------------------------------------
    # Equation (24)
    def TES_rule(model,k):
        if k == 0:
            return model.SOC_TES[k]  - (model.P_TES_char[k]*model.eta_TES_char[1] - \
                    model.P_TES_dis[k]/model.eta_TES_dis[1])*model.K_TES[1]== \
                    model.SOC_TES_ini[1]*model.eta_TES_sd[1] 
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
       return model.P_TES_char[k]  - model.P_CHP_th[k] - model.P_aux_th[k]== 0  
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
    
#==============================================================================
#      #09.02.2015    
#     def TES_SOC_Terminal_rule(model):
#         return model.SOC_TES[Np] >= 10
#         #return model.SOC_TES[Np] - model.SOC_TES_term >= 0
#     #
#     model.TES_SOC_Terminal = \
#     Constraint(rule=TES_SOC_Terminal_rule)
#        
#==============================================================================
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

#    On_Off_batt = np.zeros(PrHoBin)
#    varobject = getattr(instance, 'b_batt')
#    for i in range(0, PrHoBin):
#        On_Off_batt[i] = varobject[(i)].value
#    On_Off_batt_df = pd.DataFrame(
#                        On_Off_batt, index=horizon_stamps, columns=['b_batt'])
    #On_Off_batt_df.plot()                        
    
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
    P_PV2load_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_PV2load')
    for i in range(0, PrHoBin):
        P_PV2load_res[i] = varobject[(i)].value
    P_PV2load_res_df = pd.DataFrame(
                        P_PV2load_res, index=horizon_stamps, columns=['P_PV2load'])

    P_PV2batt_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_PV2batt')
    for i in range(0, PrHoBin):
        P_PV2batt_res[i] = varobject[(i)].value
    P_PV2batt_res_df = pd.DataFrame(
                        P_PV2batt_res, index=horizon_stamps, columns=['P_PV2batt'])

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

    
    # --------------- CHP ------------------------------------------
    P_CHP_el_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_CHP_el')
    for i in range(0, PrHoBin):
        P_CHP_el_res[i] = varobject[(i)].value
    P_CHP_el_res_df = pd.DataFrame(
                        P_CHP_el_res, index=horizon_stamps, columns=['P_CHP_el'])

#==============================================================================
#     P_CHP_el_sc_res = np.zeros(PrHoBin)
#     varobject = getattr(instance, 'P_CHP_el_sc')
#     for i in range(0, PrHoBin):
#         P_CHP_el_sc_res[i] = varobject[(i)].value
#     P_CHP_el_sc_res_df = pd.DataFrame(
#                         P_CHP_el_sc_res, index=horizon_stamps, columns=['P_CHP_el_sc'])
#    
#==============================================================================
    P_CHP2batt_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_CHP2batt')
    for i in range(0, PrHoBin):
        P_CHP2batt_res[i] = varobject[(i)].value
    P_CHP2batt_res_df = pd.DataFrame(
                        P_CHP2batt_res, index=horizon_stamps, columns=['P_CHP2batt'])

    P_CHP2load_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_CHP2load')
    for i in range(0, PrHoBin):
        P_CHP2load_res[i] = varobject[(i)].value
    P_CHP2load_res_df = pd.DataFrame(
                        P_CHP2load_res, index=horizon_stamps, columns=['P_CHP2load'])

    P_CHP_el_exp_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_CHP_el_exp')
    for i in range(0, PrHoBin):
        P_CHP_el_exp_res[i] = varobject[(i)].value
    P_CHP_el_exp_res_df = pd.DataFrame(
                        P_CHP_el_exp_res, index=horizon_stamps, columns=['P_CHP_el_exp'])

    P_CHP_th_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_CHP_th')
    for i in range(0, PrHoBin):
        P_CHP_th_res[i] = varobject[(i)].value
    P_CHP_th_res_df = pd.DataFrame(
                        P_CHP_th_res, index=horizon_stamps, columns=['P_CHP_th'])

    b_CHP_on_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'b_CHP_on')
    for i in range(0, PrHoBin):
        b_CHP_on_res[i] = varobject[(i)].value
    b_CHP_on_res_df = pd.DataFrame(
                        b_CHP_on_res, index=horizon_stamps, columns=['b_CHP_on'])

    P_CHP_gas = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_CHP_gas')
    for i in range(0, PrHoBin):
        P_CHP_gas[i] = varobject[(i)].value
    P_CHP_gas_df = pd.DataFrame(
                        P_CHP_gas, index=horizon_stamps, columns=['P_CHP_gas'])

    # -------------------------------------------------------------------------
    
    OptResult = pd.concat([P_grid_imp_res_df,P_grid_exp_res_df, \
    P_PV2batt_res_df,P_PV2load_res_df,P_PV_exp_res_df,\
    SOC_batt_res_df, P_batt_dis_res_df, P_batt_char_res_df,\
    SOC_TES_res_df, P_TES_dis_res_df, P_TES_char_res_df,\
    P_aux_th_res_df, P_aux_gas_res_df, \
    P_CHP2batt_res_df,P_CHP2load_res_df,P_CHP_el_exp_res_df,P_CHP_th_res_df,\
    P_CHP_el_res_df,b_CHP_on_res_df,P_CHP_gas_df\
    ], axis=1)
#    OptResult = pd.concat([P_grid_imp_res_df,P_grid_exp_res_df, \
#    SOC_batt_res_df, P_batt_dis_res_df, P_batt_char_res_df,\
#    SOC_TES_res_df, P_TES_dis_res_df, P_TES_char_res_df,\
#    P_PV_sc_res_df,P_PV_exp_res_df, P_aux_th_res_df, P_aux_gas_res_df, \
#    P_eboiler_th_res_df, P_eboiler_el_res_df], axis=1)
       
    return OptResult
   
def OptFlex_optimierer_dummy(day_stamps_date, BIN):

    P_grid_imp_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_Grid_imp'])                              
    P_grid_exp_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_Grid_exp'])                              
    P_PV2batt_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_PV2batt'])
    P_PV2load_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_PV2load'])
    P_PV_exp_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_PV_exp'])
    SOC_batt_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['SOC_batt'])
    P_batt_dis_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_batt_dis'])
    P_batt_char_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_batt_char'])
    SOC_TES_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['SOC_TES'])
    P_TES_dis_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_TES_dis'])
    P_TES_char_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_TES_char'])
    P_aux_th_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_aux_th'])
    P_aux_gas_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_aux_gas'])
    P_CHP2batt_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_CHP2batt'])
    P_CHP2load_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_CHP2load'])
    P_CHP_el_exp_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_CHP_el'])
    P_CHP_th_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_CHP_th'])
    P_CHP_el_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_CHP_el'])
    b_CHP_on_res_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['b_CHP_on'])
    P_CHP_gas_df = pd.DataFrame(np.ones(BIN), index=day_stamps_date, columns=['P_CHP_gas'])
        
    OptResult = pd.concat([P_grid_imp_res_df,P_grid_exp_res_df, \
    P_PV2batt_res_df,P_PV2load_res_df,P_PV_exp_res_df,\
    SOC_batt_res_df, P_batt_dis_res_df, P_batt_char_res_df,\
    SOC_TES_res_df, P_TES_dis_res_df, P_TES_char_res_df,\
    P_aux_th_res_df, P_aux_gas_res_df, \
    P_CHP2batt_res_df,P_CHP2load_res_df,P_CHP_el_exp_res_df,P_CHP_th_res_df,\
    P_CHP_el_res_df,b_CHP_on_res_df,P_CHP_gas_df\
    ], axis=1)   
    
    return OptResult   
   
if __name__ == '__main__':
    plt.close("all")
    

    print "I am just a poor Optimizer without any idea of running.\
    Please ask my friend OptFlex_MPC!"
   