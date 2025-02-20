import csv
from urllib.error import HTTPError
import os.path
from tqdm import tqdm
import re
import time
from urllib.parse import urlparse
import bs4
import pandas as pd
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By


def get_whole_page(driver, url):
    driver.get(url)
    time.sleep(1)

    try:
        ce = driver.find_elements(By.CSS_SELECTOR, ".Button.Button--inline.Button--medium")[1]
        ce.click()
        ce = driver.find_element(By.XPATH, "//button[span[text()='...more']]")
        ce.click()
        html = driver.page_source
        return html
    except:
        return None

def get_tags(soup):
    try:
        tags = []
        tag_spans = soup.find_all('span', class_='BookPageMetadataSection__genreButton')
        for tag in tag_spans:
            tags.append(tag.text)
        return tags
    except:
        return ''

def get_cover_image_uri(soup):
    try:
        series = soup.find('img', class_='ResponsiveImage')
        if series:
            series_uri = series.get('src')
            return series_uri
        else:
            return ""
    except:
        return ''

def get_isbn(soup):
    try:
        isbn_dt = soup.find_all('dt', string=lambda text: text and 'ISBN' in text)[0]
        isbn_div = isbn_dt.find_parent('div', class_='DescListItem')
        isbn = isbn_div.find('div', class_='TruncatedContent__text').text.split()[0]
        return isbn
    except:
        return "isbn not found"

def get_year_first_published(soup):
    try:
        year_first_published = soup.find('p', {'data-testid':'publicationInfo'})
        if year_first_published:
            year_first_published = year_first_published.string
            return re.search('([0-9]{3,4})', year_first_published).group(1)
        else:
            return ''
    except:
        return ''

def get_num_pages(soup):
    if soup.find('div', class_='FeaturedDetails'):
        try:
            num_pages = soup.find('p', {'data-testid': 'pagesFormat'}).text.strip()
            n = int(num_pages.split()[0])
            return int(num_pages.split()[0])
        except:
            return ''
    return ''

def get_rating_distribution(soup):
    distribution = soup.find_all('div', class_="RatingsHistogram__labelTotal")
    if len(distribution) > 0:
        try:
            distribution = [0.01 if "<" in c.text else
                            int(re.search(r'\((\d+)%\)', c.text).group(1))/100 for c in distribution]
            distribution_dict = {'5 Stars': distribution[0],
                                 '4 Stars': distribution[1],
                                 '3 Stars': distribution[2],
                                 '2 Stars': distribution[3],
                                 '1 Star':  distribution[4]}
            return distribution_dict
        except:
            return ''
    else:
        return ''

def get_series_length(soup):
    title_section = soup.find("div", class_="BookPageTitleSection__title")

    try:
        if title_section:
            link_tag = title_section.find("a")
            if link_tag and "href" in link_tag.attrs:
                new_link = link_tag["href"]

                try:
                    series_source = urlopen(new_link)
                    new_soup = bs4.BeautifulSoup(series_source, 'html.parser')

                    text_div = new_soup.find("div", class_="responsiveSeriesHeader__subtitle")
                    if text_div:
                        text = text_div.get_text(strip=True)
                        series_length = text.split(' ')[0]
                        return series_length
                except HTTPError:
                    return None
    except:
        return None

def scrape_book(driver, url):

    source = get_whole_page(driver, url)

    if source:
        soup = bs4.BeautifulSoup(source, 'html.parser')
    else:
        return None

    path = urlparse(url).path
    book_id = re.split(r'\D+', path.split('/')[3])[0]

    time.sleep(1)

    return {
        'book_id': book_id,
        'book_title': ' '.join(soup.find('h1', class_='Text__title1').text.split()),
        'isbn': get_isbn(soup),
        'author': ' '.join(soup.find('span', class_='ContributorLink__name').text.split()),
        'num_pages': get_num_pages(soup),
        'description': soup.find('span', class_='Formatted').decode_contents().replace('<br/>', ' ')
            .replace('<b>', '').replace('</b>', '').replace('  ', ' '),
        'cover_image_uri': get_cover_image_uri(soup),
        'series_length': get_series_length(soup),
        'year_first_published': get_year_first_published(soup),
        'average_rating': soup.find('div', class_='RatingStatistics__rating').text.strip(),
        'rating_distribution': get_rating_distribution(soup),
        'tags': get_tags(soup)
    }

def get_book_urls():

    driver_loc = '/snap/firefox/current/usr/lib/firefox/geckodriver'
    binary_loc = '/snap/firefox/current/usr/lib/firefox/firefox'
    service = Service(driver_loc)
    opts = webdriver.FirefoxOptions()
    opts.binary_location = binary_loc
    driver = webdriver.Firefox(service=service, options=opts)

    urls = []

    for i in range(1, 101):
        driver.get(f'https://www.goodreads.com/list/show/1.Best_Books_Ever?page={i}')
        book_titles = driver.find_elements(By.CLASS_NAME, 'bookTitle')
        urls.extend([url.get_attribute("href") for url in book_titles])

    driver.close()
    return urls

def write_to_csv(file_name, data):

    is_file = os.path.isfile("books.csv")

    with open(file_name, mode='a', newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())

        if not is_file:
            writer.writeheader()

        writer.writerows(data)

def check_last_title(books_file, url_file):

    with open(books_file, mode='r', newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            book_id = row[0]

    if book_id:
        with open(url_file, mode="r", newline="") as url_file:
            reader = csv.reader(url_file)

            for index, row in enumerate(reader):
                if index > 0 and row and re.split(r'\D+', urlparse(row[0]).path.split('/')[3])[0] == str(book_id):
                    return index
            return 0

def main(urls_enaled: bool):

    driver_loc = '/snap/firefox/current/usr/lib/firefox/geckodriver'
    binary_loc = '/snap/firefox/current/usr/lib/firefox/firefox'
    service = Service(driver_loc)
    opts = webdriver.FirefoxOptions()
    opts.binary_location = binary_loc
    driver = webdriver.Firefox(service=service, options=opts)

    if urls_enaled:
        urls = get_book_urls()
        data = pd.DataFrame({'urls': urls})
        data.to_csv('book_urls.csv', index=False)
    else:
        urls = pd.read_csv('book_urls.csv')['urls']

    if os.path.isfile('books.csv'):
        start_index = check_last_title('books.csv', 'book_urls.csv')
    else:
        start_index = 0

    book_data = []
    for i in tqdm(range(start_index, len(urls))):
        book_data.append(scrape_book(driver, urls.iloc[i]))

        if i % 100 == 0 or i == len(urls) - 1:
            book_data = [book for book in book_data if book is not None]
            write_to_csv('books.csv', book_data)
            book_data = []

if __name__ == '__main__':
    main(urls_enaled=False)