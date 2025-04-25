import os
from flask import Flask, send_from_directory, jsonify, request, make_response
from pymongo import MongoClient
import threading
import shodan
import requests
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["rootless"]
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
from flask import send_file
@app.route('/')
def root():
    return send_file(os.path.join(BASE_DIR, 'index.html'))
@app.route('/<path:filename>')
def serve_static(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(BASE_DIR, filename)
    if not (filename.startswith('api/') or filename.startswith('static/') or filename.endswith('.js') or filename.endswith('.css') or filename.endswith('.png')):
        return send_file(os.path.join(BASE_DIR, 'index.html'))
    return 'Not Found', 404
@app.route("/api/devices", methods=["GET"])
def get_devices():
    devices = list(mongo_db.data.find({}, {"_id": 0}))
    return jsonify(devices)
def get_lat_lon(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}")
        json_response = r.json()
        lat = json_response.get('lat')
        lng = json_response.get('lon')
        country_name = json_response.get('country')
        return lat, lng, country_name
    except Exception as e:
        print(f"GeoIP error for {ip}: {e}")
        return None, None, None
def searching(term_to_search, geo=None):
    import time
    import random
    import urllib.parse
    query = term_to_search
    if geo:
        query += f" geo:{geo}"
    url = f"https://maps.shodan.io/_search?q={urllib.parse.quote(query)}"
    try:
        cookies = {"polito": "YOUR_KEY!}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.7",
            "Referer": "https://maps.shodan.io/",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1"
        }
        r = requests.get(url, headers=headers, cookies=cookies)
        if r.status_code != 200:
            print(f"Shodan Map sorgusu başarısız: {r.status_code}")
            return
        results = r.json()
        existing_ips = set(x['ip'] for x in mongo_db.data.find({}, {"ip": 1}))
        new_data = []
        count = 0
        for result in results.get('matches', []):
            searching_ip = result.get('ip_str')
            port = result.get('port')
            lat = result.get('location', {}).get('latitude')
            lng = result.get('location', {}).get('longitude')
            country_name = result.get('location', {}).get('country_name')
            city = result.get('location', {}).get('city')
            region_code = result.get('location', {}).get('region_code')
            area_code = result.get('location', {}).get('area_code')
            country_code = result.get('location', {}).get('country_code')
            if not searching_ip or port is None or lat is None or lng is None or not country_name:
                continue
            if searching_ip in existing_ips:
                continue
            data = {
                "id": count,
                "ip": searching_ip,
                "port": port,
                "lat": lat,
                "lng": lng,
                "Country": country_name,
                "city": city,
                "region_code": region_code,
                "area_code": area_code,
                "country_code": country_code,
                "term": term_to_search
            }
            new_data.append(data)
            count += 1
        if new_data:
            mongo_db.data.insert_many(new_data)
            print(f"[+] Toplam {len(new_data)} yeni IP eklendi.")
        else:
            print("[!] Eklenecek yeni IP yok.")
    except Exception as e:
        print(f"Shodan Map error: {e}")
from country_grid import get_grid_boxes_for_country
@app.route('/api/clear', methods=['POST'])
def clear_devices():
    mongo_db.data.delete_many({})
    return jsonify({'status': 'ok', 'message': 'Tüm veriler silindi.'})
@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.get_json()
    term = data.get('term', '')
    geo = data.get('geo', None)
    if not term:
        return jsonify({'status': 'error', 'message': 'Arama terimi gerekli.'}), 400
    if not geo:
        return jsonify({'status': 'error', 'message': 'Geo kutusu gerekli.'}), 400
    thread = threading.Thread(target=searching, args=(term, geo))
    thread.start()
    return jsonify({'status': 'ok', 'message': 'Arama başlatıldı.'})
@app.route('/api/devices_in_bounds', methods=['POST'])
def devices_in_bounds():
    data = request.get_json()
    north = data.get('north')
    south = data.get('south')
    east = data.get('east')
    west = data.get('west')
    if None in [north, south, east, west]:
        return jsonify({'status': 'error', 'message': 'Eksik koordinat!'}), 400
    try:
        north = float(north)
        south = float(south)
        east = float(east)
        west = float(west)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Koordinatlar sayı olmalı!'}), 400
    query = {
        "lat": {"$gte": south, "$lte": north},
        "lng": {"$gte": west, "$lte": east}
    }
    devices = list(mongo_db.data.find(query, {"_id": 0}).limit(100))
    return jsonify(devices)
from concurrent.futures import ThreadPoolExecutor, as_completed
@app.route('/api/scan_country', methods=['POST'])
def scan_country():
    data = request.get_json()
    country = data.get('country')
    grid_size_km = float(data.get('grid_size_km', 22.36))
    term = data.get('term', '')
    if not country or not term:
        return jsonify({'status': 'error', 'message': 'Ülke ve arama terimi gerekli!'}), 400
    def scan_job():
        try:
            boxes = get_grid_boxes_for_country(country, grid_size_km)
            total_boxes = len(boxes)
            print(f"Found {total_boxes} grids for {country}")
            est_time = total_boxes * 2 // 4
            print(f"Estimated time: {est_time} seconds (with 4 workers)")
            app.config['SCAN_PROGRESS'] = {
                'total': total_boxes,
                'current': 0,
                'country': country,
                'completed': False,
                'message': f"Found {total_boxes} grids for {country}"
            }
            def process_grid(b):
                geo = f"{b[0]},{b[1]},{b[2]},{b[3]}"
                print(f"Processing grid: {geo}")
                searching(term, geo)
                app.config['SCAN_PROGRESS']['current'] += 1
                progress = app.config['SCAN_PROGRESS']
                print(f"Completed {progress['current']}/{progress['total']} grids")
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(process_grid, b) for b in boxes]
                for i, future in enumerate(as_completed(futures), 1):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Grid error: {e}")
            app.config['SCAN_PROGRESS']['completed'] = True
            app.config['SCAN_PROGRESS']['message'] = f"Scan completed. Total {total_boxes} grids processed."
        except Exception as e:
            print(f"Country scan error: {e}")
            app.config['SCAN_PROGRESS'] = None
    thread = threading.Thread(target=scan_job)
    thread.start()
    return jsonify({
        'status': 'ok',
        'message': f'Starting grid scan for {country}',
        'total_grids': len(get_grid_boxes_for_country(country, grid_size_km))
    })
