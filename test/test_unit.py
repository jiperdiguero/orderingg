"""Archivo de test de unidad."""
import os
import unittest

from flask import json
from flask_testing import TestCase

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))


class OrderingTestCase(TestCase):
    """Permite empezar el testeo creando un app para una base de datos."""

    def create_app(self):
        """Permite crear una base de datos para el testeo."""
        app = create_app()
        app.config.update(
            SQLALCHEMY_DB_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True
        )
        return app
    # Creamos la base de datos de test

    def setUp(self):
        """Permite hacer un test para ver si la BD tiene o no prod."""
        db.session.commit()
        db.drop_all()
        db.create_all()

    def test_iniciar_sin_productos(self):
        """Test inicio sin productos."""
        resp = self.client.get('/product')
        data = json.loads(resp.data)
        assert len(data) == 0, "La base de datos tiene productos"

    def test_crear_producto(self):
        """Test crear productos."""
        data = {
            'name': 'Tenedor',
            'price': 50
        }
        aa = '/product'
        bb = 'application/json'
        resp = self.client.post(aa, data=json.dumps(data), content_type=bb)

        # Verifica que la respuesta tenga el estado 200 (OK)
        self.assert200(resp, "Falló el POST")
        p = Product.query.all()

        # Verifica que en la lista de productos haya un solo producto
        self.assertEqual(len(p), 1, "No hay productos")

    def test_create_order_product_with_negative_quantity(self):
        """Test crear order de producto negativo."""
        def createorderproduct():
            return OrderProduct(product="Silla", quantity=-1)
        self.assertRaises(ValueError, createorderproduct)

    def test_get_order_pko_producto_pkp(self):
        """Test para orderproduct."""
        p = Product(name="cuchillo", price=60)
        db.session.add(p)
        o = Order()
        db.session.add(o)
        op = OrderProduct(order_id=1, product_id=1, product=p, quantity=25)
        db.session.add(op)
        db.session.commit()
        resp = self.client.get('/order/1/product/1')
        self.assert200(resp, "No existe orden cargada.")
        data1 = Product.query.all()
        print(data1)
        self.assertEqual(len(data1), 1, "Error en el producto.")
        data2 = Order.query.all()
        print(data2)
        self.assertEqual(len(data2), 1, "Erro en la orden.")

    def test_order_pko_producto_pkp_put(self):
        """Test para orderproduct (put)."""
        o = Order(id=1)
        db.session.add(o)
        p = Product(id=1, name='Silla', price=500)
        db.session.add(p)
        op = OrderProduct(order_id=1, product_id=1, quantity=1, product=p)
        db.session.add(op)
        db.session.commit()
        data = {
           'quantity': 15
           }
        aa = 'order/1/product/1'
        bb = 'application/json'
        self.client.put(aa, data=json.dumps(data), content_type=bb)
        produc = OrderProduct.query.all()[0]
        self.assertTrue(produc.quantity == 15, "Fallo el PUT")

    def test_calcular_totales(self):
        """Test calculo totales."""
        o = Order(id=1)
        db.session.add(o)
        precio = 200
        p = Product(id=1, name='Mesa', price=precio)
        db.session.add(p)
        cant = 5
        op = OrderProduct(order_id=1, product_id=1, quantity=cant, product=p)
        db.session.add(op)
        db.session.commit()
        preciototal = precio * cant
        self.asserTrue(o.orderPrice == preciototal, "Fallo el calcularTotales")

    def test_opcional_cantidad_negativa(self):
        """Test opcional 1."""
        o = Order(id=1)
        db.session.add(o)
        p = Product(id=1, name='Silla', price=100)
        db.session.add(p)
        op = OrderProduct(order_id=1, product_id=1, quantity=-10, product=p)
        db.session.add(op)
        db.session.commit()
        r = self.client.get('order/1/product/1')
        self.assert200(r, 'El valor de cantidad debe ser positivo.')

    def test_get_order_opcional(self):
        """Test opcional get order."""
        orden = Order()
        db.session.add(orden)
        db.session.commit()
        resp = self.client.get('/order/1')
        self.assert200(resp, "No existe orden")

    def test_delete(self):
        """Test delete."""
        p = Product(id=1, name="Heladera", price=200)
        db.session.add(p)
        o = Order(id=1)
        db.session.add(o)
        op = OrderProduct(order_id=1, product_id=1, product=p, quantity=2)
        db.session.add(op)
        db.session.commit()
        aa = 'order/1/product/1'
        bb = 'application/json'
        resp_delete = self.client.delete(aa, content_type=bb)
        resp_get = self.client.get('/order/1', content_type='aplication/json')
        data = json.loads(resp_get.data)
        self.assertEqual(resp_delete.status, "200 OK", "Falló el delete"),
        self.assertEqual(len(data["products"]), 0, "Fallo el delete")

    def test_nombre_vacio(self):
        """Test de nombre vacio."""
        producto = Product(id=1, name='Tenedor', price=25)
        db.session.add(producto)
        db.session.commit()
        p = Product.query.all()[0]
        self.assertFalse(p.name == "", "Nombre no debe estar vacio")

    # Destruimos la base de datos de test
    def tearDown(self):
        """Destruye base de datos."""
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()
