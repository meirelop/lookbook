from django.http import HttpResponse
import json
import pymongo
from django.conf import settings
import ast
import operator
from collections import OrderedDict
from ..config.settings.base import *


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