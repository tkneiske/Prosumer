# -*- coding: utf-8 -*-
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
from coopr.pyomo import *
#from coopr.opt import SolverFactory
from numpy import *
#from import coopr.environ
from pyomo.environ import *
#import sys
#import csv
import inputvalues as ipv
import matplotlib.pyplot as plt

def INEVES_Opt(eta_CHP_th_mat,P_eboiler_min_mat,P_Load_max,Np_mat,P_CHP_el_min_mat,\
P_CHP_el_max_mat,eta_CHP_el_mat,ramp_CHP_mat,eta_batt_sd_mat,eta_batt_char_mat,\
eta_batt_dis_mat,K_batt_mat,P_batt_char_max_mat,P_batt_dis_max_mat,eta_boiler_mat,\
P_PV_max_mat,eta_aux_mat,C_gas_mat,C_grid_el_mat,C_CHP_FIT_mat,C_PV_FIT_mat,\
C_CHP_cs_mat,K_TES_mat,eta_TES_sd_mat,eta_TES_char_mat,eta_TES_dis_mat,\
P_aux_th_max_mat,P_aux_th_min_mat,P_eboiler_max_mat,SOC_batt_max_mat,\
SOC_batt_min_mat,SOC_TES_max_mat,SOC_TES_min_mat,C_CHP_ex_mat,Load_mat,\
P_sh_th_mat,P_dhw_th_mat,P_PV_ava_mat,P_CHP_gas_ini_mat,b_CHP_on_ini_mat,\
SOC_batt_ini_mat,SOC_TES_ini_mat):    

    #02.02.2015
    # Create a solver
    opt = SolverFactory('cplex')
    # 15.05.2015
    # Solver Options
    #opt.options['timelimit'] =  9*60 + 50  # Maimale runtime
    #opt.options['mipgap']=0.001  #Genauigkeit
    
    model = AbstractModel() #Declare model of type Abstract

    # Creating dictionaries to initialize Param
    # For constants

    Np = 72;   #Prediction horizon welcher Zeitraum 3 Stunden 30 Stunden ??? (TMK)
    
    P_CHP_el_min = {1: P_CHP_el_min_mat}
    P_CHP_el_max = {1: P_CHP_el_max_mat}
    eta_CHP_el = {1: eta_CHP_el_mat }
    # 30.01.2015 To be modified
    #    eta_CHP_th = {}
    #    eta_CHP_th[1] = eta_CHP_th_mat;
    eta_CHP_th={1: eta_CHP_th_mat }
    ramp_CHP = {1: ramp_CHP_mat }
    eta_batt_sd = {1: eta_batt_sd_mat}
    eta_batt_char = {1 : eta_batt_char_mat}
    eta_batt_dis = {1 : eta_batt_dis_mat}
    K_batt = {1: K_batt_mat}
    P_batt_char_max = {1: P_batt_char_max_mat}
    P_batt_dis_max = {1: P_batt_dis_max_mat}
    eta_eboiler = {1: eta_boiler_mat}
    P_PV_max = {1: P_PV_max_mat}
    eta_aux = {1: eta_aux_mat }
    
    K_TES = {1: K_TES_mat}
    eta_TES_sd = {1: eta_TES_sd_mat}
    eta_TES_char = {1: eta_TES_char_mat}
    eta_TES_dis = {1: eta_TES_dis_mat}
    P_aux_th_max = {1: P_aux_th_max_mat}
    P_aux_th_min = {1: P_aux_th_min_mat}
    P_eboiler_max = {1: P_eboiler_max_mat}
    P_eboiler_min = {1: P_eboiler_min_mat}

    SOC_batt_max =  {1: SOC_batt_max_mat}
    SOC_batt_min = {1: SOC_batt_min_mat}
    SOC_TES_max = {1: SOC_TES_max_mat}
    SOC_TES_min = {1: SOC_TES_min_mat}
    
    
    # For vectors
    m = range(1,Np_mat+1) # In Python range does not consider the last value
    print m, Np_mat
    Load = {i: Load_mat[i-1] for i in m}; 
    P_sh_th = {i: P_sh_th_mat[i-1] for i in m};
    # print P_sh_th 
    # Fußbodenheizung is not yet included
    # P_fbh_th = {i: P_fbh_th_mat[i-1] for i in m};
    P_dhw_th = {i: P_dhw_th_mat[i-1] for i in m};
    P_PV_ava = {i: P_PV_ava_mat[i-1] for i in m};
    # Costs are also vectors
    C_gas = {i: C_gas_mat[i-1,0] for i in m};
    C_grid_el = {i: C_grid_el_mat [i-1,0] for i in m};
    C_CHP_FIT = {i: C_CHP_FIT_mat[i-1,0] for i in m};
    C_PV_FIT = {i: C_PV_FIT_mat[i-1,0] for i in m};
    C_CHP_cs = {i: C_CHP_cs_mat[i-1,0] for i in m};
    C_CHP_ex ={i: C_CHP_ex_mat[i-1,0] for i in m};
    
    # 04.02.2015    
    # Initial values
    P_CHP_gas_ini = {1: P_CHP_gas_ini_mat}
    b_CHP_on_ini = {1: b_CHP_on_ini_mat}
    SOC_batt_ini = {1: SOC_batt_ini_mat}
    SOC_TES_ini = {1: SOC_TES_ini_mat}
    # set K is related to prediction horizon Np. Set K = k_i+j|k_i
    # for j=1:Np-1
    # where k_i is any arbitrary initial time
    model.K = RangeSet(1,Np) 
    
    
    # Parameters
    model.I = RangeSet(1) # set I is related to scalar parameters 
    #model.Np = Param(model.I, initialize = Np)
    #model.P_CHP_el_min = Param(domain=NonNegativeReals, initialize= P_CHP_el_min)
    model.P_CHP_el_min = Param(model.I, initialize = P_CHP_el_min)
    model.P_CHP_el_max = Param(model.I, initialize= P_CHP_el_max)
    #model.P_CHP_el_max = Param(model.I, initialize= 2.7)
    model.eta_CHP_el = Param(model.I, initialize= eta_CHP_el)
    model.eta_CHP_th = Param(model.I, initialize = eta_CHP_th)
    model.ramp_CHP = Param(model.I, initialize= ramp_CHP)
    model.eta_batt_sd = Param(model.I, initialize= eta_batt_sd)
    model.eta_batt_char = Param(model.I, initialize= eta_batt_char)
    model.eta_batt_dis = Param(model.I, initialize= eta_batt_dis)
    model.K_batt = Param(model.I, initialize= K_batt)
    #model.P_batt_char_max = Param(model.I, initialize= P_batt_char_max)
    #model.P_batt_dis_max = Param(model.I, initialize= P_batt_dis_max)
    #17.02.2015 Experiment no Battery 
    #Change values to 0
    model.P_batt_char_max = Param(model.I, initialize= P_batt_char_max)
    model.P_batt_dis_max = Param(model.I, initialize= P_batt_dis_max)
    model.eta_eboiler = Param(model.I, initialize= eta_eboiler)
    #model.P_PV_max = Param(model.I, initialize= P_PV_max)
    model.P_PV_max = Param(model.I, initialize= P_PV_max )
    model.eta_aux = Param(model.I, initialize= eta_aux)
    
    
    model.K_TES = Param(model.I, initialize= K_TES)
    model.eta_TES_sd = Param(model.I, initialize= eta_TES_sd)
    model.eta_TES_char = Param(model.I, initialize= eta_TES_char)
    model.eta_TES_dis = Param(model.I, initialize= eta_TES_dis)
    #model.P_aux_th_max = Param(model.I, initialize= P_aux_th_max)
    model.P_aux_th_max = Param(model.I, initialize= P_aux_th_max )
    model.P_aux_th_min = Param(model.I, initialize=P_aux_th_min)
    #model.P_eboiler_max = Param(model.I, initialize= P_eboiler_max) # in  [kWel]
    #model.P_eboiler_max = Param(model.I, initialize= 20) # in  [kWel]
    ####11.05.2ß11 probe 
    model.P_eboiler_min = Param(model.I, initialize= P_eboiler_min)
    model.P_eboiler_max = Param(model.I, initialize= P_eboiler_max)
   
    model.SOC_batt_max =  Param(model.I, initialize= SOC_batt_max)
    model.SOC_batt_min = Param(model.I, initialize= SOC_batt_min)
    model.SOC_TES_max = Param(model.I, initialize= SOC_TES_max)
    model.SOC_TES_min = Param(model.I, initialize= SOC_TES_min)
    # Vectors
    
    model.P_Load = Param(model.K, initialize= Load)
    model.P_sh_th = Param(model.K, initialize= P_sh_th)
    # model.P_fbh_th = Param(model.K,domain=NonNegativeReals)
    model.P_dhw_th = Param(model.K, initialize= P_dhw_th)
    model.P_PV_ava = Param(model.K, initialize= P_PV_ava)
    #model.C_gas = Param(model.K, initialize= C_gas)
    #va = {i_va: 0.0652 for i_va in range(1,Np_mat[0]+1)}
    
    model.C_gas = Param(model.K, initialize= C_gas)
    model.C_grid_el = Param(model.K, initialize= C_grid_el)
    model.C_CHP_FIT = Param(model.K, initialize= C_CHP_FIT)
    model.C_PV_FIT = Param(model.K, initialize= C_PV_FIT)
    model.C_CHP_cs = Param(model.K, initialize= C_CHP_cs)
    model.C_CHP_ex = Param(model.K, initialize= C_CHP_ex)
    
    
    # Initial values -> To be integrated with Matlab
    model.P_CHP_gas_ini = Param(model.I, initialize = P_CHP_gas_ini)
    model.b_CHP_on_ini = Param(model.I, initialize = b_CHP_on_ini)
    model.SOC_batt_ini = Param(model.I, initialize = SOC_batt_ini)
    model.SOC_TES_ini = Param(model.I, initialize = SOC_TES_ini)
    model.P_Load_max = Param(model.I, initialize = P_Load_max )
    
    # 04.02.2015
    # New parameter big-M
    M_CHP_sc = P_Load_max + P_batt_char_max_mat + P_eboiler_max_mat 
   # M_CHP_sc  = 10 + 6 + 21.4
    model.M_sc = Param(model.I, initialize = M_CHP_sc)
    
    # 04.02.2015
    # Min. operation time for CHP
    #model.T_CHP_on = RangeSet(1,T_CHP_on[0])
    # At least 3 time steps
    #model.T_CHP_on = Param(model.I, initialize = 3)
    T_CHP_on = 3;
    T_CHP_off = 3;
    # the next line declares decision variables indexed by the set J 
    # Are all decision variables in INEVES nonnegatives?
    # Create decision variables for each element in INEVES 
    
    # i.e. x = [P_batt_char(k) P_batt_dis(k) P_TES_char(k) P_TES_dis(k) 
    # P_batt_char(k+1) P_batt_dis(k+1) P_TES_char(k+1) P_TES_dis(k+1)
    # ... P_batt_char(k+Np-1) P_batt_dis(k+Np-1) P_TES_char(k+Np-1) 
    # P_TES_dis(k+Np-1) b_CHP_on(k:k+Np-1) P_CHP_el(k:k+Np-1) P_CHP_el_sc(k:k+Np-1) P_CHP_el_exp(k:k+Np-1)
    # P_PV(k:k+Np-1) P_PV_SC(k:k+Np-1) P_PV_exp(k:k+Np-1) 
    # P_grid_exp(k:k+Np-1) P_grid_imp(k:k+Np-1) b_eboil(k:k+Np-1) 
    # b_aux(k:k+Np-1) b_batt(k:k+Np-1)  b_CHP_up(k:k+Np-1)
    # b_CHP_down(k:k+Np-1)]' 
    
    
    # --------------------------------------------------------------------------
    # At a single time step for the full model there are 18 decision var.
    # Continuos variables
    # --------------------------------------------------------------------------
   
    model.P_batt_char = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
    model.P_batt_dis = Var(model.K, domain=NonNegativeReals, bounds = (0,60))
    model.P_TES_char = Var(model.K, domain=NonNegativeReals, bounds=(0,100))
    model.P_TES_dis = Var(model.K, domain=NonNegativeReals, bounds= (0,100))
    model.P_CHP_el = Var(model.K, domain=NonNegativeReals, bounds=(0,50))
    # 10.02.2015    
    # Boundaries for P_CHP_el_sc: 0 <= P_CHP_el_sc <= P_Load_max + P_eboiler_max + P_batt_char_max
    model.P_CHP_el_sc = Var(model.K, domain=NonNegativeReals, bounds = (0, 50))
    model.P_CHP_el_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,50))
    model.P_PV = Var(model.K, domain=NonNegativeReals, bounds = (0,100))
    # 10.02.2015    
    # Boundaries for P_PV_sc: 0 <= P_PV_sc <= P_Load_max + P_eboiler_max + P_batt_char_max    
    model.P_PV_sc = Var(model.K, domain=NonNegativeReals, bounds = (0, 100))
    model.P_PV_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,100))
    model.P_grid_exp = Var(model.K, domain=NonNegativeReals, bounds = (0,150))
    # 10.02.2015     
    # Boundaries for P_grid_imp: 0 <= P_grid_imp <= P_Load_max + P_eboiler_max
    model.P_grid_imp = Var(model.K, domain=NonNegativeReals, bounds = (0, 100 + 200) )
    model.P_eboiler_el = Var(model.K, domain=NonNegativeReals, bounds =(0,200))
    model.P_eboiler_th = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
    model.SOC_batt = Var(model.K, domain=NonNegativeReals, bounds=(0,1000))
    model.SOC_TES = Var(model.K, domain=NonNegativeReals, bounds=(0,1000))
    
    # Auxiliary variables
    model.P_CHP_gas = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
    model.P_aux_th = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
    model.P_CHP_th = Var(model.K, domain=NonNegativeReals, bounds=(0,130))
    model.P_aux_gas = Var(model.K, domain=NonNegativeReals, bounds=(0,200))
    # Binary variables
    model.b_CHP_on = Var(model.K, domain=Binary)
    model.b_eboiler = Var(model.K, domain=Boolean)
    model.b_aux = Var(model.K, domain=Binary)
    model.b_batt = Var(model.K, domain=Binary)
    model.b_CHP_up = Var(model.K, domain=Binary)
    model.b_CHP_down = Var(model.K, domain=Binary)
    
    # big-M auxiliary binary variables
    model.d1_CHP_sc = Var(model.K, domain=Binary)
    model.d2_CHP_sc = Var(model.K, domain=Binary)
    model.d1_PV_sc = Var(model.K, domain=Binary)
    model.d2_PV_sc = Var(model.K, domain=Binary)
    
    # 11.02.2015 Battery terminal constraint as variable
    model.SOC_batt_term = Var(domain=NonNegativeReals, bounds = (0,100)) 
    model.SOC_TES_term = Var(domain=NonNegativeReals, bounds = (0,100)) 
    # Equation (1)
    # 
    # def obj_expression(model):
    #    return model.C_gas*sum(model.P_CHP_gas[j] + model.P_aux_gas[j] for j in model.k)\
    #    + model.C_grid_el*sum(model.P_grid_imp[j]  for j in model.k)\ 
    #    - model.C_CHP_FIT*sum(model.P_CHP_exp[j] for j in model.k)\ 
    #    - model.C_PV_FIT*sum(model.P_PV_FIT[j] for j in model.k)\
    #    + model.C_CHP_cs*sum(model.b_CHP_up[j] for j in model.k) == 0

    # --------------------------------------------------------------------------
    #               OBJECTIVE 
    # --------------------------------------------------------------------------
       
    def obj_expression(model):
        # Operational costs
        return sum(model.C_gas[k]*(model.P_aux_gas[k]+model.P_CHP_gas[k]) for k in model.K) +\
                sum(model.C_grid_el[k]*model.P_grid_imp[k] for k in model.K) -\
                sum(model.C_CHP_FIT[k]*model.P_CHP_el_exp[k] for k in model.K) -\
                sum(model.C_PV_FIT[k]*model.P_PV_exp[k] for k in model.K) -\
                sum(model.C_CHP_ex[k]*model.P_CHP_el_sc[k] for k in model.K) +\
                sum(model.C_CHP_cs[k]*model.b_CHP_up[k] for k in model.K) +\
                0.5*model.SOC_batt_term 
