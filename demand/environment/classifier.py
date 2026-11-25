from demand.environment.gdelt_schema import EVENT_ROOT_CODES


class EnvironmentalClassifier:

    CATEGORY_MAP = {

        "PROTEST": "SOCIAL",

        "FIGHT": "CONFLICT",

        "MASS_VIOLENCE": "CONFLICT",

        "ASSAULT": "SECURITY",

        "THREATEN": "SECURITY",

        "DEMAND": "ECONOMY",

        "AID": "HUMANITARIAN",

        "SUPPORT": "POLITICAL",

        "COOPERATE": "POLITICAL",

        "CONSULT": "POLITICAL",

        "STATEMENT": "MEDIA",

        "APPEAL": "MEDIA",

        "INVESTIGATE": "LEGAL",

    }

    def classify_root_code(self, code):

        code = str(code).zfill(2)

        event = EVENT_ROOT_CODES.get(code)

        if event is None:

            return "OTHER"

        return self.CATEGORY_MAP.get(event, "OTHER")
