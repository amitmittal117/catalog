import bs4
import re
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from Catalog import settings
from openpyxl import Workbook
import requests
import logging
import json

from django.shortcuts import render
from django.views import View
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from main.models import CoreDetail, Details

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class populate(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    def post(self, request):
        data = request.data
        Actor_one_name = data.get("Actor_one").replace("-", " ").replace("_", " ").title()
        Actor_two_name = data.get("Actor_two").replace("-", " ").replace("_", " ").title()
        logger.info(Actor_one_name)
        CoreDetail_obj = CoreDetail.objects.filter(actorname=Actor_one_name)
        if not CoreDetail_obj:
            logger.info("Not in our database")
            logger.info(Actor_one_name)
            req = {"name":Actor_one_name}
            res = requests.post("http://localhost:8000/main/dataextract/",req)
            Actor_one_list = res.json().get('movie')
        else:
            logger.info("Found in our database")
            logger.info(Actor_one_name)
            details_obj = Details.objects.filter(actorid=str(CoreDetail_obj[0].actorid))
            Actor_one_list = details_obj[0].actordetails.get('movie')
        CoreDetail_obj = CoreDetail.objects.filter(actorname=Actor_two_name)
        if not CoreDetail_obj:
            logger.info("Not in our database")
            logger.info(Actor_two_name)
            req = {"name":Actor_two_name}
            res = requests.post("http://localhost:8000/main/dataextract/",req)
            Actor_two_list = res.json().get('movie')
        else:
            logger.info("Found in our database")
            logger.info(Actor_two_name)
            details_obj =  Details.objects.filter(actorid=CoreDetail_obj[0].actorid)
            Actor_two_list = details_obj[0].actordetails.get("movie")
        logger.info(list(set(Actor_one_list) & set(Actor_two_list)))
        return Response(list(set(Actor_one_list) & set(Actor_two_list)))


class index(View):
    template_name = "index.html"

    def get(self, request):
        # logger.info(request.GET.get('abc'))
        return render(request, self.template_name, context={'name': request.GET.get('abc')})


class dataextract(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    def post(self,request):
        name = request.data.get('name')
        api_key = "?api_key=" + settings.api_key_v3
        url = settings.tmdb_url + "search/person" + api_key +"&query=" + name
        response_name = requests.get(url)
        if response_name.ok:
            actor_id = response_name.json().get("results")[0].get("id")
            if CoreDetail.objects.filter(id=actor_id) and Details.object.filter(id=actor_id):
                CoreDetail.objects.filter(id=actor_id).delete()
                Details.objects.filter(id=actor_id).delete()
            CoreDetail_obj = CoreDetail.objects.create(id=actor_id)
            CoreDetail_obj.actorname = response_name.json().get("results")[0].get("name")
            CoreDetail_obj.actorid = actor_id
            CoreDetail_obj.actorpopularity = response_name.json().get("results")[0].get("popularity")
            CoreDetail_obj.actorprofession = response_name.json().get("results")[0].get("known_for_department")
            CoreDetail_obj.save()
            url_imdb_id = settings.tmdb_url + "person/" + str(actor_id) + "/movie_credits" + api_key
            response_imdb_id = requests.get(url_imdb_id)
            movielist = []
            details_dict = dict()
            for every in response_imdb_id.json().get('cast'):
                movielist.append(every.get('title'))
            details_dict['movie'] = movielist
            details_obj = Details.objects.create(id=str(actor_id))
            details_obj.actorid = str(actor_id)
            details_obj.actordetails = details_dict
            details_obj.save()
        return Response(details_dict)

class ActorName(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    def get(self, request):
        a = []
        for every in CoreDetail.objects.all():
            a.append(every.actorname)
            # a[every.actorname] = "null"
        logger.info(a)
        return Response(a)



class dataextractextended(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    def post(self,request):
        name = request.data.get('name')
        api_key = "?api_key=" + settings.api_key_v3
        url = settings.tmdb_url + "search/person" + api_key +"&query=" + name
        response_name = requests.get(url)
        if response_name.ok:
            actor_id = response_name.json().get("results")[0].get("id")
            if CoreDetail.objects.filter(id=actor_id):
                CoreDetail.objects.filter(id=actor_id).delete()
            CoreDetail_obj = CoreDetail.objects.create(id=actor_id)
            CoreDetail_obj.actorname = response_name.json().get("results")[0].get("name")
            CoreDetail_obj.actorid = actor_id
            CoreDetail_obj.actorpopularity = response_name.json().get("results")[0].get("popularity")
            CoreDetail_obj.actorprofession = response_name.json().get("results")[0].get("known_for_department")
            CoreDetail_obj.save()
            url_imdb_id = settings.tmdb_url + "person/" + str(actor_id) + "/movie_credits" + api_key
            response_imdb_id = requests.get(url_imdb_id)
            a = []
            for every in response_imdb_id.json().get('cast'):
                title = every.get('title')
                id = every.get('id')
                popularity = every.get('popularity')
                release_date = every.get('release_date')
                res = requests.get(settings.tmdb_url + "movie/" +str(id) +"/credits" + api_key)
                # logger.info(settings.tmdb_url + "movie/" +str(id) +"/credits" + api_key)
                logger.info(res.json())
                logger.info(title + ": " + str(id) + ", " + str(popularity) + ", " + str(release_date))
                logger.info("-"*50)
        return Response(res.json())
