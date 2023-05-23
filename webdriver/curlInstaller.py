import os
import urllib3
import shutil
import re
import subprocess
import signal
import platform


def is_curl_installed():
    is_installed = False
    try:
        subprocess.check_output(['curl', '--version'])
        is_installed = True
    except OSError:
        pass
    try:
        subprocess.check_output(['webdriver\\Curl\\bin\\curl.exe', '--version'])
        is_installed = True
    except OSError:
        pass

    return is_installed


def install_curl():
    plat = platform.system()
    if plat == 'Linux' or plat == 'Darwin':
        print('The script thinks that you are lacking curl but are on Linux or macOS. '
              'Kind of an awkward situation, either for you or for me, I guess. You need curl. Exiting.')
        quit(signal.SIGTERM)

    print("Curl was first included in Windows 10 version 1803, released April 2018.")
    print('However, Curl does not appear to be installed, attempting install now...')
    url = 'https://curl.se/windows/'
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    page = response.data.decode('utf-8')

    build = re.findall(rf"(?<=<b>Build<\/b>:)\s*(.*?)(?=\s|<br>|$)", page)
    if len(build) > 0:
        build = build[0].strip()

        zipurl = f'https://curl.se/windows/dl-{build}/curl-{build}-win64-mingw.zip'
        zipname = 'curl.zip'

        dlzip = http.request('GET', zipurl)
        with open(zipname, 'wb') as out_file:
            out_file.write(dlzip.data)

        shutil.unpack_archive(zipname)
        shutil.move(os.path.join(f'curl-{build}-win64-mingw'), '.\\webdriver')
        os.remove(zipname)
        shutil.move(f'.\\webdriver\\curl-{build}-win64-mingw', '.\\webdriver\\Curl')
        print('Curl install successful!\n')
    else:
        print('The layout of the curl.se/windows site has likely changed, unable to find latest build version\n'
              'ERROR: Failed to install curl.')
        quit(signal.SIGTERM)
