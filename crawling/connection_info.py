# from connection_info import get_connection_info

import pandas as pd

def get_connection_info(key):
    df = pd.read_csv("C:/sdqi_automation/connection_info.csv", encoding='euc-kr')
    return df.loc[df["key"] == key, "value"].values[0]


if __name__ == "__main__":
    # df = pd.read_excel("C:/sdqi_automation/connection_info.xlsx")
    # df.to_csv("C:/sdqi_automation/connection_info.csv", index=False, encoding='euc-kr')

    print(pd.read_csv("C:/sdqi_automation/connection_info.csv", encoding='euc-kr'))
    print(get_connection_info("plm_host_test_server"))
