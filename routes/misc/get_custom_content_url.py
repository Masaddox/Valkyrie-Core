from . import misc
from config import PATH_TO_DATABASE


@misc.route(f"{PATH_TO_DATABASE}/getCustomContentURL.php", methods=("POST", "GET"))
def get_custom_content_url():
    return "https://geometrydashfiles.b-cdn.net"
