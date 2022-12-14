#!/usr/bin/python3

import numpy as np
import datetime as dt
from uniplot import plot
from datetime import timedelta
from skyfield import almanac
from skyfield.api import load, Angle, Star
from skyfield.framelib import ecliptic_frame
from skyfield.searchlib import find_maxima
from skyfield.almanac import find_discrete, risings_and_settings
from helpers import loadConfig, getNow, getPosition, PLANET_RADII, correctPlanetNames, angleComparedToRVec

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
		print('{}  {:4.1f}?? {} elongation'.format(
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

	plot(elongations, title="Distance between "+planet1Name+" and "+planet2Name+" as viewed from earth.", y_unit='??', lines=True)

def graphPlacesInSky(planetNames, size=20, use_ra=False, pad=6, vpad=2, horiz_empt='x', vert_empt='|', display_you=True):
	now, zone = getNow(CONFIG)
	t = ts.from_datetime(now)
	moab = getPosition(CONFIG)

	planetPositions = []
	for planetName in planetNames:
		planet, earth = eph[planetName], eph['earth']
		vpos = (earth + moab).at(t) # vpos = viewers position
		a = vpos.observe(planet).apparent()
		ra, dec, dist = a.radec()
		deg = ra._degrees if use_ra else dec._degrees
		deg = deg if deg >= 0 else deg+360
		planetPositions.append([planetName, deg, ra._degrees, dec._degrees, round(dist.km/100000)/10])

	xyPositions = []
	for x in range(-size, size): #
		xyPositions.append([x,  size, angleComparedToRVec([x,  size])])
		xyPositions.append([x, -size, angleComparedToRVec([x, -size])])
	for y in range(-size, size):
		xyPositions.append([ size, y, angleComparedToRVec([ size, y])])
		xyPositions.append([-size, y, angleComparedToRVec([-size, y])])
	def takeDeg(e): return e[2]
	xyPositions.sort(key=takeDeg)

	BUF = []
	for y in range(0, size*2+vpad*2):
		BUF.append(['  ' for i in range(0, pad*2+size*2)])

	pdeg = xyPositions[-1][2] # previous degree grabbed from last xypos
	hasDisplayedTop = 0 # record when it displays top/bottom so it can put the labels ABOVE the other labels, instead of THROUGH them
	hasDisplayedBot = 0
	for pos in xyPositions:
		tx, ty = (pos[0]+size+pad, pos[1]+size)
		planetsToPutHere = []
		for ppos in planetPositions:
			if(ppos[1] > pdeg and ppos[1] < pos[2]): # planet should be put here!
				planetsToPutHere.append(ppos)

		if len(planetsToPutHere) == 0:
			if ty == size*2 or ty == 0: BUF[ty+vpad][tx] = ' '+horiz_empt
			else: BUF[ty+vpad][tx] = ' '+vert_empt
		else: # planet found! generate a planet string!
			ppos = planetsToPutHere[0]
			tstr = ppos[0][:5] + ", " + str(ppos[4]) + " mkm away"
			if len(planetsToPutHere) > 1: tstr += " +" + str(len(planetsToPutHere)-1)
			
			BUF[ty+vpad][tx] = ' '+'X' #str(len(planetsToPutHere))
			# now insert the str
			offset = 1 if ty == size*2 else -1 if ty == 0 else 0
			noff = offset + vpad + (hasDisplayedBot if ty == size*2 else -hasDisplayedTop if ty == 0 else 0)
			if offset == -1: hasDisplayedTop += 1
			if offset ==  1: hasDisplayedBot += 1

			roff, loff = (6, -6)
			if tx-pad == size*2: roff, loff = (14, 2) # on display right
			if tx-pad == 0: roff, loff = (2, 14) # on display left
			tStrAligned = tstr[:24].center(24, ' ') if roff == 6 else tstr[:24].ljust(24, ' ') if roff == 2 else tstr[:24].rjust(24, ' ')

			BUF[ty+noff][tx+loff:tx+roff] = list(tStrAligned)

		pdeg = pos[2]
	if(display_you): BUF[size+vpad][size+pad-1:size+pad+3] = list(' you <3 ')
	BUF[size*2+vpad][size*2+pad] = ' '+horiz_empt
	
	print('\n'.join(''.join(innerBUF) for innerBUF in BUF))



def checkWhenPlanetInSky(planetName, h=24):
	now, zone = getNow(CONFIG)
	t0 = ts.from_datetime(now)
	t1 = ts.from_datetime(now + timedelta(hours=h))

	moab = getPosition(CONFIG)
	planet = correctPlanetNames([planetName])[0]
	gc = eph[planet]

	f = risings_and_settings(eph, gc, moab)

	sets, rises = None, None
	for t, updown in zip(*find_discrete(t0, t1, f)):
		if updown: rises = t.astimezone(zone)
		else: sets = t.astimezone(zone)

	return sets, rises