#        return sum(model.P_grid_imp[k] for k in model.K)  ##MINIMIZER
        #return sum(model.C_gas[k]*(model.P_CHP_gas[k]*model.P_aux_gas[k]) for k in model.K) +\
        #        sum(model.C_grid_el[k]*model.P_grid_imp[k] for k in model.K) -\
        #        sum(model.C_CHP_FIT[k]*model.P_CHP_el_exp[k] for k in model.K) -\
        #        sum(model.C_PV_FIT[k]*model.P_PV_exp[k] for k in model.K) -\
        #        sum(model.C_CHP_ex[k]*model.P_CHP_el_sc[k] for k in model.K) +\
        #        sum(model.C_CHP_cs[k]*model.b_CHP_up[k] for k in model.K)        
        # summation(model.C_gas,model.P_CHP_gas + model.P_aux_gas) +\
        #summation(model.C_grid_el,model.P_grid_imp) -\
        #summation(model.C_CHP_FIT,model.P_CHP_exp) -\
        #summation(model.C_PV_FIT,model.P_PV_FIT) -\
        #summation(model.C_CHP_ex,model.P_CHP_el_sc) +\
        #summation(model.C_CHP_cs,model.b_CHP_up)
    
    model.OBJ = Objective(rule=obj_expression)
    

    # --------------------------------------------------------------------------
    #              CONSTRAINTS
    # --------------------------------------------------------------------------
       
    # Equation (2)
    def ele_balance_constraint_rule(model,k):
        return model.P_Load[k] + model.P_batt_char[k] + model.P_eboiler_el[k] \
        + model.P_grid_exp[k] - model.P_CHP_el[k] - model.P_PV[k] \
        -  model.P_batt_dis[k] - model.P_grid_imp[k] == 0
    
    model.ele_balance_constraint = \
    Constraint(model.K, rule=ele_balance_constraint_rule)
       
    # Equation (3) 
    def PV_selfcons1_rule(model,k):
        return model.P_PV_sc[k] <= model.P_Load[k] + model.P_batt_char[k] +\
        + model.P_eboiler_el[k]
    # 16.02.2015 Test_ CHP_sc as a variable in this constraint
        #return model.P_PV_sc[k] <= model.P_Load[k] + model.P_batt_char[k] +\
        #+ model.P_eboiler_el[k] - model.P_CHP_el_sc[k]
    
    model.PV_selfcons1 = \
    Constraint(model.K, rule=PV_selfcons1_rule)
    
    def PV_selfcons2_rule(model,k):
        return model.P_PV_sc[k] <= model.P_PV[k]
    
    model.PV_selfcons2 = \
    Constraint(model.K, rule=PV_selfcons2_rule)
       
    def PV_selfcons3_rule(model,k):
        return model.P_PV_sc[k] - (model.P_Load[k] + model.P_batt_char[k] + \
        + model.P_eboiler_el[k]) +\
        model.M_sc[1]*(1-model.d1_PV_sc[k]) >= 0
    # 16.02.2015 Test_ CHP_sc as a variable in this constraint
        #return model.P_PV_sc[k] - (model.P_Load[k] + model.P_batt_char[k] + \
        #+ model.P_eboiler_el[k]) - model.P_CHP_el_sc[k] +\
        #model.M_sc[1]*(1-model.d1_PV_sc[k]) >= 0
    
    model.PV_selfcons3 = \
    Constraint(model.K, rule=PV_selfcons3_rule)
    
    def PV_selfcons4_rule(model,k):
        return model.P_PV_sc[k] - model.P_PV[k] +\
        model.M_sc[1]*(1-model.d2_PV_sc[k]) >= 0
    
    model.PV_selfcons4 = \
    Constraint(model.K, rule=PV_selfcons4_rule)
    
    def PV_selfcons5_rule(model,k):
        return model.d1_PV_sc[k] + model.d2_PV_sc[k] >= 1
    
    model.PV_selfcons5 = \
    Constraint(model.K, rule=PV_selfcons5_rule)
    
    
    # Equation (4) 
    def PV_Export_rule(model,k):
        return model.P_PV_exp[k] == model.P_PV[k] - model.P_PV_sc[k]
    
    model.PV_Export = \
    Constraint(model.K, rule=PV_Export_rule)
    
    def PV_rule(model,k):
        return model.P_PV[k] <= model.P_PV_ava[k]
    
    model.PV_rule = \
    Constraint(model.K, rule=PV_rule)
    
    # Equation (5) 
    def CHP_selfcons1_rule(model,k):
        return model.P_CHP_el_sc[k] <= model.P_Load[k] + model.P_batt_char[k] + \
        + model.P_eboiler_el[k] - model.P_PV_sc[k]
    
    model.CHP_selfcons1 = \
    Constraint(model.K, rule=CHP_selfcons1_rule)
    
    def CHP_selfcons2_rule(model,k):
        return model.P_CHP_el_sc[k] <= model.P_CHP_el[k]
    
    model.CHP_selfcons2 = \
    Constraint(model.K, rule=CHP_selfcons2_rule)
    
    def CHP_selfcons3_rule(model,k):
        return model.P_CHP_el_sc[k] - (model.P_Load[k] + model.P_batt_char[k] + \
        + model.P_eboiler_el[k] - model.P_PV_sc[k]) +\
        model.M_sc[1]*(1-model.d1_CHP_sc[k]) >= 0
    
    model.CHP_selfcons3 = \
    Constraint(model.K, rule=CHP_selfcons3_rule)
    
    def CHP_selfcons4_rule(model,k):
        return model.P_CHP_el_sc[k] - model.P_CHP_el[k] +\
        model.M_sc[1]*(1-model.d2_CHP_sc[k]) >= 0
    
    model.CHP_selfcons4 = \
    Constraint(model.K, rule=CHP_selfcons4_rule)
    
    def CHP_selfcons5_rule(model,k):
        return model.d1_CHP_sc[k] + model.d2_CHP_sc[k] >= 1
    
    model.CHP_selfcons5 = \
    Constraint(model.K, rule=CHP_selfcons5_rule)
    
    # Equation (6) 
    def CHP_Export_rule(model,k):
        return model.P_CHP_el_exp[k] == model.P_CHP_el[k] - model.P_CHP_el_sc[k]
    
    model.CHP_Export = \
    Constraint(model.K, rule=CHP_Export_rule)
    
    # Equation (7a)   PLEASE INSERT FOR MFH  ----  TMK-----
    #==============================================================================
