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

    def get_group_by_distance(self, origin: str, list_of_coords: list) -> list:
        """Формирует словарь"""
        distance_group = {'до 500 метров': [],
                          'до 1 км': [],
                          'до 2 км': [],
                          'до 5 км': [],
                          }

        for i in list_of_coords:
            distance = self.get_distance(origin=origin, destination=i)
            if distance <= 0.5:
                distance_group['до 500 метров'].append(i)
            elif distance in numpy.arange(0.51, 1.0):
                distance_group['до 1 км'].append(i)
            elif distance <= numpy.arange(1.1, 2.0):
                distance_group['до 2 км'].append(i)
            else:
                distance_group['до 5 км'].append(i)

        return distance_group


# d = Distance()
#
# test = d.get_group_by_distance(origin='59.983499, 30.392048',
#                                list_of_coords=['59.93815249999999, 30.36119429999999', '59.984878, 30.400028',
#                                                '59.9366172, 30.3110003', '59.9360016, 30.3598015'])
# print(test)
