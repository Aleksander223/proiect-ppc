import random
from concurrent.futures import ThreadPoolExecutor
import time
import requests


def getUrl(urlDict):
    return requests.get(urlDict['url'], params=urlDict['params'])


if __name__ == '__main__':
    startTime = time.time()
    urlList = []
    for _ in range(100):
        urlList.append({'url': 'http://127.0.0.1:8080/api/predict',
                        'params': {'error': int(random.uniform(3, 8)),
                                   'latitude': '{:.2f}'.format(random.uniform(40, 50)),
                                   'longitude': '{:.2f}'.format(random.uniform(20, 30)),}})
    succ = 0
    fail = 0
    with ThreadPoolExecutor(max_workers=64) as pool:
        for response in pool.map(getUrl, urlList):
            if response.status_code == 200:
                print(response.json())
                succ += 1
            else:
                print(f'Error - {response.status_code}')
                fail += 1
            print(response.elapsed)
    print(time.time() - startTime)
    print(succ, fail)
