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
    df_positive_cases = pd.DataFrame()
    df_daily_new_cases = pd.DataFrame()

        
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
                df_positive_cases.loc[dt,reg] = row["totale_positivi"]
        
    l = len(df_cases)    
    # print(df_cases.diff().iloc[l - 1].sum())
    
    
    df_cases["Italia"] = df_cases.sum(axis=1)
    # print(df_cases.diff().iloc[l - 1]["Italia"])
    # print(df_cases.diff().iloc[l - 1].sum() - df_cases.diff().iloc[l - 1]["Italia"])
    
    
    for i in range(1,l):
        df_daily_new_cases
    
    df_fatalities["Italia"] = df_fatalities.sum(axis=1)
    df_recovered["Italia"] = df_recovered.sum(axis=1)
    df_hospital["Italia"] = df_hospital.sum(axis=1)
    df_intensive_care["Posti Occupati"] = df_intensive_care.sum(axis=1)
    df_intensive_care["Posti Disponibili"] = '5324'
    df_positive_cases["Italia"] = df_positive_cases.sum(axis=1)
    df_cases.index.name = "Date"
    df_fatalities.index.name = "Date"
    df_recovered.index.name = "Date"
    df_hospital.index.name = "Date"
    df_intensive_care.index.name = "Date"
    df_positive_cases.index.name = "Date"
    df_cases = df_cases.astype(int)
    df_fatalities = df_fatalities.astype(int)
    df_recovered = df_recovered.astype(int)
    df_hospital = df_hospital.astype(int)
    df_positive_cases = df_positive_cases.astype(int)
    df_intensive_care = df_intensive_care.astype(int)
    df_cases.to_csv("covid19_cases_italy.csv", index=True)
    df_fatalities.to_csv("covid19_fatalities_italy.csv", index=True)
    df_recovered.to_csv("covid19_recovered_italy.csv", index=True)
    df_hospital.to_csv("covid19_hospital_italy.csv", index=True)
    df_intensive_care.to_csv("covid19_intensive_care_italy.csv", index=True)
    df_positive_cases.to_csv("covid19_positive_cases_italy.csv", index=True)
    
    
    
    """ Transforms the data from the vax csv to my csv """
    
    url = 'https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/platea.csv'
    df_plate = pd.read_csv(url, error_bad_lines=False)
    url_vax = 'https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv'
    df_vax = pd.read_csv(url_vax, error_bad_lines=False)


    df_tot = pd.DataFrame()
    df_vax_first = pd.DataFrame()
    df_vax_second = pd.DataFrame()
        
    regioni = df_plate["nome_area"].unique()
    fascia = df_plate["fascia_anagrafica"].unique()
    s=0
    for i, row in df_plate.iterrows():    
        for reg in regioni:
            if row["nome_area"] == reg:
                if reg == "Provincia Autonoma Bolzano / Bozen":
                    df_tot.loc[fascia[s],"P.A. Bolzano"] = row["totale_popolazione"]
                elif (reg == "Provincia Autonoma Trento"):
                    df_tot.loc[fascia[s],"P.A. Trento"] = row["totale_popolazione"]
                elif (reg == "Valle d'Aosta / Vallée d'Aoste"):
                    df_tot.loc[fascia[s],"Valle d'Aosta"] = row["totale_popolazione"]
                elif (reg == "Friuli-Venezia Giulia"):
                    df_tot.loc[fascia[s],"Friuli Venezia Giulia"] = row["totale_popolazione"]
                else:                 
                    df_tot.loc[fascia[s],reg] = row["totale_popolazione"]
            if (s==len(fascia)-1):
                s=0
            else:
                s=s+1
                    
    df_tot["Totale fascia"] = df_tot.sum(axis=1)
    
    for reg in df_tot.columns:        
        df_tot.loc["Totale",reg] = df_tot[reg].sum()
        
    df_tot = df_tot.astype(int)



    regioni = df_vax["nome_area"].unique()
    for i, row in df_vax.iterrows():    
        dt = datetime.fromisoformat(row["data_somministrazione"]).date()
        for reg in regioni:
            if row["nome_area"] == reg:
                if (dt in df_vax_first.index):
                    if reg in df_vax_first.columns:
                        df_vax_first = df_vax_first.fillna(0) 
                        df_vax_second = df_vax_second.fillna(0)                    
                        df_vax_first.loc[dt,reg] = df_vax_first.loc[dt,reg] + row["prima_dose"]
                        df_vax_second.loc[dt,reg] = df_vax_second.loc[dt,reg] + row["seconda_dose"]
                    else:
                        df_vax_first.loc[dt,reg] = row["prima_dose"]
                        df_vax_second.loc[dt,reg] = row["seconda_dose"]
                else:
                    df_vax_first.loc[dt,reg] = row["prima_dose"]
                    df_vax_second.loc[dt,reg] = row["seconda_dose"]
                    


    df_vax_first.columns = df_vax_first.columns.str.replace('Friuli-Venezia Giulia','Friuli Venezia Giulia')
    df_vax_second.columns = df_vax_first.columns.str.replace('Friuli-Venezia Giulia','Friuli Venezia Giulia')
    df_vax_first.columns = df_vax_first.columns.str.replace('Provincia Autonoma Bolzano / Bozen','P.A. Bolzano')
    df_vax_second.columns = df_vax_first.columns.str.replace('Provincia Autonoma Bolzano / Bozen','P.A. Bolzano')
    df_vax_first.columns = df_vax_first.columns.str.replace('Provincia Autonoma Trento','P.A. Trento')
    df_vax_second.columns = df_vax_first.columns.str.replace('Provincia Autonoma Trento','P.A. Trento')
    df_vax_first.columns = df_vax_first.columns.str.replace("Valle d'Aosta / Vallée d'Aoste","Valle d'Aosta")
    df_vax_second.columns = df_vax_first.columns.str.replace("Valle d'Aosta / Vallée d'Aoste","Valle d'Aosta")
   
    df_vax_first = df_vax_first.fillna(0) 
    df_vax_second = df_vax_second.fillna(0)
           
    df_vax_first["Italia"] = df_vax_first.sum(axis=1)
    df_vax_second["Italia"] = df_vax_second.sum(axis=1)
    
    df_vax_first.index.name = "Date"
    df_vax_second.index.name = "Date"
    
    df_vax_first = df_vax_first.astype(int) 
    df_vax_second = df_vax_second.astype(int) 

    df_italian_vax = pd.DataFrame(index=df_vax_first.index)
    df_italian_vax_ = pd.DataFrame(index=df_vax_first.index)
    df_italian_vax_[["Prima Dose"]] = df_vax_first[["Italia"]]
    df_italian_vax_[["Seconda Dose"]] = df_vax_second[["Italia"]]
    df_italian_vax[["Prima Dose"]] = df_vax_first[["Italia"]].cumsum()
    df_italian_vax[["Seconda Dose"]] = df_vax_second[["Italia"]].cumsum()
    df_italian_vax["Persone Vaccinabili"] = df_tot.loc["Totale","Totale fascia"]

    df_vax_first.to_csv("covid19_vax_first_italy.csv", index=True)
    df_vax_second.to_csv("covid19_vax_second_italy.csv", index=True)
    df_tot.to_csv("covid19_vax_platea_italy.csv", index=True)
    df_italian_vax.to_csv("covid19_vax_total_italy.csv", index=True)
    df_italian_vax_.to_csv("covid19_vax_italy.csv", index=True)
    
    df_intensive_care.reset_index(inplace=True)
    
    df_italian_vax_compare = pd.DataFrame(index=df_intensive_care["Date"])
    df_italian_vax_compare.reset_index(inplace=True)
    
    df_italian_vax_compare[["Posti Occupati"]] = df_intensive_care[["Posti Occupati"]]
    df_italian_vax_compare[["Nuovi Positivi"]] = df_positive_cases[["Italia"]]
    
    for i, row in df_italian_vax_compare.iterrows():
        dt = datetime.fromisoformat(str(row["Date"])).date()
        if (dt in df_vax_first.index):
            df_italian_vax_compare.loc[i,"Prima Dose"] = df_vax_first.loc[dt,"Italia"]
            df_italian_vax_compare.loc[i,"Seconda Dose"] = df_vax_second.loc[dt,"Italia"]
            
    df_italian_vax_compare = df_italian_vax_compare.fillna(0)
    df_italian_vax_compare = df_italian_vax_compare.set_index("Date")
    df_italian_vax_compare = df_italian_vax_compare[['Prima Dose', 'Seconda Dose','Posti Occupati','Nuovi Positivi']]
    df_italian_vax_compare = df_italian_vax_compare.astype(int) 
    df_italian_vax_compare.to_csv("covid19_vax_compare_italy.csv", index=True)

if __name__ == "__main__":
    main()
