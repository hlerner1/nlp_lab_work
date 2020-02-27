from bs4 import BeautifulSoup
import requests
import csv

print("test")
books = []
url = 'https://www.goodreads.com/list/show/32774.Most_Interesting_World'
website = 'https://www.goodreads.com'
response = requests.get(url, timeout=10)
content = BeautifulSoup(response.content, "html.parser")
all_links = []
pages = content.find_all(attrs={"class": "next_page"})
# print(content.find_all(attrs={"class": "next_page"}))
def fill_books():
    # the table of books for this page
    table_data = content.find_all("tr")
    for item in table_data:
        book = {}
        book_title = item.find("a", class_= "bookTitle")
        # Had to chop off the ends of the title to remove \n values
        book["title"] = book_title.get_text()[1:-1]
        book_author = item.find("a", class_="authorName")
        book["author"] = book_author.get_text()
        books.append(book)

while (len(content.find_all(attrs={"class": "next_page disabled"})) == 0):
    fill_books()
    pages = content.find_all(attrs={"class": "next_page"})
    link = pages[0]['href']
    print(url)
    url = website + link
    response = requests.get(url, timeout=10)
    content = BeautifulSoup(response.content, "html.parser")

# Fill books one more time for the last page
fill_books()
print(len(books))

with open("goodreads.csv", 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(books)