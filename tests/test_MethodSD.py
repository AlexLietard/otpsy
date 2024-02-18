import pandas as pd
import os 
import pytest
df = pd.read_csv("tests/data.csv", sep=";")

# Allow to have the local copy of package
os.chdir("./src")
import otpsy as ot

@pytest.mark.parametrize("df", [df])
class TestClass:
    # Define global variable
    sample_columns_to_test_p_col = \
            ot.Sample(df, 
                        columns_to_test=["art_looking_time", "discrimination_performance"], 
                        participant_column="index_participant")
    outliers = sample_columns_to_test_p_col.method_SD(distance=2.4, threshold_included=True)

    def test_Instantiation(self, df):
        sample_columns_to_test_p_col = \
            ot.Sample(df, 
                        columns_to_test=["art_looking_time", "discrimination_performance"], 
                        participant_column="index_participant")
        sample_columns_to_test_p_col.method_SD()
        sample_columns_to_test_p_col.method_SD(distance = 2.7)
        sample_columns_to_test_p_col.method_SD(threshold_included=True)
        self.outliers = sample_columns_to_test_p_col.method_SD(distance=2.4, threshold_included=True)
    
    def test_verify_dict_col(self, df):
        dict_col = {'art_looking_time': ['P10', 'P11'], 'discrimination_performance': ['P37']}
        assert(self.outliers.dict_col == dict_col)
    def test_verify_all_index(self, df):
        all_index = ['P11', 'P10', 'P37']
        assert(self.outliers.all_index == all_index)

os.chdir("..")
