import requests
from shapely.geometry import shape, box, Polygon
import math
def get_country_polygon(country_name):
    url = f"https://nominatim.openstreetmap.org/search?country={country_name}&polygon_geojson=1&format=json"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = r.json()
    for item in data:
        if 'geojson' in item:
            return shape(item['geojson'])
    return None
def create_grid_over_polygon(polygon: Polygon, grid_size_km=22.36):
    minx, miny, maxx, maxy = polygon.bounds
    grids = []
    step_lat = grid_size_km / 111.0
    center_lat = (miny + maxy) / 2
    step_lon = grid_size_km / (111.32 * math.cos(math.radians(center_lat)))
    y = miny
    while y < maxy:
        x = minx
        while x < maxx:
            cell = box(x, y, x + step_lon, y + step_lat)
            if polygon.intersects(cell):
                grids.append(cell.intersection(polygon))
            x += step_lon
        y += step_lat
    return grids
def get_grid_boxes_for_country(country_name, grid_size_km=22.36):
    poly = get_country_polygon(country_name)
    if not poly:
        raise Exception("Ülke sınırı alınamadı!")
    grids = create_grid_over_polygon(poly, grid_size_km)
    boxes = []
    for g in grids:
        minx, miny, maxx, maxy = g.bounds
        boxes.append((maxy, minx, miny, maxx))
    return boxes
if __name__ == "__main__":
    boxes = get_grid_boxes_for_country("Turkey")
    print(f"Grid sayısı: {len(boxes)}")
    for b in boxes[:5]:
        print(b)