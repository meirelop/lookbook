from django.http import HttpResponse
import json
import pymongo
from django.conf import settings
import ast
import operator
from urllib.parse import urlparse
from uuid import uuid4
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
import scrapyd
# from main.utils import URLUtil
from  ..models import Look
from collections import OrderedDict


def get_posts_by_country(request):
    """
    :return: For a given country, returns the number of posts associated with each hashtag

    Args:
        country - target country

    Examples:
        http://localhost:8000/get_posts_by_country?country=austria
    """

    std_response = HttpResponse('[]', content_type="application/json")
    country = request.GET.get('country', None)

    if not country:
        return std_response

    mongo_collection = get_mongo_collection()

    # TODO: make search by country names case insensitive
    result_dict = {}
    cursor = mongo_collection.find({LOOK_COUNTRY: country})

    # TODO: optimize processing of query
    for document in cursor:
        hashtags = ast.literal_eval(document[LOOK_HASHTAGS])
        for tag in hashtags:

            if tag in result_dict:
                result_dict[tag] += 1
            else:
                result_dict[tag] = 0

    if result_dict:
        return HttpResponse(json.dumps(result_dict), content_type="application/json")
    return std_response



def get_hype_by_tag(request):
    """
    :return: For a given hashtag, return the image URLs of posts sorted by “hype” (from largest to smallest)

    Args:
        hashtag - target hashtag

    Examples:
        http://localhost:8000/get_hype_by_tag?hashtag=fashion
    """

    std_response = HttpResponse('[]', content_type="application/json")
    hashtag = request.GET.get('hashtag', None)
    print(hashtag)

    if not hashtag:
        return std_response

    mongo_collection = get_mongo_collection()

    # TODO: make search by hashtag case insensitive
    hype_dict = {}
    cursor = mongo_collection.find({})

    for document in cursor:
        hashtags_list = ast.literal_eval(document[LOOK_HASHTAGS])
        hype = document[LOOK_HYPE]
        img_url = document[LOOK_IMG_URL]

        if hashtag in hashtags_list:
            hype_dict[img_url] = hype

    sorted_dict = sorted(hype_dict.items(), key=operator.itemgetter(1), reverse=True)
    if sorted_dict:
        return HttpResponse(json.dumps(sorted_dict), content_type="application/json")
    return std_response



def get_dailypost_by_tag(request):
    """
    :return: For a given hashtag, the number of posts for each day

    Args:
        hashtag - target hashtag

    Examples:
        http://localhost:8000/get_dailypost_by_tag?hashtag=fashion
    """

    std_response = HttpResponse('[]', content_type="application/json")
    hashtag = request.GET.get('hashtag', None)

    if not hashtag:
        return std_response

    mongo_collection = get_mongo_collection()

    # TODO: make search by hashtag case insensitive
    result_dict = {}
    cursor = mongo_collection.find({})

    for document in cursor:
        hashtags_list = ast.literal_eval(document[LOOK_HASHTAGS])
        created_date = document[LOOK_CREATED].date()

        if hashtag in hashtags_list:
            if str(created_date) in result_dict:
                result_dict[str(created_date)] += 1
            else:
                result_dict[str(created_date)] = 0

    ordered = OrderedDict(sorted(result_dict.items(), key=lambda t: t[0], reverse=True))
    if result_dict:
        return HttpResponse(json.dumps(ordered), content_type="application/json")
    return std_response


def get_mongo_collection():
    """
    :return: MongoDB collection instance created using credentials specified in django settings
    """
    myclient = pymongo.MongoClient(settings.MONGO_CREDENTIALS)
    mydb = myclient[settings.MONGO_DB]
    collection = mydb[settings.MONGO_COLLECTION_NAME]
    return collection


@csrf_exempt
@require_http_methods(['POST', 'GET'])  # only get and post
def crawl(request):
    # Post requests are for new crawling tasks
    if request.method == 'POST':

        url = request.POST.get('url', None)  # take url comes from client. (From an input may be?)
        max_items = request.POST.get('max_items', None)

        if not url:
            return JsonResponse({'POST error': 'Missing  args'})

        # if not is_valid_url(url):
        #     return JsonResponse({'error': 'URL is invalid'})

        # domain = urlparse(url).netloc  # parse the url and extract the domain
        unique_id = str(uuid4())  # create a unique ID.

        # This is the custom settings for scrapy spider.
        # We can send anything we want to use it inside spiders and pipelines.
        # I mean, anything
        settings = {
            'unique_id': unique_id,  # unique ID for each record for DB
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        # Here we schedule a new crawling task from scrapyd.
        # Notice that settings is a special argument name.
        # But we can pass other arguments, though.
        # This returns a ID which belongs and will be belong to this task
        # We are goint to use that to check task's status.
        task = scrapyd.schedule('default', 'lookbook_scraper',
                                settings=settings, url=url, max_items=max_items)

        return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})

    # Get requests are for getting result of a specific crawling task
    elif request.method == 'GET':
        # If crawling is completed, we respond back with a crawled data.
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)

        if not task_id or not unique_id:
            return JsonResponse({'GET error': 'Missing args'})

        # Here we check status of crawling that just started a few seconds ago.
        # If it is finished, we can query from database and get results
        # If it is not finished we can return active status
        # Possible results are -> pending, running, finished
        status = scrapyd.job_status('default', task_id)
        if status == 'finished':
            try:
                # this is the unique_id that we created even before crawling started.
                item = Look.objects.get(unique_id=unique_id)
                return JsonResponse({'data': item.to_dict['data']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'status': status})