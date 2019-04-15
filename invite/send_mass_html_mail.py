"""
send_mass_html_mail

https://stackoverflow.com/questions/7583801/send-mass-emails-with-emailmultialternatives/10215091#10215091
"""
from pathlib import Path

from django.core.mail import get_connection, EmailMultiAlternatives


def __add_attached_files(message: EmailMultiAlternatives, data: tuple):
    """Add attached files to EmailMultiAlternatives"""
    if len(data) > 5 and data[5]:
        attached_files = data[5]
        for path, filename, mimetype in attached_files:
            with Path(path).open('rb') as file:
                content = file.read()
            message.attach(filename=filename, content=content, mimetype=mimetype)


def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None,
                        connection=None, **extra_kwargs):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list[, attached_files]), sends each message to each recipient list. Returns the
    number of emails sent.

    :type datatuple: Union[List[Tuple[str, str, str, str, List[str]],
                           List[Tuple[str, str, str, str, List[str], List[Tuple[str, str, str]]]
    :type subject: str (without \n)
    :type text_content: str
    :type html_content: str
    :type from_email: str
    :type recipient_list: List[str]
    :type attached_files: Optional[List[path: str, filename: str, mimetype: str]]

    If you want to use images in html message, define physical paths and ids in tuples.
    (image paths are relative to  MEDIA_ROOT)
    example:

        attached_files=(('email_images/logo.gif', 'img1', 'image/gif'),
                        ('email_images/footer.gif', 'img2', image/gif'))

    and use them in html like this:

        <img src="cid:img1">
        ...
        <img src="cid:img2">

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.
    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for data in datatuple:
        subject, text, html, from_email, recipient = data[:5]
        message = EmailMultiAlternatives(subject, text, from_email, recipient, **extra_kwargs)
        message.attach_alternative(html, 'text/html')
        __add_attached_files(message, data)
        messages.append(message)
    return connection.send_messages(messages)
