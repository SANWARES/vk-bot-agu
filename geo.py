from math import radians, cos, sin, asin, sqrt


def object_to_object(lat, lon):
    korp = {
        "д": [53.344857, 83.776319],
        "к": [53.34281, 83.771508],
        "л": [53.347473, 83.7758],
        "м": [53.347502, 83.775089],
        "н": [53.3459, 83.788159],
        "с": [53.342202, 83.778131],
        "а": [53.368009, 83.762166],
        "э": [53.38086, 83.7329],
    }
    dist_short = ["", 10000]

    for k in korp.items():
        new_value = haversine(lat, lon, k[1][0], k[1][1])
        if new_value < dist_short[1]:
            dist_short[0] = k[0]
            dist_short[1] = new_value

    return dist_short[0]


def haversine(lat1, lon1, lat2, lon2):
    """
    Вычисляет расстояние в километрах между двумя точками, учитывая окружность Земли.
    https://en.wikipedia.org/wiki/Haversine_formula
    """

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, (lon1, lat1, lon2, lat2))

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km
