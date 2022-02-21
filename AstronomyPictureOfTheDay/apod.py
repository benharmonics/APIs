import datetime
import os
import re

import requests
from bs4 import BeautifulSoup


class APOD:
    def __new__(self, page_text: str):
        # Using regex to find image URL from full text
        url = re.search('https://apod\.nasa\.gov.*?\.[a-z]{3}', page_text)
        if not url:
            print('ERROR: Image URL not found.')
        url = url[0]

        # Getting filename from url, e.g. `example.jpg`
        filename = re.search('[A-Za-z0-9_-]*\.[a-z]{3}$', url)
        if not filename:
            print('ERROR: filename not parsed from url.')
        filename = filename[0]

        # i.e. `example.jpg` => `example`, `jpg`
        title, extension = filename.split('.')

        # We have to clean the info a bit
        info = self.parse_page_text(page_text)

        self.url: str = url
        self.title: str = title
        self.extension: str = extension
        self.info: list = info

        return self

    def parse_page_text(page_text: str):
        """Parses page text into a vector where each element is `[category]:[content]`"""
        # `split(',')` creates a problem where the `explanation` category is divided into multiple sections
        info = page_text.split(',')

        # beginning of `explanation` section starts with 'explanation:'
        explanation_i = [i for i, line in enumerate(info) if 'explanation:' in line][0]
        # end of `explanation` section ends at the `hdurl` section
        explanation_f = [i for i, line in enumerate(info) if 'hdurl:' in line][0] - 1

        # collecting the `explanation` section into a single string
        explanation = ''
        for line in info[explanation_i:explanation_f]:
            explanation += line

        # correcting the split(',') problem by subbing our `explanation` string and getting rid of extra lines
        result = [line for line in info if ':' in line.split()[0]]
        result[explanation_i] = explanation

        return result


def get_page_text() -> str:
    """Gets raw API text and removes extraneous characters"""
    # Get raw HTML from webpage
    page = requests.get('https://api.nasa.gov/planetary/apod'
                        '?api_key=DEMO_KEY')
    # Parse raw HTML into a BeautifulSoup Object
    soup = BeautifulSoup(page.content, 'html.parser')
    # We're using an API, so we're just using everything on the page.
    return re.sub('[{}\n\"]', '', soup.text)


def download_image(basedir: str = os.path.dirname(__file__)):
    def month_dir() -> str:
        date = str(datetime.date.today())
        y, m, _d = date.split('-')
        return f'{y}-{m}'

    page_text = get_page_text()
    apod = APOD(page_text)

    download_path = os.path.join(basedir, "apod")
    if not os.path.exists(download_path):
        os.mkdir(download_path)

    subdir = os.path.join(download_path, month_dir())
    if not os.path.exists(subdir):
        os.mkdir(subdir)

    image_path = os.path.join(subdir, f'{apod.title}.{apod.extension}')
    #wget.download(apod.url, image_path)

    with open(os.path.join(subdir, f'{apod.title}'), 'w+') as f:
        f.writelines('%s\n' % line for line in apod.info)


if __name__ == '__main__':
    # enter base directory, into which image will be downloaded
    download_image()
