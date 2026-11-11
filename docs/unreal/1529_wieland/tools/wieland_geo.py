"""Map coordinates for the 1529 N. Wieland site, using nothing beyond Python's own library.

Three things, so that Phase 2 needs no map-projection package installed:

1. Latitude and longitude (degrees, on the GRS 80 ellipsoid that the North
   American Datum of 1983 uses) to and from Illinois State Plane East
   coordinates, zone 1201, in US survey feet. The county's older layers
   (EPSG 3435) and its 2022 layers (EPSG 6455, the 2011 adjustment) share
   this projection and differ only in the datum's realization, which this
   file does not model: a latitude and longitude go in and out on the same
   realization as the State Plane figures they are paired with.
2. The grid convergence and point scale at a place: how far grid north lies
   from true north, and how much the projection stretches distances.
3. State Plane coordinates to and from the Unreal level, once Phase 2 has
   chosen the level's origin and north. The level's axes are those of the
   existing model: -X is north, +Y is east, +Z is up, in centimetres.

The projection is the transverse Mercator in Krueger's series as extended by
Karney (2011) to sixth order; it is good to a fraction of a millimetre
anywhere in the zone.

Run this file to check it: it converts the county's two published parcel
centres both ways and prints the differences.

    python wieland_geo.py
"""

import json
import math

# GRS 80
A_AXIS = 6378137.0
FLATTENING = 1.0 / 298.257222101

# Illinois State Plane East, zone 1201 (NAD 83 and its 2011 adjustment)
LAT_ORIGIN_DEG = 36.0 + 40.0 / 60.0
LON_ORIGIN_DEG = -(88.0 + 20.0 / 60.0)
SCALE_ON_MERIDIAN = 0.999975
FALSE_EASTING_M = 300000.0
FALSE_NORTHING_M = 0.0

US_SURVEY_FOOT_M = 1200.0 / 3937.0
CM_PER_US_SURVEY_FOOT = US_SURVEY_FOOT_M * 100.0

_N = FLATTENING / (2.0 - FLATTENING)
_E = math.sqrt(FLATTENING * (2.0 - FLATTENING))
_RECTIFYING_RADIUS = A_AXIS / (1.0 + _N) * (1.0 + _N ** 2 / 4.0 + _N ** 4 / 64.0 + _N ** 6 / 256.0)

_ALPHA = (
    _N / 2 - 2 * _N ** 2 / 3 + 5 * _N ** 3 / 16 + 41 * _N ** 4 / 180 - 127 * _N ** 5 / 288 + 7891 * _N ** 6 / 37800,
    13 * _N ** 2 / 48 - 3 * _N ** 3 / 5 + 557 * _N ** 4 / 1440 + 281 * _N ** 5 / 630 - 1983433 * _N ** 6 / 1935360,
    61 * _N ** 3 / 240 - 103 * _N ** 4 / 140 + 15061 * _N ** 5 / 26880 + 167603 * _N ** 6 / 181440,
    49561 * _N ** 4 / 161280 - 179 * _N ** 5 / 168 + 6601661 * _N ** 6 / 7257600,
    34729 * _N ** 5 / 80640 - 3418889 * _N ** 6 / 1995840,
    212378941 * _N ** 6 / 319334400,
)
_BETA = (
    _N / 2 - 2 * _N ** 2 / 3 + 37 * _N ** 3 / 96 - _N ** 4 / 360 - 81 * _N ** 5 / 512 + 96199 * _N ** 6 / 604800,
    _N ** 2 / 48 + _N ** 3 / 15 - 437 * _N ** 4 / 1440 + 46 * _N ** 5 / 105 - 1118711 * _N ** 6 / 3870720,
    17 * _N ** 3 / 480 - 37 * _N ** 4 / 840 - 209 * _N ** 5 / 4480 + 5569 * _N ** 6 / 90720,
    4397 * _N ** 4 / 161280 - 11 * _N ** 5 / 504 - 830251 * _N ** 6 / 7257600,
    4583 * _N ** 5 / 161280 - 108847 * _N ** 6 / 3991680,
    20648693 * _N ** 6 / 638668800,
)


def _conformal_tangent(tau):
    """Tangent of the conformal latitude from the tangent of the geographic latitude."""
    sigma = math.sinh(_E * math.atanh(_E * tau / math.sqrt(1.0 + tau * tau)))
    return tau * math.sqrt(1.0 + sigma * sigma) - sigma * math.sqrt(1.0 + tau * tau)


