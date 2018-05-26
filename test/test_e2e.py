import unittest
import os

from selenium import webdriver
from flask_testing import LiveServerTestCase

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))

class Ordering(LiveServerTestCase):
    def create_app(self):
        app = create_app()
        app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True
        )

        return app

    # Creamos la base de datos de test
    def setUp(self):
        self.baseURL = self.get_server_url()

        db.session.commit()
        db.drop_all()
        db.create_all()

        self.driver = webdriver.Chrome()

    def test_title(self):
        driver = self.driver
        driver.get(self.baseURL)
        self.assertIn("Ordering", driver.title)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.driver.close()
    
    def selerium_control_bug_cant_negativa(self):
        self.driver = webdriver.Chrome()
        driver.get("http://127.0.0.1:5000")
        assert "Lista de compra" in driver.h1


if __name__ == "__main__":
    unittest.main()

