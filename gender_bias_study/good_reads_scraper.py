from bs4 import BeautifulSoup
import requests
import csv
import time

# Developer key aquired from goodreads
# key = [YOUR API KEY HERE]

author_list_set = set([])
author_list_dict = {}
url = 'https://www.goodreads.com/list/show/1.Best_Books_Ever?page=137'
website = 'https://www.goodreads.com'
response = requests.get(url, timeout=(200,200))
content = BeautifulSoup(response.content, "html.parser")
all_links = []
pages = content.find_all(attrs={"class": "next_page"})

female_pronouns = ["she", "her", "hers"]
male_pronouns = ["he", "him", "his"]


# Returns "male" or "female" or "even" based on which gender has more male or female pronouns
def count_words(words):
    female_count = 0
    male_count = 0
    for word in words:
        if (word in female_pronouns):
            female_count += 1
        elif (word in male_pronouns):
            male_count += 1
    if male_count > female_count:
        return "male"
    elif female_count > male_count:
        return "female"
    else:
        return "Unknown"


def fill_books():
    # the table of books for this page
    table_data = content.find_all("tr")
    for item in table_data:
        # Adding in sleep to avoid website request overload
        time.sleep(1.5)
        book = {}
        # Title
        book_title = item.find("a", class_="bookTitle")
        # Had to chop off the ends of the title to remove \n values
        book["title"] = book_title.get_text()[1:-1]

        # Author
        book_author = item.find("a", class_="authorName")
        book["author"] = book_author.get_text()

        # print(book_author)
        author_url = book_author['href']
        # print(author_url+key)
        if (author_url not in author_list_set):
            author_response = requests.get(author_url+key, timeout=(200,200))

            author_content = BeautifulSoup(author_response.content, "html.parser")
            # print(author_content)
            author_summary = author_content.find("about")
            if (author_summary != None):
                author_summary = author_summary.get_text()
                if (len(author_summary) != 0):
                    author_gender = count_words(author_summary.split())
                else:
                    author_gender = "Unknown"
                book["author_gender"] = author_gender
                author_list_set.add(author_url)
                author_list_dict[author_url] = author_gender
            else:
                book["author_gender"] = "Unknown"
        else:
            book["author_gender"] = author_list_dict[author_url]


        book["author detailed info"] = author_content

        # Detailed info that requires going to book page
        book_link = website + item.find("a", class_="bookTitle", href=True)['href']
        temp_response = requests.get(book_link, timeout=(2000, 2000))
        temp_content = BeautifulSoup(temp_response.content, "html.parser")
        # book["book detailed info"] = temp_content
        # Summary
        span_tags = temp_content.find("div", class_="readable stacked", id="description")
        if (span_tags != None):
            span_tags = span_tags.findChildren("span")
            book_summary = ""
            if (len(span_tags)>1):
                book_summary = span_tags[1].get_text()
            elif(len(span_tags) == 1):
                book_summary = span_tags[0].get_text()
            book["book summary"] = book_summary
        else:
            book["book summary"] = "No Summary Availible"
        
        # # Characters
        detail_tags = temp_content.find("div", class_="uitext", id="bookDataBox")
        if (detail_tags == None):
        	book["characters"] = "No Characters Availible"
        else:	
	        detail_tags = detail_tags.findChildren("div")
	        flag = False
	        b_characters = None
	        for detail in detail_tags:
	            if (flag):
	                b_characters = detail.find_all("a")
	                flag = False
	            if (detail.get_text() == "Characters"):
	                flag = True
	        if (b_characters == None):
	            book["characters"] = "No Characters Availible"
	        else:
	            if (type(b_characters[0]) == str):
	                book_characters = b_characters
	            else:
	                book_characters = []
	                for character in range(len(b_characters)-1):
	                    if (type(b_characters[character]) != str):
	                        b_characters[character] = b_characters[character].get_text()
	                    else:
	                        print(b_characters[character])
	                    if (b_characters[character] != '...more' and b_characters[character] != '...less'):
	                        book_characters.append(b_characters[character])
	            book["characters"] = book_characters
        fc.writerow(book)

output_file  = open("goodreads.csv", 'a+', encoding='utf8', newline='') 
fc = csv.DictWriter(output_file, fieldnames=["title", "author", "book summary", "characters"])
count = 0
while (len(content.find_all(attrs={"class": "next_page disabled"})) == 0):
    print(count)
    count += 1
    fill_books()
    pages = content.find_all(attrs={"class": "next_page"})
    link = pages[0]['href']
    url = website + link
    time.sleep(1.5)
    response = requests.get(url, timeout=(2000,2000))
    content = BeautifulSoup(response.content, "html.parser")

# Fill books one more time for the last page
fill_books()
output_file.close()
print("done")
with open('goodreads.csv', 'w', encoding='utf8', newline='') as output_file:
    fc = csv.DictWriter(output_file, fieldnames=books[0].keys())
    fc.writeheader()
    fc.writerows(books)
