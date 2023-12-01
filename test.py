import unittest
from app import app, Cuenta, cuentas

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Prueba de exito: "Pago realizado correctamente"
    def test_pago_exitoso(self):
        response = self.app.get('/billetera/pagar?minumero=21345&numerodestino=123&valor=50')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Pago realizado', response.json['mensaje'])

    # Caso de error: "Parámetros vacios"
    def test_parametros_vacios(self):
        response = self.app.get('/billetera/pagar?minumero=&numerodestino=&valor=')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Faltan parametros', response.json['error'])

    # Caso de error: "Saldo insuficiente"
    def test_saldo_insuficiente(self):
        # Asegurándose de que el saldo es menor al valor a pagar
        cuenta_test = cuentas['21345']
        cuenta_test.saldo = 10
        response = self.app.get('/billetera/pagar?minumero=21345&numerodestino=123&valor=50')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Saldo insuficiente', response.json['error'])

    # Caso de error: "Valor de pago no valido (negativo o cero)"
    def test_valor_pago_invalido(self):
        response = self.app.get('/billetera/pagar?minumero=21345&numerodestino=123&valor=-50')
        self.assertEqual(response.status_code, 400)
        self.assertIn('El valor del pago debe ser mayor que cero', response.json['error'])

if __name__ == '__main__':
    unittest.main()
