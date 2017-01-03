import psycopg2
import time
import os
def query_pokemon_from_db(north, south, west, east):
	#1. open db connection
        conn = psycopg2.connect(host=os.environ["DB_HOST"], port = 5432, database=os.environ["DB_NAME"], user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"])

	#2. Executre SQL
	with conn.cursor() as cur:
		# cur.execute("INSERT INTO pokemon_map(encounter_id, expire, pokemon_id, latitude, longitude)" + " VALUES(%s,%s,%s,%s,%s)" + " ON CONFLICT(encounter_id) DO NOTHING;", (encounter_id, expire, pokemon_id, latitude, longitude))
		cur.execute("select pokemon_id, expire, latitude, longitude" + 
				" from pokemon_map" + 
				" where latitude < %s" + 
				" and latitude > %s" + 
				" and longitude < %s" + 
				" and longitude > %s" + 
				" and expire > %s" + 
				" limit 100;", 
				(north, south, east, west, time.time() * 1000))
		items = cur.fetchall()
		pokemons = []
		for item in items:
			pokemon = {"latitude": item[2],
					"longitude": item[3],
					"expire": item[1] / 1000,
					"pokemon_id": item[0]}
			pokemons.append(pokemon)
		#print items
	#3. connection commit
	# conn.commit()
	conn.close()
	return pokemons

if __name__ == "__main__":
	#add_pokemon_to_db(41,40.99,-73.99,-73.98)
	print query_pokemon_from_db(41,40.99,-73.99,-73.98)
