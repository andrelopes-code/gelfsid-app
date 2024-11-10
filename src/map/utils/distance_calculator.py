from dataclasses import dataclass
import httpx

from mpgsid import config
from ..models import InfoRota


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
    URL = 'https://nominatim.openstreetmap.org/search?q={}&format=json'

    @classmethod
    def get_coordinates(cls, address):
        response = httpx.get(cls.URL.format(address))
        if response.status_code != 200:
            raise Exception(f'Could not find address: {address}')

        data = response.json()
        return Coordinate(
            lat=data[0]['lat'],
            lon=data[0]['lon'],
        )


class DistanceCalculator:
    URL = 'https://graphhopper.com/api/1/route'
    API_KEY = config.settings.GRAPHHOPPER_API_KEY

    @classmethod
    def get_distance(cls, origin, destination, fetch_new=False):
        if existing_distance := cls.existing_distance(origin, destination):
            return existing_distance

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
                'vehicle': 'truck',
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

            InfoRota.objects.create(
                origem=origin,
                destino=destination,
                distancia_em_metros=distance.distance_in_meters,
                duracao_em_segundos=distance.duration_in_seconds,
            )

            return distance

        except Exception:
            raise Exception(f'Error getting distance: {response.text}')

    def existing_distance(origin, destination):
        info_rota = InfoRota.objects.filter(origem=origin, destino=destination).first()
        if info_rota:
            return RouteInfo(
                destination=info_rota.destino,
                origin=info_rota.origem,
                distance_in_meters=info_rota.distancia_em_metros,
                duration_in_seconds=info_rota.duracao_em_segundos,
            )
