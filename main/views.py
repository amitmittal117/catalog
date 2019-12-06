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


# Create your views here.

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class populate(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    def post(self, request):
        data = request.data
        logger.info(data.get("Actor_one"))
        logger.info(data.get("Actor_two"))
        my_url = "https://www.google.com/"
        uClient = uReq(my_url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        logger.info(page_soup)
        # product_name = page_soup.findAll("h1", {"class": "_3eAQiD"})[0].text
        return Response({"status": 200, "data": "Cool"})


class index(View):
    template_name = "index.html"

    def get(self, request):
        # logger.info(request.GET.get('abc'))
        return render(request, self.template_name, context={'name': request.GET.get('abc')})


class dataextract(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    def post(self,request):
        # headers = dict()
        # headers['Content-Type'] = "application/json"
        # headers['Authorization'] = "Basic %s" % settings.api_key_v4
        url = settings.tmdb_url + "search/person" + "?api_key=" + settings.api_key_v3 +"&query=Scarlett-Johansson" +"&language=en-US"
        "https://api.themoviedb.org/3/person/{person_id}?api_key=<<api_key>>&language=en-US"
        logger.info(url)
        response = requests.get(url)
        if response.ok:
            id=response.json().get('results')[0].get('id')
            # logger.info(response.get('results')[0].get('id'))
            # url-two =
            logger.info(settings.tmdb_url + "find/" + id + "?api_key=" + settings.api_key_v3 + "&external_source=imdb_id")

        return Response({"status": 200, "data": response.json()})