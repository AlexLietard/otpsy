import pandas as pd
import otpsy as ot

df = pd.read_csv("tests/data.csv", sep=";", index_col="index_participant")

def test_sample_instantiation(df_func):
    assert(df.columns[0] == "index_participant")
    print(df_func)

test_sample_instantiation(df)