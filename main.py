import tls_client 
import random
import time
import re
import toml
import ctypes
import threading
import string

from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from logmagix import Logger, Home

with open('input/config.toml') as f:
    config = toml.load(f)

DEBUG = config['dev'].get('Debug', False)
log = Logger()

def debug(func_or_message, *args, **kwargs) -> callable:
    if callable(func_or_message):
        @wraps(func_or_message)
        def wrapper(*args, **kwargs):
            result = func_or_message(*args, **kwargs)
            if DEBUG:
                log.debug(f"{func_or_message.__name__} returned: {result}")
            return result
        return wrapper
    else:
        if DEBUG:
            log.debug(f"Debug: {func_or_message}")

def debug_response(response) -> None:
    debug(response.headers)
    debug(response.text)
    debug(response.status_code)

class Miscellaneous:
    @debug
    def get_proxies(self) -> dict:
        try:
            if config['dev'].get('Proxyless', False):
                return None
                
            with open('input/proxies.txt') as f:
                proxies = [line.strip() for line in f if line.strip()]
                if not proxies:
                    log.warning("No proxies available. Running in proxyless mode.")
                    return None
                
                proxy_choice = random.choice(proxies)
                proxy_dict = {
                    "http": f"http://{proxy_choice}",
                    "https": f"http://{proxy_choice}"
                }
                log.debug(f"Using proxy: {proxy_choice}")
                return proxy_dict
        except FileNotFoundError:
            log.failure("Proxy file not found. Running in proxyless mode.")
            return None

    @debug 
    def generate_password(self):
        password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?/", k=16))
        return password
    
    @debug 
    def generate_username(self):
        return ''.join(random.choices(string.ascii_lowercase, k=16))
    
    @debug 
    def generate_email(self, domain: str = "bune.pw"):
        username = f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=20))}"
        email = f"{username}@{domain}"
        return email
    
    @debug 
    def randomize_user_agent(self) -> str:
        platforms = [
            "Windows NT 10.0; Win64; x64",
            "Windows NT 10.0; WOW64",
            "Macintosh; Intel Mac OS X 10_15_7",
            "Macintosh; Intel Mac OS X 11_2_3",
            "X11; Linux x86_64",
            "X11; Linux i686",
            "X11; Ubuntu; Linux x86_64",
        ]
        
        browsers = [
            ("Chrome", f"{random.randint(90, 140)}.0.{random.randint(1000, 4999)}.0"),
            ("Firefox", f"{random.randint(80, 115)}.0"),
            ("Safari", f"{random.randint(13, 16)}.{random.randint(0, 3)}"),
            ("Edge", f"{random.randint(90, 140)}.0.{random.randint(1000, 4999)}.0"),
        ]
        
        webkit_version = f"{random.randint(500, 600)}.{random.randint(0, 99)}"
        platform = random.choice(platforms)
        browser_name, browser_version = random.choice(browsers)
        
        if browser_name == "Safari":
            user_agent = (
                f"Mozilla/5.0 ({platform}) AppleWebKit/{webkit_version} (KHTML, like Gecko) "
                f"Version/{browser_version} Safari/{webkit_version}"
            )
        elif browser_name == "Firefox":
            user_agent = f"Mozilla/5.0 ({platform}; rv:{browser_version}) Gecko/20100101 Firefox/{browser_version}"
        else:
            user_agent = (
                f"Mozilla/5.0 ({platform}) AppleWebKit/{webkit_version} (KHTML, like Gecko) "
                f"{browser_name}/{browser_version} Safari/{webkit_version}"
            )
        
        return user_agent

    class Title:
        def __init__(self) -> None:
            self.running = False

        def start_title_updates(self, total, start_time) -> None:
            self.running = True
            def updater():
                while self.running:
                    self.update_title(total, start_time)
                    time.sleep(0.5)
            threading.Thread(target=updater, daemon=True).start()

        def stop_title_updates(self) -> None:
            self.running = False

        def update_title(self, total, start_time) -> None:
            try:
                elapsed_time = round(time.time() - start_time, 2)
                title = f'discord.cyberious.xyz | Total: {total} | Time Elapsed: {elapsed_time}s'

                sanitized_title = ''.join(c if c.isprintable() else '?' for c in title)
                ctypes.windll.kernel32.SetConsoleTitleW(sanitized_title)
            except Exception as e:
                log.debug(f"Failed to update console title: {e}")

