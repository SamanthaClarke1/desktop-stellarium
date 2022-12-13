#!/usr/bin/python3

import typer
from index import findSunSetRise, graphPlacesInSky, findPlanetRadius, findGreatestElongation, generateElongationChart, checkWhenPlanetInSky
from rich import print
from helpers import loadConfig, PLANET_RADII, checkPlanetsSupport, correctPlanetNames

main = typer.Typer()
CONFIG = loadConfig()

planetsArg = typer.Argument(..., help="A comma seperated list of planets. E.g. 'sun,moon'")
eventsArg = typer.Argument(..., help="Comma seperated name of events to query. E.g. 'rise,set'")

@main.command()
def when(planets: str = planetsArg,
	events: str = eventsArg,
	format: str = typer.Option('%a %d %H:%M', help='Strftime format string. E.g. %d %H:%M'), 
	search: int = typer.Option(24, help='Number of hours to search ahead.')):
	"""
	Find out when certain [EVENTS] happen with [PLANETS]
	"""
	planets = planets.split(',')
	events = events.split(',')

	if not checkPlanetsSupport(planets):
		return

	for planet in planets:
		for event in events:
			if(event in ['set', 'rise']):
				sets, rises = checkWhenPlanetInSky(planet)
				if event == 'set': print(sets.strftime(format))
				if event == 'rise': print(rises.strftime(format))
			else:
				print("ERROR: Invalid event", event)

@main.command()
def is_star(planets: str = planetsArg, star_type = typer.Argument("evening", help="'evening' | 'morning' - check if evening star or morning star")):
	"""
	Checks if a star is an evening or morning star.
	"Evening star" meaning that it sets after the sun, and is visible at night.
	"Morning star" meaning that it rises before the sun, and is visible in early morning.
	"""
	planets = planets.split(',')

	if not checkPlanetsSupport(planets):
		return

	sunset, sunrise = checkWhenPlanetInSky('sun')
	# we replace the year, month, and days here so that we're comparing time of day- not TIME.
	sunset = sunset.replace(year=2000, month=1, day=1) 
	sunrise = sunrise.replace(year=2000, month=1, day=1)

	for planet in planets:
		planetset, planetrise = checkWhenPlanetInSky(planet)
		planetset = planetset.replace(year=2000, month=1, day=1)
		planetrise = planetrise.replace(year=2000, month=1, day=1)
		if(star_type == "evening"):
			if(sunset < planetset): print(planet, "is currently an evening star. It sets", planetset-sunset, "later")
			else: print(planet, "is not currently an evening star.")
		if(star_type == "morning"):
			if(sunrise > planetrise): print(planet, "is currently a morning star. It rises", sunrise-planetrise, "earlier")
			else: print(planet, "is not currently a morning star.")


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
def see_planets(planets: str = planetsArg,
	size: int = typer.Option(7, help="The size of the chart"),
	pad: int = typer.Option(15, help="The padding around the sides of the chart"),
	vpad: int = typer.Option(3, help="The padding above and below the chart"),
	horiz_empt: str = typer.Option('.', help="The horizontal empty chart character"),
	vert_empt: str = typer.Option('.', help="The horizontal empty chart character"),
	display_you: bool = typer.Option(True, help="Whether or not to display 'you <3' in the centre of the chart"),
	use_ra: bool = typer.Option(False, help="Use RA or DEC")):
	"""
	Generates a visualisation of the planets in the night sky, based on their angle from the observer.
	e.g. see-planets venus,mars,sun,pluto --size=7 --horiz-empt=x --vert-empt=x --pad=10
	"""
	planets = planets.split(',')

	if not checkPlanetsSupport(planets, False):
		return
	planets = correctPlanetNames(planets)

	graphPlacesInSky(planets, size, use_ra, pad, vpad, horiz_empt, vert_empt, display_you)


@main.command()
def elong_chart(planeta: str = typer.Argument(..., help="The first planet. E.g. 'venus'"), 
	planetb: str = typer.Argument(..., help="The second planet. E.g. 'sun'"),
	days: int = typer.Option(7, help="The amount of days to step through"),
	step: int = typer.Option(12, help="The amount of hours to step by")):
	"""
	Generates a chart showing the distance between two planets over time
	"""
	planeta, planetb = correctPlanetNames([planeta, planetb])
	generateElongationChart(planeta, planetb, days=days, step=step)

if __name__ == "__main__":
	main()