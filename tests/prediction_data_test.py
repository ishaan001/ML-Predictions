import unittest
import pandas as pd
import numpy as np

import sys
import site

def get_main_path():
    test_path = sys.path[0] # sys.path[0] is current path in lib subdirectory
    split_on_char = "/"
    return split_on_char.join(test_path.split(split_on_char)[:-1])
main_path = get_main_path()
site.addsitedir(main_path+'/tests')
site.addsitedir(main_path+'/lib')
print ("Imported subfolder: %s" % (main_path+'/tests') )

from tests.input_event_test import EVENT
from prediction_config import PredictionConfig
from prediction_utils import PredictionUtils
from prediction_data import PredictionData

class PredictionDataTestCase(unittest.TestCase):
    """Tests for `prediction_data.py`."""

    def setUp(self):
        self.prediction_config = PredictionConfig(EVENT, None)
        self.prediction_utils = PredictionUtils(self.prediction_config)
        self.prediction_data = PredictionData(self.prediction_config, self.prediction_utils)
        self.dataset_choice = self.prediction_config.DATASET_CHOICE

    def tearDown(self):
        del self.prediction_config
        del self.prediction_utils
        del self.prediction_data
        del self.dataset_choice

    def test_valid_training_columns_updates_final_training_columns(self):

        # Setup
        self.prediction_data.prediction_config.DATASET_LOCATION[self.dataset_choice]["training_columns"] = []
        self.prediction_data.df_listings = pd.DataFrame({
            'col1': ['1.1'] * 3,
            'col2': [np.NaN] * 3,
            'col3': [2.2] * 3,
            'col4': [2] * 3,
            'col5': [np.NaN] * 3
        })
        self.prediction_data.target_column = "col4" # Must be int64 otherwise raises ValueError
        self.prediction_data.training_columns = []
        _all_columns = self.prediction_data.df_listings.columns.tolist()
        del _all_columns[3]
        _final_training_columns_without_target_column = _all_columns

        # Test
        self.prediction_data.validate_training_columns()
        self.assertEqual(self.prediction_data.training_columns, _final_training_columns_without_target_column)

    def test_valid_training_columns_raises_error_when_minimum_features_combo_length_not_satisfied(self):

        # Setup
        self.prediction_data.prediction_config.MIN_FEATURES_COMBO_LEN = 3
        self.prediction_data.training_columns = ["col1", "col2"]

        # Test
        self.assertRaises(ValueError)

    def test_valid_training_columns_raises_error_when_target_column_not_integer_type_when_using_logistic_regression(self):
        """"""

        # Setup
        self.prediction_data.prediction_config.ML_MODEL_LOGISTIC = True
        self.prediction_data.df_listings = pd.DataFrame({
            'col1': ['1.1'] * 3,
            'col2': [np.NaN] * 3,
            'col3': [2.2] * 3,
            'col4': [2] * 3,
            'col5': [np.NaN] * 3
        })
        self.prediction_data.target_column = "col4" # float64
        self.prediction_data.training_columns = ["col1", "col2", "col4", "col5"]

        # Test
        self.assertRaises(ValueError, self.prediction_data.validate_training_columns(), "Target column must be Categorical type i.e. int64 NOT float64 when ML_MODEL_LOGISTIC is True")

    def test_converts_multi_classification_columns_to_binary_classification_columns_and_updates_training_columns(self):

        # Setup
        self.prediction_data.prediction_config.ML_MODEL_LOGISTIC = True
        self.prediction_data.df_listings = pd.DataFrame({
            'origin': [1,2,3,2,3,3], # Categories 1, 2 or 3
            'cylinders': [3,4,4,5,5,5], # Categories 3, 4, 5
            'model-year': [70,71,80,71,70,70] # Categories 70, 71, 80
        })
        self.prediction_data.dataset_choice = "car-listings-fuel"
        self.prediction_data.target_column = "origin"
        self.prediction_data.training_columns = ["cylinders", "model-year"]
        self.prediction_data.multi_classification_input_columns = ["cylinders", "model-year"]
        self.prediction_data.convert_categorical_columns_to_dummy_binary_columns()

        # Test
        self.assertEqual(list(self.prediction_data.df_listings.columns), ["origin", "cyl_3", "cyl_4", "cyl_5", "mod_70", "mod_71", "mod_80"])
        self.assertEqual(self.prediction_data.training_columns, ["cyl_3", "cyl_4", "cyl_5", "mod_70", "mod_71", "mod_80"])

if __name__ == '__main__':
    unittest.main()
