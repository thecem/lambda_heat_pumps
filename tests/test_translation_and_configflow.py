import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
import os
from custom_components.lambda_heat_pumps import config_flow

TRANSLATION_PATH = os.path.join(
    os.path.dirname(__file__),
    '../custom_components/lambda_heat_pumps/translations/de.json'
)

class TestTranslations(unittest.TestCase):
    def test_translation_file_exists(self):
        self.assertTrue(os.path.exists(TRANSLATION_PATH), "de.json nicht gefunden!")

    def test_translation_keys(self):
        with open(TRANSLATION_PATH, encoding='utf-8') as f:
            data = json.load(f)
        # Prüfe einige wichtige Schlüssel
        self.assertIn('config', data)
        self.assertIn('step', data['config'])
        self.assertIn('user', data['config']['step'])
        self.assertIn('data', data['config']['step']['user'])
        self.assertIn('num_buff', data['config']['step']['user']['data'])
        self.assertIn('num_sol', data['config']['step']['user']['data'])
        self.assertIn('use_legacy_modbus_names', data['config']['step']['user']['data'])
        self.assertIn('options', data['config'])
        self.assertIn('init', data['config']['options']['step'])
        self.assertIn('data', data['config']['options']['step']['init'])
        self.assertIn('hot_water_min_temp', data['config']['options']['step']['init']['data'])

class TestConfigFlow(unittest.TestCase):
    def test_config_flow_class_exists(self):
        self.assertTrue(hasattr(config_flow, 'LambdaConfigFlow'))
        self.assertTrue(callable(getattr(config_flow, 'LambdaConfigFlow')))

if __name__ == '__main__':
    unittest.main()