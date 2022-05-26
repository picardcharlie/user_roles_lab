from flask import current_app, render_template
from flask_mail import Message
from . import mail
from threading import Thread

def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    # subject takes predefined prefix and an argument, recipients accepts a list of emails, sender takes predefined email.
    msg = Message(subject=current_app.config["ZOMBO_MAIL_SUBJECT_PREFIX"]+subject, recipients=[to], sender=current_app.config["ZOMBO_MAIL_SENDER"])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)
    thread = Thread(target=send_async_mail, args=[app, msg])
    thread.start()