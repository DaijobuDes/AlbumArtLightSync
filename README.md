# AlbumArtLightSync

This project is created on my free time and only as my interest.

## Why?

I recently bought a [TP-Link Tapo L530](https://www.tp-link.com/ph/home-networking/smart-bulb/tapo-l530e/) smart light bulb, got bored and
had a stupid idea to synchronize the color from the album cover's most significant color based on the color palette when playing.

![Image](https://static.tp-link.com/01_1598337266170q.jpg)

## Other notes

The light gets set to 50% brightness with 3450 light temperature.

Based on this line <https://github.com/DaijobuDes/AlbumArtLightSync/blob/e538bcd8d66745d40ae8785b64e21f323c07a024/main.py#L54>

So you might want to adjust it to your needs or modify the whole line.

## 3rd party libraries used

<https://github.com/mihai-dinculescu/tapo>

## Usage

Clone this repository first

```sh
git clone https://github.com/DaijobuDes/AlbumArtLightSync.git
```

Copy `.env.example` to `.env` and fill them up.

Last.fm API: <https://www.last.fm/api>

Yes, you are required to have a smart light bulb from TP-Link. If none, then
go buy one.

Best if you use a virtual environment, then activate

```sh
python3 -m venv .
source bin/activate
```

Install dependencies

```sh
pip3 install -r requirements.txt
```

Running

```sh
python3 main.py
```
