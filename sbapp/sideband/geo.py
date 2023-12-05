import time
import RNS
from math import pi, sin, cos, acos, asin, tan, atan, atan2
from math import radians, degrees, sqrt

# WGS84 Parameters
# a  = 6378137.0,
# f  = 0.0033528106647474805,
# e2 = 0.0066943799901413165,
# b  = 6356752.314245179,

# Planetary metrics
equatorial_radius    = 6378.137 *1e3
polar_radius         = 6356.7523142 *1e3
ellipsoid_flattening = 1-(polar_radius/equatorial_radius)
eccentricity_squared = 2*ellipsoid_flattening-pow(ellipsoid_flattening,2)
###############################

mean_earth_radius    = (1/3)*(2*equatorial_radius+polar_radius)

def geocentric_latitude(geodetic_latitude):
    e2  = eccentricity_squared
    lat = radians(geodetic_latitude)
    return degrees(atan((1.0 - e2) * tan(lat)))

def geodetic_latitude(geocentric_latitude):
    e2  = eccentricity_squared
    lat = radians(geocentric_latitude)
    return degrees(atan( (1/(1.0 - e2)) * tan(lat)))

def ellipsoid_radius_at(latitude):
    lat = radians(latitude)
    a = equatorial_radius; b = polar_radius;
    a2 = pow(a,2); b2 = pow(b,2)
    r   = sqrt(
        ( pow(a2*cos(lat), 2) + pow(b2*sin(lat), 2) )
                              /
         ( pow(a*cos(lat), 2) + pow(b*sin(lat), 2) )
    )
    return r

def euclidian_point(latitude, longitude, altitude=0, ellipsoid=True):
    # Convert latitude and longitude to radians
    # and get ellipsoid or sphere radius
    lat   = radians(latitude); lon = radians(longitude)
    r     = ellipsoid_radius_at(latitude) if ellipsoid else mean_earth_radius

    # Calculate euclidian coordinates from longitude
    # and geocentric latitude.
    gclat = radians(geocentric_latitude(latitude)) if ellipsoid else lat
    x = cos(lon)*cos(gclat)*r
    y = cos(gclat)*sin(lon)*r
    z = sin(gclat)*r

    # Calculate surface normal of ellipsoid at
    # coordinates to add altitude to point
    normal_x = cos(lat)*cos(lon)
    normal_y = cos(lat)*sin(lon)
    normal_z = sin(lat)

    if altitude != 0:
        x += altitude*normal_x
        y += altitude*normal_y
        z += altitude*normal_z

    return (x,y,z, normal_x, normal_y, normal_z)

def distance(p1, p2):
    dx = p1[0]-p2[0]
    dy = p1[1]-p2[1]
    dz = p1[2]-p2[2]
    return sqrt(dx*dx + dy*dy + dz*dz)

def euclidian_distance(c1, c2, ellipsoid=True):
    lat1 = c1[0]; lon1 = c1[1]; alt1 = c1[2]
    lat2 = c2[0]; lon2 = c2[1]; alt2 = c2[2]
    if len(c1) >= 2 and len(c2) >= 2:
        if len(c1) == 2: c1 += (0,)
        if len(c2) == 2: c2 += (0,)
        return distance(
            euclidian_point(lat1, lon1, alt1, ellipsoid=ellipsoid),
            euclidian_point(lat2, lon2, alt2, ellipsoid=ellipsoid)
        )
    else:
        return None

def central_angle(c1, c2):
    lat1 = radians(c1[0]); lon1 = radians(c1[1])
    lat2 = radians(c2[0]); lon2 = radians(c2[1])

    d_lat = abs(lat1-lat2)
    d_lon = abs(lon1-lon2)
    ca    = acos(
        sin(lat1) * sin(lat2) +
        cos(lat1) * cos(lat2) * cos(d_lon)
    )
    return ca

def arc_length(central_angle, r=mean_earth_radius):
    return r*central_angle;

def spherical_distance(c1, c2, altitude=0, r=mean_earth_radius):
    d = (r+altitude)*central_angle(c1, c2)
    return d

