#!/usr/bin/python3

import json
from pytz import timezone
import datetime as dt
from skyfield.api import wgs84

# CONSTANTS
PLANET_RADII = {
	"jupiter": 69911,
	"uranus": 25362,
	"mercury": 2439.7,
	"mars": 3389.5,
	"neptune": 24764,
	"earth": 6371,
	"saturn": 58232,
	"venus": 6051.8
}

# FUNCS
def correctPlanetNames(planets):
	nplanets = []
	for planet in planets:
		if planet in ['mercury', 'jupiter', 'pluto', 'uranus', 'saturn', 'neptune']:
			nplanets.append(planet + " barycenter")
		else:
			nplanets.append(planet)

	return nplanets

def checkPlanetsSupport(planets, sm=False):
	for planet in planets:
		if not planetSupported(planet, sm):
			print("ERROR: Planet", planet, "is not supported by this command.")
			return False
	return True

def planetSupported(planet, sm=False):
	if(sm): return planet == "sun" or planet == "moon"
	else: return planet in PLANET_RADII.keys()

def getPosition(CONFIG):
	position = wgs84.latlon(CONFIG['lat'], CONFIG['long'], CONFIG['elevation'])
	return position

def getNow(CONFIG):
	zone = timezone(CONFIG['timezone'])
	now = zone.localize(dt.datetime.now())
	return (now, zone)

def loadConfig(f="./config.json"):
	f = open(f)

	CONFIG = {
		"lat": -28.509160,
		"long": 153.405900,
		"elevation": 0.0,
		"timezone": "Australia/Sydney"
	}
	if f is not None:
		c2 = json.load(f)
		# this kinda stuff makes me miss typescript. A.a = A.a || B.a - MUCH simpler.
		for k in ['lat', 'long', 'elevation', 'timezone']:
			CONFIG[k] = tryOverrideA(CONFIG, c2, k)

	return CONFIG

def tryOverrideA(a, b, k):
	if b[k]: return b[k]
	return a[k]
