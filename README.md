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
Problem needs to be divided into several parts:

##### Crawling
In order to crawl massive amounts of data for sure we need something like distributed crawler.
Where main components will be:

- A crawler dispatcher, responsible for dispatching URLs to be crawled to the crawler supervisors, and for collecting results (fields) from them.
- Crawler supervisors, responsible for supervising child processes. Those child processes would perform the actual crawling. In case of lookbook.nu, every crawler would be responsible for certain amount of pages.
In this particular case of lookbook.nu, we could divide supervisors by countries, so that each supervisor would be responsible for some little group of countries 
- A database server, responsible for storing the initial seed URLs as well as the extracted fields. 

#### Messaging
Crawlers need to communicate with each other, to know which is responsible for which group of countries, pages etc.
Redis and/or RabbitMQ would be good fit for our case.

##### Data Processing and DB
RDBMS would not be best option given large amounts of data and necessity in low latency. Of course some RDBMS can be scaled horizontally, but it triggers other unnecessary problems. 
Instead, in order to achieve horizontal scalability, it would be better to use noSQL such as MongoDB itself, or Hadoop cluster depending on other components.\
 
#### API
Once we stored this data, we need them to be available within API. As a framework for providing API it is possible to use Flask, but Django better suits for big systems.\
Another thing is, we need data to be accessed instantaneously, with low latency. (Could we use Spark here?).
To achieve low latency, for services like **given a country which returns the number of posts associated with each hashtag**,
it is better to do all the calculations beforehand and store it in inmemory database, such as Redis (Ex. key-poland#fashion, value-120) (Can we use Spark here?)

#### Duplicates
In order to avoid duplicates, I just created Unique Index for lookID, to ignore insertion to DB after crawling. 
But it would be more efficient to store **Timestamp + lookID** (I am not sure if LookID is actually unique) as Unique Index and check before crawling if we have such item in the Database.
   
##### Monitoring, Testing and Logging
In order to have full control on the project, it is necessary to have logging, unit tests and proper monitoring.
Other than this, there might be necessity also on autotests.  
E.g For notifying maintainer in case there are some design changes at source website or to compare our scraped results with ones in lookbook.nu. 
For example lookbook shows us most 'hyped' posts by hashtag. And we can compare if our calculations matches with theirs.  
   

### 2. Clients are interested in the evolution of hashtags in popularity (average “hype”), such as seeing which hashtags are currently the most popular, or which ones had a recent decrease in popularity
#### a. How would you aggregate the “hype” of posts to compute it for each hashtag ?
#### b. Since the “hype” of existing posts will change over time, how would you retrieve the updated “hype” of existing posts and update the hashtag popularity ?
#### c. There are much more Lookbook users in the US and in Japan, which creates a bias in the hashtag popularity. How would you normalize it to make each country equally important ?


### 3. Clients are interested in trends from “StyleBoard”, a new social network. It has all the features of Lookbook, plus some additional stats such as the number of reposts. Clients must be able to filter hashtag popularity and other stats by the source of data. How would you modify the system to integrate this new source ?
 

### References
- https://github.com/an-dev/grabber 
- https://medium.com/@ali_oguzhan/how-to-use-scrapy-with-django-application-c16fabd0e62e
- https://benbernardblog.com/the-tale-of-creating-a-distributed-web-crawler/