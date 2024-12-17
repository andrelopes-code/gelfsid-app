import os
import tempfile
import zipfile

import geopandas as gpd
from django.core.exceptions import ValidationError
from pyogrio import set_gdal_config_options

from gelfcore.logger import log

set_gdal_config_options({
    'SHAPE_RESTORE_SHX': 'YES',
})


def optimize_geojson(gdf, simplify_tolerance=0.001):
    try:
        gdf.geometry = gdf.geometry.simplify(tolerance=simplify_tolerance, preserve_topology=True)
        return gdf.to_json()

    except Exception as e:
        log.error(f'Erro ao otimizar o GeoJSON: {e}')
        raise ValidationError(f'Erro ao otimizar o GeoJSON: {e}')


def from_shapefile_zip(file):
    try:
        if not zipfile.is_zipfile(file):
            raise ValidationError('O arquivo enviado não é um ZIP válido contendo o Shapefile.')

        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(file) as zf:
                zf.extractall(temp_dir)

            shapefile_path = None
            for root, _, files in os.walk(temp_dir):
                for filename in files:
                    if filename.lower().endswith('.shp'):
                        shapefile_path = os.path.join(root, filename)
                        break

            if not shapefile_path:
                raise ValidationError('O arquivo ZIP não contém um arquivo .shp válido.')

            gdf = gpd.read_file(shapefile_path)

            if gdf.empty:
                raise ValidationError('O Shapefile está vazio e não pode ser convertido para GeoJSON.')

            if gdf.crs is None:
                prj_path = shapefile_path.replace('.shp', '.prj')

                if os.path.exists(prj_path):
                    with open(prj_path, 'r') as prj_file:
                        prj_content = prj_file.read()

                    inferred_crs = gpd.tools.crs.CRS.from_string(prj_content).to_string()
                    gdf.set_crs(inferred_crs, inplace=True)

                else:
                    # Força a conversão para EPSG:31983 SIRGAS 2000 / UTM zone 23S
                    # (UTM Brasil) caso não consiga inferir qual é o crs adequado.
                    gdf.set_crs('EPSG:31983', inplace=True)

            if not gdf.geometry.is_valid.all():
                raise ValidationError('Algumas geometrias no Shapefile são inválidas.')

            # Converte o geo-dataframe em dados geojson
            geojson = gdf.to_crs('EPSG:4326').to_json()

            return geojson

    except ValidationError as ve:
        log.error(f'Erro de validação ao tentar converter Shapefile: {ve}')
        raise ve

    except Exception as e:
        log.error(f'Erro ao processar o Shapefile: {e}')
        raise ValidationError(f'Erro ao processar o Shapefile: {e}')
