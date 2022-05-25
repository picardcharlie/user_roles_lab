from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_mail(to, subject, template, **kwargs):
    # subject takes predefined prefix and an argument, recipients accepts a list of emails, sender takes predefined email.
    msg = Message(subject=current_app.config["ZOMBO_MAIL_SUBJECT_PREFIX"]+subject, recipients=[to], sender=current_app.config["ZOMBO_MAIL_SENDER"])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)