def ellipsoid_distance(c1, c2):
    # TODO: Update this to the method described by Karney in 2013
    # instead of using Vincenty's algorithm.
    try:
        if c1[:2] == c2[:2]:
            return 0

        if c1[0] == 0.0: c1 = (1e-6, c1[1])
        a = equatorial_radius
        f = ellipsoid_flattening
        b = (1 - f)*a # polar radius
        tolerance = 1e-9 # to stop iteration

        phi1, phi2 = radians(c1[0]), radians(c2[0])
        U1 = atan((1-f)*tan(phi1))
        U2 = atan((1-f)*tan(phi2))
        L1, L2 = radians(c1[1]), radians(c2[1])
        L = L2 - L1

        lambda_old = L + 0

        max_iterations = 10000
        iteration = 0
        timeout = 1.0
        st = time.time()
        while True:
            iteration += 1
            t = (cos(U2)*sin(lambda_old))**2
            t += (cos(U1)*sin(U2) - sin(U1)*cos(U2)*cos(lambda_old))**2
            sin_sigma = t**0.5
            cos_sigma = sin(U1)*sin(U2) + cos(U1)*cos(U2)*cos(lambda_old)
            sigma = atan2(sin_sigma, cos_sigma)
        
            sin_alpha = cos(U1)*cos(U2)*sin(lambda_old) / sin_sigma
            cos_sq_alpha = 1 - sin_alpha**2
            cos_2sigma_m = cos_sigma - 2*sin(U1)*sin(U2)/cos_sq_alpha
            C = f*cos_sq_alpha*(4 + f*(4-3*cos_sq_alpha))/16
        
            t = sigma + C*sin_sigma*(cos_2sigma_m + C*cos_sigma*(-1 + 2*cos_2sigma_m**2))
            lambda_new = L + (1 - C)*f*sin_alpha*t
            if abs(lambda_new - lambda_old) <= tolerance:
                break
            else:
                lambda_old = lambda_new

            if iteration%1000 == 0:
                if iteration >= max_iterations:
                    return None
                
                if time.time() > st+timeout:
                    return None

        u2 = cos_sq_alpha*((a**2 - b**2)/b**2)
        A = 1 + (u2/16384)*(4096 + u2*(-768+u2*(320 - 175*u2)))
        B = (u2/1024)*(256 + u2*(-128 + u2*(74 - 47*u2)))
        t = cos_2sigma_m + 0.25*B*(cos_sigma*(-1 + 2*cos_2sigma_m**2))
        t -= (B/6)*cos_2sigma_m*(-3 + 4*sin_sigma**2)*(-3 + 4*cos_2sigma_m**2)
        delta_sigma = B * sin_sigma * t
        s = b*A*(sigma - delta_sigma)
        return s

    except Exception as e:
        return None

def azalt(c1, c2, ellipsoid=True):              
    c2rp = rotate_globe(c1, c2, ellipsoid=ellipsoid)
    altitude = None
    azimuth = None
    if (c2rp[2]*c2rp[2]) + (c2rp[1]*c2rp[1]) > 1e-6:
        theta = degrees(atan2(c2rp[2], c2rp[1]))
        azimuth = 90 - theta
        if azimuth < 0: azimuth += 360
        if azimuth > 360: azimuth -= 360
        azimuth = round(azimuth,4)

    c1p = euclidian_point(c1[0], c1[1], c1[2], ellipsoid=ellipsoid)
    c2p = euclidian_point(c2[0], c2[1], c2[2], ellipsoid=ellipsoid)
    nvd = normalised_vector_diff(c2p, c1p)
    if nvd != None:
        cax = nvd[0]; cay = nvd[1]; caz = nvd[2]
        cnx = c1p[3]; cny = c1p[4]; cnz = c1p[5]
        a = acos(cax*cnx + cay*cny + caz*cnz)
        altitude = round(90 - degrees(a),4)

    return (azimuth, altitude,4)

def normalised_vector_diff(b, a):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    d_squared = dx*dx + dy*dy + dz*dz
    if d_squared == 0:
        return None

    d = sqrt(d_squared)
    return (dx/d, dy/d, dz/d)

def rotate_globe(c1, c2, ellipsoid=True):
    if len(c1) >= 2 and len(c2) >= 2:
        if len(c1) == 2: c1 += (0,)
        if len(c2) == 2: c2 += (0,)

        c2r  = (c2[0], c2[1]-c1[1], c2[2])
        c2rp = euclidian_point(c2r[0], c2r[1], c2r[2], ellipsoid=ellipsoid)

        lat1 = -1*radians(c1[0])
        if ellipsoid:
            lat1 = radians(geocentric_latitude(degrees(lat1)))

        lat1cos = cos(lat1)
        lat1sin = sin(lat1)

        c2x = (c2rp[0] * lat1cos) - (c2rp[2] * lat1sin)
        c2y = c2rp[1]
        c2z = (c2rp[0] * lat1sin) + (c2rp[2] * lat1cos)

        return (c2x, c2y, c2z)

def orthodromic_distance(c1, c2, ellipsoid=True):
    if ellipsoid:
        return ellipsoid_distance(c1, c2)
    else:
        return spherical_distance(c1, c2)

def distance_to_horizon(c, ellipsoid=False):
    if ellipsoid:
        raise NotImplementedError("Distance to horizon on the ellipsoid is not yet implemented")
    else:
        # TODO: This is a only barely functional simplification.
        # Need to calculate the geodesic distance to the horizon
        # instead.
        if len(c) >= 3:
            r = mean_earth_radius
            h = c[2]
            return sqrt(pow((h+r),2) - r*r)
        else:
            return None

