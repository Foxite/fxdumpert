import os

import requests
from os import path
from bs4 import BeautifulSoup
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

@app.route('/item/<video_id>')
def get_embed(video_id):
    dumpert_url = f'https://www.dumpert.nl/item/{video_id}'

    html_request = requests.get(dumpert_url)
    html_request.raise_for_status()
    html_doc = BeautifulSoup(html_request.text, "html.parser")
    title       = html_doc.find('meta', {'property': 'og:title'}).attrs.get("content")
    description = html_doc.find('meta', {'property': 'og:description'}).attrs.get("content")
    publishdate = html_doc.find('meta', {'property': 'article:publish_date'}).attrs.get("content")
    video_url   = request.path + "/video"

    body_template = """<html>
    <head>
        <meta property='og:title' content='{{title}}'>
        <meta property='og:description' content='{{description}}'>
        <meta property="article:publish_date" content="{{publishdate}}"/>
        <meta property="og:video" content="{{video_url}}"/>
        <meta property="og:site_name" content="FxDumpert"/>
    </head>
</html>

"""
    body = render_template_string(
        body_template,
        title=title,
        description=description,
        publishdate=publishdate,
        video_url=video_url,
        dumpert_url=dumpert_url
    )

    res = make_response(body)

    res.status_code = 307
    res.headers["Location"] = dumpert_url
    return res

@app.route('/item/<video_id>/video')
def get_video(video_id):
    # 7584405_79da0ea7
    video_url = f'https://www.dumpert.nl/item/{video_id}'

    html_request = requests.get(video_url)
    html_request.raise_for_status()
    html_doc = BeautifulSoup(html_request.text, "html.parser")
    m3u8_url = html_doc.find('meta', {'property': 'og:video'}).attrs.get("content")

    m3u8_request = requests.get(m3u8_url)
    m3u8 = m3u8_request.text
    m3u8_items = [line for line in m3u8.split('\n') if not line.startswith("#") and not len(line) == 0]
    print('\n'.join(m3u8_items))

    ts_files = [path.join(m3u8_url, '../' + item) for item in m3u8_items]
    print('\n'.join(ts_files))

    output = bytearray()
    for ts_file in ts_files:
        ts_request = requests.get(ts_file)
        output.extend(ts_request.content)

    return bytes(output)

if __name__ == '__main__':
    app.run(debug=True)
