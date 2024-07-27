from bs4 import BeautifulSoup as bs
import requests as re



response = re.get('https://subslikescript.com/movie/Titanic-120338')
html = response.text
soup = bs(html,"lxml")

#soup.find(id = "specific_id")


with open("html.html", "w") as file:
    file.write(soup.prettify())