def angle_to_horizon(c, ellipsoid=False):
    if ellipsoid:
        raise NotImplementedError("Angle to horizon on the ellipsoid is not yet implemented")
    else:
        r = mean_earth_radius
        h = c[2]
        if h < 0: h = 0
        return degrees(-acos(r/(r+h)))

def euclidian_horizon_distance(h):
    r = mean_earth_radius
    b = r
    c = r+h
    a = c**2 - b**2
    return sqrt(a)

def euclidian_horizon_arc(h):
    r = mean_earth_radius
    d = euclidian_horizon_distance(h)
    a = d; b = r; c = r+h
    arc = acos( (b**2+c**2-a**2) / (2*b*c) )
    return arc

def radio_horizon(h, rh=0, ellipsoid=False):
    if ellipsoid:
        raise NotImplementedError("Radio horizon on the ellipsoid is not yet implemented")
    else:
        geocentric_angle_to_horizon = euclidian_horizon_arc(h)
        geodesic_distance = arc_length(geocentric_angle_to_horizon, r=mean_earth_radius)

        return geodesic_distance

def shared_radio_horizon(c1, c2,):
    lat1 = c1[0]; lon1 = c1[1]; h1 = c1[2]
    lat2 = c2[0]; lon2 = c2[1]; h2 = c2[2]
    
    geodesic_distance = orthodromic_distance((lat1, lon1, 0.0), (lat2, lon2, 0.0) , ellipsoid=False)
    antenna_distance = euclidian_distance(c1,c2,ellipsoid=False)
    rh1 = radio_horizon(h1)
    rh2 = radio_horizon(h2)
    rhc = rh1+rh2

    return {
        "horizon1":rh1, "horizon2":rh2, "shared":rhc,
        "within":rhc > geodesic_distance,
        "geodesic_distance": geodesic_distance,
        "antenna_distance": antenna_distance
    }

def ghtest():
    import pygeodesy
    from pygeodesy.ellipsoidalKarney import LatLon
    ginterpolator = pygeodesy.GeoidKarney("./assets/geoids/egm2008-5.pgm")

    # Make an example location
    lat=51.416422
    lon=-116.217151

    # Get the geoid height
    single_position=LatLon(lat, lon)
    h = ginterpolator(single_position)
    print(h)

# def tests():
#     import RNS
#     import numpy as np
#     from geographiclib.geodesic import Geodesic
#     geod = Geodesic.WGS84
#     coords = [
#         [(51.2308, 4.38703, 0.0), (47.699437, 9.268651, 0.0)],
#         [(51.2308, 4.38703, 0.0), (47.699437, 9.268651, 30.0*1e3)],
#         [(0.0, 0.0, 0.0), (0.0, 1.0/60/60, 30.0)],
#         # [(51.230800, 4.38703, 0.0), (51.230801, 4.38703, 0.0)],
#         # [(35.3524, 135.0302, 100), (35.3532,135.0305, 500)],
#         # [(57.758793, 22.605194, 0.0), (43.048838, -9.241343, 0.0)],
#         # [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],
#         # [(-90.0, 0.0, 0.0), (90.0, 0.0, 0.0)],
#         # [(-90.0, 0.0, 0.0), (78.0, 0.0, 0.0)],
#         # [(0.0, 0.0, 0.0), (0.5, 179.5, 0.0)],
#         # [(0.7, 0.0, 0.0), (0.0, -180.0, 0.0)],
#     ]
#     for cs in coords:
#         c1 = cs[0]; c2 = cs[1]
#         print("Testing: "+str(c1)+"  ->  "+str(c2))
#         us = time.time()
#         ld = c1+c2; g = geod.Inverse(c1[0], c1[1], c2[0], c2[1])
#         print("Lib computed in "+str(round((time.time()-us)*1e6, 3))+"us")
#         us = time.time()        
#         eld = orthodromic_distance(c1,c2,ellipsoid=True)
#         if eld:
#             print("Own computed in "+str(round((time.time()-us)*1e6, 3))+"us")
#         else:
#             print("Own timed out in "+str(round((time.time()-us)*1e6, 3))+"us")
#         ed_own = euclidian_distance(c1,c2,ellipsoid=True)
#         sd_own = orthodromic_distance(c1,c2,ellipsoid=False)
#         aa = azalt(c1,c2,ellipsoid=True)
#         fac = 1
#         if eld: print("LibDiff   = "+RNS.prettydistance(g['s12']-eld)+f"  {fac*g['s12']-fac*eld}")
#         print("Spherical = "+RNS.prettydistance(sd_own)+f" {fac*sd_own}")
#         # print("EllipLib  = "+RNS.prettydistance(g['s12'])+f" {fac*g['s12']}")
#         if eld: print("Ellipsoid = "+RNS.prettydistance(eld)+f" {fac*eld}")
#         print("Euclidian = "+RNS.prettydistance(ed_own)+f" {fac*ed_own}")
#         print("AzAlt     = "+f" {aa[0]} / {aa[1]}")
#         print("")
