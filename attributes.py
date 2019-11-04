from scipy.stats import lognorm
import numpy as np
import math

from collections import namedtuple

Point = namedtuple("Point", "long lat")


class Attribute:
    def __init__(self, user_vector):
        self.user_vector = user_vector
        self.is_valid_score = False

    def calculate_score(self):
        pass


class RentAttribute(Attribute):
    def __init__(self, user_vector, room_type):
        super().__init__(user_vector)
        self._room_type = room_type
        self.area_distributions = []
        self.is_valid_score = False

    def get_area_distributions(self):
        return self.area_distributions

    #remove
    def get_room_type(self):
        return self._room_type

    def calculate_score(self):
        score = self.get_room_probability(self._room_type, self.user_vector.budget_min, self.user_vector.budget_max)
        if score != -1:
            self.is_valid_score = True
        return score

    def get_room_probability(self, room_type, price_min, price_max):
        """model rent price as log-normal distribution
        return probability of rent price falling between max and min"""

        probability = 0
        total = 0

        if not self.is_valid_room_type(room_type):
            return -1

        # for some vicinities, room type data for every area code aren't available
        # sum the area codes available, and use that as the total
        # note the less area codes used, the less representative the data will be
        for area_code in self.get_area_distributions():
            if room_type in area_code.area_code_id.room_types:
                total += area_code.proportion

        for area_code in self.get_area_distributions():
            if room_type not in area_code.area_code_id.room_types:
                continue

            proportion = area_code.proportion  # get % of ward with area code

            area_probability = area_code.area_code_id.get_room_probability(room_type,
                                                                           price_min,
                                                                           price_max)

            probability += (proportion / total) * area_probability

            if math.isnan(probability):
                print("isnan")
                return -1

        return probability

    def estimate_room_frequency(self, room_type, price_min, price_max):
        room_type_count = 0
        valid_room_types = []
        room_types = ["Room", "Studio", "One Bedroom", "Two Bedrooms", "Three Bedrooms", "Four or More Bedrooms"]

        if not self.is_valid_room_type(room_type):
            return -1

        # only count room type if vicinity has a probability value for it
        for room in room_types:
            if self.is_valid_room_type(room):
                room_type_count += 1
                valid_room_types.append(room)

        frequency = 1 / room_type_count

        denominator = 0

        # sum all room type probabilities
        for room in valid_room_types:
            denominator += (frequency * self.get_room_probability(room, price_min, price_max))

        # get probability for chosen room type only
        numerator = frequency * self.get_room_probability(room_type, price_min, price_max)

        if denominator == 0:
            return -1

        return numerator / denominator

    def is_valid_room_type(self, room_type):
        for area_code in self.get_area_distributions():
            if room_type in area_code.area_code_id.room_types:
                return True
        return False


# percentage of green spaces in each ward
class GreenAttribute(Attribute):
    def __init__(self, user_vector, green_use):
        super().__init__(user_vector)
        self.green_use = green_use
        self.is_valid_score = True

    def calculate_score(self):
        return self.green_use * 0.01


# distance between geographical centre of ward and target location
class DistanceAttribute(Attribute):
    def __init__(self, user_vector, centre_long, centre_lat):
        super().__init__(user_vector)
        self.centre = Point(centre_long, centre_lat)
        self.time_to_destination = 0
        self.is_valid_score = True

    def calculate_score(self):
        t = self.user_vector.max_time - self.time_to_destination
        print("Time:" + str(self.time_to_destination))
        score = 1.0 / (1 + math.exp(-0.5 * (t + 4)))
        return score


# used by RentAttribute, as rent price distributions are by area code
class AreaCode:
    def __init__(self, code, room_list):
        self.code = code
        self.room_types = {}

        # set up random variables for rooms
        for room in room_list:
            random_var = lognorm(s=room["variance"],
                           scale=math.exp(room["mean"]))
            self.room_types[room["room_type"]] = random_var

    def __init__(self, code):
        self.code = code
        self.room_types = {}

    def get_room_probability(self, room_type, price_min, price_max):

        return self.room_types[room_type].cdf(price_max) - self.room_types[room_type].cdf(price_min)

    def get_room_types(self):
        return self.room_types.keys()

    def add_room_type(self, room_type, variance, mean):
        # To account for samples with 0 variance
        variance += 0.0000000001
        random_var = lognorm(s=variance,
                             scale=math.exp(mean))
        self.room_types[room_type] = random_var

    def has_room_data(self):
        return not self.room_types