class AccountCreator:
    def __init__(self, proxies: dict = None) -> None:
        self.session = tls_client.Session("chrome_131", random_tls_extension_order=True)
        self.session.headers = {
            'accept': 'application/json, application/vnd.api+json',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'connection': 'keep-alive',
            'content-type': 'application/json',
            'host': 'padlet.com',
            'origin': 'https://padlet.com',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'same-origin',
            'sec-fetch-site': 'same-origin',
            'user-agent': Miscellaneous().randomize_user_agent(),
    }
        self.session.proxies = proxies

    @debug
    def send_email(self, email: str) -> bool:
        response = self.session.get('https://padlet.com/api/auth/signup/check_email', params={'email': email})
        
        debug_response(response)
        
        if response.status_code == 200 and response.json()["data"]["attributes"]["emailVerificationRequired"]:
               return True
        else:
            log.failure(f"Failed to send email: {response.text}, {response.status_code}")
            
        return False

    def get_csfr(self) -> bool:
        original_headers = self.session.headers
        self.session.headers = {}
        
        try:
            response = self.session.get('https://padlet.com/auth/signup')
            
            debug_response(response)
            
            if response.status_code == 200:
                csrf_pattern = r'<meta name="csrf-token" content="([^"]+)"'
                csrf_token = re.search(csrf_pattern, response.text).group(1)
                
                self.session.headers = original_headers
                self.session.headers.update({'x-csrf-token': csrf_token})
                return True
            else:
                log.failure(f"Failed to get CSRF token: {response.text}, {response.status_code}")
                
            return False
        finally:
            self.session.headers = original_headers
    
    def verify_email(self, email: str, code: str):
        self.get_csfr()

        response = self.session.post('https://padlet.com/api/5/auth/email/verify', json={
            'email_address': email,
            'verification_code': code,
            'purpose': 'signup',
        })
        
        debug_response(response)
        
        if response.status_code == 200:
            return True
        else:
            log.failure(f"Failed to verify email: {response.text}, {response.status_code}")
        
        return False
    
    def singup(self, email: str, password: str):
        response = self.session.post('https://padlet.com/api/auth/signup/users', json={
            'data': {
                'type': 'User',
                'attributes': {
                    'email': email,
                    'password': password,
                    'role': '',
                    'inviteLinkCode': '',
                    'codeChallenge': None,
                    'codeChallengeMethod': None,
                    'state': None,
                    'redirectUri': None,
                    'clientId': None,
                },
            },
        })
        
        debug_response(response)
        
        if response.status_code == 200:
            return True
        else:
            log.failure(f"Failed to signup: {response.text}, {response.status_code}")
        
        return False