#     if typeofsystem=='b': ##only modulate in MFH
#         def CHP_Modulation1_rule(model,k):
#             return model.b_CHP_on[k]*model.P_CHP_el_max[1] >= model.P_CHP_el[k]
#         
#         model.CHP_Modulation1 = \
#        Constraint(model.K, rule=CHP_Modulation1_rule)
#     
#     # Equation (7b) 
#         def CHP_Modulation2_rule(model,k):
#             return model.b_CHP_on[k]*model.P_CHP_el_min[1] <= model.P_CHP_el[k]
#     
#         model.CHP_Modulation2 = \
#         Constraint(model.K, rule=CHP_Modulation2_rule)
#        
#     else:
#         def CHP_rule(model,k):
#             return model.P_CHP_el[k] - model.P_CHP_el_max[1]*model.b_CHP_on[k] == 0
#             
#         model.CHP =\
#         Constraint(model.K, rule=CHP_rule)
#==============================================================================
   
    
#    def CHP_rule(model,k):
#            return model.P_CHP_el[k] - model.P_CHP_el_max[1]*model.b_CHP_on[k] == 0
#         
#    model.CHP =\
#    Constraint(model.K, rule=CHP_rule)
    # Equation (8)
    # Just steady state performance is considered
    def CHP_el_Performance_rule(model,k):
        return model.P_CHP_el[k] == model.P_CHP_gas[k]*model.eta_CHP_el[1]     
    
    model.CHP_el_Performance = \
    Constraint(model.K, rule=CHP_el_Performance_rule)
    
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
    
    # Equation (10) and equation (11) are not yet implemented
    
    # Equation (12)
    def CHP_Up_Down1_rule(model,k):
        if k == 1:
            return model.b_CHP_on[k] - model.b_CHP_on_ini[1] - model.b_CHP_up[k] + \
                    model.b_CHP_down[k] == 0 
        else: 
            return model.b_CHP_on[k]-model.b_CHP_on[k-1] - model.b_CHP_up[k] + \
        model.b_CHP_down[k] == 0
    
    model.CHP_Up_Down1 = \
    Constraint(model.K, rule=CHP_Up_Down1_rule)
    
    # Equation (13)
    def CHP_Up_Down2_rule(model,k):
        return model.b_CHP_up[k] + model.b_CHP_down[k] <= 1
    #
    model.CHP_Up_Down2 = \
    Constraint(model.K, rule=CHP_Up_Down2_rule)
    
    def CHP_min_ON_rule(model,k):
        #model.b_CHP_on[(k + t_CHP_on for t_CHP_on in model.T_CHP_on)] >= model.b_CHP_up[k]
        t_on_range = range(k+1,min(k+T_CHP_on+1,Np))        
        #if k >=70:
        #    return Constraint.Skip
        return sum(model.b_CHP_on[i] for i in t_on_range) - T_CHP_on*model.b_CHP_up[k] >= 0
        #return model.b_CHP_on[k+1] + model.b_CHP_on[k+2] + model.b_CHP_on[k+3] -3*model.b_CHP_up[k]  >= 0
    model.CHP_min_ON = \
    Constraint(model.K, rule=CHP_min_ON_rule)
    
    def CHP_min_OFF_rule(model,k):
        #model.b_CHP_on[(k + t_CHP_on for t_CHP_on in model.T_CHP_on)] >= model.b_CHP_up[k]
        t_off_range = range(k+1,min(k+T_CHP_off+1,Np))        
        #if k >=70:
        #    return Constraint.Skip
        return T_CHP_off - sum(model.b_CHP_on[i] for i in t_off_range) - T_CHP_off*model.b_CHP_down[k] >= 0
        #return model.b_CHP_on[k+1] + model.b_CHP_on[k+2] + model.b_CHP_on[k+3] -3*model.b_CHP_up[k]  >= 0
    model.CHP_min_OFF = \
    Constraint(model.K, rule=CHP_min_OFF_rule)
    
    # Equation (14)
    def Battery_rule(model,k):
        if k == 1:
            return model.SOC_batt[k] - (model.P_batt_char[k]*model.eta_batt_char[1] - \
        model.P_batt_dis[k]/model.eta_batt_dis[1])*model.K_batt[1] == model.SOC_batt_ini[1]*model.eta_batt_sd[1] 
        else: 
            return model.SOC_batt[k] -  (model.P_batt_char[k]*model.eta_batt_char[1] - \
        model.P_batt_dis[k]/model.eta_batt_dis[1])*model.K_batt[1] == model.SOC_batt[k-1]*model.eta_batt_sd[1] 
       
    
    model.Battery = \
    Constraint(model.K, rule=Battery_rule)
    
    def Battery_SOC1_rule(model,k):
        return model.SOC_batt[k] >= model.SOC_batt_min[1] 
    
    model.Battery_SOC1 = \
    Constraint(model.K, rule=Battery_SOC1_rule)
    
    def Battery_SOC2_rule(model,k):
        return model.SOC_batt[k] <= model.SOC_batt_max[1] 
    
    model.Battery_SOC2 = \
    Constraint(model.K, rule=Battery_SOC2_rule)
    
    # Equation (15a)
    def Battery_Dis1_rule (model,k):
        return model.P_batt_dis[k] >= 0
    
    model.Battery_Dis1 = \
    Constraint(model.K, rule=Battery_Dis1_rule)
    
    # Equation (15b)
    def Battery_Dis2_rule (model,k):
        return model.P_batt_dis[k] <= model.P_batt_dis_max[1]*(1 - model.b_batt[k]) 
    
    model.Battery_Dis2 = \
    Constraint(model.K, rule=Battery_Dis2_rule)
    
    # Equation (16a)
    def Battery_Char1_rule (model,k):
        return model.P_batt_char[k] >= 0
    
    model.Battery_Char1 = \
    Constraint(model.K, rule=Battery_Char1_rule)
    
    # Equation (16b)
    def Battery_Char2_rule (model,k):
        return model.P_batt_char[k] <= model.P_batt_char_max[1]*(model.b_batt[k]) 
    
    model.Battery_Char2 = \
    Constraint(model.K, rule=Battery_Char2_rule)
    
    #09.02.2015    
    #11.02.2015 Testing SOC_Terminal as decision variable    
    def Battery_SOC_Terminal_rule(model):
        #return model.SOC_batt[Np] >= 9 
        return model.SOC_batt[Np] - model.SOC_batt_term >=0
    #
    model.Battery_SOC_Terminal = \
    Constraint(rule=Battery_SOC_Terminal_rule)
    
    # Equation (17)
      # 07.05.2015
    # Modulation for eboiler
    def Eboiler_Modulation1_rule(model,k):
        return model.P_eboiler_th[k] <= model.P_eboiler_max[1]*model.b_eboiler[k]
        
    model.Eboiler_Modulation1 = \
    Constraint(model.K, rule=Eboiler_Modulation1_rule)
    
    def Eboiler_Modulation2_rule(model,k):
        return model.P_eboiler_th[k] >= model.P_eboiler_min[1]*model.b_eboiler[k]
        
    model.Eboiler_Modulation2 = \
    Constraint(model.K, rule=Eboiler_Modulation2_rule)
    
    #    def Eboiler_rule (model,k):
    #        return model.P_eboiler_th[k] - model.P_eboiler_max[1]*model.b_eboiler[k] == 1
    #        
    #    
    #    model.Eboiler = \
    #    Constraint(model.K, rule=Eboiler_rule)
    
    # Equation (18)
    def Eboiler_Performance_rule (model,k):
        return model.P_eboiler_th[k] == model.P_eboiler_el[k]*model.eta_eboiler[1]
    
    model.Eboiler_Performance = \
    Constraint(model.K, rule=Eboiler_Performance_rule)
    
    # Equation (19)
    def Grid_exp_rule(model,k):
        return model.P_grid_exp[k] <= model.P_CHP_el_exp[k] + model.P_PV_exp[k]
    
    model.Grid_exp = \
    Constraint(model.K, rule=Grid_exp_rule)
    
    # Equation (20a)
    def Grid_exp_batt1_rule(model,k):
        return model.P_grid_exp[k] >= 0
        
    model.Grid_exp_batt1 = \
    Constraint(model.K, rule=Grid_exp_batt1_rule)
    
    # Equation (20b)
    def Grid_exp_batt2_rule(model,k):
        #return model.P_grid_exp[k] - (model.P_CHP_el_max[1] + model.P_PV_max[1])*model.b_batt[k] <= 0 
        return model.P_grid_exp[k] - (model.P_CHP_el_max[1] + model.P_PV_max[1]) <= 0
    model.Grid_exp_batt2 = \
    Constraint(model.K, rule=Grid_exp_batt2_rule)
    
    # Equation (21a)
    def Grid_imp_batt1_rule(model,k):
        return model.P_grid_imp[k] >= 0
    
    model.Grid_imp_batt1 = \
    Constraint(model.K, rule=Grid_imp_batt1_rule)
    
    # Equation (21b)
    def Grid_imp_batt2_rule(model,k):
    #    return model.P_grid_imp[k] -(model.P_Load[k] + model.P_eboiler_max[1])* \
    #    (1-model.b_batt[k]) <= 0
        return model.P_grid_imp[k] - (model.P_Load_max[1]+ model.P_eboiler_max[1])*\
        (1-model.b_batt[k]) <= 0
    
    #model.Grid_imp_batt2 = \
    #Constraint(model.K, rule=Grid_imp_batt2_rule)
    
    # Equation (22)    
    def th_balance_constraint_rule(model,k):
        return model.P_sh_th[k] + model.P_dhw_th[k] \
        + model.P_TES_char[k] - model.P_CHP_th[k] - model.P_eboiler_th[k] \
        -  model.P_aux_th[k] - model.P_TES_dis[k] == 0
    # model.P_fbh_th[k]  : Fußbodenheizung is not yet included
    
    model.th_balance_constraint = \
    Constraint(model.K, rule=th_balance_constraint_rule)
    
    # Equation (23)
    def CHP_th_Performance_rule(model,k):
        return model.P_CHP_th[k] == model.P_CHP_gas[k]*model.eta_CHP_th[1]     
    
    model.CHP_th_Performance = \
    Constraint(model.K, rule=CHP_th_Performance_rule)
    
    # Equation (24)
    def TES_rule(model,k):
        if k == 1:
            return model.SOC_TES[k]  - (model.P_TES_char[k]*model.eta_TES_char[1] - \
                    model.P_TES_dis[k]/model.eta_TES_dis[1])*model.K_TES[1]== model.SOC_TES_ini[1]*model.eta_TES_sd[1] 
        else: 
            return model.SOC_TES[k] - (model.P_TES_char[k]*model.eta_TES_char[1] - \
                    model.P_TES_dis[k]/model.eta_TES_dis[1])*model.K_TES[1] == model.SOC_TES[k-1]*model.eta_TES_sd[1] 
                    
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
    
    # Equation (25)
    def TES_char_rule(model,k):
        return model.P_TES_char[k] - model.P_CHP_th[k] - model.P_aux_th[k] - \
        model.P_eboiler_th[k] == 0 
    
    model.TES_char = \
    Constraint(model.K, rule=TES_char_rule)
    
    # Equation (26)
    def TES_dis_rule(model,k):
        return model.P_TES_dis[k] == model.P_sh_th[k]  + \
        model.P_dhw_th[k]
    #  model.P_fbh_th[k] --> Not yet
    model.TES_dis = \
    Constraint(model.K, rule=TES_dis_rule)
    
     #09.02.2015    
    def TES_SOC_Terminal_rule(model):
        return model.SOC_TES[Np] >= 10
        #return model.SOC_TES[Np] - model.SOC_TES_term >= 0
    #
    model.TES_SOC_Terminal = \
    Constraint(rule=TES_SOC_Terminal_rule)
       
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
    # the next line creates one constraint for each member of the set model.I
    
    model.Aux_Performance = \
    Constraint(model.K, rule=Aux_Performance_rule)
    
    # --------------------------------------------------------------------------
    #        Create a model instance and optimize
    # --------------------------------------------------------------------------
    instance = model.create()
    results = opt.solve(instance)
    #results.write(filename="Resultados.xlm",format='xlm')
    #print results.solution
    
    
    # --------------------------------------------------------------------------
    #                      Collect the data
    # --------------------------------------------------------------------------
    vars = set()
    data = {}
    f = {}
    for var in results.solution.variable:
        vars.add(var)
        data[var] = results.solution.variable[var]['Value']
       
           
    f[1] = results.solution.objective['__default_objective__']['Value']
    #f = results.solution.objective['Value']
            #
            # Write a CSV file, with one row per solution.
            # The first column is the function value, the remaining
            # columns are the values of nonzero variables.
            #
    rows = []
    vars = list(vars)
    vars.sort()
    #rows.append(['__default_objective__']+vars)
    
    row = [f[1]]
   
    for var in vars:
        row.append( data.get(var,None) )
        
    rows.append(row)
    return rows
   
