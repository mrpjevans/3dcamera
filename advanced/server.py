from flask import Flask
from flask import request
from flask import send_file
from flask import render_template
import urllib.request
from PIL import Image
from io import BytesIO
from datetime import datetime
import os

app = Flask(__name__)

# Update these if using different names!
left_camera = "http://leftcam.local:8080/?action=snapshot"
right_camera = "http://rightcam.local:8080/?action=snapshot"
my_dir = os.path.dirname(os.path.realpath(__file__))
save_to = my_dir + "/photos"

# Following function based on https://github.com/miguelgrinberg/anaglyph.py/blob/master/anaglyph.py
# Copyright (c) 2013 by Miguel Grinberg


def make_anaglyph(left_image, right_image, color):

    matrices = {
        'true': [[0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0.299, 0.587, 0.114]],
        'mono': [[0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0.299, 0.587, 0.114, 0.299, 0.587, 0.114]],
        'color': [[1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 1]],
        'halfcolor': [[0.299, 0.587, 0.114, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 1]],
        'optimized': [[0, 0.7, 0.3, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 1]],
    }

    left = Image.open(left_image)
    right = Image.open(right_image)
    width, height = left.size
    leftMap = left.load()
    rightMap = right.load()
    m = matrices[color]

    for y in range(0, height):
        for x in range(0, width):
            r1, g1, b1 = leftMap[x, y]
            r2, g2, b2 = rightMap[x, y]
            leftMap[x, y] = (
                int(r1*m[0][0] + g1*m[0][1] + b1*m[0][2] +
                    r2*m[1][0] + g2*m[1][1] + b2*m[1][2]),
                int(r1*m[0][3] + g1*m[0][4] + b1*m[0][5] +
                    r2*m[1][3] + g2*m[1][4] + b2*m[1][5]),
                int(r1*m[0][6] + g1*m[0][7] + b1*m[0][8] +
                    r2*m[1][6] + g2*m[1][7] + b2*m[1][8])
            )
    image_buffer = BytesIO()
    left.save(image_buffer, format='JPEG')
    image_data = image_buffer.getvalue()

    return image_data


def process_image(image_type):

    left_image = urllib.request.urlopen(left_camera)
    right_image = urllib.request.urlopen(right_camera)

    if image_type == 'parallel':
        image_list = [left_image, right_image]
    elif image_type == 'cross':
        image_list = [right_image, left_image]
    elif image_type == 'triple':
        last_image = urllib.request.urlopen(left_camera)
        image_list = [left_image, right_image, last_image]
    elif image_type == 'triple_reverse':
        last_image = urllib.request.urlopen(right_camera)
        image_list = [right_image, left_image, last_image]
    else:
        return make_anaglyph(left_image, right_image, 'optimized')

    images = [Image.open(x) for x in image_list]

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

    datetime_now = datetime.now()
    timestamp_str = datetime_now.strftime("%Y%M%d%H%M%S")
    side_by_side_image.save(
        save_to + '/' + timestamp_str + '.jpg', format='JPEG')

    return image_data


@app.route('/', methods=['GET'])
def home_page():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def create_image():
    new_image = process_image(request.form['type'])
    return send_file(
        BytesIO(new_image),
        mimetype='image/jpeg',
        as_attachment=True,
        attachment_filename='3d.jpg')
