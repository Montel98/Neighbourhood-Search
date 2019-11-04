import attributes as att
import db as d
from collections import namedtuple
import requests
import json
import urllib.parse

AreaCodes = namedtuple("AreaCodes", "area_code_id proportion")
URL = "0"


def init_rent_attributes(vicinities, user_vector):
    area_code_list = init_area_codes()
    db = d.get_db()
    sql = """SELECT vicinity.name, 
                    vicinity.id,
                    has_area_code.area_code_id,
                    has_area_code.proportion
             FROM vicinity
             INNER JOIN has_area_code
                ON has_area_code.vicinity_id = vicinity.id"""

    rows = db.execute(sql)

    for row in rows:
        vicinity = vicinities.get_vicinity_by_id(int(row["id"]))
        vicinity.add_attribute("RentAttribute", att.RentAttribute(user_vector, user_vector.room_type))
        rent_attr = vicinity.get_attribute("RentAttribute")
        rent_attr.get_area_distributions().append(AreaCodes(area_code_list[row["area_code_id"]], float(row["proportion"])))


def init_green_attributes(vicinities, user_vector):
    db = d.get_db()
    sql = """SELECT vicinity_id,
                    green_use
             FROM green_space"""

    rows = db.execute(sql)

    for row in rows:
        vicinity = vicinities.get_vicinity_by_id(int(row["vicinity_id"]))
        vicinity.add_attribute("GreenAttribute", att.GreenAttribute(user_vector, row["green_use"]))


def init_distance_attributes(vicinities, user_vector):
    ward_index = []
    points = []
    params = {}

    parsed_destination = urllib.parse.quote(user_vector.target_location)
    URL2 = "0".format(parsed_destination)
    r = requests.get(url=URL2)
    response = json.loads(r.text)
    position = response["resourceSets"][0]["resources"][0]["point"]["coordinates"]
    target_latitude = position[0]
    target_longitude = position[1]

    db = d.get_db()
    sql = """SELECT vicinity.id,
                    vicinity.centre_lat,
                    vicinity.centre_long
             FROM vicinity
             """

    rows = db.execute(sql)

    for row in rows:
        ward_index.append(int(row["id"]))
        points.append({"latitude": row["centre_lat"], "longitude": row["centre_long"]})

        params["origins"] = points
        params["destinations"] = [{"latitude": target_latitude, "longitude": target_longitude}]
        params["travelMode"] = "driving"

        vicinity = vicinities.get_vicinity_by_id(int(row["id"]))
        vicinity.add_attribute("DistanceAttribute", att.DistanceAttribute(user_vector, row["centre_lat"], row["centre_long"]))

    # get matrix of times from source locations to destination
    r = requests.post(url=URL, json=params)
    response = json.loads(r.text)

    for results in response["resourceSets"][0]["resources"][0]["results"]:
        vicinity_id = ward_index[results["originIndex"]]
        vicinity = vicinities.get_vicinity_by_id(vicinity_id)
        travel_duration = results["travelDuration"]
        vicinity.get_attribute("DistanceAttribute").time_to_destination = travel_duration


def insert_attribute(user_vector, vicinities, attribute_type):
    if attribute_type == "RentAttribute":
        init_rent_attributes(vicinities, user_vector)
    elif attribute_type == "GreenAttribute":
        init_green_attributes(vicinities, user_vector)
    elif attribute_type == "DistanceAttribute":
        init_distance_attributes(vicinities, user_vector)


def init_area_codes():
    area_codes = {}

    db = d.get_db()
    sql = """SELECT t.area_code_id,
                    rent_price.room_type,
                    rent_price.mean,
                    rent_price.variance
            FROM (SELECT DISTINCT has_area_code.area_code_id FROM has_area_code) as t
            lEFT JOIN rent_price
                ON t.area_code_id = rent_price.area_code_id"""

    rows = db.execute(sql)

    for row in rows:
        area_code_id = row["area_code_id"]

        if area_code_id not in area_codes:
            area_codes[area_code_id] = att.AreaCode(area_code_id)

        if row["variance"] is not None and row["mean"] is not None:
            area_codes[area_code_id].add_room_type(row["room_type"], float(row["variance"]), float(row["mean"]))

    return area_codes
