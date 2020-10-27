import math

import numpy


class Distance:
    # Радиус земли
    R = 6373.0

    def get_distance(self, origin: str, destination: str) -> float:
        origin_latitude = math.radians(float(origin.split(', ')[0]))
        origin_longitude = math.radians(float(origin.split(', ')[1]))

        destination_latitude = math.radians(float(destination.split(', ')[0]))
        destination_longitude = math.radians(float(destination.split(', ')[1]))

        longitude_diff = destination_longitude - origin_longitude
        latitude_diff = destination_latitude - origin_latitude

        formula1 = math.sin(latitude_diff / 2) ** 2 + math.cos(origin_latitude) * math.cos(
            destination_latitude) * math.sin(longitude_diff / 2) ** 2
        formula2 = 2 * math.atan2(math.sqrt(formula1), math.sqrt(1 - formula1))

        distance = self.R * formula2

        return distance

    def get_group_by_distance(self, origin: str, dict_of_coords: dict, max_allowed_distance: int) -> dict:
        """Формирует словарь"""
        distance_group = {}
        # !TODO нужно сохранять еще и дистанцию
        for id, coords in dict_of_coords.items():
            if self.get_distance(origin=origin, destination=coords) <= float(max_allowed_distance):
                distance_group[id] = coords
            else:
                pass

        return distance_group

# d = Distance()
#
# test = d.get_group_by_distance(origin='59.983499, 30.392048',
#                                dict_of_coords=['59.93815249999999, 30.36119429999999', '59.984878, 30.400028',
#                                                '59.9366172, 30.3110003', '59.9360016, 30.3598015'])
# print(test)
