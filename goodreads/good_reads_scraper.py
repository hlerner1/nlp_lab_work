from bs4 import BeautifulSoup
import requests
import csv
import time

books = []
url = 'https://www.goodreads.com/list/show/32774.Most_Interesting_World'
website = 'https://www.goodreads.com'
response = requests.get(url, timeout=10)
content = BeautifulSoup(response.content, "html.parser")
all_links = []
pages = content.find_all(attrs={"class": "next_page"})
def fill_books():
    # the table of books for this page
    table_data = content.find_all("tr")
    for item in table_data:

        # Adding in sleep to avoid website request overload
        time.sleep(2)

        book = {}

        # Title
        book_title = item.find("a", class_= "bookTitle")
        # Had to chop off the ends of the title to remove \n values
        book["title"] = book_title.get_text()[1:-1]

        # Author
        book_author = item.find("a", class_="authorName")
        book["author"] = book_author.get_text()

        # Detailed info that requires going to book page
        book_link = website + item.find("a", class_="bookTitle", href=True)['href']
        temp_response = requests.get(book_link, timeout=10)
        temp_content = BeautifulSoup(temp_response.content, "html.parser")

        # Summary
        span_tags = temp_content.find("div", class_="readable stacked", id="description").findChildren("span")
        book_summary = ""
        if (len(span_tags)>1):
            book_summary = span_tags[1].get_text()
        elif(len(span_tags) == 1):
            book_summary = span_tags.get_text()
        book["book summary"] = book_summary

        # Characters
        detail_tags = temp_content.find("div", class_="uitext", id="bookDataBox").findChildren("div")
        flag = False
        for detail in detail_tags:
            if (flag):
                b_characters = detail.find_all("a")
                flag = False
            if (detail.get_text() == "Characters"):
                flag = True
        book_characters = []
        for character in range(len(b_characters)-1):
            b_characters[character] = b_characters[character].get_text()
            if (b_characters[character] != '...more' and b_characters[character] != '...less'):
                book_characters.append(b_characters[character])
        book["characters"] = book_characters
        books.append(book)

while (len(content.find_all(attrs={"class": "next_page disabled"})) == 0):
    fill_books()
    pages = content.find_all(attrs={"class": "next_page"})
    link = pages[0]['href']
    url = website + link
    response = requests.get(url, timeout=10)
    content = BeautifulSoup(response.content, "html.parser")

# Fill books one more time for the last page
fill_books()
print(books)
print(len(books))

with open("goodreads.csv", 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(books)