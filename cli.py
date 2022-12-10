#!/usr/bin/python3

import typer
from index import findSunSetRise, findPlanetRadius, findGreatestElongation, generateElongationChart
from rich import print
from helpers import loadConfig, PLANET_RADII, checkPlanetsSupport, correctPlanetNames

main = typer.Typer()
CONFIG = loadConfig()

planetsArg = typer.Argument(..., help="A comma seperated list of planets. E.g. 'sun,moon'")
eventsArg = typer.Argument(..., help="Comma seperated name of events to query. E.g. 'rise,set'")

@main.command()
def when(planets: str = planetsArg, events: str = eventsArg):
	"""
	Find out when certain [EVENTS] happen with [PLANETS]
	"""
	planets = planets.split(',')
	events = events.split(',')

	if not checkPlanetsSupport(planets, True):
		return

	for planet in planets:
		if(planet == 'sun'):
			Set, Rise = findSunSetRise()
			for event in events:
				if(event == 'set'): print(str(Set.time())[:8])
				if(event == 'rise'): print(str(Rise.time())[:8])

@main.command()
def place(planets: str = planetsArg):
	"""
	Get the location of planets
	"""
	planets = planets.split(',')

	if not checkPlanetsSupport(planets, False):
		return
	
	for planet in planets:
		print(planet)

@main.command()
def size(planets: str = planetsArg):
	"""
	Get the apparent size of planets in the sky (its "angular diameter" in arcseconds)
	"""
	planets = planets.split(',')

	if not checkPlanetsSupport(planets, False):
		return
	
	for planet in planets:
		print('{:.6f}'.format(findPlanetRadius(planet).arcseconds()))

@main.command()
def planets(planets: str = planetsArg):
	"""
	Display a list of all supported planet names
	"""
	print(list(PLANET_RADII.keys()))

@main.command()
def find_elongation(planeta: str = typer.Argument(..., help="The first planet. E.g. 'venus'"), planetb: str = typer.Argument(..., help="The second planet. E.g. 'sun'")):
	"""
	Finds the greatest distance in the sky between two planets
	"""
	findGreatestElongation(planeta, planetb)

@main.command()
def chart(chart = typer.Argument(..., help="The name of the chart. E.g. elongation"), 
	planeta: str = typer.Argument(..., help="The first planet. E.g. 'venus'"), 
	planetb: str = typer.Argument(..., help="The second planet. E.g. 'sun'"),
	days: int = typer.Option(7, help="The amount of days to step through"),
	step: int = typer.Option(12, help="The amount of hours to step by")):
	"""
	Generates various charts
	"""
	planeta, planetb = correctPlanetNames([planeta, planetb])
	generateElongationChart(planeta, planetb, days=days, step=step)

if __name__ == "__main__":
	main()