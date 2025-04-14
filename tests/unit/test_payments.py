from flask import url_for
from app.models import Payment, Order
from pprint import pprint
from app.schemas import PaymentSchema, OrderSchema
from app import db


def test_get_payment_methods(client):
    payment_methods = Payment.get_payment_methods()
    assert isinstance(payment_methods, list), "Expected a list of payment methods"
    assert len(payment_methods) > 0, "Expected at least one payment method"
    assert all(isinstance(pm, str) for pm in payment_methods), "Expected all payment methods to be strings"
    response = client.get(url_for('checkout.get_checkout_methods'))
    assert response.status_code == 200, "Expected status code 200"
    assert response.json == payment_methods, "Expected response to match payment methods"


def test_zelle_payment():
    zelle_payment = Payment.create_payment("Zelle")
    zelle_payment.process_payment()


def test_pago_movil_payment():
    pm_payment = Payment.create_payment("Pago Movil")
    pm_payment.process_payment()


def test_adding_payment_to_order(client, regular_user):
    # Create a sample order
    order = Order(total=10)
    print(order)
    payment = Payment.create_payment("Stripe")
    payment.stripe_account_id = "acct_123456789"
    order.payment = payment
    db.session.add(order)
    db.session.commit()
    pprint(OrderSchema().dump(order))
    assert False