def _xi_eta(lat_deg, lon_deg):
    phi = math.radians(lat_deg)
    lam = math.radians(lon_deg - LON_ORIGIN_DEG)
    tau_c = _conformal_tangent(math.tan(phi))
    xi_p = math.atan2(tau_c, math.cos(lam))
    eta_p = math.asinh(math.sin(lam) / math.sqrt(tau_c * tau_c + math.cos(lam) ** 2))
    xi, eta = xi_p, eta_p
    p, q = 1.0, 0.0
    for j, alpha in enumerate(_ALPHA, start=1):
        xi += alpha * math.sin(2 * j * xi_p) * math.cosh(2 * j * eta_p)
        eta += alpha * math.cos(2 * j * xi_p) * math.sinh(2 * j * eta_p)
        p += 2 * j * alpha * math.cos(2 * j * xi_p) * math.cosh(2 * j * eta_p)
        q += 2 * j * alpha * math.sin(2 * j * xi_p) * math.sinh(2 * j * eta_p)
    return xi, eta, tau_c, lam, phi, p, q


_XI_ORIGIN = _xi_eta(LAT_ORIGIN_DEG, LON_ORIGIN_DEG)[0]


def state_plane_from_lat_lon(lat_deg, lon_deg):
    """Easting and northing in US survey feet."""
    xi, eta = _xi_eta(lat_deg, lon_deg)[:2]
    east_m = FALSE_EASTING_M + SCALE_ON_MERIDIAN * _RECTIFYING_RADIUS * eta
    north_m = FALSE_NORTHING_M + SCALE_ON_MERIDIAN * _RECTIFYING_RADIUS * (xi - _XI_ORIGIN)
    return east_m / US_SURVEY_FOOT_M, north_m / US_SURVEY_FOOT_M


def lat_lon_from_state_plane(east_ft, north_ft):
    """Latitude and longitude in degrees."""
    eta = (east_ft * US_SURVEY_FOOT_M - FALSE_EASTING_M) / (SCALE_ON_MERIDIAN * _RECTIFYING_RADIUS)
    xi = (north_ft * US_SURVEY_FOOT_M - FALSE_NORTHING_M) / (SCALE_ON_MERIDIAN * _RECTIFYING_RADIUS) + _XI_ORIGIN
    xi_p, eta_p = xi, eta
    for j, beta in enumerate(_BETA, start=1):
        xi_p -= beta * math.sin(2 * j * xi) * math.cosh(2 * j * eta)
        eta_p -= beta * math.cos(2 * j * xi) * math.sinh(2 * j * eta)
    tau_c = math.sin(xi_p) / math.sqrt(math.sinh(eta_p) ** 2 + math.cos(xi_p) ** 2)
    lam = math.atan2(math.sinh(eta_p), math.cos(xi_p))
    tau = tau_c
    for _ in range(12):
        current = _conformal_tangent(tau)
        step = (tau_c - current) / math.sqrt(1.0 + current * current) * (1.0 + (1.0 - _E * _E) * tau * tau) / ((1.0 - _E * _E) * math.sqrt(1.0 + tau * tau))
        tau += step
        if abs(step) < 1e-15 * max(1.0, abs(tau)):
            break
    return math.degrees(math.atan(tau)), LON_ORIGIN_DEG + math.degrees(lam)


def convergence_and_scale(lat_deg, lon_deg):
    """Grid convergence in degrees and the point scale factor at a place.

    The convergence is the angle from true north to grid north, positive when
    grid north lies east (clockwise) of true north, as it does east of the
    zone's central meridian. A true bearing is the grid bearing plus this angle.
    """
    xi, eta, tau_c, lam, phi, p, q = _xi_eta(lat_deg, lon_deg)
    gamma = math.atan(tau_c / math.sqrt(1.0 + tau_c * tau_c) * math.tan(lam)) + math.atan2(q, p)
    tau = math.tan(phi)
    scale = (SCALE_ON_MERIDIAN * _RECTIFYING_RADIUS / A_AXIS
             * math.sqrt(1.0 - _E * _E * math.sin(phi) ** 2) * math.sqrt(1.0 + tau * tau)
             / math.sqrt(tau_c * tau_c + math.cos(lam) ** 2) * math.hypot(p, q))
    return math.degrees(gamma), scale


