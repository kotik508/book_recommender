import json
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


def get_whole_page(url):
    driver_loc = '/snap/firefox/current/usr/lib/firefox/geckodriver'
    binary_loc = '/snap/firefox/current/usr/lib/firefox/firefox'
    service = Service(driver_loc)
    opts = webdriver.FirefoxOptions()
    opts.binary_location = binary_loc
    driver = webdriver.Firefox(service=service, options=opts)
    driver.get(url)
    time.sleep(1)
    ce = driver.find_elements(By.CSS_SELECTOR, ".Button.Button--inline.Button--medium")[1]
    ce.click()
    html = driver.page_source
    driver.close()
    return html

def get_cover_image_uri(soup):
    series = soup.find('img', class_='ResponsiveImage')
    if series:
        series_uri = series.get('src')
        return series_uri
    else:
        return ""

def get_isbn(soup):
    try:
        isbn_dt = soup.find_all('dt', string=lambda text: text and 'ISBN' in text)[0]
        isbn_div = isbn_dt.find_parent('div', class_='DescListItem')
        isbn = isbn_div.find('div', class_='TruncatedContent__text').text.split()[0]
        return isbn
    except:
        return "isbn not found"

def get_year_first_published(soup):
    year_first_published = soup.find('p', {'data-testid':'publicationInfo'})
    if year_first_published:
        year_first_published = year_first_published.string
        return re.search('([0-9]{3,4})', year_first_published).group(1)
    else:
        return ''

def get_num_pages(soup):
    if soup.find('div', class_='FeaturedDetails'):
        num_pages = soup.find('p', {'data-testid': 'pagesFormat'}).text.strip()
        return int(num_pages.split()[0])
    return ''

def get_rating_distribution(soup):
    distribution = soup.find_all('div', class_="RatingsHistogram__labelTotal")
    distribution = [0.01 if "<" in c.text else
                    int(re.search(r'\((\d+)%\)', c.text).group(1))/100 for c in distribution]
    distribution_dict = {'5 Stars': distribution[0],
                         '4 Stars': distribution[1],
                         '3 Stars': distribution[2],
                         '2 Stars': distribution[3],
                         '1 Star':  distribution[4]}
    return distribution_dict

def get_series_length(soup):
    title_section = soup.find("div", class_="BookPageTitleSection__title")

    if title_section:
        link_tag = title_section.find("a")
        if link_tag and "href" in link_tag.attrs:
            new_link = link_tag["href"]

            series_source = urlopen(new_link)
            new_soup = bs4.BeautifulSoup(series_source, 'html.parser')

            text_div = new_soup.find("div", class_="responsiveSeriesHeader__subtitle")
            if text_div:
                text = text_div.get_text(strip=True)
                series_length = text.split(' ')[0]
                return series_length
    return 0

def scrape_book(url):

    soup = bs4.BeautifulSoup(get_whole_page(url), 'html.parser')

    path = urlparse(url).path
    book_id = path.split('/')[3].split('-')[0]

    time.sleep(1)

    return {
        'book_id': book_id,
        'isbn': get_isbn(soup),
        'author': ' '.join(soup.find('span', class_='ContributorLink__name').text.split()),
        'num_pages': get_num_pages(soup),
        'description': soup.find('span', class_='Formatted').decode_contents().replace('<br/>', ' ')
            .replace('<b>', '').replace('</b>', '').replace('  ', ' '),
        'cover_image_uri': get_cover_image_uri(soup),
        'book_title': ' '.join(soup.find('h1', class_='Text__title1').text.split()),
        'series_length': get_series_length(soup),
        'year_first_published': get_year_first_published(soup),
        'average_rating': soup.find('div', class_='RatingStatistics__rating').text.strip(),
        'rating_distribution': get_rating_distribution(soup)
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

def main(urls_enaled: bool):
    if urls_enaled:
        urls = get_book_urls()
        data = pd.DataFrame({'urls': urls})
        data.to_csv('book_urls.csv', index=False)
    else:
        urls = pd.read_csv('book_urls.csv')['urls']

    book_data = []
    for i, url in enumerate(tqdm(urls)):
        book_data.append(scrape_book(url))
        if i % 1000 == 0:
            with open(f'book_data.json', 'w') as file:
                json.dump(book_data, file)

    with open(f'book_data.json', 'w') as file:
        json.dump(book_data, file)

if __name__ == '__main__':
    main(urls_enaled=False)