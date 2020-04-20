#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 13:17:36 2020

@author: Alice
"""

import pandas as pd
from datetime import datetime


def main():
    """ Transforms the data from the standards csv to my csv """

    df = pd.read_excel('Tavola_sintetica_ISTAT.xlsx', sheet_name='Totale per sesso')
    df = df.sort_values('Unnamed: 2')
    df_regione = pd.read_csv('regioni.csv', error_bad_lines=False)


    # df_cases = pd.DataFrame()
    # df_fatalities = pd.DataFrame()
    # df_recovered = pd.DataFrame()
    # df_hospital = pd.DataFrame()
    # df_intensive_care = pd.DataFrame()
    # df_positive_cases = pd.DataFrame()
    df_fatalities_istat = pd.DataFrame()
    df_percentage = pd.DataFrame()
    dt = [2019, 2020]
    regioni = df_regione["Region"].unique()
    
    for i, row in df.iterrows():    
    #     dt = datetime.fromisoformat(row["data"]).date()
        for reg in regioni:
            if row["Unnamed: 2"] == reg:
                # print(row)
                df_fatalities_istat.loc[dt[0], reg]= 0
                df_fatalities_istat.loc[dt[1], reg]= 0
    
    
    for i, row in df.iterrows():    
        for reg in regioni:
            if row["Unnamed: 2"] == reg:
                df_fatalities_istat.loc[dt[0], reg]+= row["Unnamed: 9"]
                df_fatalities_istat.loc[dt[1], reg]+= row["Unnamed: 12"]

    for reg in regioni:
        df_percentage.loc[1,reg] = (df_fatalities_istat.loc[dt[1], reg] - df_fatalities_istat.loc[dt[0], reg])/df_fatalities_istat.loc[dt[0], reg]*100
    
    
    df_fatalities_istat["Italia"] = df_fatalities_istat.sum(axis=1)
    df_fatalities_istat.index.name = "Date"
    df_fatalities_istat = df_fatalities_istat.astype(int)

    df_percentage.index.name = "Date"
    df_fatalities_istat.to_csv("df_fatalities_istat.csv", index=True)
    df_percentage.to_csv("df_percentage.csv", index=True)

if __name__ == "__main__":
    main()
