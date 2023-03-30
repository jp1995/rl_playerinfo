import signal
from selenium import webdriver
from time import sleep
import winreg


def chromedriver_conf(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(chrome_options=options, executable_path=r'webdriver/chromedriver.exe')
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'})
    driver.get(url)
    sleep(2)
    page = driver.execute_script('return document.body.innerHTML')
    driver.quit()
    return page


def geckodriver_conf(url):

    if is_firefox_installed():
        firefox_bin = get_firefox_path()
    else:
        'Something has gone pretty wrong. Sorry mate.'
        quit(signal.SIGTERM)

    options = webdriver.FirefoxOptions()
    options.headless = True
    options.binary_location = firefox_bin

    profile = webdriver.FirefoxProfile()
    profile.set_preference("javascript.enabled", False)
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference("dom.webnotifications.enabled", False)
    profile.set_preference("media.navigator.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.set_preference('general.useragent.override',
                           'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36')
    profile.update_preferences()
    driver = webdriver.Firefox(firefox_profile=profile, options=options, executable_path=r'webdriver/geckodriver.exe')
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get(url)
    sleep(2)
    page = driver.execute_script('return document.body.innerHTML')
    driver.quit()
    return page


def is_chrome_installed():
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            return True
    except WindowsError:
        return False


def is_firefox_installed():
    reg_path = r'SOFTWARE\Mozilla\Mozilla Firefox'
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            return True
    except WindowsError:
        return False


def get_firefox_path():
    reg_path = r'SOFTWARE\Mozilla\Mozilla Firefox'
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            value, _ = winreg.QueryValueEx(key, 'CurrentVersion')
            sub_path = r'{}\bin\firefox.exe'.format(value)
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_path) as sub_key:
                firefox_path, _ = winreg.QueryValueEx(sub_key, '')
                return firefox_path
    except WindowsError:
        return None


def choosedriver():
    if is_chrome_installed():
        return 'Chrome'
    elif is_firefox_installed():
        return 'Firefox'
    else:
        return None