class EmailHandler:
    def __init__(self, proxy_dict: dict = None) -> None:
        self.session = tls_client.Session(random_tls_extension_order=True)
        self.session.proxies = proxy_dict

    @debug
    def check_mailbox(self, email: str, max_retries: int = 5) -> list | None:
        debug(f"Checking mailbox for {email}")
        
        for attempt in range(max_retries):
            try:
                json_data = {
                    'email': email,
                    'take': 10,
                    'skip': 0,
                }
                response = self.session.post(f'https://bune.pw/api/inbox', json=json_data)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    log.failure(f"Failed to check mailbox: {response.text}, {response.status_code}")
                    debug(response.json(), response.status_code)
                    break
            except Exception as e:
                log.failure(f"Error checking mailbox: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                break
        return None

    @debug
    def fetch_message(self, email: str, id: int, max_retries: int = 5) -> dict | None:
        debug(f"Fetching mailbox message for {email}")
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(f'https://bune.pw/api/inbox/message/{id}')
                
                if response.status_code == 200:
                    return response.json()
                else:
                    log.failure(f"Failed to fetch message: {response.text}, {response.status_code}")
                    break
            except Exception as e:
                log.failure(f"Error fetching message: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                break
        return None

    @debug
    def get_mail_id(self, email: str) -> str | None:
        attempt = 0
        debug(f"Getting verification message id for {email}")
        while attempt < 10: 
            messages = self.check_mailbox(email)
            if messages and messages.get('messages'):
                for message in messages['messages']:
                    subject = message.get("subject", "")
                    if 'code' in subject:
                        debug(message)
                        return message.get("id")
            attempt += 1
            time.sleep(1.5)
        debug(f"No verification message found after {attempt} attempts")
        return None 

    @debug
    def get_verification_code(self, email: str, max_attempts: int = 10) -> str | None:
        debug(f"Getting verification code for {email}")
        attempts = 0
        while attempts < max_attempts:
            try:
                messages = self.check_mailbox(email)
                if messages and messages.get('messages'):
                    for message in messages['messages']:
                        subject = message.get("subject", "")
                        if 'code' in subject:
                            code_match = re.search(r'(?:est|is) (\d+)', subject)
                            if code_match:
                                return code_match.group(1)
                            debug("No verification code found in subject")
                else:
                    debug("No messages found")
                
                attempts += 1
                if attempts < max_attempts:
                    time.sleep(1.5)
                    
            except Exception as e:
                log.failure(f"Error getting verification code: {str(e)}")
                attempts += 1
                if attempts < max_attempts:
                    time.sleep(2)
                    
        log.failure(f"Failed to get verification code after {max_attempts} attempts")
        return None

def create_account() -> bool:
    try:
        account_start_time = time.time()

        Misc = Miscellaneous()
        proxies = Misc.get_proxies()
        Email_Handler = EmailHandler(proxies)
        Account_Generator = AccountCreator(proxies)
        
        email = Misc.generate_email()
        username = Misc.generate_username()
        password = config["data"].get("password") or Misc.generate_password()

        log.info(f"Starting a new account creation process for {email[:8]}...")
    
        if Account_Generator.send_email(email):
           log.info("OTP sent successfully. Retrieving verification code...")
           code = Email_Handler.get_verification_code(email)
           log.info(f"Got code: {code}. Verifying email...")
           if Account_Generator.verify_email(email, code):
               log.info(f"Email successfully verified. Signing up...")
               if Account_Generator.singup(email, password):
                    with open("output/accounts.txt", "a") as f:
                        f.write(f"{email}:{password}\n")
                            
                    log.message("Padlet", f"Account created successfully: {email[:8]}... | {password[:8]}... | {username[:6]}... ", account_start_time, time.time())
                    return True
               
        return False
    except Exception as e:
        log.failure(f"Error during account creation process: {e}")
        return False


def main() -> None:
    try:
        start_time = time.time()
        
        # Initialize basic classes
        Misc = Miscellaneous()
        Banner = Home("Padlet Generator", align="center", credits="discord.cyberious.xyz")
        
        # Display Banner
        Banner.display()

        total = 0
        thread_count = config['dev'].get('Threads', 1)

        # Start updating the title
        title_updater = Misc.Title()
        title_updater.start_title_updates(total, start_time)
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            while True:
                futures = [
                    executor.submit(create_account)
                    for _ in range(thread_count)
                ]

                for future in as_completed(futures):
                    try:
                        if future.result():
                            total += 1
                    except Exception as e:
                        log.failure(f"Thread error: {e}")

    except KeyboardInterrupt:
        log.info("Process interrupted by user. Exiting...")
    except Exception as e:
        log.failure(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()