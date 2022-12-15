from logging import Logger
from urllib.request import urlopen, Request
from urllib.parse import urljoin
import io
from bs4 import BeautifulSoup
import uuid
import threading
import itertools
import time
import requests
import json
import os
import re 

api = 'http://0.0.0.0:80'

is_loading = True
is_error = False

root = 'sites'

def __writePage(file_name: str, content: str):
    global root
    if not os.path.exists(root):
        os.mkdir(root)
    with io.open(f'{root}/{file_name}.html', 'w', encoding='utf-8') as f:
        f.write(content)

def writePage(file_name: str, content: str, exception_logger: Logger):
    is_success = True
    try:
        __writePage(file_name, content)
    except Exception as ex:
        exception_logger.exception(ex)
        is_success = False
    return is_success

def loader():
    global is_loading
    global is_error
    for c in itertools.cycle(['⢿', '⣻', '⣽', '⣾', '⣷', '⣯', '⣟', '⡿']):
        if is_loading == False:
            break
        print(f'\rScrapping the page... {c}', flush=True, end='')
        time.sleep(0.1)
    if (is_error):
        return
    print(f'\rDone!                       ')

def scrape_process(url: str):
    global is_loading
    global is_error
    try:
        if (url == None or url.strip() == ''):
            raise Exception(f'unknown url type: {url}')

        loader_thread = threading.Thread(target=loader)
        loader_thread.start()
        req = Request(url, headers={'User-Agent' : 'Magic Browser'}) 
        soup = BeautifulSoup(urlopen(req), 'html.parser')

        for link in soup('script', attrs={'src': re.compile(".*")}):
            script_path = link.get('src')
            if (str(script_path).startswith('http') == False):
                script_path = urljoin(url, script_path)
            f = urlopen(script_path)

            encoding = 'utf-8' if f.headers.get_content_charset() == None else f.headers.get_content_charset()
            link_url_res = f.read().decode(encoding)
            
            link.append(link_url_res)
            del link['src']

        return (True, soup)
    except Exception as ex:
        is_error = True
        is_loading = False  
        print(f'\r{ex}'.ljust(50))
        return (False, None)

def __scrape(url: str):
    title = ''
    is_success, soup = scrape_process(url)

    if (is_success == False):
        return (None, None)

    if (soup != None and soup.title != None):
        title = soup.title.get_text()
    
    if (title == None or title.strip() == ''):
        title = str(uuid.uuid1())
    else:
        title = ''.join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()

    content = soup.decode_contents()
    return (title, content)

def scrape(url: str):
    global is_loading
    scrape_content = __scrape(url)
    time.sleep(0.2)
    is_loading = False
    time.sleep(0.070)
    return scrape_content

def automatic_scrape():
    global is_loading
    global is_error
    while (True):
        url = input('> ')
        print(url)
        is_loading = True
        is_error = False

        if (url != None and url.strip().lower() == 'stop'):
            break
            
        title, content = __scrape(url)

        if (title == None or content == None):
            continue

        __writePage(title, content)
        
        # res = requests.post(api + '/save_scraped_content', json = {
        #     "content": content,
        #     "fileName": title
        # })

        # data = json.loads(res.text)
        # if (data['status'] != 'success'):
        #     print('\nError while saving the page on the server')
        
        time.sleep(0.2)
        is_loading = False
        time.sleep(0.070)

if __name__ == "__main__":
    automatic_scrape()