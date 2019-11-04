import db as d


class Vicinity:
    def __init__(self, vicinity_id, name, local_authority):
        self.vicinity_id = vicinity_id
        self.name = name
        self.local_authority = local_authority
        self.attributes = {}
        self.score_vector = []
        self.score = 0

    def get_attribute(self, attribute_type):
        return self.attributes[attribute_type]

    def add_attribute(self, attribute_type, obj):
        if attribute_type not in self.attributes:
            self.attributes[attribute_type] = obj

    def get_score_vector(self):
        self.score_vector = [a.calculate_score() for a in self.attributes.values()]
        return self.score_vector


class VicinityList:
    def __init__(self):
        self.vicinities = {}
        self.exclusion_count = 0  # no. of vicinities excluded from results

    def get_vicinity_by_id(self, vicinity_id):
        # will return a reference to the vicinity object with the matching ID parameter
        return self.vicinities[vicinity_id]

    # returns list of vicinities sorted by their similarity score attribute
    def get_most_similar(self, user_vector, entries=None):

        v_list = list(self.vicinities.values())
        #user_score = [1, user_vector.green_space, 1]
        user_score = [1, user_vector.green_space]

        for v in v_list:
            # similarity metric
            # square difference between target and user score
            score = sum(map(lambda x, y: (x - y)**2, v.get_score_vector(), user_score))

            if len(v.attributes) == 1:
                v.score = -1
                self.exclusion_count += 1
            else:
                # clamp score between 0 and 100
                v.score = round(100 * (1 / (1 + score)), 1)

            # ensure vicinities with incomplete/invalid results are pushed to the bottom
            for att in v.attributes:
                if not v.attributes[att].is_valid_score:
                    v.score = -1
                    self.exclusion_count += 1

        v_list.sort(key=lambda x: x.score, reverse=True)

        # limit the amount of results returned to [entries]
        if entries:
            return v_list[0:entries]
        return v_list

    def get_vicinities(self):
        return self.vicinities.values()

    def insert_vicinities(self):
        db = d.get_db()
        sql = """SELECT vicinity.id, vicinity.name, vicinity.local_authority
                 FROM vicinity
                 WHERE NOT EXISTS (SELECT 1
                                   FROM has_alias
                                   WHERE has_alias.vicinity_id = vicinity.id)
                 UNION
                 SELECT vicinity.id, has_alias.alias, vicinity.local_authority
                 FROM has_alias
                 INNER JOIN vicinity
                    ON vicinity.id = has_alias.vicinity_id;"""

        rows = db.execute(sql)

        for row in rows:
            self.vicinities[row["id"]] = Vicinity(row["id"], row["name"], row["local_authority"])