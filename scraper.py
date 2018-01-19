import logging
import requests
from lxml import html

from libsanctions import Source, Entity, make_uid

log = logging.getLogger(__name__)
URL = 'http://www.worldpresidentsdb.com/list/current/'  # noqa


def parse_entry(source, entry):
    url = entry.get('href')
    res = requests.get(url)
    doc = html.fromstring(res.content)
    content = doc.find('.//div[@id="content"]')
    
    uid = make_uid(url)
    
    entity = source.create_entity(uid)
    entity.type = Entity.TYPE_INDIVIDUAL
    entity.function = 'President'
    entity.url = url
    entity.first_name, entity.last_name = content.find('h1').text.split(' ', 1)
    
    for element in content.findall('.//p'):
        type = element.find('.//span')
        
        if type == None:
            continue
        else:
            type = type.text
        
        if type == 'Country:':
            nationality = entity.create_nationality()
            nationality.country = element.find('a').text
        elif type == 'Birth Date:':
            value = element[0].tail.strip()
            month, day, year = value.split('-', 2)
            birth_date = entity.create_birth_date()
            birth_date.date = year+'-'+month+'-'+day
            birth_date.quality = 'strong'
        elif type == 'Birth Place:':
            value = element[0].tail.strip()
            birth_place = entity.create_birth_place()
            birth_place.place = value
        elif type == 'Political Party:':
            value = element[0].tail.strip()
            entity.program = value
        elif type == 'Other Political Titles:':
            value = element[0].tail.strip()
            entity.summary = value
    
    entity.save()


def parse():
    source = Source('worldpresidentsdb')
    
    url = URL
    res = requests.get(url)
    doc = html.fromstring(res.content)
    for member in doc.findall('.//table[@id="list_table"]//td//a'):
        parse_entry(source, member)

    source.finish()


if __name__ == '__main__':
    parse()
