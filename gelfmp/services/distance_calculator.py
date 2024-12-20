from dataclasses import dataclass
from http import HTTPStatus

import httpx
from django.conf import settings


@dataclass
class Coordinate:
    lat: str
    lon: str


@dataclass
class RouteInfo:
    distance_in_meters: int
    duration_in_seconds: int
    origin: str
    destination: str


class OpenStreetMap:
    API_URL = 'https://nominatim.openstreetmap.org/search?q={}&format=json'

    @classmethod
    def get_coordinates(cls, address):
        response = httpx.get(cls.API_URL.format(address))
        if response.status_code != HTTPStatus.OK:
            raise Exception(f'could not find address: {address}')

        data = response.json()
        return Coordinate(
            lat=data[0]['lat'],
            lon=data[0]['lon'],
        )


class DistanceCalculator:
    URL = 'https://graphhopper.com/api/1/route'
    API_KEY = settings.GRAPHHOPPER_API_KEY

    @classmethod
    def get_distance(cls, origin, destination, fetch_new=False):
        if not fetch_new:
            return RouteInfo(
                destination=None,
                origin=None,
                distance_in_meters=None,
                duration_in_seconds=None,
            )

        origin_coordinates = OpenStreetMap.get_coordinates(origin)
        destination_coordinates = OpenStreetMap.get_coordinates(destination)

        origin_point = f'{origin_coordinates.lat},{origin_coordinates.lon}'
        destination_point = f'{destination_coordinates.lat},{destination_coordinates.lon}'

        response = httpx.get(
            cls.URL + '?point=' + origin_point + '&point=' + destination_point,
            params={
                'key': cls.API_KEY,
                'vehicle': 'car',
                'instructions': 'false',
            },
        )

        try:
            data = response.json()

            distance = RouteInfo(
                destination=destination,
                origin=origin,
                distance_in_meters=int(data['paths'][0]['distance']),
                duration_in_seconds=int(data['paths'][0]['time'] / 1000),
            )

            return distance

        except Exception:
            raise Exception(f'error getting distance: {response.text}')
