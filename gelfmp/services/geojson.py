import os
import tempfile
import zipfile
from io import BytesIO

import geopandas as gpd
from django.core.exceptions import ValidationError
from pyogrio import set_gdal_config_options

set_gdal_config_options({
    'SHAPE_RESTORE_SHX': 'YES',
})


def optimize_geojson(gdf, simplify_tolerance=0.001):
    try:
        gdf.geometry = gdf.geometry.simplify(tolerance=simplify_tolerance, preserve_topology=True)
        return gdf.to_json()

    except Exception as e:
        raise ValidationError(f'Erro ao otimizar o GeoJSON: {str(e)}')


def from_shapefile_zip(file):
    try:
        if not zipfile.is_zipfile(file):
            raise ValidationError('O arquivo enviado não é um ZIP válido contendo o Shapefile.')

        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(file) as zf:
                zf.extractall(temp_dir)

            shapefile_path = None
            for root, dirs, files in os.walk(temp_dir):
                for filename in files:
                    if filename.lower().endswith('.shp'):
                        shapefile_path = os.path.join(root, filename)
                        break

            if not shapefile_path:
                raise ValidationError('O arquivo ZIP não contém um arquivo .shp válido.')

            gdf = gpd.read_file(shapefile_path)

            if gdf.empty:
                raise ValidationError('O Shapefile está vazio e não pode ser convertido para GeoJSON.')

            if not gdf.geometry.is_valid.all():
                raise ValidationError('Algumas geometrias no Shapefile são inválidas.')

            geojson = gdf.to_crs('EPSG:4326').to_json()

            return geojson

    except ValidationError as ve:
        raise ve

    except Exception as e:
        raise ValidationError(f'Erro ao processar o Shapefile: {str(e)}')


def from_shapefile(file):
    try:
        if not file.name.lower().endswith('.shp'):
            raise ValidationError('O arquivo enviado não é um Shapefile válido.')

        file_bytes = BytesIO(file.read())

        with tempfile.NamedTemporaryFile(delete=False, suffix='.shp') as tmp_file:
            tmp_file.write(file_bytes.read())
            tmp_file_path = tmp_file.name

        gdf = gpd.read_file(tmp_file_path)
        if gdf.empty:
            raise ValidationError('O Shapefile está vazio e não pode ser convertido para GeoJSON.')

        if not gdf.geometry.is_valid.all():
            raise ValidationError('Algumas geometrias no Shapefile são inválidas.')

        geojson = gdf.to_json()
        os.remove(tmp_file_path)

        return geojson

    except ValidationError as ve:
        raise ve

    except Exception as e:
        raise ValidationError(f'Erro ao processar o Shapefile: {str(e)}')
