"""Test de unidad."""
import unittest
import os
import time
import threading
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium import NoSuchElementException
from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))


class Ordering(unittest.TestCase):

    # Creamos la base de datos de test.
    """Clase para base de datos."""

    def setUp(self):
        """Permite crear base de datos de prueba."""
        self.app = create_app()
        self.app.config.update(
            SQLALCHEM_DB_URI='sqlite:///'+os.path.join(basedir, 'test.db'),
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
        """Permite testear la aparicion del modal."""
        driver = self.driver
        driver.get(self.baseURL)
        apr = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        apr.click()
        modal = driver.find_element_by_id('modal')
        assert modal.is_displayed(), "El modal no esta visible"

    def tearDown(self):
        """Permite eliminar la base de datos usado para el testeo."""
        self.driver.get('http://localhost:5000/shutdown')
        db.session.remove()
        db.drop_all()
        self.driver.close()
        self.app_context.pop()

    def test_cantidad_negativa(self):
        """Permite tester si guarda o no un pedido de cant negativa."""
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

    def test_productos_repetidos_opcional(self):
        """Permite testear si se puede agregar productos repetidos o no."""
        o = Order(id=1)
        db.session.add(o)
        p = Product(id=1, name='Individual', price=50)
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

    def test_borrar(self):
        """Permite testear si se puede borrar correctamente o no una orden."""
        o = Order(id=1)
        db.session.add(o)
        p = Product(id=1, name='Individual', price=50)
        db.session.add(p)
        op = OrderProduct(order_id=1, product_id=1, product=p, quantity=25)
        db.session.add(op)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        xdel = '/html/body/main/div[2]/div/table/tbody/tr[1]/td[6]/button[2]'
        delprod = driver.find_element_by_xpath(xdel)
        delprod.click()
        driverfind = driver.find_element_by_xpath
        self.assertRaises(NoSuchElementException, driverfind, "xpath")

    def test_existe_informacion(self):
        """Permite testear si se guarda correctamente la informacion."""
        o = Order(id=1)
        db.session.add(o)
        p = Product(id=1, name='Silla', price=50)
        db.session.add(p)
        cant = 3
        op = OrderProduct(order_id=1, product_id=1, quantity=cant, product=p)
        db.session.add(op)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        time.sleep(1)
        xpathadd = '//*[@id="orders"]/table[1]/tbody[1]/tr[1]/td[6]/button[1]'
        addprodedit = driver.find_element_by_xpath(xpathadd)
        addprodedit.click()
        time.sleep(1)
        optionselprod = Select(driver.find_element_by_id('select-prod'))
        optionselprod.select_by_visible_text("Silla")
        addcantprod = driver.find_element_by_xpath('//*[@id="quantity"]')
        addcantprod.get_attribute('value')
        self.assertTrue(optionselprod != "", 'NO PUEDE ESTAR VACIO')
        self.assertTrue(addcantprod != "", 'NO PUEDE ESTAR VACIO')


if __name__ == "__main__":
    unittest.main()
