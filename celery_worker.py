"""prefork worker doesn't work in windows , so we have to use (-P solo) or (-P eventlet)\
as following:
celery -A celery_worker worker --loglevel=INFO -P eventlet
"""
import os
import time
from celery import Celery
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import redis
# import pandas as pd
redis_client = redis.Redis(host='localhost', port=6379, db=0)

load_dotenv(dotenv_path=".env")

import csv
import random
import glob
import time
import requests
from datetime import datetime
import json
import os
import logging
import sys
from scrapingbee import ScrapingBeeClient

TITLES = ["Instagram ID",
          "Username",
          "Full name",
          "Profile link",
          "Avatar pic",
          "Followed by viewer",
          "Is verified",
          "Followers count",
          "Following count",
          "Biography",
          "Public email",
          "Posts count",
          "Phone country code",
          "Phone number",
          "City",
          "Address",
          "Is private",
          "Is business",
          "External url"]
valid_names = ['ronaldo_champ_12', 'OliverPeyton2ReubenMohamed9',
           'KingstonMaximo1RussellVicente3', 'KarsonAlejandro1OmarEden5', 'DrewZayne3KobeGian3',
           'RodneyCrosby1JensenReid5']
API_KEY = '1OIJO2KV8K9MTYZLWMJ5O6U41LSFCQYYWGS7N396IZDS1RLC6U1KDMUN6WJQU7WMQPN4IUP12M3AYQTY'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)


class CSVExporter:

    def __init__(self):
        self.titles = []
        self.initialized = False

    def initialize(self, file_name=f"{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.csv"):
        if not self.initialized:
            with open(file_name, 'w') as file:
                self.writer = csv.writer(file)
                if len(self.titles) > 0:
                    self.writer.writerow(self.titles)
                self.initialized = True
                print("csv initialized")
            return file_name

    def insert_row(self, filename, data):
        if len(data) == len(self.titles):
            print(filename)
            with open(filename, 'a') as file:
                writer = csv.writer(file)
                writer.writerow(data)


class DataFormater:
    def __init__(self):
        self.exporter = CSVExporter()
        self.exporter.titles = TITLES

    def initialize(self, file_name):
        return self.exporter.initialize(file_name=file_name)

    def load_json_file(self, path: str):
        with open(glob.glob(path)[0], 'r') as f:
            data = json.load(f)
            return data

    def export(self, file_name):
        path = "Following-Sync/floraqueen.it"
        celebrity_file_names = glob.glob(path + "/*.json")
        for c_f in celebrity_file_names:
            # celebrity_name = c_f.split('/')[-1][:-5]
            data = self.load_json_file(c_f)
            user = data[0]['data']["user"]
            self.exporter.insert_row(file_name,
                                     [user["id"]
                                         , user["username"]
                                         , user["full_name"]
                                         , "https://www.instagram.com/giusyvitale85/" + user["username"]
                                         , user["profile_pic_url_hd"]
                                         , user["followed_by_viewer"]
                                         , user["is_verified"]
                                         , user["edge_followed_by"]["count"]
                                         , user["edge_follow"]["count"]
                                         , user["biography"]
                                         , user["business_email"]
                                         , user["edge_owner_to_timeline_media"]["count"]
                                         , "country code"
                                         , user['business_phone_number']
                                         , "city"
                                         , user["business_address_json"]
                                         , user["is_private"]
                                         , user["is_business_account"]
                                         , user["external_url"]
                                      ])

