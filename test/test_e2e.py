import unittest
import os
import time
import threading
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))

from werkzeug.serving import make_server

class Ordering(unittest.TestCase):
    # Creamos la base de datos de test
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True
        )

        self.app_context = self.app.app_context()
        self.app_context.push()

        self.baseURL = 'http://localhost:5000'

        db.session.commit()
        db.drop_all()
        db.create_all()

        self.t = threading.Thread(target=self.app.run)
        self.t.start()

        time.sleep(1)

        self.driver = webdriver.Chrome()

    def test_title(self):
        driver = self.driver
        driver.get(self.baseURL)
        add_product_button = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        add_product_button.click()
        modal = driver.find_element_by_id('modal')
        assert modal.is_displayed(), "El modal no esta visible"

    def tearDown(self):
        self.driver.get('http://localhost:5000/shutdown')
        db.session.remove()
        db.drop_all()
        self.driver.close()
        self.app_context.pop()

    def test_cantidad_negativa(self):
        driver = self.driver
        driver.get(self.baseURL)
        add_product_button = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        add_product_button.click()
        select_product = Select(driver.find_element_by_id('select-prod'))
        select_product.select_by_visible_text("Silla")
        cantidad_product = driver.find_element_by_id('quantity')
        cantidad_product.send_keys("-1")
        guardar_button = driver.find_element_by_id('save-button')
        self.assertFalse(guardar_button.is_enabled(), "Boton de guardado debe estar inhabilitado.")

    def test_productos_repetidos_OPCIONAL(self):
        o=Order(id=1)
        db.session.add(o)
        p=Product(id=1, name='Individual', price=50)
        db.session.add(p)
        op=OrderProduct(order_id=1, product_id=1, product=p, quantity=25)
        db.session.add(op)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        add_product_button = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        add_product_button.click()
        select_product = Select(driver.find_element_by_id('select-prod'))
        select_product.select_by_visible_text("Individual")
        cantidad_product = driver.find_element_by_id('quantity')
        cantidad_product .send_keys("1")
        guardar_button = driver.find_element_by_id('save-button')
        guardar_button.click()
        negado_guardar_button = driver.find_element_by_id('save-button')
        self.assertFalse(negado_guardar_button.is_enabled(), "No puede haber productos repetidos.")
    
    def test_borrar(self)
        o=Order(id=1)
        db.session.add(o)
        p=Product(id=1, name='Individual', price=50)
        db.session.add(p)
        op=OrderProduct(order_id=1, product_id=1, product=p, quantity=25)
        db.session.add(op)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        delete_product_button = driver.find_element_by_xpath('/html/body/main/div[2]/div/table/tbody/tr[1]/td[6]/button[2]')
        delete_product_button.click()
        self.assertRaises(NoSuchElementException, driver.find_element_by_xpath, "xpath")
        
if __name__ == "__main__":
    unittest.main()

