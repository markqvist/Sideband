import RNS
import time
from math import pi, sin, cos, acos, tan, atan, atan2
from math import radians, degrees, sqrt


# Default planetary metrics
equatorial_radius    = 6378.137     *1e3
polar_radius         = 6356.7523142 *1e3
ellipsoid_flattening = 1-(polar_radius/equatorial_radius)
eccentricity_squared = 2*ellipsoid_flattening-pow(ellipsoid_flattening,2)
mean_earth_radius    = (1/3)*(2*equatorial_radius+polar_radius)

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

def euclidian_point(latitude, longtitude, altitude=0, ellipsoid=True):
    # Convert latitude and longtitude to radians
    # and get ellipsoid or sphere radius
    lat   = radians(latitude); lon = radians(longtitude)
    r     = ellipsoid_radius_at(latitude) if ellipsoid else mean_earth_radius

    # Calculate euclidian coordinates from longtitude
    # and geocentric latitude.
    gclat = radians(geocentric_latitude(latitude)) if ellipsoid else lat
    x = cos(lat)*cos(lon)*r
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

    return (x,y,z)

def distance(p1, p2):
    dx = p1[0]-p2[0]
    dy = p1[1]-p2[1]
    dz = p1[2]-p2[2]
    return sqrt(dx*dx+dy*dy+dz*dz)

def euclidian_distance(c1, c2, ellipsoid=True):
    if len(c1) >= 2 and len(c2) >= 2:
        if len(c1) == 2: c1 += (0,)
        if len(c2) == 2: c2 += (0,)
        return distance(
            euclidian_point(c1[0], c1[1], c1[2], ellipsoid=ellipsoid),
            euclidian_point(c2[0], c2[1], c2[2], ellipsoid=ellipsoid)
        )
    else:
        return None

def spherical_distance(c1, c2, altitude=0, r=mean_earth_radius):
    d = (r+altitude)*central_angle(c1, c2)
    return d

def ellipsoid_distance(c1, c2):
    # TODO: Update this to the method described by Karney in 2013
    # instead of using Vincenty's algorithm.
    try:
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

def orthodromic_distance(c1, c2, spherical=False):
    if spherical:
        return spherical_distance(c1, c2)
    else:
        return ellipsoid_distance(c1, c2)

# def tests():
#     from geographiclib.geodesic import Geodesic
#     geod = Geodesic.WGS84
#     coords = [
#         [(57.758793, 22.605194), (43.048838, -9.241343)],
#         [(0.0, 0.0), (0.0, 0.0)],
#         [(-90.0, 0.0), (90.0, 0.0)],
#         [(-90.0, 0.0), (78.0, 0.0)],
#         [(0.0, 0.0), (0.5, 179.5)],
#         [(0.7, 0.0), (0.0, -180.0)],
#     ]
#     for cs in coords:
#         c1 = cs[0]; c2 = cs[1]
#         print("Testing: "+str(c1)+"  ->  "+str(c2))
#         us = time.time()
#         ld = c1+c2; g = geod.Inverse(*ld)
#         print("Lib computed in "+str(round((time.time()-us)*1e6, 3))+"us")
#         us = time.time()
#         eld = orthodromic_distance(c1,c2,spherical=False)
#         if eld:
#             print("Own computed in "+str(round((time.time()-us)*1e6, 3))+"us")
#         else:
#             print("Own TIMED OUT in "+str(round((time.time()-us)*1e6, 3))+"us")

#         print("Euclidian = "+RNS.prettydistance(euclidian_distance(c1,c2)))
#         print("Spherical = "+RNS.prettydistance(orthodromic_distance(c1,c2)))    
#         if eld: print("Ellipsoid = "+RNS.prettydistance(eld))
#         print("EllipLib  = "+RNS.prettydistance(g['s12']))
#         if eld: print("Diff      = "+RNS.prettydistance(g['s12']-eld))
#         print("")
