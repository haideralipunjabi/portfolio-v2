import jinja2
from cairosvg import svg2png
from PIL import Image

import json
import os
from os import listdir
from os.path import isfile, join, splitext
import requests


templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)

templates = [
    {
        "input": "index.html",
        "data": ["backpack.json","settings.json","projects.json","timeline.json"],
        "output": "index.html"
    },
    {
        "input": "colors.css",
        "data": ["settings.json"],
        "output": "assets/css/colors.css"
    }
]

def gen_favicons():
    icon_svg = "assets/media/icon.svg"
    manifest = json.load(open("manifest.json","r"))
    icons = manifest["icons"]
    for icon in icons:
        svg2png(url=icon_svg, write_to=icon["src"][1:], parent_width=int(icon["sizes"].split("x")[0]), parent_height=int(icon["sizes"].split("x")[1]))
    Image.open("assets/favicons/icon-512x512.png").save("assets/favicons/favicon.ico")
    template = templateEnv.get_template("favicons.html")
    print(template.render(icons=icons,appname=manifest["short_name"], appcolor=manifest["theme_color"], bgcolor=manifest["background_color"]),file=open("favicons.html","w"))


def gen_templates():
    for template_data in templates:
        TEMPLATE_FILE = "templates/"+template_data["input"]
        data = {}
        for file in template_data["data"]:
            data_file = json.load(open("data/"+file,"r"))
            data.update(data_file)
        template = templateEnv.get_template(TEMPLATE_FILE)
        print(template.render(**data),file=open(template_data["output"],"w"))

def gen_sitemap():
    sitemap_file = open("sitemap.xml","w")
    sitemap_file.write('<?xml version="1.0" encoding="UTF-8"?>')
    sitemap_file.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for f in onlyfiles:
        if EXCLUDE_FILES.__contains__(f):
            continue
        sitemap_file.write(
            '''
            <url>
                <loc>%s</loc>
            </url>
            '''
        %("https://covidkashmir.org/"+f.replace("index","").replace(".html","")))
    sitemap_file.write('</urlset>')
    sitemap_file.close()




# gen_favicons()
gen_templates()
# gen_sitemap()
