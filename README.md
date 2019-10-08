# LookBook API

Web app featuring new looks from every country from lookbook.nu

Scrapes and saves following fields as a MongoDB document:
- ID (Unique integer)
- Full ID (string)
- Hype count (integer)
- Created date (BSON datetime)
- Image source (string)
- Country (strig)
- Hashtags (list of hashtags as string)
- Django created date (BSON datetime)
- Django modified date (BSON datetime)

## Scraper can be executed by 2 options:
- From POST request to Django 'crawl' service, need to uncomment __init__ function in spyder code
- Periodically executing by crontab

## Steps to follow to deploy project and run within crontab
* Clone the repo 
* Create a virtualenv

```
$ virtualenv venv
$ source venv/bin/activate
```

* Install dependencies
`$ pip install -r requirements.txt`

* Create/modify a .secret/base.json file containing basic db config (For MongoDB - write 'djongo')
```
{
  "DJANGO_DB_ENGINE":"django.db.backends.xxx",
  "DJANGO_DB_NAME":"xxx.xxx",
  "DJANGO_DB_USER":"",
  "DJANGO_DB_PASSWORD":"",
  "DJANGO_DB_HOST":"full MongoDB credential to access also from views.py"
}
```

* Run Django migrations
`$ python manage.py makemigrations`
`$ python manage.py migrate`

* Create superuser for admin consulting
`$ python manage.py createsuperuser`


* Create a script to be executed by cron calling the scraper
```
#~/.cron/lookscraper
#!/bin/bash

WD="/Users/meirkhan/projects/lookbook"
SPIDER_PATH="django_lookbook/lookscraper/lookscraper/spiders/"
VENV_ACTIVATE="venv/bin/activate"


cd $WD
source ./$VENV_ACTIVATE
cd ./$SPIDER_PATH
scrapy crawl lookbook_scraper
```

* And give it proper permissions
`$ chmod +x ~/.cron/lookscraper.sh`

* Edit the crontab to periodically scraping data from 
`*/30 * * * * ~/.cron/scraper.sh # runs the command every 30 minutes`

* Run the Django server 
`$ python manage.py runserver`


# Design Task
### 1. What changes would you perform to crawl and exploit millions of posts ?
Problem needs to be divided into 2 parts: **Crawling** and **Data Processing**.
In order to crawl massive amounts of data for sure we need something like distributed crawler.
Where main components will be:

- A crawler dispatcher, responsible for dispatching URLs to be crawled to the m crawler supervisors, and for collecting results (fields) from them.
- m crawler supervisors, responsible for supervising n child processes. Those child processes would perform the actual crawling. I'll refer to them as crawlers for convenience.
In this particular case of lookbook.nu, we could divide supervisors by countries, so that each supervisor would be responsible for some little group of countries 
- A database server, responsible for storing the initial seed URLs as well as the extracted fields. 

**Data Processing and DB**
RDBMS would be bad option given large amounts of data and necessity in low latency. Of course some RDBMS can be scaled horizontally, but it triggers other unnecessary problems. 
Instead, in order to achieve horizontal scalability, it would be better to use noSQL such as MongoDB itself, or Hadoop cluster depending on other components.
With Hadoop, as it is 'write once, read many times', we could use it's MapReduce tools to precalculate stuff and store it in memory database   



### 2. Clients are interested in the evolution of hashtags in popularity (average “hype”), such as seeing which hashtags are currently the most popular, or which ones had a recent decrease in popularity
#### a. How would you aggregate the “hype” of posts to compute it for each hashtag ?
#### b. Since the “hype” of existing posts will change over time, how would you retrieve the updated “hype” of existing posts and update the hashtag popularity ?
#### c. There are much more Lookbook users in the US and in Japan, which creates abias in the hashtag popularity. How would you normalize it to make each country equally important ?

### 3. Clients are interested in trends from “StyleBoard”, a new social network. It has all the features of Lookbook, plus some additional stats such as the number of reposts. Clients must be able to filter hashtag popularity and other stats by the source of data. How would you modify the system to integrate this new source ?
 

### References
- https://github.com/an-dev/grabber 
- https://medium.com/@ali_oguzhan/how-to-use-scrapy-with-django-application-c16fabd0e62e
- https://benbernardblog.com/the-tale-of-creating-a-distributed-web-crawler/