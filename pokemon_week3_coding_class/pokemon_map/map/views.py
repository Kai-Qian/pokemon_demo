from django.shortcuts import render
from django.http import JsonResponse
from db_accessor import *
from scan_area import scan_area
# Create your views here.
def pokemons(request):
	north = float(request.GET["north"])
	south = float(request.GET["south"])
	west = float(request.GET["west"])
	east = float(request.GET["east"])
	
	result = query_pokemon_from_db(north, south, west, east)
	scan_area(north, south, west, east)
	return JsonResponse(result, safe=False)
