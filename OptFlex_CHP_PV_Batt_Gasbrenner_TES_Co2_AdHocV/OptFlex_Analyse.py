# -*- coding: utf-8 -*-
"""
Created on Wed May 18 19:47:11 2016
@author: tkreiske
19.5.16 ToDo: Calculate: Strom-Kosten, Gas-Kosten, Einnahmen aus PV Exp, Einnahmen aus CHP Eig/Exp
      Calculate: Battery2Load, PV2Load, CHPel2Load
      Calculate: CHPrunning time, on/off
      Calculated CHP2Batt/2/Capacity, PV2Batt/2/Capacity für Batterieplot
"""

import numpy as np
#import scipy as sci
import scipy.io as sio
import matplotlib.pyplot as plt
import pandas as pd
from itertools import cycle, islice
import seaborn as sns

# --------------------------------
# Analyse total, integrated values
# --------------------------------

def Analyse_Horizon():
    
    plt.close("all")
    # --------------------------------
    # Read Input-KPI Files
    # --------------------------------
    name = 'Real'
 
   #Haushalt = ['EFH','MFH']    
    #Haushalt = ['MFH']    # add values and InputFiles TMK 3.6.16
    Haushalt = ['EFH']    
    
    #TimeSeriesIn = ['VDE', 'LPG']    
    #TimeSeriesIn = ['VDE']    
    TimeSeriesIn = ['LPG']    
    
    #InChoice = ['ohneFIT','Default']     
    #InChoice = ['ohneFIT']     
    InChoice = ['Default']    
    
    #fore_method = ['Persistenz', 'Mittel']
    fore_method = ['Persistenz']
    #fore_method = ['Mittel']
    #fore_method = ['Perfekt']   
        
    
    Horizon = [2, 15, 36, 72, 144] 
    #Horizon = [36]
    #Horizon = [144]
    
    Saison = ['Winter','Sommer','Uebergang']    
    #Saison = ['Winter']    
    #Saison = ['Uebergang']
    #Saison = ['Sommer']          
   
      
    for g in range (0, len(Haushalt)):
     haushalt = Haushalt[g]   
     for h in range(0, len(TimeSeriesIn)):  
      datachoice = TimeSeriesIn[h]
      for l in range(0, len(InChoice)):
        inputchoice = InChoice[l]
        for k in range(0, len(fore_method)):
          fore = fore_method[k]
          for j in range(0, len(Saison)):
            saison = Saison[j]  
            for i in range(0, len(Horizon)):
             PrHoBin = Horizon[i]   
           
             INOUT_string1 = str(PrHoBin/6.)+'_'+saison+'_'+fore+'_'+inputchoice+'_'+datachoice+'_'+haushalt

             if i==0 and j==0:  
              
                KPI = pd.read_csv('Results\KPIsAdhocV'+str(name)+'_'+INOUT_string1+'.csv')             
                # --------------------------------
                # First row is falsly the index, new row index is added ???
                # Try to fix it here
                # --------------------------------
                INDEX1 = KPI.columns[0]
                INDEX2 = KPI.columns[1]
                INDEX_df = pd.DataFrame(np.array([[INDEX1, INDEX2]]), index=['100'], \
                columns=['name',''+str(PrHoBin/6)+'h, '+Saison[j]+''])
                #print INDEX1, INDEX2
                #print INDEX_df
                KPI.columns = ['name', ''+str(PrHoBin/6)+'h, '+Saison[j]+'']
                KPI= KPI.append(INDEX_df)
                #print KPI.ix[:,1]
                # --------------------------------
                print KPI
            
             else:
                PrHoBin = Horizon[i]    
                KPIlocal = pd.read_csv('Results\KPIsAdhocV'+str(name)+'_'+INOUT_string1+'.csv')    
            
                # --------------------------------
                # First row is falsly the index, new row index is added ???
                # Try to fix it here
                # --------------------------------
                INDEX1 = KPIlocal.columns[0]
                INDEX2 = float(KPIlocal.columns[1])
                INDEX_df = pd.DataFrame(np.array([[INDEX1, INDEX2]]), index=['100'], \
                columns=['name',''+str(PrHoBin/6)+'h, '+Saison[j]+''])
                #print INDEX1, INDEX2
                #print INDEX_df
                KPIlocal.columns = ['name', ''+str(PrHoBin/6)+'h, '+Saison[j]+'']
                KPIlocal = KPIlocal.append(INDEX_df)
                #print KPI.ix[:,0].values
                # --------------------------------
 
                
                KPI = pd.concat([KPI, KPIlocal.ix[:,1]], axis=1)
         # change to correct index         
      KPI.index = KPI.ix[:,0].values  
      del KPI['name']
      #print KPI
      # -------------- Ändert x und y achse und erzeugt numerische Werte   
      KPI=KPI.T
      KPI = KPI.convert_objects(convert_numeric=True)    
      # ----------------------------------------------------------------    
      INOUT_string = fore+'_'+inputchoice+'_'+haushalt+'_'+datachoice+'_'+haushalt
    
      Compare_KPIs(KPI,name,INOUT_string)  
      
    return 0
    
