import os
import logging
import time
import argparse
from typing import Dict, Tuple

import requests
from bs4 import BeautifulSoup
import urllib3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

urllib3.disable_warnings()

# Константи
SHIB_LOGIN_URL = 'https://shibboleth.im.jku.at'
MOODLE_HOME_URL = 'https://moodle.jku.at/my/'
MOODLE_LOGIN_URL = 'https://moodle.jku.at/login/index.php'
MOODLE_LOGIN_BY_SHIB_URL = "https://moodle.jku.at/auth/shibboleth/index.php"
MOODLE_PROFILE_URL = 'https://moodle.jku.at/user/profile.php'

HEADERS_FOR_AUTH = {
    'accept': 'text/html,application/xhtml+xml,application/xml',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

HEADERS_FOR_MOODLE = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
}


def request_get(session: requests.Session, url: str, headers: Dict = None, cookies: Dict = None,
                allow_redirects: bool = False) -> requests.Response:
    headers = headers or HEADERS_FOR_AUTH
    try:
        return session.get(url, headers=headers, cookies=cookies, verify=False, allow_redirects=allow_redirects)
    except requests.RequestException as e:
        logger.error(f"Error during GET request to {url}: {e}")
        raise


def request_post(session: requests.Session, url: str, data: Dict, headers: Dict = None, cookies: Dict = None,
                 allow_redirects: bool = False) -> requests.Response:
    headers = headers or HEADERS_FOR_AUTH
    try:
        return session.post(url, data=data, headers=headers, cookies=cookies, verify=False,
                            allow_redirects=allow_redirects)
    except requests.RequestException as e:
        logger.error(f"Error during POST request to {url}: {e}")
        raise


def create_payload(csrf_token: str, username: str, password: str) -> Dict:
    return {
        'csrf_token': csrf_token,
        'j_username': username,
        'j_password': password,
        "_eventId_proceed": "Login",
    }


def get_jsessionid_for_login(session: requests.Session, username: str, password: str) -> Tuple[Dict, str, Dict, Dict]:
    logger.info("Starting session and getting MoodleSessionjkuSessionCookie")
    moodle_session_response = request_get(session, MOODLE_HOME_URL, headers=HEADERS_FOR_MOODLE, allow_redirects=True)
    moodle_session_cookie = {
        'MoodleSessionjkuSessionCookie': moodle_session_response.cookies['MoodleSessionjkuSessionCookie']}

    request_get(session, MOODLE_LOGIN_URL, cookies=moodle_session_cookie)

    shib_page = request_get(session, MOODLE_LOGIN_BY_SHIB_URL, cookies=moodle_session_cookie)
    soup = BeautifulSoup(shib_page.text, 'lxml')
    token_url_shib = soup.find('a').attrs['href']

    shib_token_page = request_get(session, token_url_shib)
    url_shib_auth = shib_token_page.headers['Location']

    jsessionid_cookie = {'JSESSIONID': shib_token_page.cookies['JSESSIONID']}
    shib_login = request_get(session, url_shib_auth, cookies=jsessionid_cookie)
    soup = BeautifulSoup(shib_login.text, 'lxml')
    redirect_url = soup.find('form', attrs={'name': 'form1'}).attrs['action']
    csrf_token = soup.find('input', attrs={'name': 'csrf_token'}).attrs['value']

    payload = create_payload(csrf_token, username, password)
    return payload, redirect_url, jsessionid_cookie, moodle_session_cookie


def get_tokens_for_sso(session: requests.Session, payload: Dict, redirect_url: str, jsessionid_cookie: Dict,
                       username: str, password: str) -> Tuple[str, str]:
    logger.info("Posting login to Shibboleth")
    response = request_post(session, f'{SHIB_LOGIN_URL}{redirect_url}', data=payload, cookies=jsessionid_cookie,
                            allow_redirects=True)

    soup = BeautifulSoup(response.text, 'lxml')
    login_url_params = soup.find('form', attrs={'id': 'loginform'}).attrs['action']
    csrf_token = soup.find('input', attrs={'name': 'csrf_token'}).attrs['value']

    payload = create_payload(csrf_token, username, password)
    response = request_post(session, f'{SHIB_LOGIN_URL}{login_url_params}', data=payload, cookies=jsessionid_cookie)

    soup = BeautifulSoup(response.text, 'lxml')
    relay_state = soup.find('input', attrs={'name': 'RelayState'}).attrs['value']
    saml_response = soup.find('input', attrs={'name': 'SAMLResponse'}).attrs['value']
    return relay_state, saml_response


def set_shibsession_for_moodle(session: requests.Session, relay_state: str, saml_response: str,
                               moodle_session_cookie: Dict):
    logger.info("Setting shibsession for Moodle")
    response = request_post(session, 'https://moodle.jku.at/Shibboleth.sso/SAML2/POST',
                            data={"RelayState": relay_state, "SAMLResponse": saml_response})
    headers = response.headers
    shibsession_header = headers.get('Set-Cookie', '')
    if '_shibsession_' in shibsession_header:
        shibsession_value = shibsession_header.split('_shibsession_')[1].split('=')[1].split(';')[0]
        shibsession_key = shibsession_header.split('_shibsession_')[1].split('=')[0]
        shibsession_key = f'_shibsession_{shibsession_key}'

        session.cookies.set(shibsession_key, shibsession_value, domain='moodle.jku.at', path='/')

    session.cookies.set('MoodleSessionjkuSessionCookie', moodle_session_cookie["MoodleSessionjkuSessionCookie"],
                        domain='moodle.jku.at', path='/')

    response = request_get(session, MOODLE_LOGIN_BY_SHIB_URL, headers=HEADERS_FOR_MOODLE)
    new_moodle_ses_cookie = response.headers["Set-Cookie"].split('=')[1].split(';')[0]
    session.cookies.set('MoodleSessionjkuSessionCookie', new_moodle_ses_cookie, domain='moodle.jku.at', path='/')


def main(username: str, password: str):
    start_time = time.time()
    with requests.Session() as session:
        try:
            payload, redirect_url, jsessionid_cookie, moodle_session_cookie = get_jsessionid_for_login(session,
                                                                                                       username,
                                                                                                       password)
            relay_state, saml_response = get_tokens_for_sso(session, payload, redirect_url, jsessionid_cookie, username,
                                                            password)
            set_shibsession_for_moodle(session, relay_state, saml_response, moodle_session_cookie)

            response = request_get(session, MOODLE_PROFILE_URL, headers=HEADERS_FOR_MOODLE)
            soup = BeautifulSoup(response.text, 'lxml')
            logger.info(f"Logged in as: {soup.find('title').text.split(':')[0]}")
            logger.info(f"Login process took {time.time() - start_time:.2f} seconds")

            start_time = time.time()
            response = request_get(session, "https://moodle.jku.at/course/view.php?id=23653",
                                   headers=HEADERS_FOR_MOODLE)
            soup = BeautifulSoup(response.text, 'lxml')
            logger.info(f"Course title: {soup.find('h1', attrs={'class': 'h2'}).text}")
            logger.info(f"Course page loaded in {time.time() - start_time:.2f} seconds")
        except Exception as e:
            logger.error(f"An error occurred: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Login to Moodle')
    parser.add_argument('--username', help='Moodle username')
    parser.add_argument('--password', help='Moodle password')
    args = parser.parse_args()

    username = args.username or os.getenv('MOODLE_USERNAME')
    password = args.password or os.getenv('MOODLE_PASSWORD')

    if not username or not password:
        logger.error(
            "Username and password must be provided either as command-line arguments or environment variables.")
    else:
        main(username, password)