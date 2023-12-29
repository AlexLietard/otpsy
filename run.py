import pandas as pd
import otpsy



df_test = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=";")
df_outliers = df_test.drop(
    ["premiere_lettre", "LIB_NOM_PAT_IND_TPW_IND"], axis=1)

sample = otpsy.Sample(df_test,
                column_to_test=["CLI1", "PAT1", "ASD1", "EXP1"],
                participant_column="LIB_NOM_PAT_IND_TPW_IND")

outliers_iqr = sample.method_IQR()
outliers_mad = sample.method_MAD()
outliers_multi = outliers_iqr + ["1"]
print(outliers_multi)
