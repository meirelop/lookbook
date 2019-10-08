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
 

### References
- https://github.com/an-dev/grabber 
- https://medium.com/@ali_oguzhan/how-to-use-scrapy-with-django-application-c16fabd0e62e