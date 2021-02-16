from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail

import boto3
from botocore.exceptions import ClientError

# ''' Send email asynchronously. '''
# def send_async_email(app, msg):
#     with app.app_context():
#         mail.send(msg)

# ''' Prepare email before being sent. '''
# def send_mail(subject, recipients, text_body, html_body, 
#             attachments=None, sync=False):
#     msg = Message(subject, recipients=recipients, sender='riccardo.andronache14@gmail.com')
#     msg.body = text_body
#     msg.html = html_body

#     if attachments:
#         for attachment in attachments:
#             # *sth is used to decompress tupples into individual arguments.
#             msg.attach(*attachment)
    
#     if sync:
#         mail.send(msg)
#     else:
#         Thread(target=send_async_email, 
#             args=(current_app._get_current_object(), msg)).start()

def send_awsses_mail(subject, text_body, html_body):
    # try to send mail
    try:
        response = current_app.ses_client.send_email(
            Destination={
                'ToAddresses': current_app.config['ADMINS']
            },
            Message={
                'Body': {
                    'Html':{
                        'Charset': current_app.config['AWS_SES_CHARSET'],
                        'Data': html_body,
                    },
                    'Text':{
                        'Charset': current_app.config['AWS_SES_CHARSET'],
                        'Data': text_body,
                    },
                },
                'Subject':{
                    'Charset': current_app.config['AWS_SES_CHARSET'],
                    'Data': subject,
                },
            },
            Source=current_app.config['AWS_SES_SENDER'])
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print( f'Email sent!' )
        
