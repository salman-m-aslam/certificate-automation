import numpy as np
import pandas as pd
import cv2
from PIL import ImageFont, ImageDraw, Image, ImageOps
import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import formataddr
from datetime import date

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'secrets/client_secret.json'
APPLICATION_NAME = 'Gmail API Python Send Email'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def SendMessage(sender, to, subject, msgHtml, msgPlain, attachmentFile):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message1 = createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
    result = SendMessageInternal(service, "me", message1)
    return result

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print("Email sent successfully!")
        print('Email Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"

def createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile):
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    messageA = MIMEMultipart('alternative')
    messageR = MIMEMultipart('related')
    messageR.attach(MIMEText(msgHtml, 'html'))
    messageA.attach(MIMEText(msgPlain, 'plain'))
    messageA.attach(messageR)
    message.attach(messageA)
    #print("create_message_with_attachment: file: %s" % attachmentFile)
    content_type, encoding = mimetypes.guess_type(attachmentFile)
    main_type, sub_type = content_type.split('/', 1)
    fp = open(attachmentFile, 'rb')
    msg = MIMEApplication(fp.read(), _subtype=sub_type)
    fp.close()
    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

def main():
    to = data['Email'][i]
    sender = formataddr((str(Header('<Sender Name>', 'utf-8')), '<Sender Email>'))
    subject = "<Email Subject>"
    msgHtml = """<HTML Email>"""
    msgPlain = "<Plain Email>"
    attachmentFile = 'certificates/Certificate_%s.pdf' % data['Membership No.'][i]
    SendMessage(sender, to, subject, msgHtml, msgPlain, attachmentFile)

data_path = 'content/member_list.csv'
name_font_path = 'content/name_font.ttf'
stamp_text_font_path = 'content/stamp_text_font.ttf'
template_path = 'others/certificate.png'

data = pd.read_csv(data_path)
today = date.today()
validity = "<Certificate Expiration Date>"  # "{:02}/{}/{}".format(int(today.strftime("%d")) + 1, today.strftime("%m"), int(today.strftime("%y")) + 1)

for i in range(len(data)):

    if data["Issue Status"][i] != "No":

        continue

    else:

        img = cv2.imread(template_path)
        name = data['Name'][i]
        name_font = ImageFont.truetype(name_font_path, 140)
        name_size = name_font.getsize(name)

        if name_size[0] <= 1500:

            x = int((img.shape[1] - name_size[0]) / 2)
            y = int((img.shape[0] - name_size[1]) / 2 - 93)
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # change colour space of image array
            pil_img = Image.fromarray(rgb)  # change array to pillow image
            img_draw = ImageDraw.Draw(pil_img)
            img_draw.text((x, y), text=name, font=name_font, fill=(94, 52, 139, 0))  # add text
            bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)  # convert pillow image to array & change colour space

        else:

            df = pd.DataFrame({'Name': [name]})
            df.to_csv('content/long_name_list.csv', mode='a', index=False, header=False)
            continue

        mem_no = data['Membership No.'][i]
        stamp_text = 'Mem. No.: {:04}\nValid till {}'.format(mem_no, validity)
        stamp_text_font = ImageFont.truetype(stamp_text_font_path, 25)
        stamp_text_size = stamp_text_font.getsize(stamp_text)

        x = int((img.shape[1] - stamp_text_size[1]) / 2 - 105)
        y = int((img.shape[0] - stamp_text_size[1]) / 2 + 298)
        new_canvas = Image.new('L', (225, 60), color=None)
        img_draw_new = ImageDraw.Draw(new_canvas)
        img_draw_new.multiline_text((0, 0), text=stamp_text, font=stamp_text_font, fill=255, align="center")
        rot = new_canvas.rotate(32, expand=1)
        pil_img.paste(ImageOps.colorize(rot, (94, 52, 139), (94, 52, 139)), (x, y), rot)

        pil_img.save('certificates/Certificate_{}.pdf'.format(mem_no))
        print("Certificate_{}.pdf generated!".format(mem_no))
        
        if __name__ == '__main__':
              main()
