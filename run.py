import pandas as pd
import otpsy

df = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=';')
outliers = otpsy.Sample(
    df, ["PAT1", "CLI1", "DIF1"], "LIB_NOM_PAT_IND_TPW_IND").method_IQR(2.5).visualisation()
