from bs4 import BeautifulSoup
import requests
import copy
import json
import re
import time



def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def stringify(list):
    ret_string = ""
    for item in list:
        ret_string += str(item)
    return ret_string

url = 'https://tvtropes.org/pmwiki/pmwiki.php/Main/Characters'
response = requests.get(url, timeout=100, verify=True)
content = BeautifulSoup(response.content, "html.parser")
lists = content.find_all('li', class_='plus')
links = content.select("div#main-article > ul > li > a", class_="twikilink")

my_set = set([])
objects = []
queue = []
for link in links:
    if link.has_attr('href'):
        new_url = link['href']
        queue.append(new_url)
while len(queue) != 0:
    copy_queue = copy.copy(queue)
    for url in queue:
        if url not in my_set:
            my_set.add(url)
            real_url = 'https://tvtropes.org' + url
            try:
                response = requests.get(real_url, timeout=100, verify=True)
                content = BeautifulSoup(response.content, "html.parser")
                links = content.select("div#main-article > ul > li > a", class_="twikilink")
                examples = stringify(content.select("div#main-article > div#folder"))
                description = stringify(content.select("div#main-article > p"))
                arr = url.split("/")
                name = arr[-1]
                object = {"name": name, "description": cleanhtml(description), "examples": examples}
                objects.append(object)
            except requests.exceptions.RequestException as e:
                print('exception caught', e)
                time.sleep(1)
            for nl in links:
                if nl.has_attr('href'):
                    if nl['href'] not in my_set:
                        my_set.add(nl['href'])
                        real_url = 'https://tvtropes.org' + nl['href']
                        try:
                            response = requests.get(real_url, timeout=100, verify=True)
                            content = BeautifulSoup(response.content, "html.parser")
                            examples = stringify(content.select("div#main-article > div#folder"))
                            description = stringify(content.select("div#main-article > p"))
                            arr = url.split("/")
                            name = arr[-1]
                            object = {"name": name, "description": cleanhtml(description), "examples": examples}
                            objects.append(object)
                            copy_queue.append(nl['href'])
                        except requests.exceptions.RequestException as e:
                            print('exception caught', e)
                            time.sleep(1)
        copy_queue.remove(url)
    queue = copy_queue

test_url = 'https://tvtropes.org/pmwiki/pmwiki.php/Main/ActionFashionista'
response = requests.get(test_url, timeout=100, verify=True)
content = BeautifulSoup(response.content, "html.parser")
examples = stringify(content.select("div#main-article > div#folder"))
print("my_set length: "+str(len(my_set)))
print(my_set)
print("objects length: " + str(len(objects)))
print(objects)
print(objects)
