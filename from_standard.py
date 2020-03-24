import pandas as pd
from datetime import datetime


def main():
    """ Transforms the data from the standards csv to my csv """

    url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv'
    df = pd.read_csv(url, error_bad_lines=False)
    url_regione = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv'
    df_regione = pd.read_csv(url_regione, error_bad_lines=False)


    df_cases = pd.DataFrame()
    df_fatalities = pd.DataFrame()
    df_recovered = pd.DataFrame()
    df_hospital = pd.DataFrame()
    df_intensive_care = pd.DataFrame()
        
    regioni = df_regione["denominazione_regione"].unique()
    
    for i, row in df.iterrows():    
        dt = datetime.fromisoformat(row["data"]).date()
        for reg in regioni:
            if row["denominazione_regione"] == reg:
                df_cases.loc[dt,reg] = row["totale_casi"]
                df_fatalities.loc[dt,reg] = row["deceduti"]
                df_recovered.loc[dt,reg] = row["dimessi_guariti"]
                df_hospital.loc[dt,reg] = row["totale_ospedalizzati"]
                df_intensive_care.loc[dt,reg] = row["terapia_intensiva"]
        
        
    df_cases["Italia"] = df_cases.sum(axis=1)
    df_fatalities["Italia"] = df_fatalities.sum(axis=1)
    df_recovered["Italia"] = df_recovered.sum(axis=1)
    df_hospital["Italia"] = df_hospital.sum(axis=1)
    df_intensive_care["Posti Occupati"] = df_intensive_care.sum(axis=1)
    df_intensive_care["Posti Disponibili"] = '8000'
    df_cases.index.name = "Date"
    df_fatalities.index.name = "Date"
    df_recovered.index.name = "Date"
    df_hospital.index.name = "Date"
    df_intensive_care.index.name = "Date"
    df_cases = df_cases.astype(int)
    df_fatalities = df_fatalities.astype(int)
    df_recovered = df_recovered.astype(int)
    df_hospital = df_hospital.astype(int)
    df_intensive_care = df_intensive_care.astype(int)
    df_cases.to_csv("covid19_cases_italy.csv", index=True)
    df_fatalities.to_csv("covid19_fatalities_italy.csv", index=True)
    df_recovered.to_csv("covid19_recovered_italy.csv", index=True)
    df_hospital.to_csv("covid19_hospital_italy.csv", index=True)
    df_intensive_care.to_csv("covid19_intensive_care_italy.csv", index=True)


if __name__ == "__main__":
    main()