if __name__ == '__main__':
    plt.close("all")
    # -------------------------------------------------------------------------
    # Prepare Input
    # -------------------------------------------------------------------------
    # MPC sampling time [min].          
    Delta_t = 10
    # Read Input Values    
    # include create vectors in inputdata
    # P_dhw_th_Tot, P_sh_th_Tot,xcop6, P_PV_avacop,DATE,ycop,x7,start_date, \
    # end_date,ini,final= createvectors.createvectors(start_date,end_date,Np)
    P_PV_ava, P_dhw_th, P_sh_th, Load_cop,P_eboiler_min,Cap_TES,Np,P_Load_max,eta_CHP_th,\
    P_CHP_el_min,P_CHP_el_max,eta_CHP_el,ramp_CHP,eta_batt_sd,eta_batt_char,\
    eta_batt_dis ,K_batt ,P_batt_char_max ,\
    P_batt_dis_max ,eta_boiler ,P_PV_max ,eta_aux ,C_gas ,C_grid_el ,C_CHP_FIT , \
    C_PV_FIT ,C_CHP_cs ,K_TES ,eta_TES_sd ,eta_TES_char ,eta_TES_dis ,P_aux_th_max , \
    P_aux_th_min ,P_eboiler_max ,SOC_batt_max ,SOC_batt_min ,SOC_TES_max ,SOC_TES_min , \
    C_CHP_ex ,P_CHP_gas_ini ,b_CHP_on_ini ,SOC_batt_ini,SOC_TES_ini, Cap_batt \
    = ipv.inputvaluesEFH(Delta_t)
    
    # -------------------------------------------------------------------------
    # Optimze    
    # -------------------------------------------------------------------------
    INEVES_Opt(eta_CHP_th,P_eboiler_min,P_Load_max,Np,P_CHP_el_min,P_CHP_el_max, \
    eta_CHP_el,ramp_CHP,eta_batt_sd,eta_batt_char,eta_batt_dis ,K_batt ,P_batt_char_max , \
    P_batt_dis_max ,eta_boiler ,P_PV_max ,eta_aux ,C_gas ,C_grid_el ,C_CHP_FIT , \
    C_PV_FIT ,C_CHP_cs ,K_TES ,eta_TES_sd ,eta_TES_char ,eta_TES_dis ,P_aux_th_max , \
    P_aux_th_min ,P_eboiler_max ,SOC_batt_max ,SOC_batt_min ,SOC_TES_max ,SOC_TES_min , \
    C_CHP_ex ,Load_cop ,P_sh_th ,P_dhw_th ,P_PV_ava ,P_CHP_gas_ini ,b_CHP_on_ini , \
    SOC_batt_ini,SOC_TES_ini)
   