import os
import urllib.request
from http.server import SimpleHTTPRequestHandler, HTTPServer
from PIL import Image
from io import BytesIO

port = 8081
control_html = os.path.dirname(os.path.realpath(__file__)) + '/control.html'
# Reverse the URLs to create cross-eye images instead of parallel
left_camera = "http://leftcam.local:8080/?action=snapshot"
right_camera = "http://rightcam.local:8080/?action=snapshot"


def process_image():
    left_image = urllib.request.urlopen(left_camera)
    right_image = urllib.request.urlopen(right_camera)
    images = [Image.open(x) for x in [left_image, right_image]]

    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)

    side_by_side_image = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for image in images:
        side_by_side_image.paste(image, (x_offset, 0))
        x_offset += image.size[0]

    image_buffer = BytesIO()
    side_by_side_image.save(image_buffer, format='JPEG')
    image_data = image_buffer.getvalue()

    return image_data


class handle_request(SimpleHTTPRequestHandler):
    def do_GET(self):
        print('Sending control HTML')
        f = open(control_html, 'rb')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.copyfile(f, self.wfile)

    def do_POST(self):
        new_image = process_image()
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Content-disposition',
                         'attachment; filename="3d.jpg"')
        self.end_headers()
        self.wfile.write(new_image)


httpd = HTTPServer(("", port), handle_request)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

httpd.server_close()
