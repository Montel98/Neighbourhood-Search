from flask import Flask
from flask import render_template
from flask import request, session
import attribute_init as attin
import UserVector as uv
import Vicinity as vic

import random
from collections import namedtuple

app = Flask(__name__)
app.secret_key = ""
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/", methods=["GET", "POST"])
def user():
    if request.method == "POST":
        user_vector = uv.UserVector()

        # retrieve user input from form
        user_vector.budget_min = int(request.form["budget_min"])
        user_vector.budget_max = int(request.form["budget_max"])
        user_vector.room_type = request.form["room_type"]
        user_vector.green_space = float(request.form["green_space"])
        #user_vector.max_time = int(request.form["travel_time"])
        #user_vector.target_location = request.form["destination"]

        # Save the user input to the session
        session["user_vector"] = user_vector.__dict__

        vicinities = vic.VicinityList()
        vicinities.insert_vicinities()
        attin.insert_attribute(user_vector, vicinities, "RentAttribute")
        attin.insert_attribute(user_vector, vicinities, "GreenAttribute")
        #attin.insert_attribute(user_vector, vicinities, "DistanceAttribute")

        return render_template("results.html", v=vicinities.get_most_similar(user_vector),
                               c=vicinities.exclusion_count)

    return render_template("enter_details.html", i=(random.random() * 100))


@app.route("/results/<bla>")
def hello_world():
    return render_template("results.html", i=(random.random() * 100))

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = '0'
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/vicinity/<int:vicinity_id>")
def vicinity_details(vicinity_id):
    vicinities = vic.VicinityList()
    vicinities.insert_vicinities()
    user_vector = uv.UserVector()
    user_vector.room_type = session["user_vector"]["room_type"]
    user_vector.budget_min = session["user_vector"]["budget_min"]
    user_vector.budget_max = session["user_vector"]["budget_max"]
    attin.insert_attribute(user_vector, vicinities, "RentAttribute")
    vicinity = vicinities.get_vicinity_by_id(int(vicinity_id))

    frequencies = get_room_frequencies(vicinity, user_vector)
    likely_room = None

    for room in frequencies:
        if likely_room is None:
            likely_room = room
        elif room["frequency"] > likely_room["frequency"]:
            likely_room = room

    return render_template("report.html", v=vicinity,
                           l=likely_room["room_type"],
                           u=user_vector,
                           s=round(100 * vicinity.get_attribute("RentAttribute").calculate_score(), 0),
                           f=get_room_frequencies(vicinity, user_vector))


def get_room_frequencies(vicinity, user_vector):
    room_dist = namedtuple("Frequency", "room_type, frequency")
    room_types = ["Room", "Studio", "One Bedroom", "Two Bedrooms", "Three Bedrooms", "Four or More Bedrooms"]
    frequencies = []

    for room in room_types:
        if vicinity.get_attribute("RentAttribute").is_valid_room_type(room):
            dist = vicinity.get_attribute("RentAttribute").estimate_room_frequency(room,
                                                                                    user_vector.budget_min,
                                                                                    user_vector.budget_max)
            frequencies.append({"room_type": room, "frequency": dist})
    return frequencies


if __name__ == "__main__":
    app.run(debug=True)
