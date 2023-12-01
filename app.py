from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

class Cuenta:
    def __init__(self, numero, nombre, saldo, contactos):
        self.numero = numero
        self.nombre = nombre
        self.saldo = saldo
        self.contactos = contactos
        self.historial = []


    def agregar_operacion(self, operacion):
        self.historial.append(operacion)

    def obtener_contactos(self):
        return self.contactos

    def realizar_pago(self, destino, valor):
        if self.saldo < valor:
            return False, "Saldo insuficiente para realizar el pago."
        self.saldo -= valor
        destino.saldo += valor
        operacion_origen = Operacion(self.numero, destino.numero, datetime.now(), -valor)  # Negativo <- indica dinero saliente
        operacion_destino = Operacion(self.numero, destino.numero, datetime.now(), valor) # Positivo <- indica dinero entrante
        self.agregar_operacion(operacion_origen)
        destino.agregar_operacion(operacion_destino)
        return True, "Pago realizado con exito."

class Operacion:
    def __init__(self, numero_origen, numero_destino, fecha, valor):
        self.numero_origen = numero_origen
        self.numero_destino = numero_destino
        self.fecha = fecha
        self.valor = valor

# Cuentas de Prueba:
cuentas = {
    "21345": Cuenta("21345", "Arnaldo", 200, ["123", "456"]),
    "123": Cuenta("123", "Luisa", 400, ["456"]),
    "456": Cuenta("456", "Andrea", 300, ["21345"])
}

@app.route('/')
def index():
    return jsonify({'mensaje': 'Hola, Bienvenido a Yape'})


@app.route('/billetera/contactos', methods=['GET'])
def obtener_contactos():
    minumero = request.args.get('minumero')

    if not minumero:
        return jsonify({'error': 'No se proporciono un nro de cuenta. Por favor, proporcione un nro de cuenta valido.'}), 400

    cuenta = cuentas.get(minumero)
    if cuenta:
        contactos_info = {contacto: cuentas[contacto].nombre for contacto in cuenta.obtener_contactos()}
        return jsonify(contactos_info), 200
    
    return jsonify({'error': 'Nro de cuenta no encontrado.'}), 404


@app.route('/billetera/pagar', methods=['GET'])
def ruta_pagar():
    minumero = request.args.get('minumero')
    numerodestino = request.args.get('numerodestino')
    valor_str = request.args.get('valor')
    
    if not minumero or not numerodestino or valor_str in (None, ''):
        return jsonify({'error': 'Faltan parametros o hay campos vacios para realizar el pago.'}), 400

    try:
        valor = float(valor_str)
        # El valor siosi tiene que ser mayor que cero:
        if valor <= 0:
            raise ValueError('El valor del pago debe ser mayor que cero.')
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    cuenta_origen = cuentas.get(minumero)
    cuenta_destino = cuentas.get(numerodestino)
    
    if cuenta_origen and cuenta_destino:
        pago_exitoso, mensaje = cuenta_origen.realizar_pago(cuenta_destino, valor)
        if pago_exitoso:
            fecha = datetime.now().strftime("%d/%m/%Y")
            return jsonify({'mensaje': mensaje, 'fecha': fecha}), 200
        else:
            return jsonify({'error': mensaje}), 400
    
    return jsonify({'error': 'Verifique los nros de cuenta y asegurese de que ambos sean correctos.'}), 400


@app.route('/billetera/historial', methods=['GET'])
def historial():
    minumero = request.args.get('minumero')
    
    if not minumero:
        return jsonify({'error': 'El campo del nro de cuenta esta vacio. Por favor, proporcione un nro de cuenta.'}), 400

    cuenta = cuentas.get(minumero)
    if cuenta:
        historial_info = {
            'saldo': cuenta.saldo,
            'operaciones': [
                {
                    'fecha': op.fecha.strftime("%d/%m/%Y"),
                    'valor': op.valor,
                    'numero_destino': op.numero_destino
                } for op in cuenta.historial
            ]
        }
        return jsonify(historial_info), 200
    return jsonify({'error': 'Nro de cuenta no encontrado'}), 404


if __name__ == '__main__':
    app.run(debug=True)
