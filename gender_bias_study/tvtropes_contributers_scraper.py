from bs4 import BeautifulSoup
import requests
from requests import Session
import csv
import time

payload = {
    "action"  : "login",
	"username": "username",
	"password": "password"
}
session = requests.Session()
response = session.post("https://tvtropes.org/pmwiki/login_prompt.php", data=payload)
response = session.get('https://tvtropes.org/pmwiki/contributor_list.php')
url = 'https://tvtropes.org/pmwiki/contributor_list.php'
website = 'https://tvtropes.org'
content = BeautifulSoup(response.content, "html.parser")
# print(content.prettify())
all_links = []
contributors = content.find_all(attrs={"class": "twikilink"})
for i in range(len(contributors)):
    contributors[i] = contributors[i]['href']

print("done scraping contributor links")
print(len(contributors))

output_file = open("tvtropes_contributors.csv", 'a+', encoding='utf8', newline='')
fc = csv.DictWriter(output_file, fieldnames=["name", "troper_content"])
for i in range(14613,len(contributors)):
    contributor = {}
    contributor_response = session.get(contributors[i], timeout=(200, 200))
    contributor_content = BeautifulSoup(contributor_response.content, "html.parser")

    # Name
    name = contributor_content.find(attrs={"class": "entry-title"})
    name = name.get_text(strip=True)[9:]
    contributor['name'] = name

    # Troper content
    troper_content = contributor_content.find(attrs={"id" : "main-article"}).get_text(strip=True)
    troper_content = (troper_content[:2000] + '...') if len(troper_content) > 2000 else troper_content
    troper_content = troper_content.replace(',', '')
    if (troper_content == "\n\n"):
        troper_content = ""
    elif (troper_content == None):
        troper_content = ""
    contributor["troper_content"] = troper_content
    fc.writerow(contributor)
    print(i)
    time.sleep(0.5)

output_file.close()


print("done")