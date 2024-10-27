# It is important to run "pip install -e ." before running test.

import pandas as pd
import numpy as np
import pytest
import otpsy as ot


df = pd.read_csv("./tests/data.csv", sep=";")
class TestClass:
    sample_columns_to_test_p_col = \
            ot.Sample(df, 
                        columns_to_test=['likert1', 'likert2', 'likert3', 'likert4'], 
                        participant_column="index_participant")
    outliers = sample_columns_to_test_p_col.method_identical(frequency=0.95, threshold_included=True)

    def test_Instantiation(self):
        self.sample_columns_to_test_p_col.method_identical()
        self.sample_columns_to_test_p_col.method_identical(frequency = 0.95)
        self.sample_columns_to_test_p_col.method_identical(threshold_included=True)

    def test_verify_dict_col(self):
        dict_col = {'Identical': ['P4', 'P6']}
        assert(self.outliers.dict_col == dict_col)

    def test_verify_all_index(self):
        all_index = ['P4', 'P6']
        assert(self.outliers.all_index == all_index)
    
    def test_verify_nb(self):
        nb = {'Identical': 2}
        assert(self.outliers.nb == nb)

    def test_verify_position(self):
        position = {'Identical': [3, 5]}
        assert(self.outliers.position == position)

    def test_threshold_value(self):
        threshold = {'Identical': 0.95}
        assert(self.outliers.threshold == threshold)

    def test_add_method(self):
        self.outliers.add("P8")
        assert(self.outliers.dict_col == 
                {'Identical': ['P4', 'P6'], 
                 "added_manually": ["P8"]}
                 )
        assert(self.outliers.position == 
               {'Identical': [3, 5], 
                "added_manually":[7]}
                )
        assert(self.outliers.nb ==
               {'Identical':2, "added_manually":1})
        assert(self.outliers.all_index == ["P4", "P6", "P8"])

    def test_remove_method(self):
        self.outliers.remove("P4")
        assert(self.outliers.dict_col ==
                {'Identical': ['P6'], 
                 "added_manually": ["P8"]}
                 )
        assert(self.outliers.position == 
               {'Identical': [5], 
                 "added_manually": [7]}
                )
        assert(self.outliers.nb ==
               {'Identical': 1, "added_manually":1})
        assert(self.outliers.all_index == ["P6", 'P8'])

    def test_manage_method(self):
        df1 = self.outliers.manage(method="delete")
        assert(len(df1.index) == 59)

        with pytest.raises(ValueError):
            df2 = self.outliers.manage(method = "winsorise")

        df3 = self.outliers.manage(method = "na")
        assert(np.isnan(df3.loc["P6", "likert1"]))
