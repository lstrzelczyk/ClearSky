import unittest
from src.main import App, ApiService, Satellite
from unittest.mock import patch
from skyfield.api import load


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def test_merkator_projection(self):
        test_cases = [
            ("52N", "21E", 469, 217),
            ("37S", "144E", 756, 453),
            ("8S", "35W", 338, 378),
            ("42N", "87W", 217, 251)
        ]
        map_width = 840
        map_height = 720
        results = [self.app.merkator_projection(lat, lon, map_width, map_height) for lat, lon, _, _ in test_cases]
        expected = [(x, y) for _, _, x, y in test_cases]
        self.assertEqual(results, expected)


class TestApi(unittest.TestCase):
    def setUp(self):
        self.api = ApiService()

    def test_call(self):
        res = self.api.call("25544")
        self.assertNotEqual(res['info']['satname'], None)


class TestSatelliteClass(unittest.TestCase):
    def setUp(self) -> None:
        self.sat = Satellite()

    def test_predict_pass(self):
        satellite_instance = self.sat
        sample_sat_data = {
            'tle': '1 25544U 98067A   23222.04318669  .00034014  00000-0  59941-3 0 '
                   '9991\r\n2 25544  51.6404  61.6944 0000233 342.2146 167.3767 15.50094389410143'
        }
        prediction = satellite_instance.predict_pass(sample_sat_data)
        self.assertEqual(len(prediction), 299)

    def test_calculate_satellite_position(self):
        sample_sat_data = {
            'info': {'satid': 25544, 'satname': 'SPACE STATION', 'transactionscount': 24},
            'tle': '1 25544U 98067A   23222.04318669  .00034014  00000-0  59941-3 0  '
                   '9991\r\n2 25544  51.6404  61.6944 0000233 342.2146 167.3767 15.50094389410143'
        }
        static_time = load.timescale().utc(2023, 8, 7, 12, 0, 0)
        with patch('skyfield.api.load.timescale') as mock_timescale:
            mock_timescale.return_value.now.return_value = static_time
            latitude, longitude = self.sat.calculate_satellite_position(sample_sat_data)

        self.assertIsInstance(latitude, float)
        self.assertIsInstance(longitude, float)
        self.assertEqual(latitude, -8.604739171924301)
        self.assertEqual(longitude, -68.29602563305329)


if __name__ == '__main__':
    unittest.main()