def Compare_KPIs(KPI,name, INOUT_string):    

# --------------------------------
# Use Colours from time-serious plots (OptFlex_plotting.py)
# --------------------------------

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
        
    #KPI.to_excel('OUTPUT\KPItotal.xlsx', sheet_name='Sheet1')
    #my_colors = list(islice(cycle(['b', 'r', 'g', 'y', 'k']), None, len(KPI)))

    # ----------------------------------------------------------------    
    # Möglichkeit die KPIs einzeln anzusehen als Test
    # please uncomment if necessary
    # note not all KPIs are listed, please add if necessary
    # ----------------------------------------------------------------    
    my_colors = list(islice(([\
    CPV2Bat,CPV2Bat, CPV2Bat, CPV2Bat, CPV2Bat,CPVGrid,CPVGrid,\
    CPVGrid,CPVGrid,CPVGrid,CNGBurner2QLoad,CNGBurner2QLoad,\
    CNGBurner2QLoad,CNGBurner2QLoad,CNGBurner2QLoad,\
    ]), None, len(KPI)))
    #print my_colors
#    plt.figure()
#    KPI['totalGridImp [kWh]'].plot(kind='bar', title='GesamtSC [%]',stacked=True, color=my_colors)
#    plt.figure()    
#    KPI['totalPVExp [kWh]'].plot(kind='bar', title='totalPVExp [kWh]',stacked=True, color=my_colors)
#    plt.figure()   
#    KPI['totalCHPExp [kWh]'].plot(kind='bar', title='totalCHPExp [kWh]',stacked=True, color=my_colors)
#    plt.figure()   
#    KPI['totalCHPelProd [kWh]'].plot(kind='bar', title='totalCHPelProd [kWh]',stacked=True, color=my_colors)
#    plt.figure()    
#    KPI['totalCHPthProd [kWh]'].plot(kind='bar', title='totalCHPthProd [kWh]',stacked=True, color=my_colors)
#    plt.figure()    
#    KPI['CHPsc [kWh]'].plot(kind='bar', title='CHPsc [kWh]',stacked=True, color=my_colors)
#    plt.figure()    
#    KPI['PVsc [kWh]'].plot(kind='bar', title='PVsc [kWh]',stacked=True, color=my_colors)
#    plt.figure()    
#    KPI['totalPV [kWh]'].plot(kind='bar', title='totalPV [kWh]',stacked=True, color=my_colors)
#    plt.figure()   
#    KPI['totalEcon [kWh]'].plot(kind='bar', title='totalEcon [kWh]',stacked=True, color=my_colors)
#    plt.figure()    
#    KPI['totalQcon [kWh]'].plot(kind='bar', title='totalQcon [kWh]',stacked=True, color=my_colors)
#    plt.figure()    
#    KPI['totalAUX [kWh]'].plot(kind='bar', title='totalAUX [kWh]',stacked=True, color=my_colors)
#    plt.figure()   
#    #KPI['totalEH [kWh]'].plot(kind='bar', title='totalEH [kWh]',stacked=True, color=my_colors)
#    #plt.figure()    
#    KPI['Autarcy [%]'].plot(kind='bar', title='Autarcy [%]',stacked=True, color=my_colors)
    plt.figure()    
    KPI['BatteryCyc '].plot(kind='bar', title='BatteryCyc ('+INOUT_string+')',stacked=True, color=my_colors)
    plt.savefig('OUTPUT\AdHocV_BattCyc_'+str(name)+'_'+INOUT_string+'.png', dpi=300)
    
    plt.figure()    
    KPI['CompTime Max [s]'].plot(kind='bar', title='Rechenzeit ('+INOUT_string+')',stacked=True, color=my_colors)
    plt.savefig('OUTPUT\AdHocV_Rechenzeit_'+str(name)+'_'+INOUT_string+'.png', dpi=300)
