from configparser import ConfigParser
from datetime import date, datetime
import pandas as pd
from pytz import timezone


class DataLoader:
    def __init__(self, parser: ConfigParser):
        self.italian_cases = pd.read_csv(parser.get("urls", "italian_cases"))
        self.italian_fatalities = pd.read_csv(parser.get("urls", "italian_fatalities"))
        self.italian_demography = pd.read_csv(
            parser.get("urls", "italian_demography"), index_col=0
        )
        self.world_cases = self.__simplify_world_data(
            pd.read_csv(parser.get("urls", "world_cases"))
        )
        self.world_fataltities = self.__simplify_world_data(
            pd.read_csv(parser.get("urls", "world_fatalities"))
        )
        self.world_population = self.__get_world_population()

        self.italian_cases_by_date = self.italian_cases.set_index("Date")
        self.italian_fatalities_by_date = self.italian_fatalities.set_index("Date")

        self.italian_cases_by_date_filled = self.italian_cases_by_date.fillna(
            method="ffill", axis=0
        )

        self.italian_cases_by_date_filled_per_capita = (
            self.__get_italian_cases_by_date_filled_per_capita()
        )

        self.latest_date = self.__get_latest_date()
        self.updated_regions = self.__get_updated_regions()
        self.new_italian_cases = self.__get_new_cases()
        self.total_italian_cases = self.__get_total_italian_cases()
        self.total_italian_fatalities = self.__get_total_italian_fatalities()
        self.italian_case_fatality_rate = (
            self.total_italian_fatalities / self.total_italian_cases
        )

        # Put the date at the end
        self.italian_cases_as_dict = self.italian_cases.to_dict("list")
        date_tmp = self.italian_cases_as_dict.pop("Date")
        self.italian_cases_as_dict["Date"] = date_tmp
        self.italian_cases_normalized_as_dict = (
            self.__get_italian_cases_as_normalized_dict()
        )

        self.italian_fatalities_as_dict = self.italian_fatalities.to_dict("list")
        self.regional_labels = [
            region
            for region in self.italian_cases_as_dict
            if region != "Italia" and region != "Date"
        ]
        self.regional_centres = self.__get_regional_centres()

        #
        # World related data
        #

        self.world_case_fatality_rate = (
            self.world_fataltities.iloc[-1] / self.world_cases.iloc[-1]
        )

        self.italian_world_cases_normalized = self.__get_italian_world_cases_normalized()

    def __get_latest_date(self):
        return self.italian_cases.iloc[len(self.italian_cases) - 1]["Date"]

    def __get_updated_regions(self):
        l = len(self.italian_cases_by_date)
        return [
            region
            for region in self.italian_cases_by_date.iloc[l - 1][
                self.italian_cases_by_date.iloc[l - 1].notnull()
            ].index
        ]

    def __get_italian_cases_by_date_filled_per_capita(self):
        tmp = self.italian_cases_by_date_filled.copy()

        for column in tmp:
            tmp[column] = (
                tmp[column] / self.italian_demography["Population"][column] * 10000
            )
        return tmp

    def __get_new_cases(self):
        if (
            date.fromisoformat(self.latest_date)
            != datetime.now(timezone("Europe/Rome")).date()
        ):
            return 0

        l = len(self.italian_cases_by_date_filled)
        return (
            self.italian_cases_by_date_filled.diff().iloc[l - 1].sum()
            - self.italian_cases_by_date_filled.diff().iloc[l - 1]["Italia"]
        )

    def __get_total_italian_cases(self):
        l = len(self.italian_cases_by_date_filled)
        return (
            self.italian_cases_by_date_filled.iloc[l - 1].sum()
            - self.italian_cases_by_date_filled.iloc[l - 1]["Italia"]
        )

    def __get_total_italian_fatalities(self):
        l = len(self.italian_fatalities_by_date)
        return (
            self.italian_fatalities_by_date.iloc[l - 1].sum()
            - self.italian_fatalities_by_date.iloc[l - 1]["Italia"]
        )

    def __get_italian_cases_as_normalized_dict(self):
        tmp = [
            (
                str(region),
                [
                    round(i, 2)
                    for i in self.italian_cases_as_dict[region]
                    / self.italian_demography["Population"][region]
                    * 10000
                ],
            )
            for region in self.italian_cases_as_dict
            if region != "Date"
        ]
        tmp.append(("Date", self.italian_cases_as_dict["Date"]))
        return dict(tmp)

    def __simplify_world_data(self, df: pd.DataFrame):
        df.drop(columns=["Lat", "Long"], inplace=True)
        df["Province/State"].fillna("", inplace=True)
        df = df.rename(columns={"Country/Region": "Day"})
        df = df.groupby("Day").sum()
        df = df.T
        df.drop(
            df.columns.difference(
                ["France", "Germany", "Switzerland", "Spain", "United Kingdom", "US"]
            ),
            1,
            inplace=True,
        )
        df.index = range(0, len(df))
        return df

    def __get_italian_world_cases_normalized(self, min_prevalence: int = 0.4):
        tmp = self.world_cases.copy()
        tmp["Italy"] = pd.Series(self.italian_cases_as_dict["Italia"])

        for column in tmp:
            tmp[column] = tmp[column] / self.world_population[column] * 10000

        tmp[tmp < min_prevalence] = 0
        for column in tmp:
            while tmp[column].iloc[0] == 0:
                tmp[column] = tmp[column].shift(-1)
        tmp.dropna(how="all", inplace=True)

        return tmp

    def __get_world_population(self):
        return {
            "France": 65273511,
            "Germany": 83783942,
            "Italy": 60461826,
            "Spain": 46754778,
            "US": 331002651,
            "United Kingdom": 67886011,
            "Switzerland": 8654622,
        }

    def __get_regional_centres(self):
        return {
            "Piemonte": {"lat": 45.06043, "lon": 7.92349},
            "Valle d'Aosta": {"lat": 45.72979, "lon": 7.38737},
            "Lombardia": {"lat": 45.52052, "lon": 9.76912},
            "P.A. Bolzano": {"lat": 46.94129, "lon": 11.28183},
            "P.A. Trento": {"lat": 46.54129, "lon": 11.28183},
            "Veneto": {"lat": 45.22135, "lon": 11.85863},
            "Friuli Venezia Giulia": {"lat": 46.15144, "lon": 13.05559},
            "Liguria": {"lat": 44.06433, "lon": 8.70434},
            "Emilia Romagna": {"lat": 44.62567, "lon": 11.03837},
            "Toscana": {"lat": 43.65059, "lon": 11.12596},
            "Umbria": {"lat": 42.96592, "lon": 12.48991},
            "Marche": {"lat": 43.34819, "lon": 13.13775},
            "Lazio": {"lat": 41.97950, "lon": 12.76641},
            "Abruzzo": {"lat": 42.52756, "lon": 13.85475},
            "Molise": {"lat": 41.68433, "lon": 14.59590},
            "Campania": {"lat": 40.85954, "lon": 14.84018},
            "Puglia": {"lat": 41.28457, "lon": 16.62015},
            "Basilicata": {"lat": 40.29983, "lon": 16.08151},
            "Calabria": {"lat": 39.06817, "lon": 16.34802},
            "Sicilia": {"lat": 37.58843, "lon": 14.14697},
            "Sardegna": {"lat": 40.08804, "lon": 9.030305},
        }
