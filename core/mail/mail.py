# coding: utf8
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.utils import parseaddr, formataddr
from jinja2 import Environment, FileSystemLoader
import smtplib

from core import toLog
from config import settings


class Email(object):
    def __init__(self, sender, subject, content):
        self.sender = sender
        self.subject = subject
        self.content = content

        self.host = settings.email_host
        self.port = settings.email_port
        self.user = settings.email_host_user
        self.password = settings.email_host_password

        self.jinja_env = Environment(
            loader=FileSystemLoader(settings.EMAIL_TEMPLATE_DIR),
            trim_blocks=True
        )

        self._prepare()

    def _prepare(self):
        if isinstance(self.subject, dict):
            self.subject = self.jinja_env.get_template(self.subject['filename']).render(self.subject['context'])

        if isinstance(self.content, dict):
            self.content = self.jinja_env.get_template(self.content['filename']).render(self.content['context'])

        self.msg = MIMEMultipart()
        self.msg['From'] = self._format_addr(u'<%s>' % self.sender)
        self.msg['Subject'] = Header(u'%s' % self.subject, 'utf-8').encode()
        self.msg.attach(MIMEText(self.content, 'html', 'utf-8'))

    def _smtp(self, receiver):
        server = smtplib.SMTP(self.host, self.port)
        server.starttls()
        server.login(self.user, self.password)
        server.sendmail(self.sender, [receiver], self.msg.as_string())
        server.quit()

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((
            Header(name, 'utf-8').encode(),
            addr.encode('utf-8') if isinstance(addr, unicode) else addr
        ))

    def send_email(self, receiver):
        self.msg['To'] = self._format_addr(u'<%s>' % receiver)

        if settings.email_backend == 'smtp':
            self._smtp(receiver)
        elif settings.email_backend == 'debug':
            toLog(self.msg.as_string(), 'debug')

        return True
