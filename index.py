#!/usr/bin/python3

import numpy as np
import datetime as dt
from uniplot import plot
from datetime import timedelta
from skyfield import almanac
from skyfield.api import load, Angle
from skyfield.framelib import ecliptic_frame
from skyfield.searchlib import find_maxima
from helpers import loadConfig, getNow, getPosition, PLANET_RADII

CONFIG = loadConfig()
eph = load('de421.bsp')
ts = load.timescale()

def findSunSetRise(eph=eph):
	now, zone = getNow(CONFIG)
	midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
	next_midnight = midnight + dt.timedelta(days=1)

	t0 = ts.from_datetime(midnight) # start time of search in almanac
	t1 = ts.from_datetime(next_midnight) # end time of search in almanac

	position = getPosition(CONFIG)
	f = almanac.sunrise_sunset(eph, position)
	times, events = almanac.find_discrete(t0, t1, f)

	Set = times[np.where(events == 0)][0].astimezone(zone)
	Rise = times[np.where(events == 1)][0].astimezone(zone)

	return (Set, Rise)

def findPlanetRadec(planetName, eph=eph):
	radius_km = PLANET_RADII[planetName]
	earth, planet = eph['earth'], eph[planetName]
	now, zone = getNow(CONFIG)

	astrometric = earth.at(ts.from_datetime(now)).observe(planet)
	ra, dec, distance = astrometric.apparent().radec()
	return (ra, dec, distance, radius_km)

def findPlanetRadius(planet, eph=eph):
	ra, dec, dist, rad = findPlanetRadec(planet, eph)
	return Angle(radians=np.arcsin(rad / dist.km) * 2.0)

def spiceElongationAt(planet1, planet2, earth):
	def elongation_at(t):
		e = earth.at(t)
		s = e.observe(planet1).apparent()
		v = e.observe(planet2).apparent()
		return s.separation_from(v).degrees
	return elongation_at

def findGreatestElongation(planet1Name, planet2Name, eph=eph, days=600, step=15):
	now, zone = getNow(CONFIG)
	t0 = ts.from_datetime(now)
	t1 = ts.from_datetime(now + timedelta(days=days))

	planet1, earth, planet2 = eph[planet1Name], eph['earth'], eph[planet2Name]

	elongation_at = spiceElongationAt(planet1, planet2, earth)
	elongation_at.step_days = step
	times, elongations = find_maxima(t0, t1, elongation_at)

	for t, elongation_degrees in zip(times, elongations):
		e = earth.at(t)
		_, slon, _ = e.observe(planet1).apparent().frame_latlon(ecliptic_frame)
		_, vlon, _ = e.observe(planet2).apparent().frame_latlon(ecliptic_frame)
		is_east = (vlon.degrees - slon.degrees) % 360.0 < 180.0
		direction = 'east' if is_east else 'west'
		print('{}  {:4.1f}° {} elongation'.format(
			t.utc_strftime(), elongation_degrees, direction))

def generateElongationChart(planet1Name, planet2Name, eph=eph, days=60, step=24*4):
	planet1, planet2, earth = eph[planet1Name], eph[planet2Name], eph['earth']
	elongation_at = spiceElongationAt(planet1, planet2, earth)
	now, zone = getNow(CONFIG)
	now = now.replace(hour=21, minute=0, second=0, microsecond=0)
	t0 = ts.from_datetime(now)

	elongations = []
	for dp in range(0, days*24, step):
		t1 = ts.from_datetime(now + timedelta(hours=dp))
		elongation_deg = elongation_at(t1)
		elongations.append(elongation_deg)

	plot(elongations, title="Distance between "+planet1Name+" and "+planet2Name+" as viewed from earth.", y_unit='°', lines=True)



