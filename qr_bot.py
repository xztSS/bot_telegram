import cv2
from pyzxing import BarCodeReader
import os
import requests
import tempfile

reader = BarCodeReader()

# Загрузка картинки
url = "https://example.com/file.png"
response = requests.get(url)

with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
    tmp_file.write(response.content)
    tmp_filename = tmp_file.name

try:
    results = reader.decode(tmp_filename)
    print(results)
finally:
    if os.path.exists(tmp_filename):
        os.remove(tmp_filename)
