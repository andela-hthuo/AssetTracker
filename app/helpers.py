""" Helper functions"""
from flask_mail import Message
from app import mail

import base64
import os


def send_email(**kwargs):
    msg = Message(
        kwargs.get('subject'),
        sender=kwargs.get('sender'),
        recipients=kwargs.get('recipients'))
    msg.body = kwargs.get('body')
    msg.html = kwargs.get('html')
    mail.send(msg)


def random_base64(accept_function=lambda token: True):
    while True:
        token = base64.urlsafe_b64encode(os.urandom(24))
        if accept_function(token):
            return token
