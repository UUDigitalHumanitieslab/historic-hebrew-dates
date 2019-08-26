import csv
import glob
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen
import os

import dateutil
from bs4 import BeautifulSoup

from historic_hebrew_dates.date_parser import DateParser


def harvest_records_files():
    overview_url = 'http://www.steinheim-institut.de/cgi-bin/epidat?info=howtoharvest'
    html = urlopen(overview_url).read()
    soup = BeautifulSoup(html, f'html.parser')
    anchors = soup.find_all('a', text='list of records ')
    records_list_urls = [
        'http://www.steinheim-institut.de/cgi-bin/epidat'+a['href'] for a in anchors]
    id_pattern = r'^.*resources\-(\w+)$'
    for i, url in enumerate(records_list_urls):
        db_id = re.match(id_pattern, url).group(1)

        with(open(f'data/epidat/records_files/{db_id}.xml', 'wb')) as f:
            content = urlopen(url).read()
            f.write(content)

        print(f'{i}/{len(records_list_urls)}', end='\r')
    print('\n')


def harvest_all_dbs():
    file_list = glob.glob('data/epidat/records_files/*.xml')
    for i, filename in enumerate(file_list):
        print(f'{i}/{len(file_list)}')
        try:
            harvest_tei(filename)
        except:
            print(f'failed:\t{filename}')
        print('\n')


def harvest_tei(records_file):
    db_id = os.path.basename(records_file.strip('.xml'))

    tree = ET.parse(records_file)
    i = 0
    size = sum(1 for _ in tree.iter())
    for elem in tree.iter():
        if elem.tag == 'resource':
            data = urlopen(elem.attrib['href'])
            file_path = f'data/epidat/TEI/{db_id}/{elem.attrib["id"]}.xml'
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(data.read())
        i += 1
        print(f'{db_id}:\t\t{i}/{size}', end='\r')


def extract_inscriptions():
    file_list = glob.glob('data/*/*.xml', recursive=True)

    with open('data/epidat_worms_transcriptions.xml', 'w') as wf:
        csv_writer = csv.writer(
            wf, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(["id", "transcription", "year", "month", "day"])

        for file_path in sorted(file_list):
            fields = {
                'file_id': Path(file_path).name.rstrip('.xml'),
                'transcription': None,
                'year': None,
                'month': None,
                'day': None
            }

            with open(file_path) as f:
                soup = BeautifulSoup(f.read(), 'lxml')

                try:
                    edition = soup.find('div', {'type': 'edition'})
                    ab = edition.find('ab').text
                    lines = [l.lstrip().rstrip() for l in ab.splitlines()]
                    non_empty_lines = [l for l in lines if len(l) > 0]
                    fields['transcription'] = ' '.join(non_empty_lines)
                except:
                    pass

                try:
                    # TODO: multiple people in one inscription
                    person = soup.find('person')
                    death = person.find('death')
                    when = death['when']
                    parsed = dateutil.parser.parse(when)
                    fields['year'], fields['month'], fields['day'] = parsed.year, parsed.month, parsed.day
                except:
                    pass

                csv_writer.writerow(fields.values())


def extract_dates(transcriptions_file, search_pattern):
    data = csv.DictReader(open(transcriptions_file))
    for entry in data:
        match = re.match(search_pattern, entry['transcription'])


def main():
    # worms_records = 'data/epidat_worms_records.xml'
    # harvest_tei (worms_records)
    # parser = DateParser(lang='hebrew')
    # extract_dates('data/epidat_worms_transcriptions.xml',
    #               parser.search_pattern)
    harvest_all_dbs()


if __name__ == '__main__':
    main()