from utils.InstagramCli import InstagramCLI
class Insta():
    def __init__(self, username, password):
        self.name = username
        self.api_key = API_KEY
        self.session = requests.Session()
        self.session.cookies.update({
            "csrftoken": "",
            "ds_user_id": "",
            "ig_did": "",
            "ig_nrcb": "",
            "rur": "",
            "sessionid": ""
        })
        self.url = "https://app.scrapingbee.com/api/v1/"
        # self.insta_login(username=username, password=password)

    def sb_post(self, url):
        self.sb_headers = {str("Spb-" + key): value for (key, value) in self.session.headers.items()}
        self.sb_cookies = ';'.join([key + "=" + value for (key, value) in self.session.cookies.get_dict().items()])

        response = self.session.post(
            url='https://app.scrapingbee.com/api/v1/',
            params={
                'api_key': self.api_key,
                'url': url,
                'wait': '100',
                'cookies': self.sb_cookies,
                'forward_headers': 'true',
                'block_resources': 'false',
                'premium_proxy': 'true',
                'country_code': 'us',

            },
            data=self.credentials,
            headers=self.sb_headers
        )
        return response

    def insta_login(self, username, password):
        self.session.headers = {'Referer': 'https://www.instagram.com/',
                                'user-agent': 'Instagram 123.0.0.21.114 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15'}
        base_request = self.session.get('https://www.instagram.com/')
        # if "csrftoken" in base_request.cookies.get_dict():
        self.session.headers.update({'X-CSRFToken': base_request.cookies['csrftoken']})
        self.credentials = {'username': username, 'password': password}
        response = self.sb_post('https://www.instagram.com/accounts/login/ajax/')
        if response.status_code == 200:
            self.sb_headers.update(
                {'Spb-x-ig-app-id': '936619743392459', 'Spb-X-CSRFToken': self.session.cookies.get_dict()['csrftoken'],
                 'Spb-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
            # self.cookies is required to get following names list.
            self.cookies = response.cookies  # will check it later.
            response = response.json()
            if "authenticated" in response and response['authenticated']:
                print("Login Successful for user: " + username)
                return True
            else:
                print("Login Failed for user: " + username)
                return False
        else:
            if "reason" in response.json():
                raise Exception(response.json()['reason'])
            if "two_factor_required" in response.json():
                # Two factor authentication is enabled for your account. Please disable it for sometime. You can enable it again after finishing scraping. Its not like i can't add input() to accept otp. It's just that taking user otp input while program execution feels different. Eg. I mean if someone includes this library in their code and the program just stops to take input() the whole process will stop. Then there is no point in making an automated library. In future if i feel to add it i will surely add this functionality. But for now its not there.
                raise Exception("Two factor authentication is enabled. Please disable it.")
            else:
                raise Exception("Login Failed")

    def save(self, path: str, file: str, data, plain_text=False):
        path = os.path.join(os.getcwd(), path)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, file), 'w', encoding='utf-8') as f:
            if plain_text:
                f.writelines(data)
            else:
                json.dump(data, f, indent=4)
            f.truncate()
        print(f"SAVED : {path}/{file}")

    def error_smaco(self, e, message):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error(
            "\nError in %s function at line %s.\nError Message - %s\nType - %s\nPlease try again. If issue persists,then open github issue and upload error snapshot - https://github.com/suyashjawale/InstagramCLI/issues""",
            message, exc_tb.tb_lineno, e, exc_type)
        exit()

    def get_info_sb(self, username):
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

        response = self.session.get(
            url='https://app.scrapingbee.com/api/v1/',
            params={
                'api_key': self.api_key,
                'url': url,
                'wait': '100',
                'cookies': self.sb_cookies,
                'forward_headers': 'true',
                'block_resources': 'false',
                'premium_proxy': 'true',
                'country_code': 'us'
            },
            headers=self.sb_headers
        )
        return response

    def get_info(self, username=None):
        try:
            res = self.get_info_sb(username)
            if res.status_code == 200:
                return res.json(),True
            else:
                logging.error("User not found")
                return {}, False
        except Exception as e:
            self.error_smaco(e, "__init__")

    def exception_handler(self, request, exception):
        print("Request failed : ", request)

    def get_following(self, username, save=False, cli_context="following"):
        try:
            if username != None:
                user_info, status = self.get_info(username)
                if status:
                    big_list = True
                    users = []
                    res = {"next_max_id": None}
                    user_id = user_info['data']['user']['id']
                    logging.info(f"Fetching {username} {cli_context} data")
                    count = int(user_info['data']['user']['edge_follow']['count'])
                    search_surface = None
                    if cli_context == "followers":
                        search_surface = "follow_list_page"
                    try:
                        self.counter = 0
                        while big_list and self.counter < count:
                            payload = {
                                "count": 12,
                                "max_id": res['next_max_id'],
                                "search_surface": search_surface
                            }
                            self.counter += 12
                            print(self.counter, " Done")
                            time.sleep(1)
                            res = self.session.get(
                                f"https://i.instagram.com/api/v1/friendships/{user_id}/{cli_context}/",
                                cookies=self.cookies, params=payload).json()
                            big_list = res['big_list']
                            users.extend(res['users'])
                    except Exception as e:
                        self.error_smaco(e, "")
                        logging.error(f'Cannot scrape user {cli_context}.')
                    # if save:
                    #     self.make_folder(optimized)
                    #     self.save_json(optimized, data=users)
                    return users
                else:
                    return []
            else:
                logging.error("Please enter valid user.")
                return []
        except Exception as e:
            self.error_smaco(e, f"get_{cli_context}")

    def load_json_file(self, path: str):
        with open(glob.glob(path)[0], 'r') as f:
            data = json.load(f)
            return data


def get_cli():
    cli = random.choice(clis)
    print(f"Using {cli.name} as an Instagram account")
    return cli
# from src.InstagramCli import InstagramCLI
def get_following_cli():
    return InstagramCLI(username="IsaiahKristian6BensonEzra7", password="MyPassword@11")


def export(writer, data,External=False):
    try:
        if data:
            if External:
                if "data" in data.keys() and "user" in data['data'].keys():
                    user = data['data']["user"]
            else:
                if "data" in data[0].keys() and "user" in data[0]['data'].keys():
                    user = data[0]['data']["user"]
            writer.writerow([user["id"]
                                , user["username"]
                                , user["full_name"]
                                , "https://www.instagram.com/" + user["username"]
                                , user["profile_pic_url_hd"]
                                , user["followed_by_viewer"]
                                , user["is_verified"]
                                , user["edge_followed_by"]["count"]
                                , user["edge_follow"]["count"]
                                , user["biography"]
                                , user["business_email"]
                                , user["edge_owner_to_timeline_media"]["count"]
                                , ""
                                , user['business_phone_number']
                                , ""
                                , user["business_address_json"]
                                , user["is_private"]
                                , user["is_business_account"]
                                , user["external_url"]
                             ])
    except Exception as e:
        print(e)
        pass


