# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 12:34:54 2015

@author: tkneiske (nach Vorlagen von Jan von Appen)
"""

from __future__ import division
import numpy as np
import bwf_functions as bwff
import itertools as itto
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.sankey import Sankey
import scipy.special as ssp
import seaborn as sns
import pandas as pd


def Plotting(Result_Grid_End, Result_BAT_End, Result_PV_End,\
PVava_TOT_df, P_PV_max,P_Load_max, LoadAll_TOT_df, Battery, Costs):
#--------------------------------------
# Type of available energysystem
#--------------------------------------

    Load = 0
    LoadSupply = 0
    QLoad = 0
    EHeatQStor = 0
    GridLoad = 0
    PV = 1
    CHP = 0
    CHP1 = 0
    CHP2 = 0
    QStor = 0
    EStor = 10
    SellToGrid = 0
    NGBurner = 0
    NGBurner1 = 0
    NGBurner2 = 0
    NGBurner3 = 0
    
    NoYes = pd.Series([Load, LoadSupply, QLoad, EHeatQStor, GridLoad, PV, CHP, CHP1,CHP2,QStor \
                ,EStor ,SellToGrid ,NGBurner ,NGBurner1 ,NGBurner2 ,NGBurner3], \
                index=['Load', 'LoadSupply','QLoad', 'EHeatQStor', 'GridLoad', 'PV', 'CHP', \
                'CHP1','CHP2','QStor','EStor' ,'SellToGrid' ,'NGBurner' ,\
                'NGBurner1' ,'NGBurner2','NGBurner3'])
    
    # Anzahl an  ?                
    Timesteps = 42               

    Week = 42

    plotEFlows = 1
    plotAnalyses = 0
        
    Variables
    
    Parameter

    Plot_Results(Variables, Parameter, NoYes, Timesteps,Week,plotEFlows,plotAnalyses)                

def Plot_Results(Variables, Parameter,NoYes,Timesteps,Week,plotEFlows,plotAnalyses):
    
    Plotcounter = 0
    if plotEFlows == 1:
#--------------------------------------

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
        
        SubPlots1=0  
        SubPlots2=0 
        SubPlots3=0 
        SubPlots4=0 
        SubPlots5=0 
    
        LengthWeek=Timesteps//365*7
#--------------------------------------
        if NoYes['Load'] == 1:
            if NoYes['GridLoad'] == 1:
                GridLoadWeek = Variables['EFlow']['data']['GridLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.            
            if NoYes['LoadSupply'] == 0:
                BurnerLoadWeek = Variables['EFlow']['data']['BurnerLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.            
            if NoYes['EStor'] == 1:
                Bat2LoadWeek = Variables['EFlow']['data']['Bat2Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.
            SubPlots1=SubPlots1+1
        if NoYes['SellToGrid'] == 1:
            SubPlots1=SubPlots1+1
        if NoYes['PV'] == 1:
            PV2LoadWeek=Variables['EFlow']['data']['PV2Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.
            PVBurnerWeek=Variables['EFlow']['data']['PVBurner'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.
            if NoYes['SellToGrid'] == 1:
                PVGridWeek=Variables['EFlow']['data']['PVGrid'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.
                GridFeedIn=Variables['EFlow']['data']['PVGrid']*Timesteps/8760.
            if NoYes['EStor'] == 1:
                PV2BatWeek=Variables['EFlow']['data']['PV2Bat'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.            
            if Variables['Size']['data']['PV'] >= 0.005:
                SubPlots2=SubPlots2+1 
        if NoYes['CHP1'] == 1 or NoYes['CHP2'] == 1 or NoYes['CHP3'] == 1:  
            CHP12LoadWeek=np.zeros(LengthWeek)
            CHP22LoadWeek=np.zeros(LengthWeek)
            CHP32LoadWeek=np.zeros(LengthWeek)
            CHP1GridWeek=np.zeros(LengthWeek)
            CHP2GridWeek=np.zeros(LengthWeek)
            CHP3GridWeek=np.zeros(LengthWeek)
            CHP1GridFeedIn=np.zeros(Timesteps)
            CHP2GridFeedIn=np.zeros(Timesteps)
            CHP3GridFeedIn=np.zeros(Timesteps)
            CHP12BatWeek=np.zeros(LengthWeek)
            CHP22BatWeek=np.zeros(LengthWeek)
            CHP32BatWeek=np.zeros(LengthWeek)
            
            if NoYes['CHP1'] == 1:
                CHP12LoadWeek=Variables['EFlow']['data']['CHP12Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.                
                if NoYes['SellToGrid'] == 1:
                    CHP1GridWeek=Variables['EFlow']['data']['CHP1Grid'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
                    CHP1GridFeedIn=Variables['EFlow']['data']['CHP1Grid']*Timesteps/8760.
                if NoYes['EStor'] == 1:
                    CHP12BatWeek=Variables['EFlow']['data']['CHP12Bat'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
            if NoYes['CHP2'] == 1:            
                CHP22LoadWeek=Variables['EFlow']['data']['CHP22Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.                
                if NoYes['SellToGrid'] == 1:
                    CHP2GridWeek=Variables['EFlow']['data']['CHP2Grid'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
                    CHP2GridFeedIn=Variables['EFlow']['data']['CHP2Grid']*Timesteps/8760.
                if NoYes['EStor'] == 1:
                    CHP22BatWeek=Variables['EFlow']['data']['CHP22Bat'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
            if NoYes['CHP3'] == 1:            
                CHP32LoadWeek=Variables['EFlow']['data']['CHP32Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.                
                if NoYes['SellToGrid'] == 1:
                    CHP3GridWeek=Variables['EFlow']['data']['CHP3Grid'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
                    CHP3GridFeedIn=Variables['EFlow']['data']['CHP3Grid']*Timesteps/8760.
                if NoYes['EStor'] == 1:
                    CHP32BatWeek=Variables['EFlow']['data']['CHP32Bat'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.
            CHP2LoadWeek= CHP12LoadWeek + CHP22LoadWeek + CHP32LoadWeek
            if NoYes['SellToGrid'] == 1:
                CHPGridWeek = CHP1GridWeek + CHP2GridWeek + CHP3GridWeek 
                CHPGridFeedIn = CHP1GridFeedIn+ CHP2GridFeedIn + CHP3GridFeedIn                   
            if NoYes['EStor'] == 1:
                CHP2BatWeek = CHP12BatWeek + CHP22BatWeek + CHP32BatWeek

            if NoYes['CHP1'] == 1 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 1:            
                if Variables['Num']['data']['CHP1'] or Variables['Num']['data']['CHP2'] or Variables['Num']['data']['CHP3']>= 0.005:
                    SubPlots2=SubPlots2+3  
            elif NoYes['CHP1'] == 1 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0: 
                if Variables['Num']['data']['CHP1'] or Variables['Num']['data']['CHP2'] >= 0.005:
                    SubPlots2=SubPlots2+2
            elif NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 1:            
                if Variables['Num']['data']['CHP1'] or Variables['Num']['data']['CHP3']>= 0.005:
                    SubPlots2=SubPlots2+2 
            elif NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 1:            
                if Variables['Num']['data']['CHP2'] or Variables['Num']['data']['CHP3']>= 0.005:
                    SubPlots2=SubPlots2+2  
            elif NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 0:            
                if Variables['Num']['data']['CHP1']:
                    SubPlots2=SubPlots2+1                  
            elif NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:            
                if Variables['Num']['data']['CHP2']:
                    SubPlots2=SubPlots2+1
            elif NoYes['CHP1'] == 0 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 1:            
                if Variables['Num']['data']['CHP3']:
                    SubPlots2=SubPlots2+1
 
        if NoYes['EStor'] == 1:
            if Variables['Size']['data']['EStor'] >= 0.005:
                SubPlots3=SubPlots3+2
        if NoYes['QLoad'] == 1:
            NGBurner12QLoadWeek=np.zeros(LengthWeek)
            NGBurner22QLoadWeek=np.zeros(LengthWeek)
            NGBurner32QLoadWeek=np.zeros(LengthWeek)
            CHP12QLoadWeek=np.zeros(LengthWeek)
            CHP22QLoadWeek=np.zeros(LengthWeek)
            CHP32QLoadWeek=np.zeros(LengthWeek)
            QStor12QLoadWeek=np.zeros(LengthWeek)
            QStor22QLoadWeek=np.zeros(LengthWeek)
            QStor32QLoadWeek=np.zeros(LengthWeek)
                        
            if NoYes['NGBurner1'] == 1:
                NGBurner12QLoadWeek=Variables['QFlow']['data']['NGBurner12QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['NGBurner2'] == 1:
                NGBurner22QLoadWeek=Variables['QFlow']['data']['NGBurner22QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['NGBurner3'] == 1:
                NGBurner32QLoadWeek=Variables['QFlow']['data']['NGBurner32QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760                    
            if NoYes['CHP1'] == 1:
                CHP12QLoadWeek=Variables['QFlow']['data']['CHP12QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['CHP2'] == 1:
                CHP22QLoadWeek=Variables['QFlow']['data']['CHP22QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['CHP3'] == 1:
                CHP32QLoadWeek=Variables['QFlow']['data']['CHP32QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['QStor1'] == 1:
                QStor12QLoadWeek=Variables['QFlow']['data']['QStor12QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['QStor2'] == 1:
                QStor22QLoadWeek=Variables['QFlow']['data']['QStor22QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            if NoYes['QStor3'] == 1:
                QStor32QLoadWeek=Variables['QFlow']['data']['QStor32QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760
            NGBurner2QLoadWeek=NGBurner12QLoadWeek + NGBurner22QLoadWeek + NGBurner32QLoadWeek
            CHP2QLoadWeek=CHP12QLoadWeek + CHP22QLoadWeek +CHP32QLoadWeek
            QStor2QLoadWeek=QStor12QLoadWeek+QStor22QLoadWeek+QStor32QLoadWeek
            
            SubPlots4=SubPlots4+1

        if NoYes['QStor'] == 1:
            NGBurner12QStor1Week=np.zeros(LengthWeek)
            NGBurner22QStor1Week=np.zeros(LengthWeek)
            NGBurner32QStor1Week=np.zeros(LengthWeek)
            CHP12QStor1Week=np.zeros(LengthWeek)
            CHP22QStor1Week=np.zeros(LengthWeek)
            CHP32QStor1Week=np.zeros(LengthWeek)
            NGBurner12QStor2Week=np.zeros(LengthWeek)
            NGBurner22QStor2Week=np.zeros(LengthWeek)
            NGBurner32QStor2Week=np.zeros(LengthWeek)
            CHP12QStor2Week=np.zeros(LengthWeek)
            CHP22QStor2Week=np.zeros(LengthWeek)
            CHP32QStor2Week=np.zeros(LengthWeek)
            NGBurner12QStor3Week=np.zeros(LengthWeek)
            NGBurner22QStor3Week=np.zeros(LengthWeek)
            NGBurner32QStor3Week=np.zeros(LengthWeek)
            CHP12QStor3Week=np.zeros(LengthWeek)
            CHP22QStor3Week=np.zeros(LengthWeek)
            CHP32QStor3Week=np.zeros(LengthWeek)
            EHeatQStor2QStor1Week=np.zeros(LengthWeek)
            EHeatQStor2QStor2Week=np.zeros(LengthWeek)
            EHeatQStor2QStor3Week=np.zeros(LengthWeek)
            QStor1C=np.zeros(Timesteps)
            QStor2C=np.zeros(Timesteps)
            QStor3C=np.zeros(Timesteps)
            QStor1D=np.zeros(Timesteps)
            QStor2D=np.zeros(Timesteps)
            QStor3D=np.zeros(Timesteps)
            QinS1=np.zeros(Timesteps)
            QinS2=np.zeros(Timesteps)
            QinS3=np.zeros(Timesteps)
            
            if NoYes['QStor1'] == 1:
                QStor1C = Timesteps/8760.*Variables['QFlow']['data']['QStor1C']
                QStor1D =Timesteps/8760.*Variables['QFlow']['data']['QStor1D'] 
                QinS1 = Variables['QinS']['data']['QStor1C']\
                /(Variables['Num']['data']['QStor1C']*Parameter['QStorCapSize']['data']['QStor1C'])*100\
                /Parameter['QStorUseCap']['data']['QStor1C']
                if NoYes['NGBurner1'] == 1:  
                    NGBurner12QStor1Week=Variables['QFlow']['data']['NGBurner12QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['NGBurner2'] == 1:  
                    NGBurner12QStor1Week=Variables['QFlow']['data']['NGBurner22QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                if NoYes['NGBurner3'] == 1:  
                    NGBurner12QStor1Week=Variables['QFlow']['data']['NGBurner32QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760                  
                if NoYes['CHP1'] == 1:   
                    CHP12QStor1Week=Variables['QFlow']['data']['CHP12QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP2'] == 1:   
                    CHP22QStor1Week=Variables['QFlow']['data']['CHP22QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP3'] == 1:   
                    CHP32QStor1Week=Variables['QFlow']['data']['CHP32QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['EHeatQStor'] == 1:   
                    EHeatQStor2QStor1Week=Variables['QFlow']['data']['EHeatQStor2QStor1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                    EEHeatQStorWeek=Variables['EFlow']['data']['EHeatQStor'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760 
                    
            if NoYes['QStor2'] == 1:
                QStor2C = Timesteps/8760.*Variables['QFlow']['data']['QStor2C']
                QStor2D =Timesteps/8760.*Variables['QFlow']['data']['QStor2D']               
                QinS2 = Variables['QinS']['data']['QStor2C']\
                /(Variables['Num']['data']['QStor2C']*Parameter['QStorCapSize']['data']['QStor2C'])*100\
                /Parameter['QStorUseCap']['data']['QStor2C']
                if NoYes['NGBurner1'] == 1:  
                    NGBurner12QStor2Week=Variables['QFlow']['data']['NGBurner12QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['NGBurner2'] == 1:  
                    NGBurner12QStor2Week=Variables['QFlow']['data']['NGBurner22QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                if NoYes['NGBurner3'] == 1:  
                    NGBurner12QStor2Week=Variables['QFlow']['data']['NGBurner32QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760                  
                if NoYes['CHP1'] == 1:   
                    CHP12QStor2Week=Variables['QFlow']['data']['CHP12QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP2'] == 1:   
                    CHP22QStor2Week=Variables['QFlow']['data']['CHP22QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP3'] == 1:   
                    CHP32QStor2Week=Variables['QFlow']['data']['CHP32QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['EHeatQStor'] == 1:   
                    EHeatQStor2QStor2Week=Variables['QFlow']['data']['EHeatQStor2QStor2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                    EEHeatQStorWeek=Variables['EFlow']['data']['EHeatQStor'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760 
                    
            if NoYes['QStor3'] == 1:
                QStor3C = Timesteps/8760.*Variables['QFlow']['data']['QStor3C']
                QStor3D =Timesteps/8760.*Variables['QFlow']['data']['QStor3D']
                QinS3 = Variables['QinS']['data']['QStor3C']\
                /(Variables['Num']['data']['QStor3C']*Parameter['QStorCapSize']['data']['QStor3C'])*100\
                /Parameter['QStorUseCap']['data']['QStor3C']
                if NoYes['NGBurner1'] == 1:  
                    NGBurner12QStor3Week=Variables['QFlow']['data']['NGBurner12QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['NGBurner2'] == 1:  
                    NGBurner12QStor3Week=Variables['QFlow']['data']['NGBurner22QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                if NoYes['NGBurner3'] == 1:  
                    NGBurner12QStor3Week=Variables['QFlow']['data']['NGBurner32QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760                  
                if NoYes['CHP1'] == 1:   
                    CHP12QStor3Week=Variables['QFlow']['data']['CHP12QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP2'] == 1:   
                    CHP22QStor3Week=Variables['QFlow']['data']['CHP22QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['CHP3'] == 1:   
                    CHP32QStor3Week=Variables['QFlow']['data']['CHP32QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760   
                if NoYes['EHeatQStor'] == 1:   
                    EHeatQStor2QStor3Week=Variables['QFlow']['data']['EHeatQStor2QStor3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760  
                    EEHeatQStorWeek=Variables['EFlow']['data']['EHeatQStor'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760 
                
            NGBurner2QStorWeek=NGBurner12QStor1Week + NGBurner22QStor1Week + NGBurner32QStor1Week + NGBurner12QStor2Week \
            + NGBurner22QStor2Week + NGBurner32QStor2Week + NGBurner12QStor3Week + NGBurner22QStor3Week + NGBurner32QStor3Week
            CHP2QStorWeek=CHP12QStor1Week + CHP22QStor1Week +CHP32QStor1Week + CHP12QStor2Week + CHP22QStor2Week +CHP32QStor2Week \
            + CHP12QStor3Week + CHP22QStor3Week +CHP32QStor3Week
            
            EHeatQStor2QStorWeek= EHeatQStor2QStor1Week + EHeatQStor2QStor2Week +EHeatQStor2QStor3Week
            
            QStorC=QStor1C + QStor2C + QStor3C
            QStorD=QStor1D + QStor2D + QStor3D            
            QinS = QinS1 + QinS2+ QinS3
                
            if max(QStorD) >= 0.005:
                SubPlots5=SubPlots5+2 
                
        if NoYes['CHP'] == 1 and NoYes['PV'] == 1 and NoYes['SellToGrid'] == 1:
            GridFeedIn=Variables['EFlow']['data']['PVGrid']*Timesteps/8760.+CHPGridFeedIn
        elif NoYes['CHP'] == 1 and NoYes['PV'] == 0 and NoYes['SellToGrid'] == 1:
            GridFeedIn=CHPGridFeedIn
        elif NoYes['CHP'] == 0 and NoYes['PV'] == 1 and NoYes['SellToGrid'] == 1:
            GridFeedIn=Variables['EFlow']['data']['PVGrid']*Timesteps/8760.
        else:
            GridFeedIn = np.zeros(Timesteps)
#--------------------------------------------------------------------------------------  
    if SubPlots1 > 0:        
            plt.figure(Plotcounter, figsize=(6,3*SubPlots1))         
            SubPlotCounter=1
            x_axis=np.arange(0,LengthWeek)/(Timesteps/365.)
            
            if NoYes['Load'] == 1:  
                plt.subplot(SubPlots1*100+10+SubPlotCounter)
                SubPlotCounter=SubPlotCounter+1
                if NoYes['EHeatQStor'] == 1:
                    plt.plot(x_axis,Parameter['EProfil']['data']['Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='E-Load, HH',linewidth=0.7)
                    plt.plot(x_axis,Parameter['EProfil']['data']['Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.+EEHeatQStorWeek,label='E-Load, HH (inc. e-heating)',linewidth=0.7)
                else:                     
                    plt.plot(x_axis,Parameter['EProfil']['data']['Load'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='load, gesamt',linewidth=0.7) 
                                
                if NoYes['GridLoad'] == 1: 
                    if NoYes['PV'] == 1 and NoYes['CHP'] == 1 and NoYes['EStor'] == 1: 
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
                    if NoYes['PV'] == 1:               
                        if NoYes['CHP1'] == 1:
                            if NoYes['EStor'] == 1:
                                fcolors=[CPV2Load, CCHP2Load, CBat2Load, CBurnerLoad]
                                plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,Bat2LoadWeek,BurnerLoadWeek,colors=fcolors)  
                                plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                                plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                                plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging')
                                plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')
                            else:
                                fcolors=[CPV2Load, CCHP2Load, CBurnerLoad]
                                plt.stackplot(x_axis,PV2LoadWeek,CHP2LoadWeek,BurnerLoadWeek,colors=fcolors)  
                                plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                                plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                                plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')
                        elif NoYes['EStor'] == 1:
                            fcolors=[CPV2Load, CBat2Load, CBurnerLoad]
                            plt.stackplot(x_axis,PV2LoadWeek,Bat2LoadWeek,BurnerLoadWeek,colors=fcolors)  
                            plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                            plt.plot([], [], color=CBat2Load, linewidth=10, label='Battery-load-discharging')
                            plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')
                        else:
                            fcolors=[CPV2Load, CBurnerLoad]
                            plt.stackplot(x_axis,PV2LoadWeek,BurnerLoadWeek,colors=fcolors)  
                            plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                            plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')                     
                    else:
                        fcolors=[CBurnerLoad]
                        plt.stackplot(x_axis,BurnerLoadWeek,colors=fcolors)  
                        plt.plot([], [], color=CBurnerLoad, linewidth=10, label='load-Abregelung')  
    
                plt.ylabel('Power [kW]')
                plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                plt.xlim(0,7)
                if NoYes['EHeatQStor'] == 1:
                    plt.ylim(0,np.round(max((Parameter['EProfil']['data']['Load']+Variables['EFlow']['data']['EHeatQStor'])*Timesteps/8760)+.5),0)                    
                else:
                    plt.ylim(0,np.round(max(Parameter['EProfil']['data']['Load']*Timesteps/8760)+.5),0)
                plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            
            if NoYes['SellToGrid'] == 1:  
                plt.subplot(SubPlots1*100+10+SubPlotCounter)
                SubPlotCounter=SubPlotCounter+1
                
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
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(-np.round((max(Variables['EFlow']['data']['GridLoad']*Timesteps/8760)+.5),0),\
                    np.round((max(GridFeedIn)+.5),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            
            plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
            plt.savefig('Results\GridFlowsWeek.png', dpi=300, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, bbox_inches='tight', pad_inches=0.1,
                frameon=None)
            Plotcounter=Plotcounter+1
               
    # Generation plots 
    if SubPlots2 > 0:
            plt.figure(Plotcounter, figsize=(6,3*SubPlots2))         
            SubPlotCounter=1
            
            if NoYes['PV'] == 1:
                if Variables['Size']['data']['PV'] >= 0.005:
                    plt.subplot(SubPlots2*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.plot(x_axis,Parameter['EProfil']['data']['PV'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Variables['Size']['data']['PV']*Timesteps/8760.,label='PV, generated',linewidth=0.7)                
                                                                   
                    if NoYes['SellToGrid'] == 1:                    
                        if NoYes['EStor'] == 1:
                            fcolors=[CPV2Load, CPV2Bat, CPVGrid, CPVBurner]
                            plt.stackplot(x_axis,PV2LoadWeek,PV2BatWeek,PVGridWeek,PVBurnerWeek,colors=fcolors)
                            plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                            plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')   
                            plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in') 
                            plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')                         
                        else:  
                            fcolors=[CPV2Load, CPVGrid, CPVBurner]
                            plt.stackplot(x_axis,PV2LoadWeek,PVGridWeek,PVBurnerWeek,colors=fcolors) 
                            plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                            plt.plot([], [], color=CPVGrid, linewidth=10, label='PV-Grid feed-in') 
                            plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')    
                    elif NoYes['EStor'] == 1:
                        fcolors=[CPV2Load, CPV2Bat, CPVBurner]
                        plt.stackplot(x_axis,PV2LoadWeek,PV2BatWeek,PVBurnerWeek,colors=fcolors)       
                        plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                        plt.plot([], [], color=CPV2Bat, linewidth=10, label='PV-Battery charging')   
                        plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')                                    
                    else:
                        fcolors=[CPV2Load, CPVBurner]
                        plt.stackplot(x_axis,PV2LoadWeek,PVBurnerWeek,colors=fcolors)  
                        plt.plot([], [], color=CPV2Load, linewidth=10, label='PV-Direct consumption')
                        plt.plot([], [], color=CPVBurner, linewidth=10, label='PV-Curtailment losses')
                   
                    plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(0,np.round((max(Parameter['EProfil']['data']['PV']\
                    *Variables['Size']['data']['PV']*Timesteps/8760)+.5),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                    
            if NoYes['CHP1'] == 1: 
                if Variables['Num']['data']['CHP1'] >= 0.005:
                    plt.subplot(SubPlots2*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.plot(x_axis,Variables['EFlow']['data']['CHP1'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='E-CHP eco1.0, generated',linewidth=0.7) 
    
                    if NoYes['SellToGrid'] == 1:                    
                        if NoYes['EStor'] == 1:
                            fcolors=[CCHP2Load, CCHP2Bat, CCHPGrid]
                            plt.stackplot(x_axis,CHP12LoadWeek,CHP12BatWeek,CHP1GridWeek,colors=fcolors)
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                            plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')   
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')                     
                        else:  
                            fcolors=[CCHP2Load, CCHPGrid]
                            plt.stackplot(x_axis,CHP12LoadWeek, CHP1GridWeek,colors=fcolors) 
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption') 
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')     
                    elif NoYes['EStor'] == 1:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP12LoadWeek,CHP12BatWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                        plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP-Battery charging')   
                    else:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP12LoadWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP-Direct consumption')
                                   
                    plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(0,np.round((Variables['Num']['data']['CHP1']*Parameter['CHP1FixedSize']['data']),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                    
            if NoYes['CHP2'] == 1: 
                if Variables['Num']['data']['CHP2'] >= 0.005:
                    plt.subplot(SubPlots2*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.plot(x_axis,Variables['EFlow']['data']['CHP2'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='E-CHP eco3.0, generated',linewidth=0.7) 
    
                    if NoYes['SellToGrid'] == 1:                    
                        if NoYes['EStor'] == 1:
                            fcolors=[CCHP2Load, CCHP2Bat, CCHPGrid]
                            plt.stackplot(x_axis,CHP22LoadWeek,CHP22BatWeek,CHP2GridWeek,colors=fcolors)
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption')
                            plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP2-Battery charging')   
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP2-Grid feed-in')                     
                        else:  
                            fcolors=[CCHP2Load, CCHPGrid]
                            plt.stackplot(x_axis,CHP22LoadWeek, CHP2GridWeek,colors=fcolors) 
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption') 
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP-Grid feed-in')     
                    elif NoYes['EStor'] == 1:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP22LoadWeek,CHP22BatWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption')
                        plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP2-Battery charging')   
                    else:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP22LoadWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP2-Direct consumption')
                                   
                    plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(0,np.round((Variables['Num']['data']['CHP2']*Parameter['CHP2FixedSize']['data']),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            
            if NoYes['CHP3'] == 1: 
                if Variables['Num']['data']['CHP3'] >= 0.005:
                    plt.subplot(SubPlots2*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.plot(x_axis,Variables['EFlow']['data']['CHP3'][LengthWeek*(Week-1):LengthWeek*Week]\
                    *Timesteps/8760.,label='E-CHP eco4.7, generated',linewidth=0.7) 
    
                    if NoYes['SellToGrid'] == 1:                    
                        if NoYes['EStor'] == 1:
                            fcolors=[CCHP2Load, CCHP2Bat, CCHPGrid]
                            plt.stackplot(x_axis,CHP32LoadWeek,CHP32BatWeek,CHP3GridWeek,colors=fcolors)
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption')
                            plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP3-Battery charging')   
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP3-Grid feed-in')                     
                        else:  
                            fcolors=[CCHP2Load, CCHPGrid]
                            plt.stackplot(x_axis,CHP32LoadWeek, CHP3GridWeek,colors=fcolors) 
                            plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption') 
                            plt.plot([], [], color=CCHPGrid, linewidth=10, label='CHP3-Grid feed-in')     
                    elif NoYes['EStor'] == 1:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP32LoadWeek,CHP32BatWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption')
                        plt.plot([], [], color=CCHP2Bat, linewidth=10, label='CHP3-Battery charging')   
                    else:
                        fcolors=[CCHP2Load, CCHP2Bat]
                        plt.stackplot(x_axis,CHP32LoadWeek,colors=fcolors)
                        plt.plot([], [], color=CCHP2Load, linewidth=10, label='CHP3-Direct consumption')
                                   
                    plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.xlim(0,7)
                    plt.ylim(0,np.round((Variables['Num']['data']['CHP3']*Parameter['CHP3FixedSize']['data']),0))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))            
            plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
            plt.savefig('Results\GenerationFlowsWeek.png', dpi=300, facecolor='w', edgecolor='w',
                orientation='portrait', papertype=None, format=None,
                transparent=False, bbox_inches='tight', pad_inches=0.1,
                frameon=None)
            Plotcounter=Plotcounter+1
               
        # E-Storage plots 
    if SubPlots3 > 0:
            plt.figure(Plotcounter, figsize=(6,3*SubPlots3))         
            SubPlotCounter=1
                
            if NoYes['EStor'] == 1:
                if Variables['Size']['data']['EStor'] >= 0.005:
                    plt.subplot(SubPlots3*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.plot(x_axis,(Timesteps/8760.*Variables['EFlow']['data']['BatCEStor'][LengthWeek*(Week-1):LengthWeek*Week]\
                    -Timesteps/8760.*Variables['EFlow']['data']['EStorBatD'][LengthWeek*(Week-1):LengthWeek*Week])
                    ,label='Battery power',linewidth=0.5)
                    
                    if NoYes['PV'] == 1 and NoYes['CHP'] == 1:
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
                    plt.xlim(0,7)
                    plt.ylim(-np.round((Variables['Size']['data']['BatC']*Timesteps/8760+.25),0),np.round((Variables['Size']['data']['BatC']*Timesteps/8760+.25),0))
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                    
                    plt.subplot(SubPlots3*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    
                    plt.stackplot(x_axis,(Variables['EinS']['data'][LengthWeek*(Week-1):LengthWeek*Week]*100/Variables['Size']['data']['EStor']/Parameter['UseableEStorCap']['data']),colors=[CEStor])  
                    plt.plot([], [], color=CEStor, linewidth=10, label='Energy in battery')                
                    plt.ylabel('SOC [%]')
                    plt.xlim(0,7)
                    plt.ylim(0,100)
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))   
            
                    plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
                    plt.savefig('Results\EStorageWeek.png', dpi=300, facecolor='w', edgecolor='w',
                        orientation='portrait', papertype=None, format=None,
                        transparent=False, bbox_inches='tight', pad_inches=0.1,
                        frameon=None)
                    Plotcounter=Plotcounter+1
               
        # Q-Load plots   
    if SubPlots4 > 0:       
            plt.figure(Plotcounter, figsize=(6,3*SubPlots4))         
            SubPlotCounter=1
            
            if NoYes['QLoad'] == 1:  
                plt.subplot(SubPlots4*100+10+SubPlotCounter)
                SubPlotCounter=SubPlotCounter+1
                plt.plot(x_axis,Parameter['QProfil']['data']['QLoad'][LengthWeek*(Week-1):LengthWeek*Week]\
                *Timesteps/8760.,label='Q-load, total',linewidth=0.7) 
                            
                if NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['QStor'] == 1:
                    fcolors=[CCHP2QLoad, CNGBurner2QLoad, CQStor2QLoad]
                    plt.stackplot(x_axis,CHP2QLoadWeek,NGBurner2QLoadWeek,QStor2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-load')                        
                    plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-load')
                    plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')
                elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['QStor'] == 0:
                    fcolors=[CCHP2QLoad, CNGBurner2QLoad]
                    plt.stackplot(x_axis,CHP2QLoadWeek,NGBurner2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-load')
                    plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-load')
                elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['QStor'] == 1:
                    fcolors=[CNGBurner2QLoad, CQStor2QLoad]
                    plt.stackplot(x_axis,NGBurner2QLoadWeek,QStor2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-load')            
                    plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')
                elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['QStor'] == 0:
                    fcolors=[CNGBurner2QLoad]
                    plt.stackplot(x_axis,NGBurner2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CNGBurner2QLoad, linewidth=10, label='NG burner-load')     
                elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['QStor'] == 1:
                    fcolors=[CCHP2QLoad, CQStor2QLoad]
                    plt.stackplot(x_axis,CHP2QLoadWeek,QStor2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-load')
                    plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')
                elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['QStor'] == 0:
                    fcolors=[CCHP2QLoad]
                    plt.stackplot(x_axis,CHP2QLoadWeek,colors=fcolors)  
                    plt.plot([], [], color=CCHP2QLoad, linewidth=10, label='Q-CHP-load')  
                elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 0 and NoYes['QStor'] == 1:
                    fcolors=[CQStor2QLoad,]
                    plt.stackplot(x_axis,QStor2QLoadWeek,Week,colors=fcolors)  
                    plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')                     
    
                plt.ylabel('Power [kW]')
                plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                plt.xlim(0,7)
                plt.ylim(0,np.round(max(Parameter['QProfil']['data']['QLoad']*Timesteps/8760)+.5),0)
                plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))  
                
                plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
                plt.savefig('Results\QFlowsWeek.png', dpi=300, facecolor='w', edgecolor='w',
                    orientation='portrait', papertype=None, format=None,
                    transparent=False, bbox_inches='tight', pad_inches=0.1,
                    frameon=None)
                Plotcounter=Plotcounter+1
               
        # Q-Storage plots  
    if SubPlots5 > 0:
            plt.figure(Plotcounter, figsize=(6,3*SubPlots5))         
            SubPlotCounter=1
                
            if NoYes['QStor'] == 1:                           
                if max(QStorD) >= 0.005:
                    plt.subplot(SubPlots5*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.plot(x_axis,QStorC[LengthWeek*(Week-1):LengthWeek*Week],color=sns.xkcd_rgb["light blue"],label='Q-storage charging power',linewidth=0.7)                 
                    plt.plot(x_axis,-QStorD[LengthWeek*(Week-1):LengthWeek*Week],color=sns.xkcd_rgb["dark blue"],label='Q-storage discharging power',linewidth=0.7)                             
                    if NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 0:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CNGBurner2QStor, CCHP2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,NGBurner2QStorWeek,CHP2QStorWeek,colors=fcolors2)  
                        plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
                        plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load')
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['EHeatQStor'] == 0:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CNGBurner2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,NGBurner2QStorWeek,colors=fcolors2)   
                        plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 0 and NoYes['EHeatQStor'] == 1:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CNGBurner2QStor,CEHeat2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,NGBurner2QStorWeek,EHeatQStor2QStorWeek,colors=fcolors2)   
                        plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
                        plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 1 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 1:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CNGBurner2QStor,CCHP2QStor,CEHeat2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,NGBurner2QStorWeek,CHP2QStorWeek,EHeatQStor2QStorWeek,colors=fcolors2)   
                        plt.plot([], [], color=CNGBurner2QStor, linewidth=10, label='NG burner-storage charging')
                        plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
                        plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 0:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CCHP2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,CHP2QStorWeek,colors=fcolors2)    
                        plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 0 and NoYes['EHeatQStor'] == 1:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CEHeat2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,EHeatQStor2QStorWeek,colors=fcolors2)    
                        plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    elif NoYes['NGBurner'] == 0 and NoYes['CHP'] == 1 and NoYes['EHeatQStor'] == 1:
                        fcolors1=[CQStor2QLoad]
                        fcolors2=[CCHP2QStor,CEHeat2QStor]
                        plt.stackplot(x_axis,-QStor2QLoadWeek,colors=fcolors1) 
                        plt.stackplot(x_axis,CHP2QStorWeek,EHeatQStor2QStorWeek,colors=fcolors2)   
                        plt.plot([], [], color=CCHP2QStor, linewidth=10, label='Q-CHP-storage charging')
                        plt.plot([], [], color=CEHeat2QStor, linewidth=10, label='E. heater-storage charging')
                        plt.plot([], [], color=CQStor2QLoad, linewidth=10, label='Q-storage-load') 
                        plt.ylabel('Power [kW]')
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))    
                    plt.xlim(0,7)
                    plt.ylim(-np.round((max(QStorD)+.5),0)*Timesteps/8760.,\
                    np.round((max(QStorC)+.5),0)*Timesteps/8760.)                                        
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
                    
                    plt.subplot(SubPlots5*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.stackplot(x_axis,QinS[LengthWeek*(Week-1):LengthWeek*Week],colors=[CQStor])
                    plt.plot([], [], color=CQStor, linewidth=10, label='Energy in Q-storage')                
                    plt.ylabel('SOC [%]')
                    plt.xlim(0,7)
                    plt.ylim(0,100)
                    plt.xticks(np.arange(0,LengthWeek/(Timesteps/365)+1, 1))
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5)) 
                    
                    plt.xlabel('Day of ''week no. '+str(Week)+' of the year')
                    plt.savefig('Results\QStorageWeek.png', dpi=300, facecolor='w', edgecolor='w',
                        orientation='portrait', papertype=None, format=None,
                        transparent=False, bbox_inches='tight', pad_inches=0.1,
                        frameon=None)
                    Plotcounter=Plotcounter+1
        
    if plotAnalyses == 1:  
# Energy usage
        
        CPV2Load=sns.xkcd_rgb["medium green"]
        CPV2Bat=sns.xkcd_rgb["dark lavender"]
        CPVGrid=sns.xkcd_rgb["pale red"]
        CPVBurner=sns.xkcd_rgb["dark yellow"]
        
        CCHP2Load=sns.xkcd_rgb["deep green"]
        CCHP2Bat=sns.xkcd_rgb["dark violet"]
        CCHPGrid=sns.xkcd_rgb["deep red"]
        CCHPBurner=sns.xkcd_rgb["dark yellow"]      
        CCHP2Load=sns.xkcd_rgb["light green"]
        CCHP2Bat=sns.xkcd_rgb["violet"]
        CCHPGrid=sns.xkcd_rgb["light red"]
        CCHP2Burner=sns.xkcd_rgb["yellow"]  
        
        y_ticks=np.arange(0,101,20)
        tickslabel=np.arange(0,101,20) 
        SubPlots=2    
        plt.figure((Plotcounter), figsize=(6,3*SubPlots))
        SubPlotCounter=1              
        plt.subplot(SubPlots*100+10+SubPlotCounter)
        SubPlotCounter=SubPlotCounter+1
        width = 0.5  
                   
        if NoYes['PV'] == 1 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP1Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1'])        
            
            elif Variables['Num']['data']['CHP1'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
            
            elif Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])
                
        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP2Grid_per)            
                Gen2Load = (PV2Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP22Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP2'])        
            
            elif Variables['Num']['data']['CHP2'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])
        
        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 0 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 1:
            if Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP3'])        
            
            elif Variables['Num']['data']['CHP3'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (CHP3Grid_per)            
                Gen2Load = (CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP32Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])
    
        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2,3])                
                Gen2Grid = (PVGrid_per, CHP1Grid_per, CHP2Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per, CHP22Bat_per)
                Gen2Burner = (PVBurner_per, 0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1', 'CHP2'])  
            
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP1Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1'])  
                
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP2Grid_per)            
                Gen2Load = (PV2Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP22Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP2']) 
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005:
                BarCounter = np.array([1,2])                
                Gen2Grid = (CHP1Grid_per, CHP2Grid_per)            
                Gen2Load = (CHP12Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per, CHP22Bat_per)
                Gen2Burner = (0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1', 'CHP2'])                 
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
            
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])  

        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 1:
            if Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2,3])               
                Gen2Grid = (PVGrid_per, CHP1Grid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1', 'CHP2'])  
            
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP1Grid_per)            
                Gen2Load = (PV2Load_per, CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP12Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1'])  
                
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP2']) 
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005:
                BarCounter = np.array([1,2])                
                Gen2Grid = (CHP1Grid_per, CHP3Grid_per)            
                Gen2Load = (CHP12Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per, CHP32Bat_per)
                Gen2Burner = (0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1', 'CHP2'])                 
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
            
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP3Grid_per)            
                Gen2Load = (CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP32Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])  
                
        elif NoYes['PV'] == 1 and NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 1:
            if Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2,3])               
                Gen2Grid = (PVGrid_per, CHP2Grid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP22Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP22Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1', 'CHP2'])  
            
            elif Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP2Grid_per)            
                Gen2Load = (PV2Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP22Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP1'])  
                
            elif Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (PVGrid_per, CHP3Grid_per)            
                Gen2Load = (PV2Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per, CHP32Bat_per)
                Gen2Burner = (PVBurner_per, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV', 'CHP2']) 
                
            elif Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005:
                BarCounter = np.array([1,2])                
                Gen2Grid = (CHP2Grid_per, CHP3Grid_per)            
                Gen2Load = (CHP22Load_per, CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per, CHP32Bat_per)
                Gen2Burner = (0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1', 'CHP2'])                 
                
            elif Variables['Num']['data']['CHP2'] >= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
            
            elif Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Num']['data']['CHP3'] >= 0.005 and Variables['Size']['data']['PV'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP3Grid_per)            
                Gen2Load = (CHP32Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP32Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])
            
            elif Variables['Num']['data']['CHP2'] <= 0.005 and Variables['Num']['data']['CHP3'] <= 0.005 and Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV']) 
                
        elif NoYes['PV'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 0:
            if Variables['Size']['data']['PV'] >= 0.005:
                BarCounter = np.array([1])                
                Gen2Grid = (PVGrid_per)            
                Gen2Load = (PV2Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (PV2Bat_per)
                Gen2Burner = (PVBurner_per)
                    
                plt.bar(BarCounter, Gen2Grid, color=CPVGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CPV2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CPVBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['PV'])        
                
        elif NoYes['PV'] == 0 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 0 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP1'] >= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
                
        elif NoYes['PV'] == 0 and NoYes['CHP1'] == 0 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP2'] >= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])    
                
        elif NoYes['PV'] == 0 and NoYes['CHP1'] == 1 and NoYes['CHP2'] == 1 and NoYes['CHP3'] == 0:
            if Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] <= 0.005: 
                BarCounter = np.array([1])                
                Gen2Grid = (CHP1Grid_per)            
                Gen2Load = (CHP12Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1'])
                
            elif Variables['Num']['data']['CHP1'] <= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005:  
                BarCounter = np.array([1])                
                Gen2Grid = (CHP2Grid_per)            
                Gen2Load = (CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP22Bat_per)
                Gen2Burner = (0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHP2Burner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CCHP2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP2'])  
                
            elif Variables['Num']['data']['CHP1'] >= 0.005 and Variables['Num']['data']['CHP2'] >= 0.005: 
                BarCounter = np.array([1,2])                
                Gen2Grid = (CHP1Grid_per, CHP2Grid_per)            
                Gen2Load = (CHP12Load_per, CHP22Load_per)
                if NoYes['EStor'] == 1:
                    Gen2Bat = (CHP12Bat_per, CHP22Bat_per)
                Gen2Burner = (0, 0)
                    
                plt.bar(BarCounter, Gen2Grid, color=CCHPGrid, width=width, linewidth=0, label='Grid feed-in')  
                plt.bar(BarCounter, Gen2Load,bottom=Gen2Grid, color=CCHP2Load, width=width, linewidth=0, label='Direct consumption')
                plt.bar(BarCounter, Gen2Burner,bottom=np.array(Gen2Load)+np.array(Gen2Grid), color=CCHPBurner, width=width, linewidth=0, label='Curtailment losses')
                if NoYes['EStor'] == 1:
                    plt.bar(BarCounter, Gen2Bat,bottom=np.array(Gen2Load)+np.array(Gen2Grid)+np.array(Gen2Burner), color=CPV2Bat, width=width, linewidth=0, label='Battery charging')
                plt.xlim(BarCounter[0]-0.5*width, BarCounter[-1]+1.5*width)
                plt.xticks(BarCounter+0.5*width, ['CHP1', 'CHP2']) 
        
        plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
        plt.xlabel('Installed DER')
        plt.ylabel('Energy [%]')
        plt.ylim(0,100)
        plt.yticks(y_ticks, tickslabel)
        plt.savefig('Results\EnergyDistribution.png', dpi=300, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches='tight', pad_inches=0.1,
        frameon=None)
        Plotcounter=Plotcounter + 1
               
# Power distribution 
        if NoYes['NGBurner'] == 1 or NoYes['CHP'] == 1 \
        or NoYes['EStor'] == 1:          
            x_axis=np.arange(0,Timesteps)
            x_ticks=np.arange(0,(Timesteps+1),Timesteps/5)
            SubPlots=0
            if NoYes['NGBurner1'] == 1:
                if Variables['Num']['data']['NGBurner1'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['NGBurner2'] == 1:
                if Variables['Num']['data']['NGBurner2'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['NGBurner3'] == 1:
                if Variables['Num']['data']['NGBurner3'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['CHP1'] == 1:
                if Variables['Num']['data']['CHP1'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['CHP2'] == 1:
                if Variables['Num']['data']['CHP2'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['CHP3'] == 1:
                if Variables['Num']['data']['CHP3'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
                    Plotcounter = Plotcounter + 1
            if NoYes['EStor'] == 1:
                if Variables['Size']['data']['EStor'] >= 0.005: 
                    SubPlots=SubPlots+1 
                    plt.figure(Plotcounter, figsize=(6,3*SubPlots))
            SubPlotCounter=1
            if NoYes['NGBurner1'] == 1:
                if Variables['Num']['data']['NGBurner1'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['QFlow']['data']['NGBurner1']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['NGBurner1']*Parameter['QMaxSize']['data']['NGBurner1'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of NG burner1 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            if NoYes['NGBurner2'] == 1:
                if Variables['Num']['data']['NGBurner2'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['QFlow']['data']['NGBurner2']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['NGBurner2']*Parameter['QMaxSize']['data']['NGBurner2'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of NG burner2 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))   
            if NoYes['NGBurner3'] == 1:
                if Variables['Num']['data']['NGBurner3'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['QFlow']['data']['NGBurner3']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['NGBurner3']*Parameter['QMaxSize']['data']['NGBurner3'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of NG burner3 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))                     
            if NoYes['CHP1'] == 1:
                if Variables['Num']['data']['CHP1'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['EFlow']['data']['CHP1']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['CHP1']*Parameter['CHP1FixedSize']['data'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of CHP1 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            if NoYes['CHP2'] == 1:
                if Variables['Num']['data']['CHP2'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['EFlow']['data']['CHP2']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['CHP2']*Parameter['CHP2FixedSize']['data'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of CHP2 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))   
            if NoYes['CHP3'] == 1:
                if Variables['Num']['data']['CHP3'] >= 0.005: 
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort(Variables['EFlow']['data']['CHP3']))*100*(Timesteps/8760)/\
                    (Variables['Num']['data']['CHP3']*Parameter['CHP3FixedSize']['data'])\
                    ,0,facecolor=sns.xkcd_rgb["denim blue"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["denim blue"],label='Distribution of CHP3 power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5)) 
            if NoYes['EStor'] == 1:
                if Variables['Size']['data']['EStor'] >= 0.005:
                    plt.subplot(SubPlots*100+10+SubPlotCounter)
                    SubPlotCounter=SubPlotCounter+1
                    plt.fill_between(x_axis,(np.sort((Variables['EFlow']['data']['BatCEStor']+Variables['EFlow']['data']['EStorBatD'])))*\
                    100*(Timesteps/8760)/Variables['Size']['data']['BatC'],0,facecolor=sns.xkcd_rgb["medium green"])
                    plt.ylabel('Power [%]')
                    plt.plot([], [], sns.xkcd_rgb["medium green"],label='Distribution of battery power')
                    plt.xlim(0,Timesteps)
                    plt.ylim(0,100)
                    plt.yticks(y_ticks, tickslabel)
                    plt.xticks(x_ticks, tickslabel)
                    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
            plt.xlabel('Percentage of opertion hours [%/a]')
            plt.savefig('Results\PowerDistribution.png', dpi=300, facecolor='w', edgecolor='w',
            orientation='portrait', papertype=None, format=None,
            transparent=False, bbox_inches='tight', pad_inches=0.1,
            frameon=None)

#--------------------------------------

            
#==============================================================================
#     if plotSankey == 1:
#         fig = plt.figure(figsize=(8, 3))
#         ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[])
#         sankey = Sankey(ax=ax, format='%.1G', unit=' MWh', gap=0.5, scale=0.6/PV_tot)
#         
#         sankey.add(label='PV', facecolor='#37c959', rotation=-90,
#            flows=[-PVGrid_tot, -PVBurner_tot, PV_tot, -PV2Load_tot, -PV2Bat_tot,],
#            labels=['', '', '', '', ''],
#            pathlengths=[0.5,0.5,0.5,0.5,0.1],
#            orientations=[-1, -1, 0, 1, 1])        
#         sankey.add(label='Battery', facecolor='r',
#            flows=[PV2Bat_tot, -BatDisch_tot, -BatBurner_tot],
#            labels=[None, None, None],
#            pathlengths=[0.05, 0.1, 0.1],
#            orientations=[0, 1, -1], prior=0, connect=(4, 0))
#         sankey.add(label='Load', facecolor='g',
#            flows=[BatDisch_tot, PV2Load_tot, ELoadGrid_tot, -ELoad_tot],
#            labels=['', '', '', ''],
#            pathlengths=[0.3, 0.01, 0.1, 0.5],
#            orientations=[-1, 0, -1, 0], prior=0, connect=(3, 1))
#         sankey.add(label='Grid exchange', facecolor='b',
#            flows=[PVGrid_tot, -ELoadGrid_tot],
#            labels=['', ''],
#            pathlengths=0.25,
#            orientations=[-1, 1], prior=0, connect=(0, 0))
#         diagrams = sankey.finish()
#         plt.legend(loc='best')
#         plt.show()
#         fig.savefig('Sankey.png', dpi=300, facecolor='w', edgecolor='w',
#         orientation='portrait', papertype=None, format=None,
#         transparent=False, bbox_inches='tight', pad_inches=0.1,
#         frameon=None)
#                     
#     Eco['npv']=npv
#     Eco['Invest'] = Fix_I
#     Eco['EInvest'] = EFix_I
#     Eco['QInvest'] = QFix_I
#     if NoYes['PV'] == 1:
#         Eco['PVGridSales'] = sum([Parameter['Sign']['data']['PVGrid']*sum([Parameter['EVarCost']['data']['PVGrid'][t-1]*Variables['EFlow']['data']['PVGrid'][t-1] for t in set(Sets['Time_Set']['data'])])\
#         *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['EVarCost_Inc']['data']['PVGrid'],Parameter['RRR']['data'])])
#         Eco['LoadGridCost'] = sum([Parameter['Sign']['data']['GridLoad']*sum([Parameter['EVarCost']['data']['GridLoad'][t-1]*Variables['EFlow']['data']['GridLoad'][t-1] for t in set(Sets['Time_Set']['data'])])\
#         *bwff.bwf_F10(Parameter['CalcPeriod']['data'],Parameter['EVarCost_Inc']['data']['GridLoad'],Parameter['RRR']['data'])])
#     Eco['NGcost']= cQVar
#     if NoYes['EStorSub'] == 1:    
#         Eco['EStorSub'] = Variables['EStorSub']['data']    
#     
#     if NoYes['PV'] == 1:
#         SysSize['PVkWp'] = Variables['Size']['data']['PV']
#     
#     if NoYes['EStor'] == 1:
#         SysSize['EStorkWh'] = Variables['Size']['data']['EStor']
#         SysSize['EStorkW'] = Variables['Size']['data']['BatC']    
#     
#     if NoYes['PV'] == 1:
#         PVdata['PV_total'] = PV_tot  
#         PVdata['PVGrid_total'] = PVGrid_tot
#         PVdata['PVGrid_percentage'] = PVGrid_per
#         PVdata['PVSelf_total'] = PVSelf_tot
#         PVdata['PVSelf_percentage'] = PVSelf_per
#         PVdata['PVLosses_total'] = PVBurner_tot
#         PVdata['PVLosses_percentage'] = PVBurner_per
#     
#     ELoaddata['ELoad_total'] = ELoad_tot 
#     ELoaddata['ELoadGrid_total'] = ELoadGrid_tot
#     ELoaddata['ELoadGrid_percentage'] = ELoadGrid_per
#    ELoaddata['ELoadSelf_total'] = ELoadSelf_tot
#    ELoaddata['ELoadSelf_percentage'] = ELoadSelf_per
#==============================================================================
            