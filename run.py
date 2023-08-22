import pandas as pd
import outliers_toolbox


df = pd.read_csv("C:/Users/alexl/Downloads/blabla.csv", sep=';')
outliers = outliers_toolbox.Sample(
    df, ["PAT1", "CLI1", "DIF1"], "LIB_NOM_PAT_IND_TPW_IND").method_IQR(2.5)
print(outliers)