#    KPI['SelfconsumptionPV [%]'].plot(kind='bar', title='SelfconsumptionPV [%]',stacked=True, color=my_colors)
#    plt.figure()    
#    KPI['SelfconsumptionCHP [%]'].plot(kind='bar', title='SelfconsumptionCHP [%]',stacked=True, color=my_colors)
#    plt.figure()    
#    KPI['GesamtSC [%]'].plot(kind='bar', title='GesamtSC [%]',stacked=True, color=my_colors)
    plt.figure()    
    KPI['CHPrunningTime [h]'].plot(kind='bar', title='CHP running time [h] ('+INOUT_string+')',stacked=True, color=my_colors)
    plt.savefig('OUTPUT\AdHocV_CHPruntime_'+str(name)+'_'+INOUT_string+'.png', dpi=300)
    plt.figure()       
    KPI['totalCost [Euro]'].plot(kind='bar', title='totalCost [Euro]('+INOUT_string+')',stacked=True, color=my_colors)
    plt.savefig('OUTPUT\AdHocV_totalCost_'+str(name)+'_'+INOUT_string+'.png', dpi=300)

    # ----------------------------------------------------------------    

    # ----------------------------------------------------------------    
    # -----------Compare Costs -------------------------
    # ----------------------------------------------------------------    
    sub_dfCost1 = KPI['totalCHPFeedInCost [Euro]']
    sub_dfCost2 = KPI['totalCHPonofCost [Euro]']
    sub_dfCost3 = KPI['totalCHP2BattCost [Euro]']
    sub_dfCost4 = KPI['totalCHP2eLoadCost [Euro]']
    # --- Possible other KPIs use when nessecary
    # sub_dfCost5 = KPI['totalCost [Euro]']
    # sub_dfCost5 = KPI['totalPV2BattCost [Euro]']
    # sub_dfCost6 = KPI['totalPV2LoadCost [Euro]']
    # sub_dfCost6 = KPI['totalCHPEigenCost [Euro]'] 
    sub_dfCost7 = KPI['totalGasCost [Euro]'] 
    sub_dfCost8 = KPI['totalStromCost [Euro]'] 
    sub_dfCost9 = KPI['totalPVFeedInCost [Euro]']  
    sub_df = pd.concat([sub_dfCost1, sub_dfCost2, sub_dfCost3, sub_dfCost4\
    , sub_dfCost7, sub_dfCost8, sub_dfCost9\
    ],keys=['totalCHPFeedInCost [Euro]',\
    'totalCHPonoffCost [Euro]','totalCHP2BattCost [Euro]',\
    'totalCHP2eLoadCost [Euro]','totalGasCost [Euro]',\
    'totalStromCost [Euro]','totalPVFeedInCost [Euro]']).unstack()
    sub_df = sub_df.T   
    sub_df.plot(kind='bar',stacked=True, title='Costs ('+INOUT_string+')')
    plt.savefig('OUTPUT\AdHocV_Costs_'+str(name)+'_'+INOUT_string+'.png', dpi=300)
    
    
    StromCostJahr = 365./2. * KPI['totalStromCost [Euro]']['0h, Uebergang'] \
             + 365./4. * KPI['totalStromCost [Euro]']['0h, Sommer'] \
             + 365./4. * KPI['totalStromCost [Euro]']['0h, Winter']   
    GasCostJahr = 365./2. * KPI['totalGasCost [Euro]']['0h, Uebergang'] \
             + 365./4. * KPI['totalGasCost [Euro]']['0h, Sommer'] \
             + 365./4. * KPI['totalGasCost [Euro]']['0h, Winter']   
    print 'Geschätze Jahressumme ohne CHP:', StromCostJahr, GasCostJahr
    # ----------------------------------------------------------------    
    # ------------ PV -------------------------  
    # ----------------------------------------------------------------    
    sub_dfPV1 =- KPI['totalPV [kWh]']
    sub_dfPV2 = KPI['totalPVExp [kWh]']
    sub_dfPV3 = KPI['totalPV2Batt[kWh]']    
    sub_dfPV4 = KPI['totalPV2Load[kWh]']    
    sub_df = pd.concat([sub_dfPV1,sub_dfPV2, sub_dfPV3, sub_dfPV4\
    ],keys=["totalPV [kWh]","totalPVExp [kWh]",\
    'PV2Batt [kWh]','PV2load [kWh]']).unstack()
    sub_df = sub_df.T   
    sub_df.plot(kind='bar',stacked=True, title='PV ('+INOUT_string+')')
    plt.savefig('OUTPUT\AdHocV_PV_'+str(name)+'_'+INOUT_string+'.png', dpi=300)

    # ----------------------------------------------------------------    
    # ------------ CHP elektrisch-------------------------  
    # ----------------------------------------------------------------    
    sub_dfCHP1 = -KPI['totalCHPelProd [kWh]']
    sub_dfCHP2 = KPI['totalCHPExp [kWh]']
    sub_dfCHP3 = KPI['totalCHP2Batt[kWh]']    
    sub_dfCHP4 = KPI['totalCHP2eLoad[kWh]']    
    sub_df = pd.concat([sub_dfCHP1,sub_dfCHP2, sub_dfCHP3, sub_dfCHP4\
    ],keys=["totalCHP [kWh]","totalCHPExp [kWh]",\
    'totalCHP2Batt[kWh]', 'totalCHP2eLoad[kWh]']).unstack()
    sub_df = sub_df.T   
    sub_df.plot(kind='bar',stacked=True,title='CHP ('+INOUT_string+')')
    plt.savefig('OUTPUT\AdHocV_CHP_'+str(name)+'_'+INOUT_string+'.png', dpi=300)

    # ----------------------------------------------------------------    
    # ------------ Q Bedarf -------------------------  
    # ----------------------------------------------------------------    
    # Beitrag vom Speicherentladen fehlt !!!! 24.5.16 TMK 
    sub_dfQL1 = -KPI['totalQcon [kWh]']
    #sub_dfQL2 = KPI['totalCHPthProd [kWh]']
    #sub_dfQL2 = KPI['totalCHP2qLoad [kWh]']
    sub_dfQL2 = KPI['totalCHP2qLoad [kWh]']
    sub_dfQL3 = KPI['totalAUX [kWh]']    
    sub_dfQL4 = KPI['totalTES2Load [kWh]'] 
    sub_df = pd.concat([sub_dfQL1,sub_dfQL2, sub_dfQL3, sub_dfQL4,\
    ],keys=["totalQcon [kWh]","totalCHP2qLoad [kWh]",\
    'totalAUX [kWh]','totalTES2Load [kWh]']).unstack()
    sub_df = sub_df.T   
    sub_df.plot(kind='bar',stacked=True,title='Waermebedarf ('+INOUT_string+')')
    plt.savefig('OUTPUT\AdHocV_Q_Load_'+str(name)+'_'+INOUT_string+'.png', dpi=300)

    # ----------------------------------------------------------------    
    # ------------ E Bedarf -------------------------  
    # ----------------------------------------------------------------    
    sub_dfEL1 = -KPI['totalEcon [kWh]']
    sub_dfEL2 = KPI['totalCHP2eLoad[kWh]']
    sub_dfEL3 = KPI['totalGridImp [kWh]']  
    sub_dfEL4 = KPI['totalPV2Load[kWh]']        
    sub_dfEL5 = KPI['totalBattdis [kWh]']        
    sub_df = pd.concat([sub_dfEL1,sub_dfEL2, sub_dfEL3, sub_dfEL4,sub_dfEL5\
    ],keys=["totalEcon [kWh]","totalCHP2Load [kWh]",\
    'totalGridImp [kWh]', 'totalPV2Load [kWh]',\
    'totalBattdis [kWh]']).unstack()
    sub_df = sub_df.T   
    sub_df.plot(kind='bar',stacked=True,title='Strombedarf ('+INOUT_string+')')
    plt.savefig('OUTPUT\AdHocV_E_Load_'+str(name)+'_'+INOUT_string+'.png', dpi=300)

    # ----------------------------------------------------------------    
    # ------------ Battery -------------------------  
    # ----------------------------------------------------------------    
    sub_dfBat1 = -KPI['totalBattchar [kWh]']
    sub_dfBat2 = KPI['totalPV2Batt[kWh]']
    sub_dfBat3 = KPI['totalCHP2Batt[kWh]']
    sub_df = pd.concat([sub_dfBat1,sub_dfBat2, sub_dfBat3],\
             keys=["totalBattchar [kWh]","totalPV2Batt [kWh]",\
    'totalCHP2Batt [kWh]']).unstack()
    sub_df = sub_df.T   
    sub_df.plot(kind='bar',stacked=True,title='BatterieLoad ('+INOUT_string+')')
    plt.savefig('OUTPUT\AdHocV_Battery_Load_'+str(name)+'_'+INOUT_string+'.png', dpi=300)

        
    QJahr = 365./2. * KPI['totalQcon [kWh]']['0h, Uebergang'] \
             + 365./4. * KPI['totalQcon [kWh]']['0h, Sommer'] \
             + 365./4. * KPI['totalQcon [kWh]']['0h, Winter']   
    EJahr = 365./2. * KPI['totalEcon [kWh]']['0h, Uebergang'] \
             + 365./4. * KPI['totalEcon [kWh]']['0h, Sommer'] \
             + 365./4. * KPI['totalEcon [kWh]']['0h, Winter']   
    print 'Geschätzer Jahresenergieverbrauch:(25.000/5200)', QJahr, EJahr
    print 'Gas in Euro', QJahr * 0.0652 #0.07248
    print "The End!"
    return 0


    
        
    
if __name__ == '__main__':
    Analyse_Horizon()