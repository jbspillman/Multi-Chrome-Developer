import time
import os
import socket
from playwright.sync_api import sync_playwright
from subprocess import Popen
DETACHED_PROCESS = 0x00000008

accounts = [
    {
        "username": "account1@gmail.com",
        "password": "password1"
    },
    {
        "username": "account2@gmail.com",
        "password": "password2"
    }
]


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def launch_chrome_instances():

    user_profiles = os.path.join("user_profiles")
    os.makedirs(user_profiles, exist_ok=True)

    exe_counter = 0
    chrome_port = 9000
    for account in accounts:
        exe_counter += 1
        chrome_port += 1
        act_name = account["username"]
        act_short = act_name.split("@")[0]
        act_pass = account["password"]
        pass_hide = len(act_pass) * "*"

        print()
        print("chrome_port:".ljust(30), chrome_port)
        print("act_name:".ljust(30), act_name)
        print("act_pass:".ljust(30), pass_hide)

        account_folder = os.path.join(user_profiles, act_short, "user")
        os.makedirs(account_folder, exist_ok=True)
        chrome_user_dir = os.path.abspath(account_folder)
        print("chrome_user_dir:".ljust(30), chrome_user_dir)

        chrome_executable = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        chrome_debugging = " --remote-debugging-port="
        chrome_extra_args = " --safe-plugins --incognito --new-window www.linkedin.com/login"
        chrome_user_dir = ' --user-data-dir="' + chrome_user_dir + '"'
        chrome_cmd = chrome_executable + chrome_debugging + str(chrome_port) + chrome_extra_args + chrome_user_dir

        print("chrome_cmd:".ljust(30), chrome_cmd)
        is_open = is_port_in_use(chrome_port)
        if not is_open:
            chrome_open = Popen(
                chrome_cmd, shell=False, stdin=None, stdout=None, stderr=None,
                close_fds=True, creationflags=DETACHED_PROCESS,
            )
            time.sleep(3)
            is_open = is_port_in_use(chrome_port)
        print("chrome_open:".ljust(30), is_open)

        """ Assume if the browser is open on the port, we have already launched and logged in. """
        if is_open:
            local_url = "http://localhost:" + str(chrome_port)
            with (sync_playwright() as p):
                try:
                    browser = p.chromium.connect_over_cdp(local_url, timeout=7500)
                except Exception as e:
                    print(e)
                    continue

                default_context = browser.contexts[0]
                page = default_context.pages[0]
                if "feed" in str(page.title()).lower() or "feed" in str(page.url).lower():
                    print("Account:".ljust(30), act_name + " Already logged in.")
                else:
                    login_url = "https://www.linkedin.com/login/"
                    page.goto(login_url)
                    page.get_by_label('Email or Phone').fill(act_name)
                    page.get_by_label('Password').fill(act_pass)
                    page.get_by_label('Sign in', exact=True).click()
                browser.close()


def main():
    if len(accounts) == 0:
        print("No Accounts Provided!")
        exit(1)
    else:
        launch_chrome_instances()


if __name__ == "__main__":
    main()
