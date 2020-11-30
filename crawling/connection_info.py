# from connection_info import get_connection_info

import pandas as pd

def get_connection_info(key):
    df = pd.read_excel("C:/sdqi_automation/connection_info.xlsx")
    return df.loc[df["key"] == key, "value"].values[0]
