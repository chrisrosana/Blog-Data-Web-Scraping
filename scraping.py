import requests  # use for HTTP requests
from bs4 import BeautifulSoup  # use for web scraping
from csv import writer  # use for csv
import gspread  # use for Google Sheets
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# Open a sheet from a spreadsheet
spreadsheet = client.open("BlogScraping")

base_url = "https://www.rithmschool.com"
url = "/blog?page=1"

all_articles = []

while url:
    # GET request
    res = requests.get(f"{base_url}{url}")
    # Scraping time
    soup = BeautifulSoup(res.text, "html.parser")  # res.text turns it to HTML
    # Find <article> tags in HTML
    articles = soup.find_all("article")

    for article in articles:
        title = article.find("a").get_text()
        link = article.find("a")["href"]
        date = article.find("small").get_text()
        # append the title, link, date to all_articles list
        all_articles.append({
            "title": title,
            "link": link,
            "date": date
        })
    # write csv file
    with open("blog_data.csv", "w") as csv_file:
        csv_writer = writer(csv_file)
        csv_writer.writerow(["Title", "Link", "Date"])

        for article in all_articles:
            csv_writer.writerow([article["title"], article["link"], article["date"]])
    # find the next button
    next_button = soup.find(class_="next")
    # grab the url
    url = next_button.find("a")["href"] if next_button else None

# read csv file
content = open('blog_data.csv', 'r').read()
# import csv to Google Sheets
client.import_csv(spreadsheet.id, data=content.encode('utf-8'))
# select a worksheet, the most common case: Sheet1
worksheet = spreadsheet.sheet1
# resize the column width
set_column_widths(worksheet, [('A', 500), ('B', 400), ('C', 150)])
# set A1:B1 text format to bold and font size to 12
worksheet.format('A1:C1', {
    'textFormat': {
        'bold': True,
        'fontSize': 12
    }
})
# freeze the first row
worksheet.freeze(1,3)
