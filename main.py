import queue
import requests
import time
import threading
import os

AGENT = input('Enter your user-agent: ')
TARGET = input("Enter your target's URL: ")
if TARGET.endswith('/'):
    TARGET = TARGET[:-1]
if not TARGET.startswith('http'):
    print('Please include the https:// in the URL and run this file again.')
    exit()
THREADS = 100
WORDLIST = 'extensions.txt'


def setup():
    if not os.path.exists('Output'):
        os.mkdir('Output')
    for file in ['found.txt', 'forbidden.txt', 'notfound.txt', 'unknown.txt']:
        if not os.path.exists(f'Output/{file}'):
            with open(f'Output/{file}', 'w') as f:
                f.close()

def record(record_type: str, text: str):
    """
    record_type: found / forbidden / notfound
    """
    path = 'Output/' + record_type + '.txt'
    with open(path, 'a') as f:
        f.write(text + '\n')
        f.close()


def get_words() -> queue.Queue:
    words = queue.Queue()
    with open('extensions.txt') as f:
        raw_words = f.read()
    for word in raw_words.split():
        if '.' in word: # file 
            words.put(f'{TARGET}/{word}')
        else: # folder dir
            words.put(f'{TARGET}/{word}/')
    return words




def bruter(words: queue.Queue):
    headers = {'user-agent' : AGENT}
    while not words.empty():
        url = words.get()
        time.sleep(2)
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            continue

        if r.status_code == 200:
            print(f'[+] Found: {r.status_code} : {url}')
            record('found', url)
        elif r.status_code == 404:
            print(f'[-] Not found: {url} {words.qsize()}')
            record('notfound', url)
        elif r.status_code == 403:
            print(f'[+] Found, but forbidden: {url} (403 status code)')
            record('forbidden', url)
        elif r.status_code == 429:
            print('Too much traffic, pausing for 10s.')
            time.sleep(10)
        else:
            print(f'[?] {r.status_code} => {url}')
            record('unknown', f'{url} : {r.status_code}')

if __name__ == '__main__':
    print('Setting up logging files and fetching wordlist.')
    setup()
    words = get_words()
    input('Press return to continue.')
    for _ in range(THREADS):
        t = threading.Thread(target=bruter, args=(words, ))
        t.start()

