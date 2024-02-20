import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from typing import List

from pydantic import EmailStr

from src.services import BaseEmail


class SimpleHtmlGmail(BaseEmail):
    def __init__(self, default_from_email, password):
        self.default_from_email = default_from_email
        self.password = password

    def send_email(
        self,
        subject: str,
        email_to_list: List,
        from_email: EmailStr = None,
        email_body_text: str = None,
        email_body_html: str = None,
        email_cc_list: List = None,
        email_bcc_list: List = None,
    ):
        if email_bcc_list is None:
            email_bcc_list = []
        if email_cc_list is None:
            email_cc_list = []
        email_msg = MIMEMultipart("alternative")
        email_msg["Subject"] = subject
        from_email = from_email or self.default_from_email
        email_msg["From"] = from_email
        email_msg["To"] = ", ".join(email_to_list)
        email_msg["Cc"] = ", ".join(email_cc_list)
        email_msg["Bcc"] = ", ".join(email_bcc_list)
        # Turn these into plain/html MIMEText objects
        textpart = MIMEText(email_body_text, "plain", _charset="UTF-8")
        htmlpart = MIMEText(email_body_html, "html", _charset="UTF-8")
        # Add HTML/plain-text parts to MIMEMultipart email_msg
        # The email client will try to render the last part first
        email_msg.attach(textpart)
        email_msg.attach(htmlpart)

        # Create secure connection with server and send email
        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, context=(ssl.create_default_context())
        ) as server:
            server.login(from_email, self.password)
            server.sendmail(
                from_email,
                email_to_list + email_cc_list + email_bcc_list,
                email_msg.as_string(),
            )

    def send_email_html_file(
        self,
        subject: str,
        email_to_list: List,
        from_email: EmailStr = None,
        email_body_text: str = None,
        email_html_path: str = None,
        email_cc_list: List = None,
        email_bcc_list: List = None,
        **kwargs,
    ):
        if email_bcc_list is None:
            email_bcc_list = []
        if email_cc_list is None:
            email_cc_list = []
        with open(email_html_path, encoding="utf-8") as email_html:
            email_body_html = email_html.read()
            template = Template(email_body_html)
        return self.send_email(
            subject=subject,
            email_to_list=email_to_list,
            from_email=from_email,
            email_body_text=email_body_text,
            email_body_html=template.substitute(**kwargs),
            email_cc_list=email_cc_list,
            email_bcc_list=email_bcc_list,
        )
