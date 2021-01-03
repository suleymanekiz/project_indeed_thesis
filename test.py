import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def get_url(position, location):
    """Generate url from position and location"""
    template = 'https://nl.indeed.com/vacatures?q={}&l={}'
    position = position.replace(' ', '+')
    location = location.replace(' ', '+')
    url = template.format(position, location)
    return url

url = get_url('thesis data', 'nederland')
print(url)

#extract raw data
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
cards = soup.find_all('div', 'jobsearch-SerpJobCard')
print(len(cards))

#prototype the model with a single record
card = cards[0]
atag = card.h2.a

#job title
job_title = atag.get('title')
job_url = 'https://nl.indeed.com' + atag.get('href')

##company name##
company = card.find('span', 'company').text.strip() #tested - worked #strip is to remove whitespaces

##city of job location##
job_location = card.find('div', 'recJobLoc').get('data-rc-loc') #city of job location extracted

##job summary##
job_summary = card.find('div', 'summary').text.strip()

#job date listing
job_date_listing = card.find('span', 'date').text

#current date to compare towards the relative date of the job posting
today = datetime.today().strftime('%d-%m-%Y')

#job salary range
job_salary = card.find('span', 'salaryText')
if job_salary:
    salary = job_salary.text.strip()
else:
    salary = ''

print(job_salary)

###generalize model with a function###

def get_record(card):
    """extract job data from a single record"""
    atag = card.h2.a
    job_title = atag.get('title')
    job_url = 'https://nl.indeed.com' + atag.get('href')
    company = card.find('span', 'company').text.strip() #tested - worked #strip is to remove whitespaces
    job_location = card.find('div', 'recJobLoc').get('data-rc-loc') #city of job location extracted
    job_summary = card.find('div', 'summary').text.strip()
    job_date_listing = card.find('span', 'date').text
    today = datetime.today().strftime('%d-%m-%Y')
    #this does not exist for all jobs, so we take care of the exceptions
    job_salary = card.find('span', 'salaryText')
    if job_salary :
        salary = job_salary.text.strip()
    else:
        salary = ''

    record = (job_title, company, job_location, job_date_listing, today, job_summary, salary, job_url)
    return record

records = []

for card in cards:
    record = get_record(card)
    records.append(record)


##getting to the next page##
while True:
    try:
        url = 'https://nl.indeed.com' + soup.find('a', {'aria-label': 'Volgende'}).get('href')
    except AttributeError:
        break
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    cards = soup.find_all('div', 'jobsearch-SerpJobCard')

    for card in cards:
        record = get_record(card)
        records.append(record)

print(len(records))#133 thesis data postions in NL

###### PUTTING IT ALL TOGETHER ######
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_url(position, location):
    """generate url"""
    template = 'https://nl.indeed.com/vacatures?q={}&l={}'
    url = template.format(position, location)
    return url

def get_record(card):
    """extract job data from a single record"""
    atag = card.h2.a
    job_title = atag.get('title')
    job_url = 'https://nl.indeed.com' + atag.get('href')
    company = card.find('span', 'company').text.strip() #tested - worked #strip is to remove whitespaces
    job_location = card.find('div', 'recJobLoc').get('data-rc-loc') #city of job location extracted
    job_summary = card.find('div', 'summary').text.strip()
    job_date_listing = card.find('span', 'date').text
    today = datetime.today().strftime('%d-%m-%Y')
    try: 
        job_salary = card.find('span', 'salaryText')
    except AttributeError:
        job_salary = ''

    record = (job_title, company, job_location, job_date_listing, today, job_summary, salary, job_url)

    return record

def main(position, location):
    """Run the main program"""
    records = []
    url = get_url(position, location)

    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', 'jobsearch-SerpJobCard')

        for card in cards:
            record = get_record(card)
            records.append(record)

        try:
            url = 'https://nl.indeed.com' + soup.find('a', {'aria-label': 'Volgende'}).get('href')
        except AttributeError:
            break 

    #save the thesis job data
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'Salary', 'JobUrl'])
        writer.writerows(records)
#run the main program
main('thesis data', 'nederland')