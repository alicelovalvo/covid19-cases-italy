import pandas as pd
from datetime import datetime


def main():
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
    
    df_italian_vax_compare = pd.DataFrame(index=self.italian_intensive_care["Date"])
    df_italian_vax_compare.reset_index(inplace=True)
    
    # df_italian_vax_compare["Date"]=self.italian_intensive_care.index
    df_italian_vax_compare[["Posti Occupati"]] = self.italian_intensive_care[["Posti Occupati"]]
    df_italian_vax_compare[["Nuovi Positivi"]] = self.italian_positive_cases[["Italia"]]
    for i, row in df_italian_vax_compare.iterrows():    
        dt = datetime.fromisoformat(row["Date"]).date()
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