class LevelFrame:
    """The tie between State Plane coordinates and the Unreal level.

    origin_east_ft, origin_north_ft, origin_height_ft: the map point that sits
        at the level point (origin_x_cm, origin_y_cm, origin_z_cm).
    north_grid_bearing_deg: the grid bearing of the level's north (its -X axis),
        clockwise from grid north. Zero means the level's north is grid north.
    Heights are US survey feet above the map data's vertical datum.
    """

    def __init__(self, origin_east_ft, origin_north_ft, origin_height_ft=0.0, north_grid_bearing_deg=0.0,
                 origin_x_cm=0.0, origin_y_cm=0.0, origin_z_cm=0.0):
        self.origin_east_ft = float(origin_east_ft)
        self.origin_north_ft = float(origin_north_ft)
        self.origin_height_ft = float(origin_height_ft)
        self.north_grid_bearing_deg = float(north_grid_bearing_deg)
        self.origin_x_cm = float(origin_x_cm)
        self.origin_y_cm = float(origin_y_cm)
        self.origin_z_cm = float(origin_z_cm)

    def level_from_map(self, east_ft, north_ft, height_ft=None):
        theta = math.radians(self.north_grid_bearing_deg)
        d_east = east_ft - self.origin_east_ft
        d_north = north_ft - self.origin_north_ft
        along_north = d_east * math.sin(theta) + d_north * math.cos(theta)
        along_east = d_east * math.cos(theta) - d_north * math.sin(theta)
        x = self.origin_x_cm - along_north * CM_PER_US_SURVEY_FOOT
        y = self.origin_y_cm + along_east * CM_PER_US_SURVEY_FOOT
        if height_ft is None:
            return x, y
        return x, y, self.origin_z_cm + (height_ft - self.origin_height_ft) * CM_PER_US_SURVEY_FOOT

    def map_from_level(self, x_cm, y_cm, z_cm=None):
        theta = math.radians(self.north_grid_bearing_deg)
        along_north = -(x_cm - self.origin_x_cm) / CM_PER_US_SURVEY_FOOT
        along_east = (y_cm - self.origin_y_cm) / CM_PER_US_SURVEY_FOOT
        east = self.origin_east_ft + along_north * math.sin(theta) + along_east * math.cos(theta)
        north = self.origin_north_ft + along_north * math.cos(theta) - along_east * math.sin(theta)
        if z_cm is None:
            return east, north
        return east, north, self.origin_height_ft + (z_cm - self.origin_z_cm) / CM_PER_US_SURVEY_FOOT

    def to_dict(self):
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=1)

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))


# The county's own figures for the two parcel centres (SOURCES.md), used only by the check below.
COUNTY_PARCEL_CENTRES = (
    ("17-04-203-010-0000 (1529)", 41.9102490, -87.6353897, 1174226.83, 1910657.55),
    ("17-04-203-011-0000 (1527)", 41.9101811, -87.6353878, 1174227.55, 1910632.81),
)


def _check():
    print("Illinois State Plane East, US survey feet. County figures against this file's conversion.")
    forward = []
    for name, lat, lon, east, north in COUNTY_PARCEL_CENTRES:
        e, n = state_plane_from_lat_lon(lat, lon)
        forward.append((e, n))
        back_lat, back_lon = lat_lon_from_state_plane(e, n)
        la, lo = lat_lon_from_state_plane(east, north)
        print("%s" % name)
        print("  from latitude and longitude: east %.3f  north %.3f   county: %.2f  %.2f   difference %+.3f  %+.3f ft" % (
            e, n, east, north, e - east, n - north))
        print("  from the county's east and north: latitude %.7f  longitude %.7f   county: %.7f  %.7f" % (la, lo, lat, lon))
        print("  there and back: %.2e degrees of latitude, %.2e of longitude" % (abs(back_lat - lat), abs(back_lon - lon)))
    d_e = forward[1][0] - forward[0][0]
    d_n = forward[1][1] - forward[0][1]
    c_e = COUNTY_PARCEL_CENTRES[1][3] - COUNTY_PARCEL_CENTRES[0][3]
    c_n = COUNTY_PARCEL_CENTRES[1][4] - COUNTY_PARCEL_CENTRES[0][4]
    print("from the first centre to the second: this file %+.3f east %+.3f north; county %+.2f east %+.2f north" % (d_e, d_n, c_e, c_n))
    gamma, scale = convergence_and_scale(COUNTY_PARCEL_CENTRES[0][1], COUNTY_PARCEL_CENTRES[0][2])
    print("at the first centre: grid north lies %.4f degrees east of true north; point scale %.8f (%.1f mm in 100 m)" % (
        gamma, scale, (scale - 1.0) * 100000.0))
    frame = LevelFrame(1174200.0, 1910600.0, 595.0, north_grid_bearing_deg=-1.7, origin_x_cm=100.0, origin_y_cm=-200.0, origin_z_cm=5.0)
    x, y, z = frame.level_from_map(1174250.0, 1910700.0, 600.0)
    e, n, h = frame.map_from_level(x, y, z)
    print("level frame there and back: %.2e ft east, %.2e ft north, %.2e ft height" % (abs(e - 1174250.0), abs(n - 1910700.0), abs(h - 600.0)))
    north_x, north_y = frame.level_from_map(1174200.0 + math.sin(math.radians(-1.7)) * 100.0, 1910600.0 + math.cos(math.radians(-1.7)) * 100.0)
    print("a point 100 ft along the level's north lands at x %+.2f cm, y %+.2f cm from the origin (expect x -3048.01, y 0.00)" % (north_x - 100.0, north_y + 200.0))


if __name__ == "__main__":
    _check()
