import json

import logging

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from scan_area import scan_point
from db_accessor import add_pokemon_to_db
# Create your views here.

def crawl_point(request):
    """ Rquest body contains a json format object, which has a key "cell_id" """
    request_obj = json.loads(request.body)

    cell_id = request_obj["cell_id"]

    logging.getLogger("crawler").info("Crawling cell: {0}".format(cell_id))
    
    pokemons = scan_point(cell_id)

    logging.getLogger("crawler").info("Pokemon: {0}".format(pokemons))    

    for pokemon in pokemons:
        add_pokemon_to_db(pokemon["encounter_id"], pokemon["expiration_timestamp_ms"], pokemon["pokemon_id"], pokemon["latitude"], pokemon["longitude"])
    return JsonResponse(pokemons, safe=False)
    
