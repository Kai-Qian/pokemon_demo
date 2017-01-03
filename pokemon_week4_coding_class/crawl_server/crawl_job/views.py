import json

import logging
import redis
import os

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from scan_area import scan_point
from db_accessor import add_pokemon_to_db

# Create your views here.

redis_client = redis.StrictRedis(host=os.environ["REDIS_HOST"], port = 6379, db = 0)

def crawl_point(request):
    """ Rquest body contains a json format object, which has a key "cell_id" """
    request_obj = json.loads(request.body)
    print request.body
    print request_obj
    cell_id = request_obj["cell_id"]
    print cell_id
    # Check redis, if cell already crawled, skip it
    val = redis_client.get(cell_id)
    #print val    
    # print "test"
    if val == "1":
	return JsonResponse("Skipped", safe=False)
    # If not crawled, set the key in redis, crawl this cell
    redis_client.setex(cell_id, 60, "1")

    logging.getLogger("crawler").info("Crawling cell: {0}".format(cell_id))
    
    pokemons = scan_point(cell_id)
    #print "test1"
   # print pokemons
   # print "test2"
    logging.getLogger("crawler").info("Pokemon: {0}".format(pokemons))    
   
    for pokemon in pokemons:
        add_pokemon_to_db(pokemon["encounter_id"], pokemon["expiration_timestamp_ms"], pokemon["pokemon_id"], pokemon["latitude"], pokemon["longitude"])
    return JsonResponse(pokemons, safe=False)
    
