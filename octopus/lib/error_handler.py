import logging
import logging.handlers
import sys

from octopus.lib.mail import send_mail


class TlsSMTPHandler(logging.Handler):

    def __init__(self, mailhost, mailport, fromaddr, toaddrs, subject, credentials):
        super(TlsSMTPHandler, self).__init__()
        self.mailhost = mailhost
        self.mailport = mailport
        if isinstance(credentials, tuple):
            self.username, self.password = credentials
        else:
            raise ValueError("credentials must be a tuple: ('username', 'password')")
        self.fromaddr = fromaddr
        if isinstance(toaddrs, basestring):
            self.toaddrs = [toaddrs]
        else:
            self.toaddrs = toaddrs
        if subject and isinstance(subject, basestring):
            self.subject = subject
        else:
            raise ValueError("subject can't be blank and must be a string")

    def emit(self, record):
        """
        Emit a record.
 
        Format the record and send it to the specified addressees.
        """

        try:
            msg = self.format(record)
            send_mail(to=self.toaddrs, subject=self.subject, template_name="emails/error_report.txt", error_report=msg)
        except Exception:
            self.handleError(record)


def setup_error_logging(app, email_subject, stdout_logging_level=logging.ERROR, email_logging_level=logging.ERROR):
    # Custom logging WILL BE IGNORED by Flask if app.debug == True -
    # even if you remove the condition below.
    if app.debug:
        return

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    send_to = app.config.get('ERROR_LOGGING_ADDRESSES', [app.config.get('ADMIN_EMAIL')])
    if send_to and not app.config.get('SUPPRESS_ERROR_EMAILS'):
        if 'MAIL_SERVER' in app.config and 'MAIL_PORT' in app.config and 'MAIL_USERNAME' in app.config and 'MAIL_PASSWORD' in app.config:
            import platform
            hostname = platform.uname()[1]
            mail_handler = TlsSMTPHandler(
                app.config['MAIL_SERVER'],
                app.config['MAIL_PORT'],
                'server-error@' + hostname,
                send_to,
                email_subject,
                credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            )
            mail_handler.setLevel(email_logging_level)
            mail_handler.setFormatter(formatter)
            app.logger.addHandler(mail_handler)

    # send errors to stderr, supervisord will capture them in the app's
    # error log
    send_errors_to_supervisor = logging.StreamHandler(sys.stderr)
    send_errors_to_supervisor.setLevel(stdout_logging_level)
    send_errors_to_supervisor.setFormatter(formatter)
    app.logger.addHandler(send_errors_to_supervisor)
