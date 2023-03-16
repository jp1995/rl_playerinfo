from selenium import webdriver
from time import sleep


def webdriver_conf(url):
    options = webdriver.ChromeOptions()
    options.add_argument("javascript.enabled")
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("--enable-javascript")
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
    #driver.implicitly_wait(30)
    page = driver.execute_script('return document.body.innerHTML')
    return page
