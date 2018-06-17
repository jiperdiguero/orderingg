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
"""Permite crear una base de datos para usar en el test"""
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            SQLALCHEM_DB_URI='sqlite:///'+os.path.join(basedir,'test.db'),
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
"""Permite testear al aparicion del modal"""
    def test_title(self):
        driver = self.driver
        driver.get(self.baseURL)
        apr = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        apr.click()
        modal = driver.find_element_by_id('modal')
        assert modal.is_displayed(), "El modal no esta visible"
"""Permite eliminar la base de datos usado para el testeo"""				
    def tearDown(self):
        self.driver.get('http://localhost:5000/shutdown')
        db.session.remove()
        db.drop_all()
        self.driver.close()
        self.app_context.pop()
"""Permite testear si se puede o no guardar un pedido con cantidad negativa"""
    def test_cantidad_negativa(self):
        driver = self.driver
        driver.get(self.baseURL)
        apr = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        apr.click()
        select_product = Select(driver.find_element_by_id('select-prod'))
        select_product.select_by_visible_text("Silla")
        cantidad_product = driver.find_element_by_id('quantity')
        cantidad_product.send_keys("-1")
        guardar_button = driver.find_element_by_id('save-button')
        self.assertFalse(guardar_button.is_enabled(), "Error guardado")
"""Permite testear si se puede agregar productos repetidos o no"""
    def test_productos_repetidos_OPCIONAL(self):
        o = Order(id=1)
        db.session.add(o)
        p = Product(id=1,name='Individual',price=50)
        db.session.add(p)
        op = OrderProduct(order_id=1, product_id=1, product=p, quantity=25)
        db.session.add(op)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        apr = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        apr.click()
        select_product = Select(driver.find_element_by_id('select-prod'))
        select_product.select_by_visible_text("Individual")
        cantidad_product = driver.find_element_by_id('quantity')
        cantidad_product .send_keys("1")
        guardar_button = driver.find_element_by_id('save-button')
        guardar_button.click()
        negado_guardar = driver.find_element_by_id('save-button')
        self.assertFalse(negado_guardar.is_enabled(), "Error repetidos")
"""Permite testear si se pueded borrar correctamente o no una orden"""
    def test_borrar(self):
        o = Order(id=1)
        db.session.add(o)
        p = Product(id=1, name='Individual', price=50)
        db.session.add(p)
        op = OrderProduct(order_id=1, product_id=1, product=p, quantity=25)
        db.session.add(op)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        delprod = driver.find_element_by_xpath('/html/body/main/div[2]/div/table/tbody/tr[1]/td[6]/button[2]')
        delprod.click()
        self.assertRaises(NoSuchElementException, driver.find_element_by_xpath, "xpath")
"""Permite testear si se guarda correctamente la informacion"""
    def test_existe_informacion(self):
        o =Order(id=1)
        db.session.add(o)
        p = Product(id=1, name='Silla', price=50)
        db.session.add(p)
        cantidad = 3
        op=OrderProduct(order_id=1,product_id=1,quantity=cantidad,product=p)
        db.session.add(op)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        time.sleep(1)
        add_product_opendEdit = driver.find_element_by_xpath('//*[@id="orders"]/table[1]/tbody[1]/tr[1]/td[6]/button[1]')
        add_product_opendEdit.click()
        time.sleep(1)
        option_select_product = Select(driver.find_element_by_id('select-prod'))
        option_select_product.select_by_visible_text("Silla")   
        add_cantidad_productos = driver.find_element_by_xpath('//*[@id="quantity"]')
        add_cantidad_productos.get_attribute('value')
        self.assertTrue(option_select_product != "", 'EL CAMPO DETALLE DE PRODUCTOS NO PUEDE ESTAR VACIO')
        self.assertTrue(add_cantidad_productos != "", 'EL CAMPO CANTIDAD DE PRODUCTOS NO PUEDE ESTAR VACIO') 

if __name__ == "__main__":
    unittest.main()

