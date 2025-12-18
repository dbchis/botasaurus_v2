import re


def extract_lat_lng_from_url(url):
    # Case 1: !3dLAT!4dLNG
    match = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))

    # Case 2: /@LAT,LNG
    match = re.search(r'/@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))

    return None, None


# === SỬ DỤNG ===
# link = "https://www.google.com/maps/place/NH%C3%80+H%C3%80NG+PH%E1%BB%90+C%E1%BB%94/data=!4m7!3m6!1s0x314219b9272e70b7:0x97b724d961f4bb93!8m2!3d16.0213385!4d108.1983081!16s%2Fg%2F11j1j9wxvb!19sChIJt3AuJ7kZQjERk7v0Ydkkt5c?authuser=0&hl=en&rclk=1"

# lat, lng = extract_lat_lng_from_url(link)

# location = {
#     "Latitude": lat,
#     "Longitude": lng
# }

# print(location)