def scrap_data(influencer_name,cli_,client_name):
    ost = time.time()
    # now we find names of following.
    st = time.time()

    time.sleep(random.randint(1, 5))
    influencer_data = cli_.get_following(username=influencer_name, save=False)
    print('Time to load Following : ', time.time() - st, ' Seconds')
    st = time.time()
    path = f"public/{influencer_name}"
    cli= get_cli()
    cli.save(path=path, file=f"{influencer_name}.json", data=influencer_data)
    following_unames = [followed["username"] for followed in influencer_data]
    following_count = len(following_unames)
    cli.save(path=path, file=f"following_names_{len(following_unames)}.json", data=following_unames)
    print('Time to save in files : ', time.time() - st, ' Seconds')
    print('Over all Time : ', time.time() - ost, ' Seconds')

    # # now we scrap users without async
    ost = time.time()
    with open(f"public/{influencer_name}/" + f"{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.csv", 'a') as file:
        writer = csv.writer(file)
        writer.writerow(TITLES)
        time.sleep(random.randint(1, 3))
        for i, name in enumerate(following_unames):
            print(f"{influencer_name} IS FOLLOWING  : {name} {i + 1} OF {following_count}")
            cli = get_cli()
            celebrity_data ,status= cli.get_info(username=name)
            export(writer, celebrity_data,External=True)
            redis_client.set(name=client_name, value=str(i + 1) + "," + str(following_count))
    print('Over all Time to scrap following : ', time.time() - ost, ' Seconds')


def get_influencers(influencer_names=None,client_name=None):
    print("INFLUENCERS IN WORKER ", influencer_names)
    st = time.time()

    cli_ = get_following_cli()
    for influencer in influencer_names:
        scrap_data(influencer,cli_,client_name)
        print("INFLUENCER GOING TO BE SCRAPPED AFTER 3 MINUTES :  With Agent : ","IsaiahKristian6BensonEzra7")
        time.sleep(180)
    print('SCRAPPER FOLLOWING OF ALL INFLUENCER  IN  : ', time.time() - st, ' Seconds')

def populate_html_file(user_name, influencers):
    base_url = f"{os.environ.get('SSO_BACKEND_URL')}api/v1/image/"
    if not "http" in base_url:
        base_url = "http://" + base_url
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("email.html")
    html_ = template.render(user_name=user_name, influencers=influencers)
    # print(base_url)
    with open('email.html', 'wb') as f:
        f.write(html_.encode())
        # f.truncate()


def wait_until_found_file(file_path):
    while not os.path.exists(file_path):
        print(f"\t{file_path} not found")
        time.sleep(.5)

    if os.path.isfile(file_path):
        print(f"\tSuccess {file_path} found")
        file_ = open(file_path)
        return file_
    else:
        raise ValueError("%s isn't a file!" % file_path)


def send_email(name, recipient, influencers, attachment=None):
    try:
        print("===================================================")
        print("                Email Task Started                 ")
        print("===================================================")

        populate_html_file(name, influencers)
        file_ = wait_until_found_file("email.html")

        mail_content = MIMEText(file_.read(), "html")
        # The mail addresses and password
        # The mail addresses and password
        sender_address = os.environ.get("EMAIL_SENDER")
        sender_pass = os.environ.get("EMAIL_SENDER_PASSWORD")
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = recipient
        message['Subject'] = os.environ.get("EMAIL_SUBJECT")
        # The body and the attachments for the mail
        message.attach(mail_content)
        # attach files if given
        if attachment:


            # read_file = pd.read_csv(attachment)
            # attachment = attachment.replace(".csv", ".xlsx")
            # read_file.to_excel(attachment, index=None, header=True)
            attach_file = open(attachment, 'rb')  # Open the file as binary mode
            payload = MIMEBase('application', 'octate-stream')
            payload.set_payload((attach_file).read())
            encoders.encode_base64(payload)  # encode the attachment
            # add payload header with filename
            payload.add_header('content-disposition', 'attachment', filename=attachment.split("\"")[-1])
            message.attach(payload)
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, recipient, text)
        session.quit()
        print("===================================================")
        print(f"      Success: {recipient}")
        print("===================================================")
        return True
    except Exception as e:
        print(str(e))
        return False


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")


@celery.task(name="email_sender")
def email_sender(name, email, influencers):
    return send_email(name, email, influencers, attachment="public/littlecrumb_.csv")


@celery.task(name="insta_scraper")
def insta_scraper(influencer_names,client_name):
    influencer_names = influencer_names.split(",")


    print("INFLUENCERS IN WORKER START", influencer_names)
    global clis
    clis = []
    for name in valid_names:
        c = Insta(username=name, password="MyPassword@11")
        if c.insta_login(username=name, password="MyPassword@11"):
            clis.append(c)
    return get_influencers(influencer_names,client_name)


if __name__ == '__main__':
    insta_scraper("vogueitalia,valeriepasqualini","tester")
