# LookBook API

Web app featuring new looks from every country from lookbook.nu

--master edit 2
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
Redis and/or RabbitMQ would be good fit for our case since both of them easy to use, manage and lightweight solutions.

##### Data Processing and DB
RDBMS would not be best option given large amounts of data and necessity in low latency. Of course some RDBMS can be scaled horizontally, but it triggers other unnecessary problems. 
Instead, in order to achieve horizontal scalability, it would be better to use noSQL such as MongoDB itself.\
To have fault tolerancy and horizontal scalability it is necessary to deploy MongoDB sharded cluster with replicas of each server.
In my opinion, MongoDB cluster would be best suit for this project. But if we are going to have much more data, and/or integrate with other data, create data lake, we can also consider using Hadoop cluster further.  
 
##### API
Once we stored this data, we need them to be available within API. As a framework for providing API it is possible to use Flask, but Django better suits for big systems.\
Another thing is, we need data to be accessed instantaneously, with low latency.
To achieve low latency, for services like **given a country which returns the number of posts associated with each hashtag**,
it is better to do all the calculations beforehand and store it in inmemory database, such as Redis (Ex. key-poland#fashion, value-120)

##### Duplicates
In order to avoid duplicates, I just created Unique Index for lookID, to ignore insertion to DB after crawling. 
But it would be more efficient to store **Timestamp + lookID** (I am not sure if LookID is actually unique) as Unique Index and check before crawling if we have such item in the Database.
   
##### Monitoring, Testing and Logging
In order to have full control on the project, it is necessary to have logging, unit tests and proper monitoring.
Other than this, there might be necessity also on autotests.  
E.g For notifying maintainer in case there are some design changes at source website or to compare our scraped results with ones in lookbook.nu. 
For example lookbook shows us most 'hyped' posts by hashtag. And we can compare if our calculations matches with theirs.  
   

### 2. Clients are interested in the evolution of hashtags in popularity (average “hype”), such as seeing which hashtags are currently the most popular, or which ones had a recent decrease in popularity
Another way of finding popularity would be computing not the average hype, but the mentions of hashtag in distinct posts, or at least it should be taken into consideration.\
Intuitively, a trending hashtag should be one that is being used more than usual, as a result of something specific that is happening in that moment.\
If hashtag has spike, hence if hashtag has a huge mentions in recent looks compared to the past, the hashtag should be identified as trending right now.\
To identify good trend, we can consider things like:
- Popularity - the trend should be of interest for many people in community.
- Novelty — the trend should be about something new. People were not posting about it before, or at least not with the same intensity.
- Average number of hypes for hashtag
- Karma of users
Finally, we need filter to ignore hashtags with too low absolute value.

Obviously, the calculation can be costly given the huge amount of hashtags everyday. In this case, we can consider using offline pipelines, same as described above.
More specifically, we can keep several pipelines running in the offline that calculates the ratio of each tag and output the results to some storage system. 
The pipelines may refresh every several hours/days assuming there’s no big difference between a short period of time. 
So when 'the business' checks the trending topics from the API, we can just this user with pre-computed results.

#### a. How would you aggregate the “hype” of posts to compute it for each hashtag ?

Obviously, we cannot just take mean hype for each hashtag. Because hashtag #ILoveShittyDress could be only such hashtag, but it's average hype would be high.\
It forces us to take into account also number of occurrences. With this logic, hashtag #look would be among trending, since it has tons of usage and have good average hype.
But in fact, it is one of the regular tags, which most probably can not be trending tag. Hence, we also should consider time. For simplicity, let's take just average time of posts with given tag.
So, if we need some tool to aggregate the hype before involving Data Science, base solution can be multiplication of normalized version of features described above. 

**Aggregated hype  = Mean hype * normalized frequency * normalized time**  
      
| Tags              | Mean hype     | Frequency  | Mean hours ago | Normalized freq.| 1-Normalized time| AGG hype | 
| ------------------|:-------------:| :---------:| :-------------:| :--------------:| :---------------:| :-------:|
| #halloween        | 37            |   245      |      140       |     1           |       0.8        | 30       |
| #RedTie           | 45            |   120      |      67        |     0.45        |       0.9        | 18       | 
| #ILoveShittyDress | 350           |    1       |      3         |     0           |       1          | 0        | 
| #autumn           | 95            |   180      |      670       |     0.7         |       0          | 0        | 
| #dress            | 85            |   150      |      380       |     0.4         |       0.4        | 13       |
| #sakura           | 80            |   60       |      120       |     0.24        |       0.8        | 15       |

To sum up, with this kind of logic we would prevent rare tags (#ILoveShittyDress) and regular tags (#autumn) from having big influence.
And even though some tags would have low mean hype value, (#halloween, #RedTie) we can say that they are trending thanks to their distribution across community and average freshness of posts.    

#### b. Since the “hype” of existing posts will change over time, how would you retrieve the updated “hype” of existing posts and update the hashtag popularity ?
To retrieve updated information for existing posts, we could use it's ID and periodically crawl from lookbook current hype and also update 'modified date' field.\
Another service can recompute periodically popularity. But "freshness" of post related to the hashtag always should be one of the main features.
While increased hype will increase hashtag's popularity, antiquity of post in contrary, will decrease it over time. 

#### c. There are much more Lookbook users in the US and in Japan, which creates a bias in the hashtag popularity. How would you normalize it to make each country equally important ?
We can equalize the weight of each country by computing the most popular hashtag in given country and taking ratio to each hashtag.\
E.g. for given hashtag popularity X, popularity of normalized X = X - min(absolute popularity) / max(popularity) - min(absolute popularity)
Ex: #sakura could be most popular in Japan, and since there are more users in Japan, it would affect to combined international results and show that it popular worldwide hashtag, when in fact it is mostly only in Japan.\
We normalize it by taking #sakura popularity as 1. And for all the hashtags from Japan, we take ratio with respect to #sakura. From 0 to 1

### 3. Clients are interested in trends from “StyleBoard”, a new social network. It has all the features of Lookbook, plus some additional stats such as the number of reposts. Clients must be able to filter hashtag popularity and other stats by the source of data. How would you modify the system to integrate this new source ?
From technical point of view, if we are going to integrate another platforms in the future, most importantly we should design database, services, API, data types and etc. as abstract as possible.
  

### References
- https://github.com/an-dev/grabber 
- https://medium.com/@ali_oguzhan/how-to-use-scrapy-with-django-application-c16fabd0e62e
- https://benbernardblog.com/the-tale-of-creating-a-distributed-web-crawler/
