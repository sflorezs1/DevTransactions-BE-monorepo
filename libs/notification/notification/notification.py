import logging
from .config import SUPPORT_EMAIL, API_KEY
from mailersend import emails

logger = logging.getLogger(__name__)


def send_template_email(to_name, to_email, template_id, template_data, subject):
    mailer = emails.NewEmail(API_KEY.replace("\n", ""))

    # define an empty dict to populate with mail values
    mail_body = {}

    mail_from = {
        "name": "Dev Transactions Team",
        "email": SUPPORT_EMAIL.replace("\n", ""),
    }

    recipients = [
        {
            "name": to_name,
            "email": to_email,
        }
    ]

    variables = [
        {
            "email": to_email,
            "data": { 
                **template_data,
                "account_name": "Dev Transactions"
            }
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_template(template_id, mail_body)
    mailer.set_advanced_personalization(variables, mail_body)

    logger.info(f"Sending email {mail_body}")

    mailer.send(mail_body)