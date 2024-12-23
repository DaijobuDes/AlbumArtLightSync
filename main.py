import asyncio
import colorsys
import logging
import numpy as np
import os
import requests
from colored_log import ColoredFormatter
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image
from sklearn.cluster import KMeans
from tapo import ApiClient

load_dotenv()

OLD_IMAGE_URL = ""
LAST_FM_USER = os.getenv("LAST_FM_USER")
LAST_FM_API_KEY = os.getenv("LAST_FM_API_KEY")

r =requests.Session()

log = logging.getLogger('main')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

cf = ColoredFormatter("[%(asctime)s][%(name)s][%(levelname)s] = %(message)s (%(filename)s:%(lineno)d)")

ch.setFormatter(cf)
log.addHandler(ch)

log.setLevel(logging.DEBUG)

async def main():
    tapo_username = os.getenv("TAPO_USERNAME")
    tapo_password = os.getenv("TAPO_PASSWORD")
    ip_address = os.getenv("TAPO_IP_ADDRESS")

    client = ApiClient(tapo_username, tapo_password)
    device = await client.l530(ip_address)

    log.info("Turning device on...")
    await device.on()

    log.info("Waiting 2 seconds...")
    await asyncio.sleep(2)

    # Get image of album
    while (True):
        image_data = await get_album_image()

        if image_data == -1:
            log.info("Not playing anything")
            await device.set().brightness(50).color_temperature(3450).send(device)
            await asyncio.sleep(5)
            continue

        if image_data == 1:
            log.info("Same image. Skipping.")
            await asyncio.sleep(5)
            continue

        log.info("Got an image")
        colors = await extract_color_palette(image_data, 1)

        if type(colors) == bool and colors == -1:
            log.error("Cannot fetch colors and assign to HSL. Invalid image passed. Probably non-existent image?")
            await asyncio.sleep(5)
            continue

        log.info(f"Colors: {colors[0]}")
        h, s, l = await rgb_to_hsl(*colors[0])

        log.info(f"HSL: {[h, s, l]}")

        log.info("Setting device params")
        await device.set().brightness(l).hue_saturation(h, s).send(device)
        log.info("Done. Sleeping for 5s")
        await asyncio.sleep(5)

async def extract_color_palette(image_path, num_colors=6):
    try:
        # Open the image using Pillow
        image = Image.open(image_path)
        image = image.convert('RGB')  # Ensure the image is in RGB mode

        # Resize the image to reduce the number of pixels (optional)
        image = image.resize((100, 100))

        # Convert the image data to a numpy array
        image_data = np.array(image)

        # Reshape the image data to a 2D array of pixels
        pixels = image_data.reshape((-1, 3))

        # Use KMeans to cluster the pixel colors
        kmeans = KMeans(n_clusters=num_colors)
        kmeans.fit(pixels)

        # Get the cluster centers (the colors)
        colors = kmeans.cluster_centers_.astype(int)

        return colors
    except Exception:
        log.error("An error occurred when trying to read image.")
        return -1

async def get_album_image():
    global OLD_IMAGE_URL
    URL = f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={LAST_FM_USER}&api_key={LAST_FM_API_KEY}&limit=1&format=json"

    data = r.get(URL).json()

    # Now playing has @attr nowplaying true
    is_playing = data['recenttracks']['track'][0].get('@attr', None)

    if is_playing is None:
        OLD_IMAGE_URL = ""
        return -1

    log.debug(data['recenttracks']['track'][0]['image'][3])
    has_image = data['recenttracks']['track'][0]['image'][3].get('#text', None)

    if has_image is None:
        return -1

    # If same image URL
    if OLD_IMAGE_URL == has_image:
        return 1

    OLD_IMAGE_URL = has_image

    image_data = r.get(has_image).content

    return BytesIO(image_data)

async def rgb_to_hsl(r, g, b):
    r /= 255.0
    g /= 255.0
    b /= 255.0

    h, l, s = colorsys.rgb_to_hls(r, g, b)

    h = h * 360  # Hue to degrees
    s = s * 100  # Saturation to percentage
    l = l * 100  # Lightness to percentage

    if h <= 0:
        h = 1

    if s <= 0:
        s = 1

    if l <= 0:
        l = 1

    return int(h), int(s), int(l)

if __name__ == '__main__':
    asyncio.run(main())
