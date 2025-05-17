import os
import time
import requests
import sys, getopt
from django.conf import settings


def send_request(token, url):
    try:
        subdir_raw = getattr(settings, 'HOST_SUBDIRECTORY', '').strip('/')
        subdir = f'/{subdir_raw}' if subdir_raw else ''

        response = requests.get(url + subdir + '/cron/ping/', headers={'Authorization': f'Token {token}'}, timeout=5)
    except Exception as e:
        print(e)
        return
         
    if response.status_code != 200:
        print(response.status_code, response.content)


def main(argv):
    token = '' #nosec
    url = ''
    try:
        opts, args = getopt.getopt(argv,"h:",["token=", "url=",])
    except getopt.GetoptError:
        print ('python3 cron.py --token <token> --url <url>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('python3 cron.py --token <token> --url <url>')
            sys.exit()
        elif opt in ("--token",):
            token = arg
        elif opt in ("--url",):
            url = arg

    while True:
        send_request(token, url)
        time.sleep(10)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psono.settings")
    main(sys.argv[1:])
