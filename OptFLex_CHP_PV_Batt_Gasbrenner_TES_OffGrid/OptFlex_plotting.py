# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 12:34:54 2015

@author: tkneiske (nach Vorlagen von Jan von Appen)
"""

from __future__ import division
import numpy as np
#import bwf_functions as bwff
import itertools as itto
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.sankey import Sankey
import scipy.special as ssp
import seaborn as sns
import pandas as pd
import OptFlex_MPC as main


def Plotting(Result_Grid_End, Result_BAT_End, Result_PV_End,\
    Result_CHP_End, Result_Heat_End, Result_TES_End,\
    PVavaPeriod, P_PV_max, P_Load_max, LoadPeriod\
    , Battery, Costs, date, date_end, Plotcounter, \
    name, maxx, PrHoBin, INOUT_string):
#--------------------------------------
# Type of available energysystem
#--------------------------------------

    Load = 1
    GridLoad = 1  # on-Grid
    PV = 1
    EStor = 1
    SellToGrid = 1
    LoadSupply = 0
    
    QLoad = 1
    EHeatQStor = 0
    CHP = 1
    CHP1 = 0
    CHP2 = 0
    QStor = 1
    NGBurner = 1
    NGBurner1 = 0
    NGBurner2 = 0
    NGBurner3 = 0
    
    
    NoYes = pd.Series([Load, LoadSupply, QLoad, EHeatQStor, GridLoad, PV, CHP, CHP1,CHP2,QStor \
                ,EStor ,SellToGrid ,NGBurner ,NGBurner1 ,NGBurner2 ,NGBurner3], \
                index=['Load', 'LoadSupply','QLoad', 'EHeatQStor', 'GridLoad', 'PV', 'CHP', \
                'CHP1','CHP2','QStor','EStor' ,'SellToGrid' ,'NGBurner' ,\
                'NGBurner1' ,'NGBurner2','NGBurner3'])
#    print NoYes
    
    plotEFlows = 1

  
    #maxxSim = len(LoadPeriod['ELoad'])
    maxxSim = maxx
    n_days = maxxSim/144            # 10min
    #print n_days    
    #--------------------------------------
    #print PVBurnerWeek
    #Fill= pd.DataFrame(np.zeros(maxx-maxxSim)) 
#    PVProfile = PVavaPeriod['PV 2013, Kassel, 10min'][:maxx]
#    EProfile = LoadPeriod['ELoad'][:maxx]
#    PV2LoadWeek = Result_PV_End['PV load selfcon'][:maxx]
#    GridLoadWeek = Result_Grid_End['Grid Import'][:maxx]
#    Bat2LoadWeek = Result_BAT_End['Battery dis-charging'][:maxx]
#    PVGridWeek = Result_PV_End['PV Grid export'][:maxx]
#    PV2BatWeek = Result_PV_End['PV batt selfcon'][:maxx]
#    socBat =  Result_BAT_End['SOC battery'][:maxx]
#    # Thermal    
#    QProfile = LoadPeriod['QLoad1'][:maxx]+LoadPeriod['QLoad2'][:maxx]
#    CHP2LoadWeek = Result_CHP_End['CHP load self'][:maxx]      
#    CHPGridWeek = Result_CHP_End['CHP Export'][:maxx]
#    CHPel = Result_CHP_End['CHP el'][:maxx]
#    CHP12LoadWeek = CHP2LoadWeek
#    CHP12BatWeek = Result_CHP_End['CHP batt self'][:maxx] 
#    CHP1GridWeek = CHPGridWeek
#    CHP2BatWeek = CHP12BatWeek
#    #Thermal storage
#    CHP2QStorWeek = Result_CHP_End['CHP th2TES'][:maxx]  
#    CHP2QLoadWeek = Result_CHP_End['CHP th2load'][:maxx] 
#    # AuxGas bedient den Speicher und direkt dadurch die Last
#    NGBurner2QLoadWeek = Result_Heat_End['Aux Gasbrenner'][:maxx]
#    NGBurner2QStorWeek = Result_Heat_End['Aux Gasbrenner'][:maxx]
#    QStor2QLoadWeek =  QProfile-CHP2QLoadWeek-NGBurner2QLoadWeek 
#    QStorC = Result_TES_End['TES charging'][:maxx] 
#    QStorD = Result_TES_End['TES dis-charging'][:maxx]
#    QinS = Result_TES_End['SOC TES'][:maxx]
#    QDischarge = QProfile# everything will be met through the thermnal storage
#    #EHeatQStor2QStorWeek =  
       
    # ----------------------------------------------
    # PV
    # ----------------------------------------------        
    PVProfile = PVavaPeriod['PV 2013, Kassel, 10min'][:maxx]
    PV2LoadWeek = Result_PV_End['PV load selfcon'][:maxx]
    PVGridWeek = Result_PV_End['PV Grid export'][:maxx]
    PV2BatWeek = Result_PV_End['PV batt selfcon'][:maxx]

    # ----------------------------------------------
    # Energy Profiles
    # ----------------------------------------------
    EProfile = LoadPeriod['ELoad'][:maxx]
    QProfile = LoadPeriod['QLoad1'][:maxx]+LoadPeriod['QLoad2'][:maxx]

    # ----------------------------------------------
    # Grid
    # ----------------------------------------------
    GridLoadWeek = Result_Grid_End['Grid Import'][:maxx]

    # ----------------------------------------------
    # Battery
    # ----------------------------------------------
    Bat2LoadWeek = Result_BAT_End['Battery dis-charging'][:maxx]
    socBat =  Result_BAT_End['SOC battery'][:maxx]

    # ----------------------------------------------
    # CHP
    # ----------------------------------------------
    # ELEK    
    CHPel = Result_CHP_End['CHP el'][:maxx]
    CHP2LoadWeek = Result_CHP_End['CHP load self'][:maxx]      
    CHPGridWeek = Result_CHP_End['CHP Export'][:maxx]
    CHP2BatWeek = Result_CHP_End['CHP batt self'][:maxx] 
    #THERMAL
    CHP2QStorWeek = Result_CHP_End['CHP th'][:maxx]  
    #CHP2QLoadWeek = Result_CHP_End['CHP th2load'][:maxx] 
    #CHP12LoadWeek = CHP2LoadWeek
    #CHP1GridWeek = CHPGridWeek
    #CHP2BatWeek = CHP12BatWeek
    
    # ----------------------------------------------
    # AUX Gasboiler
    # ---------------------------------------------
    # AuxGas bedient den Speicher und direkt dadurch die Last
    #NGBurner2QLoadWeek = Result_Heat_End['Aux Gas2Load'][:maxx]
    #NGBurner2QStorWeek = Result_Heat_End['Aux Gas2TES'][:maxx]
    #NGBurner2QLoadWeek = Result_Heat_End['Aux Gasbrenner'][:maxx]
    NGBurner2QStorWeek = Result_Heat_End['Aux Gasbrenner'][:maxx]

    # ----------------------------------------------
    #Thermal storage
    # ----------------------------------------------
    QStor2QLoadWeek = QProfile# -NGBurner2QLoadWeek -  CHP2QLoadWeek 
    
  #  print 'Plotting:',QStor2QLoadWeek[42], QProfile[42], NGBurner2QLoadWeek[42],  CHP2QLoadWeek[42]
    QStorC = Result_TES_End['TES charging'][:maxx] 
    QStorD = Result_TES_End['TES dis-charging'][:maxx]
    QinS = Result_TES_End['SOC TES'][:maxx]
    QDischarge = QProfile# everything will be met through the thermnal storage

#    QStor2full = Result_TES_End['TES too full']
   
    if plotEFlows == 1:
        
# Colors for EFlows        
        CPV2Load=sns.xkcd_rgb["medium green"]
        CPV2Bat=sns.xkcd_rgb["light violet"]
        CPVGrid=sns.xkcd_rgb["pale red"]
        CPVBurner=sns.xkcd_rgb["sun yellow"]
        CCHP2Load=sns.xkcd_rgb["emerald green"]
        CCHP2Bat=sns.xkcd_rgb["dark violet"]
        CCHPGrid=sns.xkcd_rgb["deep red"]                    
        CGridLoad=sns.xkcd_rgb["dark grey"]
        CBurnerLoad=sns.xkcd_rgb["black"]
        CBat2Load=sns.xkcd_rgb["pale pink"]
        CEStor=sns.xkcd_rgb["pinkish"]
        
# Colors for QFlows  
        CNGBurner2QLoad=sns.xkcd_rgb["khaki"]
        CNGBurner2QStor=sns.xkcd_rgb["army green"]        
        CCHP2QLoad=sns.xkcd_rgb["emerald green"]
        CCHP2QStor=sns.xkcd_rgb["dark violet"]        
        CEHeat2QStor=sns.xkcd_rgb["black"]              
        CQStor2QLoad=sns.xkcd_rgb["pale pink"]
        CQStor=sns.xkcd_rgb["pinkish"]
        
        SubPlots1=2
        SubPlots2=2
        SubPlots3=2
        SubPlots4=1 
        SubPlots5=2

#--------------------------------------------------------------------------------------  
    if SubPlots1 > 0:        
            plt.figure(Plotcounter, figsize=(6,3*SubPlots1))         
            SubPlotCounter=1
         
#--------------------------------------------------------------
#  Load on Grid                    
            if NoYes['Load'] == 1:  
                plt.subplot(SubPlots1*100+10+SubPlotCounter)
                plt.ylabel('Power [kW]')                      
                #x_axis = np.arange(0,maxxSim)
                x_axis = LoadPeriod['ELoad'][:maxx].index
                #x_ticks=np.arange(0,maxxSim, maxxSim/(4*n_days))
                plt.xlabel('For ' +str(int(n_days))+ ' Days starting from '+str(date))
                #plt.xticks(x_ticks)
                #plt.xlim(0,7)
                #print len(x_axis)
                        
                SubPlotCounter=SubPlotCounter+1
                if NoYes['EHeatQStor'] == 1:
                    plt.plot(x_axis,EProfile,label='E-Load, HH',linewidth=0.7)
              #      plt.plot(x_axis,Parameter['EProfil']['data']['Load'][LengthWeek*(Week-1):LengthWeek*Week]\
              #      *Timesteps/8760.+EEHeatQStorWeek,label='E-Load, HH (inc. e-heating)',linewidth=0.7)
                else:                     
                    plt.plot(x_axis,EProfile,label='load, gesamt',linewidth=0.7)                                 
                if NoYes['GridLoad'] == 1: 
                     if NoYes['PV'] == 1 and NoYes['CHP'] == 1 and NoYes['EStor'] == 1: 
                         #print 'PV, CHP, Batt'
                         fcolors=[CPV2Load, CCHP2Load, CBat2Load, CGridLoad]
                         plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,Bat2LoadWeek,GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                         plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-Load-discharging')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')                  
                     elif NoYes['PV'] == 1 and NoYes['CHP'] == 1 and NoYes['EStor'] == 0: 
                         fcolors=[CPV2Load, CCHP2Load, CGridLoad]
                         plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')
                     elif NoYes['PV'] == 1 and NoYes['CHP'] == 0 and NoYes['EStor'] == 1:
                         fcolors=[CPV2Load, CBat2Load, CGridLoad]
                         plt.stackplot(x_axis,PV2LoadWeek,Bat2LoadWeek,GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                         plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-Load-discharging')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')
                     elif NoYes['PV'] == 1 and NoYes['CHP'] == 0 and NoYes['EStor'] == 0:
                         fcolors=[CPV2Load, CGridLoad]
                         plt.stackplot(x_axis,PV2LoadWeek,GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')     
                         print "PV"
                     elif NoYes['PV'] == 0 and NoYes['CHP'] == 1 and NoYes['EStor'] == 1:
                         fcolors=[CCHP2Load, CBat2Load, CGridLoad]
                         plt.stackplot(x_axis,CHP2LoadWeek,Bat2LoadWeek,GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                         plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-Load-discharging')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')                        
                     elif NoYes['PV'] == 0 and NoYes['CHP'] == 1 and NoYes['EStor'] == 0:
                         fcolors=[CCHP2Load, CGridLoad]
                         plt.stackplot(x_axis,CHP2LoadWeek,GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')
                     elif NoYes['PV'] == 0 and NoYes['CHP'] == 0 and NoYes['EStor'] == 1:
                         fcolors=[CBat2Load, CGridLoad]
                         plt.stackplot(x_axis,Bat2LoadWeek,GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-Load-discharging')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')                    
                     else:
                         fcolors=[CGridLoad]
                         plt.stackplot(x_axis,GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')  
                else:
                    print 'Off-Grid not implemented'                         
            plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
#--------------------------------------------------------------
#  Load off Grid                    
#                 else:
#                     if NoYes['PV'] == 1:               
#                         if NoYes['CHP1'] == 1:
#                             if NoYes['EStor'] == 1:
#                                 fcolors=[CPV2Load, CCHP2Load, CBat2Load, CBurnerLoad]
#                                 plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,Bat2LoadWeek,BurnerLoadWeek,colors=fcolors)  
#                                 plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
#                                 plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
#                                 plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging')
#                                 plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')
#                             else:
#                                 fcolors=[CPV2Load, CCHP2Load, CBurnerLoad]
#                                 plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,BurnerLoadWeek,colors=fcolors)  
#                                 plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
#                                 plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
#                                 plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')
#                         elif NoYes['EStor'] == 1:
#                             fcolors=[CPV2Load, CBat2Load, CBurnerLoad]
#                             plt.stackplot(x_axis,PV2LoadWeek,Bat2LoadWeek,BurnerLoadWeek,colors=fcolors)  
#                             plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
#                             plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging')
#                             plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')
#                         else:
#                             fcolors=[CPV2Load, CBurnerLoad]
#                             plt.stackplot(x_axis,PV2LoadWeek,BurnerLoadWeek,colors=fcolors)  
#                             plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
#                             plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')                     
#                     else:
#                         fcolors=[CBurnerLoad]
#                         plt.stackplot(x_axis,BurnerLoadWeek,colors=fcolors)  
#                         plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')  
#     
#                 plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
#                 plt.xlim(0,7)
#                 if NoYes['EHeatQStor'] == 1:
#                     plt.ylim(0,np.round(max((Parameter['EProfil']['data']['Load']+Variables['EFlow']['data']['EHeatQStor'])*Timesteps/8760)+.5),0)                    
#                 else:
#                     plt.ylim(0,np.round(max(Parameter['EProfil']['data']['Load']*Timesteps/8760)+.5),0)
#             
#--------------------------------------------------------------
#   Grid exchange
            if NoYes['SellToGrid'] == 1:  
                plt.subplot(SubPlots1*100+10+SubPlotCounter)
                SubPlotCounter=SubPlotCounter+1  
                plt.ylabel('Power [kW] test')                      
           #     x_axis = np.arange(0,maxxSim)
                x_axis = LoadPeriod['ELoad'][:maxx].index
                #x_ticks=np.arange(0,maxxSim, maxxSim/(4*n_days))
                #x_axis = LoadPeriod['ELoad'].index
                plt.xlabel('For ' +str(int(n_days))+ ' Days starting from '+str(date))
                #plt.xticks(x_ticks)
                #plt.xlim(0,7)
                #print len(x_axis)
                if NoYes['GridLoad'] == 1:                 
                     if NoYes['PV'] == 1 and NoYes['CHP'] == 1:
                         plt.plot(x_axis,(PVGridWeek+CHPGridWeek-GridLoadWeek),label='Grid exchange',linewidth=0.7) 
                         fcolors=[CPVGrid, CCHPGrid, CGridLoad]
                         plt.stackplot(x_axis,PVGridWeek,CHPGridWeek,-GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in')
                         plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')                
                     elif NoYes['PV'] == 0 and NoYes['CHP'] == 1:
                         plt.plot(x_axis,(CHPGridWeek-GridLoadWeek),label='Grid exchange',linewidth=0.7) 
                         fcolors=[CCHPGrid, CGridLoad]
                         plt.stackplot(x_axis,CHPGridWeek,-GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')                                             
                     elif NoYes['PV'] == 1 and NoYes['CHP'] == 0:
                         plt.plot(x_axis,(PVGridWeek-GridLoadWeek),label='Grid exchange',linewidth=0.7) 
                         fcolors=[CPVGrid, CGridLoad]
                         plt.stackplot(x_axis,PVGridWeek,-GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in')
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption') 
                     else:
                         plt.plot(x_axis,(-GridLoadWeek),label='Grid exchange',linewidth=0.7) 
                         fcolors=[CGridLoad]
                         plt.stackplot(x_axis,-GridLoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CGridLoad, linewidth=10, label='Grid consumption')  
                 
                     plt.ylabel('Power [kW]')
                     #plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                     #plt.xlim(0,7)
                     #plt.ylim(-np.round((max(Variables['EFlow']['data']['GridLoad']*Timesteps/8760)+.5),0),\
                     #np.round((max(GridFeedIn)+.5),0))
                     plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
             
            plt.savefig('RESULTS\GridFlowsOffGrid'+str(name)+'_'+INOUT_string+'.png', dpi=300, facecolor='w', edgecolor='w',
                       orientation='portrait', papertype=None, format=None,
                 transparent=False, bbox_inches='tight', pad_inches=0.1,
                 frameon=None)
            Plotcounter = Plotcounter + 1
                
#--------------------------------------------------------------
#      Generation plots 
#--------------------------------------------------------------
    if SubPlots2 > 0:
             plt.figure(Plotcounter, figsize=(6,3*SubPlots2))         
             SubPlotCounter=1
          #   x_axis=np.arange(0,maxxSim)
         #    x_ticks=np.arange(0,maxxSim, maxxSim/(4*n_days))
             #x_ticks=(np.arange(0,maxxSim, maxxSim/(4*n_days)),['0','1','2','3','0','1','2','3'])
            # plt.xlabel('Days from '+str(date)+' to '+str(date_end))
             #plt.xticks(x_ticks)
             if NoYes['PV'] == 1:
#                 if Variables['Size']['data']['PV'] >= 0.005:
                     plt.subplot(SubPlots2*100+10+SubPlotCounter)
                     SubPlotCounter=SubPlotCounter+1
                     plt.xlabel('For ' +str(int(n_days))+ ' Days starting from '+str(date))
                    
                     plt.plot(x_axis,PVProfile,label='PV, generated',linewidth=0.7)                
#                    x_axis = np.arange(0,maxxSim)
                     x_axis = LoadPeriod['ELoad'][:maxx].index
                 
                     if NoYes['SellToGrid'] == 1:                    
                         if NoYes['EStor'] == 1:
                            # fcolors=[CPV2Load, CPV2Bat, CPVGrid, CPVBurner]
                            # plt.stackplot(x_axis,PV2LoadWeek,PV2BatWeek,PVGridWeek,PVBurnerWeek,colors=fcolors)
                             fcolors=[CPV2Load, CPV2Bat, CPVGrid]
                             plt.stackplot(x_axis,PV2LoadWeek,PV2BatWeek,PVGridWeek,colors=fcolors)
                             plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                             plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')   
                             plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in') 
                             #plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')                         
                         else:  
                             #fcolors=[CPV2Load, CPVGrid, CPVBurner]
                             #plt.stackplot(x_axis,PV2LoadWeek,PVGridWeek,PVBurnerWeek,colors=fcolors) 
                             fcolors=[CPV2Load, CPVGrid]
                             plt.stackplot(x_axis,PV2LoadWeek,PVGridWeek,colors=fcolors) 
                             plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                             plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in') 
                             #plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')    
                     elif NoYes['EStor'] == 1:
                        # fcolors=[CPV2Load, CPV2Bat, CPVBurner]
                        # plt.stackplot(x_axis,PV2LoadWeek,PV2BatWeek,PVBurnerWeek,colors=fcolors)       
                         fcolors=[CPV2Load, CPV2Bat]
                         plt.stackplot(x_axis,PV2LoadWeek,PV2BatWeek,colors=fcolors)       
                         plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                         plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')   
                        # plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')                                    
                     else:
                        # fcolors=[CPV2Load, CPVBurner]
                        # plt.stackplot(x_axis,PV2LoadWeek,PVBurnerWeek,colors=fcolors)  
                         fcolors=[CPV2Load]
                         plt.stackplot(x_axis,PV2LoadWeek,colors=fcolors)  
                         plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                        # plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')
                    
                     plt.ylabel('Power [kW]')
#                     plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
#                     plt.xlim(0,7)
#                     plt.ylim(0,np.round((max(Parameter['EProfil']['data']['PV']\
#                     *Variables['Size']['data']['PV']*Timesteps/8760)+.5),0))
                     #x_ticks=np.arange(0,maxxSim, maxxSim/(4*n_days))
                     #x_axis = LoadPeriod['ELoad'].index
                     #plt.xticks(x_ticks)
                     #plt.xlim(0,7)
                     #print len(x_axis)
           
                     plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                     
             if NoYes['CHP'] == 1: 
                # if Variables['Num']['data']['CHP1'] >= 0.005:
                     plt.subplot(SubPlots2*100+10+SubPlotCounter)
                     SubPlotCounter=SubPlotCounter+1
                     
                     plt.plot(x_axis,CHPel,label='E-CHP eco1.0, generated',linewidth=0.7) 
                     plt.xlabel('For ' +str(int(n_days))+ ' Days starting from '+str(date))
                     x_axis = LoadPeriod['ELoad'][:maxx].index
       
                     if NoYes['SellToGrid'] == 1:                    
                         if NoYes['EStor'] == 1:
                             fcolors=[CCHP2Load, CCHP2Bat, CCHPGrid]
                             plt.stackplot(x_axis,CHP2LoadWeek,CHP2BatWeek,CHPGridWeek,colors=fcolors)
                             plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                             plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')   
                             plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')                     
                         else:  
                             fcolors=[CCHP2Load, CCHPGrid]
                             plt.stackplot(x_axis,CHP2LoadWeek, CHPGridWeek,colors=fcolors) 
                             plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption') 
                             plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')     
                     elif NoYes['EStor'] == 1:
                         fcolors=[CCHP2Load, CCHP2Bat]
                         plt.stackplot(x_axis,CHP2LoadWeek,CHP2BatWeek,colors=fcolors)
                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                         plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')   
                     else:
                         fcolors=[CCHP2Load, CCHP2Bat]
                         plt.stackplot(x_axis,CHP2LoadWeek,colors=fcolors)
                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                                    
                     plt.ylabel('Power [kW]')
#                     plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
#                     plt.xlim(0,7)
#                     plt.ylim(0,np.round((Variables['Num']['data']['CHP1']*Parameter['CHP1FixedSize']['data']),0))
                     plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
#                     
#             if NoYes['CHP1'] == 1: 
#                 if Variables['Num']['data']['CHP2'] >= 0.005:
#                     plt.subplot(SubPlots2*100+10+SubPlotCounter)
#                     SubPlotCounter=SubPlotCounter+1
#                     
#                     plt.plot(x_axis,Variables['EFlow']['data']['CHP2'][LengthWeek*(Week-1):LengthWeek*Week]\
#                     *Timesteps/8760.,label='E-CHP eco3.0, generated',linewidth=0.7) 
#     
#                     if NoYes['SellToGrid'] == 1:                    
#                         if NoYes['EStor'] == 1:
#                             fcolors=[CCHP2Load, CCHP2Bat, CCHPGrid]
#                             plt.stackplot(x_axis,CHP22LoadWeek,CHP22BatWeek,CHP2GridWeek,colors=fcolors)
#                             plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption')
#                             plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP2-Battery charging')   
#                             plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP2-Grid feed-in')                     
#                         else:  
#                             fcolors=[CCHP2Load, CCHPGrid]
#                             plt.stackplot(x_axis,CHP22LoadWeek, CHP2GridWeek,colors=fcolors) 
#                             plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption') 
#                             plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')     
#                     elif NoYes['EStor'] == 1:
#                         fcolors=[CCHP2Load, CCHP2Bat]
#                         plt.stackplot(x_axis,CHP22LoadWeek,CHP22BatWeek,colors=fcolors)
#                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption')
#                         plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP2-Battery charging')   
#                     else:
#                         fcolors=[CCHP2Load, CCHP2Bat]
#                         plt.stackplot(x_axis,CHP22LoadWeek,colors=fcolors)
#                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption')
#                                    
#                     plt.ylabel('Power [kW]')
#                     plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
#                     plt.xlim(0,7)
#                     plt.ylim(0,np.round((Variables['Num']['data']['CHP2']*Parameter['CHP2FixedSize']['data']),0))
#                     plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
#             
#             if NoYes['CHP2'] == 1: 
#                 if Variables['Num']['data']['CHP3'] >= 0.005:
#                     plt.subplot(SubPlots2*100+10+SubPlotCounter)
#                     SubPlotCounter=SubPlotCounter+1
#                     
#                     plt.plot(x_axis,Variables['EFlow']['data']['CHP3'][LengthWeek*(Week-1):LengthWeek*Week]\
#                     *Timesteps/8760.,label='E-CHP eco4.7, generated',linewidth=0.7) 
#     
#                     if NoYes['SellToGrid'] == 1:                    
#                         if NoYes['EStor'] == 1:
#                             fcolors=[CCHP2Load, CCHP2Bat, CCHPGrid]
#                             plt.stackplot(x_axis,CHP32LoadWeek,CHP32BatWeek,CHP3GridWeek,colors=fcolors)
#                             plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption')
#                             plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP3-Battery charging')   
#                             plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP3-Grid feed-in')                     
#                         else:  
#                             fcolors=[CCHP2Load, CCHPGrid]
#                             plt.stackplot(x_axis,CHP32LoadWeek, CHP3GridWeek,colors=fcolors) 
#                             plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption') 
#                             plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP3-Grid feed-in')     
#                     elif NoYes['EStor'] == 1:
#                         fcolors=[CCHP2Load, CCHP2Bat]
#                         plt.stackplot(x_axis,CHP32LoadWeek,CHP32BatWeek,colors=fcolors)
#                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption')
#                         plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP3-Battery charging')   
#                     else:
#                         fcolors=[CCHP2Load, CCHP2Bat]
#                         plt.stackplot(x_axis,CHP32LoadWeek,colors=fcolors)
#                         plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption')
#                                    
#                     plt.ylabel('Power [kW]')
#                     plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
#                     plt.xlim(0,7)
#                     plt.ylim(0,np.round((Variables['Num']['data']['CHP3']*Parameter['CHP3FixedSize']['data']),0))
#                     plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))            
#             plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
             plt.savefig('RESULTS\GenerationFlowsOffGrid'+str(name)+'_'+INOUT_string+'.png', dpi=300, facecolor='w', edgecolor='w',
                        orientation='portrait', papertype=None, format=None,
                        transparent=False, bbox_inches='tight', pad_inches=0.1,
                        frameon=None)
             Plotcounter = Plotcounter + 1
                
#------------------------------------------------------------------------
#         E-Storage plots 
#------------------------------------------------------------------------
    if SubPlots3 > 0:
             plt.figure(Plotcounter, figsize=(6,3*SubPlots3))         
             SubPlotCounter=1
                 
             if NoYes['EStor'] == 1:
                 #if Variables['Size']['data']['EStor'] >= 0.005:
                     plt.subplot(SubPlots3*100+10+SubPlotCounter)
                     SubPlotCounter=SubPlotCounter+1
                     plt.plot(x_axis,PV2BatWeek-Bat2LoadWeek,label='Battery power',linewidth=0.5)
                     plt.xlabel('For ' +str(int(n_days))+ ' Days starting from '+str(date))
                     x_axis = LoadPeriod['ELoad'][:maxx].index
                         
                     if NoYes['PV'] == 1 and NoYes['CHP'] == 1:
                         #print 'PV, CHP'
                         fcolors=[CPV2Bat, CCHP2Bat, CBat2Load]                
                         plt.stackplot(x_axis,PV2BatWeek,CHP2BatWeek,-Bat2LoadWeek,colors=fcolors)                  
                         plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')
                         plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')
                         plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging') 
                     elif NoYes['PV'] == 0 and NoYes['CHP'] == 1:
                         fcolors=[CCHP2Bat, CBat2Load]                
                         plt.stackplot(x_axis,CHP2BatWeek,-Bat2LoadWeek,colors=fcolors)                  
                         plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')
                         plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging') 
                     elif NoYes['PV'] == 1 and NoYes['CHP'] == 0:
                         fcolors=[CPV2Bat, CBat2Load]                
                         plt.stackplot(x_axis,PV2BatWeek,-Bat2LoadWeek,colors=fcolors)                        
                         plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')
                         plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging') 
                             
                     plt.ylabel('Power [kW]')
                    # plt.xlim(0,7)
                    # plt.ylim(-np.round((Variables['Size']['data']['BatC']*Timesteps/8760+.25),0),np.round((Variables['Size']['data']['BatC']*Timesteps/8760+.25),0))
                    # plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                     plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                     
# --------------- battery SOC
                     plt.subplot(SubPlots3*100+10+SubPlotCounter)
                     SubPlotCounter=SubPlotCounter+1
                     
                     #plt.stackplot(x_axis,(Variables['EinS']['data'][LengthWeek*(Week-1):LengthWeek*Week]*100/Variables['Size']['data']['EStor']/Parameter['UseableEStorCap']['data']),colors=[CEStor])  
                     plt.stackplot(x_axis,(socBat), colors=[CEStor])
                     plt.plot([], [], color=CEStor, linewidth=10, label='Energy in battery')                
                     plt.ylabel('SOC [%]')
#                     plt.xlim(0,7)
                     plt.ylim(0,100)
#                     plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                     plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))   
                     plt.xlabel('For ' +str(int(n_days))+ ' Days starting from '+str(date))
                     x_axis = LoadPeriod['ELoad'][:maxx].index
       
#                     plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
                     plt.savefig('RESULTS\EStorageOffGrid'+str(name)+'_'+INOUT_string+'.png', dpi=300, facecolor='w', edgecolor='w',
                                 orientation='portrait', papertype=None, format=None,
                         transparent=False, bbox_inches='tight', pad_inches=0.1,
                         frameon=None)
                     Plotcounter=Plotcounter+1
#-----------------------------------------------------------------------------                
         # Q-Load plots   
#-----------------------------------------------------------------------------                
    if SubPlots4 > 0:       
             plt.figure(Plotcounter, figsize=(6,3*SubPlots4))         
             SubPlotCounter=1
             
             if NoYes['QLoad'] == 1:  
                 plt.subplot(SubPlots4*100+10+SubPlotCounter)
                 SubPlotCounter=SubPlotCounter+1
                 plt.plot(x_axis, QProfile,label='Q-load, total',linewidth=0.7) 
                # plt.plot(x_axis,-QProfile,label='Q-load, total',linewidth=0.7) 
                 plt.xlabel('For ' +str(int(n_days))+ ' Days starting from '+str(date))
                 x_axis = LoadPeriod['ELoad'][:maxx].index
                        
                 if NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['QStor'] == 1:
                     #fcolors=[CCHP2QLoad, CNGBurner2QLoad, CQStor2QLoad]
                     fcolors=[CQStor2QLoad]
                     plt.stackplot(x_axis,QStor2QLoadWeek,colors=fcolors)  
                    # plt.stackplot(x_axis,CHP2QStorWeek,NGBurner2QStorWeek,QStor2QLoadWeek,colors=fcolors)  
                     #plt.stackplot(x_axis,CHP2QLoadWeek,NGBurner2QLoadWeek,colors=fcolors)  
                     #plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-2-storage')                        
                     #plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-2-load')
                     plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-2-load')
                 elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['QStor'] == 0:
                    # fcolors=[CCHP2QLoad, CNGBurner2QLoad]
                    # plt.stackplot(x_axis,CHP2QStorWeek,NGBurner2QStorWeek,colors=fcolors)  
                     fcolors=[CQStor2QLoad]
                     plt.stackplot(x_axis,QStor2QLoadWeek,colors=fcolors)  
                     plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-2-storage')
                  #   plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-2-load')
                 elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['QStor'] == 1:
                     #fcolors=[CNGBurner2QLoad, CQStor2QLoad]
                     #plt.stackplot(x_axis,NGBurner2QStorWeek,QStor2QLoadWeek,colors=fcolors)  
                     fcolors=[CQStor2QLoad]
                     plt.stackplot(x_axis,QStor2QLoadWeek,colors=fcolors)                   
                   #  plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-2-load')            
                     plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-2-load')
              #   elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['QStor'] == 0:
              #       fcolors=[CNGBurner2QLoad]
              #       plt.stackplot(x_axis,NGBurner2QLoadWeek,colors=fcolors)  
              #       plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-load')     
                 elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['QStor'] == 1:
            #         fcolors=[CCHP2QLoad, CQStor2QLoad]
            #         plt.stackplot(x_axis,CHP2QLoadWeek,QStor2QLoadWeek,colors=fcolors)  
            #         plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-2-load') 
                     fcolors=[CQStor2QLoad]
                     plt.stackplot(x_axis,QStor2QLoadWeek,colors=fcolors)  
                  
                     plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-2-load')
            #     elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['QStor'] == 0:
            #         fcolors=[CCHP2QLoad]
            #         plt.stackplot(x_axis,CHP2QLoadWeek,colors=fcolors)  
            #         plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-load')  
                 elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 0 and NoYes['QStor'] == 1:
                     fcolors=[CQStor2QLoad,]
                     plt.stackplot(x_axis,QStor2QLoadWeek,colors=fcolors)  
                     plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-2-load')                     
     
                 plt.ylabel('Power [kW]')
#                 plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
#                 plt.xlim(0,7)
#                 plt.ylim(0,np.round(max(Parameter['QProfil']['data']['QLoad']*Timesteps/8760)+.5),0)
                 plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))  
                 
#                 plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
                 plt.savefig('RESULTS\QFlowsOffGrid'+str(name)+'_'+INOUT_string+'.png', dpi=300, facecolor='w', edgecolor='w',
                            orientation='portrait', papertype=None, format=None,
                     transparent=False, bbox_inches='tight', pad_inches=0.1,
                     frameon=None)
                 Plotcounter=Plotcounter+1

#-------------------------------------------------------------------------------                
#         # Q-Storage plots  
#-------------------------------------------------------------------------------                
    if SubPlots5 > 0:
             plt.figure(Plotcounter, figsize=(6,3*SubPlots5))         
             SubPlotCounter=1
                 
             if NoYes['QStor'] == 1:                           
               #  if max(QStorD) >= 0.005:
                     plt.subplot(SubPlots5*100+10+SubPlotCounter)
                     SubPlotCounter=SubPlotCounter+1
                     plt.plot(x_axis,QStorC,color=sns.xkcd_rgb["light blue"],label='Q-storage charging power',linewidth=0.7)                 
                     plt.plot(x_axis,-QStorD,color=sns.xkcd_rgb["dark blue"],label='Q-storage discharging power',linewidth=0.7)                             
                     plt.xlabel('For ' +str(int(n_days))+ ' Days starting from '+str(date))
                     x_axis = LoadPeriod['ELoad'][:maxx].index
               
                     if NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 0:
                         fcolors1=[CQStor2QLoad]
                         fcolors2=[CNGBurner2QStor, CCHP2QStor]
                         plt.stackplot(x_axis,-QDischarge,colors=fcolors1) 
                         plt.stackplot(x_axis,CHP2QStorWeek,NGBurner2QStorWeek,colors=fcolors2)  
                         plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-2-storage')
                        # plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-storage-2-load')                     
                         plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-2-storage')
                         plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-2-load')
                         plt.ylabel('Power [kW]')
                     elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['EHeatQStor'] == 0:
                         fcolors1=[CQStor2QLoad]
                         fcolors2=[CNGBurner2QStor]
                         plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                         plt.stackplot(x_axis,NGBurner2QStorWeek,colors=fcolors2)   
                         plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-2-storage')
                         plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                         plt.ylabel('Power [kW]')
          #           elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['EHeatQStor'] == 1:
          #               fcolors1=[CQStor2QLoad]
          #               fcolors2=[CNGBurner2QStor,CEHeat2QStor]
          #               plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
          #               plt.stackplot(x_axis,NGBurner2QStorWeek,EHeatQStor2QStorWeek,colors=fcolors2)   
          #               plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
          #               plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
          #               plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
          #               plt.ylabel('Power [kW]')
           #          elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 1:
           #              fcolors1=[CQStor2QLoad]
           #              fcolors2=[CNGBurner2QStor,CCHP2QStor,CEHeat2QStor]
           #              plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
           #              plt.stackplot(x_axis,NGBurner2QStorWeek,CHP2QStorWeek,EHeatQStor2QStorWeek,colors=fcolors2)   
           #              plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
           #              plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
           #              plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
           #              plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
           #              plt.ylabel('Power [kW]')
                     elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 0:
                         fcolors1=[CQStor2QLoad]
                         fcolors2=[CCHP2QStor,CCHP2QLoad]
                         plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                         plt.stackplot(x_axis,CHP2QStorWeek,CHP2QStorWeek,colors=fcolors2)    
                         plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage-2-storage')
                         plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-storage-2-load')                     
                         plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-2-load') 
                         plt.ylabel('Power [kW]')
         #            elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 0 and NoYes['EHeatQStor'] == 1:
         #                fcolors1=[CQStor2QLoad]
         #                fcolors2=[CEHeat2QStor]
         #                plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
         #                plt.stackplot(x_axis,EHeatQStor2QStorWeek,colors=fcolors2)    
         #                plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
         #                plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
         #                plt.ylabel('Power [kW]')
         #            elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 1:
         #                fcolors1=[CQStor2QLoad]
         #                fcolors2=[CCHP2QStor,CEHeat2QStor]
         #                plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
         #                plt.stackplot(x_axis,CHP2QStorWeek,EHeatQStor2QStorWeek,colors=fcolors2)   
         #                plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
         #                plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
          #               plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
          #               plt.ylabel('Power [kW]')
#                     plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))    
#                     plt.xlim(0,7)
#                     plt.ylim(-np.round((max(QStorD)+.5),0)*Timesteps/8760.,\
#                     np.round((max(QStorC)+.5),0)*Timesteps/8760.)                                        
                     plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                     
                     plt.subplot(SubPlots5*100+10+SubPlotCounter)
                     SubPlotCounter=SubPlotCounter+1
                     plt.stackplot(x_axis,QinS,colors=[CQStor])
                     plt.plot([], [], color=CQStor, linewidth=10, label='Energy in Q-storage')                
                     plt.xlabel('For ' +str(int(n_days))+ ' Days starting from '+str(date))
                 
                     plt.ylabel('SOC [%]')
#                     plt.xlim(0,7)
                     plt.ylim(0,100)
#                     plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                     plt.legend(loc='center left',bbox_to_anchor=(1, 0.5)) 
#                     
#                     plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
                     plt.savefig('RESULTS\QStorageOffGrid'+str(name)+'_'+INOUT_string+'.png', dpi=300, facecolor='w', edgecolor='w',
                                 orientation='portrait', papertype=None, format=None,
                         transparent=False, bbox_inches='tight', pad_inches=0.1,
                         frameon=None)
                     Plotcounter=Plotcounter+1
    return Plotcounter
  
if __name__ == '__main__':
    plt.close("all")
    main.MPC()            