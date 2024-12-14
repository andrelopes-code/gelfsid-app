import geopandas as gpd

shapefile = './static/data/montecarmelo/Limite_do_Municipio.shp'
gdf = gpd.read_file(shapefile)
print(gdf)
# Converter para GeoJSON
geojson = gdf.to_json()
# Salvar o GeoJSON em um arquivo
with open('output.geojson', 'w') as f:
    f.write(geojson)