@app.route('/api/scan_progress', methods=['GET'])
def get_scan_progress():
    progress = app.config.get('SCAN_PROGRESS')
    if not progress:
        return jsonify({'status': 'no_scan'})
    return jsonify({
        'status': 'completed' if progress['completed'] else 'scanning',
        'total': progress['total'],
        'current': progress['current'],
        'country': progress['country'],
        'percent': (progress['current'] / progress['total'] * 100) if progress['total'] > 0 else 0
    })
@app.route('/api/list_terms', methods=['GET'])
def list_terms():
    try:
        terms = mongo_db.data.distinct('term')
        return jsonify(terms)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
@app.route('/api/list_countries', methods=['GET'])
def list_countries():
    try:
        countries = mongo_db.data.distinct('Country')
        return jsonify(countries)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
@app.route('/api/devices_by_term', methods=['POST'])
def devices_by_term():
    try:
        data = request.get_json()
        term = data.get('term', '')
        country = data.get('country', '')
        query = {}
        if term:
            query['term'] = term
        if country:
            query['Country'] = country
        if not query:
            return jsonify({'status': 'error', 'message': 'En az bir filtreleme kriteri gerekli!'}), 400
        devices = list(mongo_db.data.find(query, {"_id": 0}))
        return jsonify(devices)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
@app.route('/api/download_ips', methods=['GET', 'POST'])
def download_ips():
    try:
        if request.method == 'POST':
            data = request.get_json()
            term = data.get('term', '')
            country = data.get('country', '')
        else:
            term = request.args.get('term', '')
            country = request.args.get('country', '')
        query = {}
        if term:
            query['term'] = term
        if country:
            query['Country'] = country
        if not query:
            return jsonify({'status': 'error', 'message': 'En az bir filtreleme kriteri gerekli!'}), 400
        devices = list(mongo_db.data.find(query, {"ip": 1, "port": 1, "_id": 0}))
        if not devices:
            return jsonify({'status': 'error', 'message': 'Bu kriterler için cihaz bulunamadı'}), 404
        content = '\n'.join([f"{device['ip']}:{device['port']}" for device in devices])
        filename = f"{term or 'all'}_"
        if country:
            filename += f"{country}_"
        filename += "ips.txt"
        response = make_response(content)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-Type"] = "text/plain"
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
@app.route('/api/scan_bounds', methods=['POST'])
def scan_bounds():
    data = request.get_json()
    north = data.get('north')
    south = data.get('south')
    east = data.get('east')
    west = data.get('west')
    term = data.get('term')
    if None in [north, south, east, west, term]:
        return jsonify({'status': 'error', 'message': 'Eksik parametre!'}), 400
    try:
        north = float(north)
        south = float(south)
        east = float(east)
        west = float(west)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Koordinatlar sayı olmalı!'}), 400
    def scan_job():
        try:
            geo = f"{north},{west},{south},{east}"
            print(f"Grid: {geo}")
            searching(term, geo)
        except Exception as e:
            print(f"Geo tarama hatası: {e}")
    thread = threading.Thread(target=scan_job)
    thread.start()
    return jsonify({'status': 'ok', 'message': 'Seçili alan için tarama başlatıldı.'})
@app.route('/api/global_stats')
def get_global_stats():
    try:
        total_count = mongo_db.data.count_documents({})
        pipeline_ports = [
            {"$group": {"_id": "$port", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_ports = list(mongo_db.data.aggregate(pipeline_ports))
        top_ports = [[str(p["_id"]), p["count"]] for p in top_ports]
        pipeline_countries = [
            {"$group": {"_id": "$Country", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_countries = list(mongo_db.data.aggregate(pipeline_countries))
        top_countries = [[c["_id"], c["count"]] for c in top_countries]
        return jsonify({
            "total": total_count,
            "top_ports": top_ports,
            "top_countries": top_countries
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)