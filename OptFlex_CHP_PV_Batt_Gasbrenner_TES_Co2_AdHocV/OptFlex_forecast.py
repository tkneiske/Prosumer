# -*- coding: utf-8 -*-
"""
Created on Wed Jun 01 08:06:02 2016

Different Forecast method

- Tagespersistenz

@author: tkreiske
"""

import pandas as pd

def TagesPersistenz(TOT_df, day_stamps_date, BIN):
    
    print 'Forecast-Method: Tagespersistenz.'
    
    day_stamps_fore = day_stamps_date - pd.DateOffset(days=1) # 1 Tag vorher
    date_fore = day_stamps_fore[0].strftime('%m/%d/%Y')
    date_fore_end = day_stamps_fore[BIN-1].strftime('%m/%d/%Y')
 
    # --------- Zeitreihe, verschiebe Zeitindex um einen Tag nach hinten
    PF = TOT_df[date_fore:date_fore_end] 
    PeriodFore =PF.set_index(day_stamps_date) # Re-index
    
    return PeriodFore
    
def DreiTageRunAverage(TOT_df, day_stamps_date, BIN):
    
    print 'Forecast-Method: 3-Tage Running Average.'

    day_stamps_fore1 = day_stamps_date - pd.DateOffset(days=1) # 1 Tag vorher
    # 4.Tage nimmt Eintrag average der drei Vortage    
    date_fore1 = day_stamps_fore1[0].strftime('%m/%d/%Y')
    date_fore_end1 = day_stamps_fore1[BIN-1].strftime('%m/%d/%Y') 
    PF = TOT_df[date_fore1:date_fore_end1] 
    PeriodFore1 =PF.set_index(day_stamps_date) # Re-index

    day_stamps_fore2 = day_stamps_date - pd.DateOffset(days=2) # 2 Tag vorher
    # 4.Tage nimmt Eintrag average der drei Vortage    
    date_fore2 = day_stamps_fore2[0].strftime('%m/%d/%Y')
    date_fore_end2 = day_stamps_fore2[BIN-1].strftime('%m/%d/%Y') 
    PF = TOT_df[date_fore2:date_fore_end2] 
    PeriodFore2 =PF.set_index(day_stamps_date) # Re-index

    day_stamps_fore3 = day_stamps_date - pd.DateOffset(days=3) # 3 Tag vorher    
    # 4.Tage nimmt Eintrag average der drei Vortage    
    date_fore3 = day_stamps_fore3[0].strftime('%m/%d/%Y')
    date_fore_end3 = day_stamps_fore3[BIN-1].strftime('%m/%d/%Y') 
    PF = TOT_df[date_fore3:date_fore_end3] 
    PeriodFore3 =PF.set_index(day_stamps_date) # Re-index

    # Average
    PeriodFore = (PeriodFore1 + PeriodFore2 + PeriodFore3) / 3.
    
    
    return PeriodFore