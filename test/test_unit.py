import os
import unittest

from flask import json
from flask_testing import TestCase

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))

class OrderingTestCase(TestCase):
"""Permite empezar el testeo creando un app para una base de datos"""
    def create_app(self):
        config_name = 'testing'
        app = create_app()
        app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True
        )
        return app
"""Permite crear una base de datos para el testeo"""
   # Creamos la base de datos de test   
    def setUp(self):
        db.session.commit()
        db.drop_all()
        db.create_all()
"""Permite hacer un test para verificar si la base de datos tiene o no productos"""
    def test_iniciar_sin_productos(self):
        resp = self.client.get('/product')
        data = json.loads(resp.data)

        assert len(data) == 0, "La base de datos tiene productos"

    def test_crear_producto(self):
        data = {
            'name': 'Tenedor',
            'price': 50
        }

        resp = self.client.post('/product', data=json.dumps(data), content_type='application/json')

        # Verifica que la respuesta tenga el estado 200 (OK)
        self.assert200(resp, "Falló el POST")
        p = Product.query.all()

        # Verifica que en la lista de productos haya un solo producto
        self.assertEqual(len(p), 1, "No hay productos")

    def test_create_order_product_with_negative_quantity(self):
        def createOrderProduct():
            return OrderProduct(product="Silla", quantity=-1)
        self.assertRaises(ValueError, createOrderProduct)

    def test_get_order_pko_producto_pkp(self):
        p=Product(name="cuchillo", price=60)
        db.session.add(p)
        o=Order()
        db.session.add(o)
        op=OrderProduct(order_id=1,product_id=1,product=p,quantity=25)
        db.session.add(op)
        db.session.commit()
        resp=self.client.get('/order/1/product/1')
        self.assert200(resp, "No existe orden cargada.")
        data1=Product.query.all()
        print(data1)
        self.assertEqual(len(data1),1, "Error en el producto.")
        data2=Order.query.all()
        print(data2)
        self.assertEqual(len(data2),1, "Erro en la orden.")

    def test_order_pko_producto_pkp_put(self):
        o = Order(id=1)
        db.session.add(o)
        p = Product(id= 1, name= 'Silla', price= 500)
        db.session.add(p)
        oProduct = OrderProduct(order_id= 1, product_id= 1, quantity=1, product=p)
        db.session.add(oProduct)
        db.session.commit()
        data = {
           'quantity': 15
           }         
        self.client.put('order/1/product/1', data=json.dumps(data), content_type='application/json')
        produc = OrderProduct.query.all()[0]
        self.assertTrue(produc.quantity == 15, "Fallo el PUT")

    def test_calcular_totales(self):
        o = Order(id=1)
        db.session.add(o)
        precio = 200
        p = Product(id=1, name='Mesa', price=precio)
        db.session.add(p)
        cantidad = 5
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=cantidad, product=p)
        db.session.add(orderProduct)
        db.session.commit()
        precioTotal = precio * cantidad
        self.asserTrue(o.orderPrice == precioTotal, "Fallo el calcularTotales")

    def test_opcional_cantidad_negativa(self):
        o = Order(id=1)
        db.session.add (o)
        p = Product(id=1, name='Silla', price=100)
        db.session.add(p)
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=-10, product=p)
        db.session.add(orderProduct)
        db.session.commit()
        r = self.client.get('order/1/product/1')
        self.assert200
        (r, "el valor de cantidad debe ser positivo") 

    def test_get_order_OPCIONAL(self):
        orden=Order()
        db.session.add(orden)
        db.session.commit()
        resp=self.client.get('/order/1')
        self.assert200(resp, "No existe orden")

    def test_delete(self):
        p=Product(id=1, name="Heladera", price=200)
        db.session.add(p)
        o=Order(id=1)
        db.session.add(o)
        op=OrderProduct(order_id = 1, product_id = 1, product=p, quantity=2)
        db.session.add(op)
        db.session.commit()
        resp_delete=self.client.delete('order/1/product/1', content_type='application/json')
        resp_get=self.client.get('/order/1',content_type='aplication/json')
        data=json.loads(resp_get.data)
        self.assertEqual(resp_delete.status, "200 OK", "Falló el delete") 
        self.assertEqual(len(data["products"]),0, "Fallo el delete")

    def test_nombre_vacio(self):
        producto=Product(id=1, name='Tenedor', price=25)
        db.session.add(producto)
        db.session.commit()
        p=Product.query.all()[0]
        self.assertFalse(p.name=="","El nombre del producto no puede estar vacío")

    # Destruimos la base de datos de test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

if __name__ == '__main__':
    unittest.main()

