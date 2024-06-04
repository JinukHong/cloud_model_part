# test_app.py
import pytest
from flask_testing import TestCase
from api_server import app  # Adjust the import according to your app structure

class MyTest(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_image_generation(self):
        response = self.client.get('/generate-and-send-image/dog,cat,cloud')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'image/png')

# Run tests with pytest
