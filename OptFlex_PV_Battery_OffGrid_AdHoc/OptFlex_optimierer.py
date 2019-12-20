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

def OptFlex_optimierer(horizon_stamps, PrHoBin, P_PV_ava, P_PV_max_mat, P_Load_max_mat, \
Load, P_sh_th, P_dhw_th, Battery, Costs):
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
    #  ------------------- Costs --------------------------------------------
    #-----------------------------------------------------------------------
#    C_gas_ar = Costs['C_gas']*np.ones((Np,1))
    C_grid_el_ar = Costs['C_grid_el']*np.ones((Np,1))
#    C_CHP_FIT_ar = Costs['C_CHP_FIT']*np.ones((Np,1))
#    C_CHP_cs_ar = Costs['C_CHP_cs']*np.ones((Np,1))
#    C_CHP_ex_ar = Costs['C_CHP_ex']*np.ones((Np,1)) # [0 bis 71]
    C_PV_FIT_ar = Costs['C_PV_FIT']*np.ones((Np,1))
    C_PV_eig_ar = Costs['C_PV_eig']*np.ones((Np,1))
    
#    C_gas = {i: C_gas_ar[i-1,0] for i in m};
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
    # -------------- Costs ----------------------------------------     
#    model.C_gas = Param(model.K, initialize= C_gas)
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
    #model.P_PV = Var(model.K, domain=NonNegativeReals, bounds = (0, 100))
    model.P_PV_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,100))
    #-------------------------- Grid ------------------------------
    model.P_grid_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,150))
    model.P_grid_imp = Var(model.K, initialize=10, domain=NonNegativeReals, bounds = (0, 150) )
    # --------------------------- Battery -----------------------
    model.SOC_batt = Var(model.K, domain=NonNegativeReals, bounds=(0,1000))
    model.P_batt_char = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
    model.P_batt_dis = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
    model.b_batt = Var(model.K, initialize=1, domain=Binary) # Laden = 1, Entladen = 0

# --------------------------------------------------------------------------
#                  OBJECTIVE 
# --------------------------------------------------------------------------
#    def obj_expression(model):
        
       # Minimize grid_export - Eigenverbrauch --- geht so nicht
       #return sum(model.P_grid_imp[k] for k in model.K)  #MIN
       
       # Maximize selfconsumption - Eigenverbrauch  
#       return sum(model.P_PV_sc[k] for k in model.K) # MAX
       
       # Minimize grid_import - Autarkie --- geht so nicht
       #return sum(model.P_grid_exp[k] for k in model.K)  #MIN
       
    def obj_expression(model):
        # Operational costs
#        return sum(model.C_grid_el[k]*model.P_grid_imp[k] for k in model.K) -\
#               sum(model.C_PV_FIT[k]*model.P_PV_exp[k] for k in model.K)# -\
                #sum(model.C_gas[k]*(model.P_aux_gas[k]+model.P_CHP_gas[k]) for k in model.K) +\
                #sum(model.C_CHP_FIT[k]*model.P_CHP_el_exp[k] for k in model.K) -\
                #sum(model.C_CHP_ex[k]*model.P_CHP_el_sc[k] for k in model.K) +\
                #sum(model.C_CHP_cs[k]*model.b_CHP_up[k] for k in model.K) +\
                #0.5*model.SOC_batt_term    
        # Microgrid
        return sum(model.P_grid_imp[k] for k in model.K) \
               +sum(model.P_PV_exp[k] for k in model.K)# -\
       
    #model.OBJ = Objective(rule=obj_expression, sense=max)
    model.OBJ = Objective(rule=obj_expression) #min
 
     # --------------------------------------------------------------------------
     #              CONSTRAINTS
     # --------------------------------------------------------------------------
     
     # Equation (2)  now eq (3) Energyconservation (or Powerconservation?)
    def ele_balance_constraint_rule(model,k):
         return model.P_Load[k] - model.P_grid_imp[k] \
             + model.P_grid_exp[k] - model.P_PV_ava[k] \
             + model.P_batt_char[k] - model.P_batt_dis[k] == 0
    model.ele_balance_constraint = \
    Constraint(model.K, rule=ele_balance_constraint_rule)
    
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
    def PV_selfcons1load_rule(model,k):
         return model.P_PV2load[k] <= model.P_Load[k] 
    model.PV_selfcons1load = \
    Constraint(model.K, rule=PV_selfcons1load_rule)
  
    def PV_selfcons1batt_rule(model,k):
         return model.P_PV2batt[k] == model.P_batt_char[k] 
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
                        
    P_PV2load_res = np.zeros(PrHoBin)
    varobject = getattr(instance, 'P_PV2load')
    for i in range(0, PrHoBin):
        P_PV2load_res[i] = varobject[(i)].value
    P_PV2load_res_df = pd.DataFrame(
                        P_PV2load_res, index=horizon_stamps, columns=['P_PV2load'])


    OptResult = pd.concat([P_grid_imp_res_df,P_grid_exp_res_df, \
    SOC_batt_res_df, P_batt_dis_res_df, P_batt_char_res_df,\
    #P_PV_res_df,\
    P_PV2load_res_df,P_PV2batt_res_df,P_PV_exp_res_df], axis=1)
    
    #print P_PV_exp_res_df, P_PV_sc_res_df
    return OptResult
   
if __name__ == '__main__':
    plt.close("all")
    

    print "I am just a poor Optimizer without any idea of running.\
    Please ask my friend OptFlex_MPC!"
   