import jinja2
from cairosvg import svg2png
from PIL import Image

import json
import os
from os import listdir
from os.path import isfile, join, splitext
import requests
import feedparser
from functools import reduce
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)

BLOG_RSS_URL = "https://blog.haideralipunjabi.com/index.xml"
GITHUB_API_URL = "https://api.github.com/users/%s/repos?per_page=100&page=%s"
FOSS_CONTRIBUTIONS_DATA = "data/foss-contributions.json"
def get_blog_posts(num):
    feed = feedparser.parse(BLOG_RSS_URL)
    return {"blog_posts":feed['entries'][:num]}

def get_github_data(username):
    repos = []
    page = 1
    while True:
        data = requests.get(GITHUB_API_URL%(username,page)).json()
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    source_repos_len = len(list(filter(lambda repo: repo["fork"]==False,repos)))
    stargazers = reduce(lambda a,b: a+b["stargazers_count"],repos,0)
    forks = reduce(lambda a,b: a+b["forks"],repos,0)
    most_popular = list(sorted(repos, key=lambda repo: repo['stargazers_count'],reverse=True))[:3]
    return {
        "github":{
            "repo_count": source_repos_len,
            "stargazers": stargazers,
            "forks": forks,
            "most_popular": most_popular
        }
    }
def get_foss_contributions():
    contributions = json.load(open(FOSS_CONTRIBUTIONS_DATA,"r"))["contributions"]
    contributions_data = []
    for contribution in contributions:
        api_url = contribution["link"].replace("github.com","api.github.com/repos")
        data = requests.get(api_url).json()
        contributions_data.append(data)
    return {
        "contributions": contributions_data
    }
templates = [
    {
        "input": "index.html",
        "data_files": ["backpack.json","settings.json","projects.json","timeline.json"],
        "data":[get_blog_posts(5),get_github_data("haideralipunjabi"),get_foss_contributions()],
        "output": "index.html"
    },
    {
        "input": "colors.css",
        "data_files": ["settings.json"],
        "data":[],
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
        for file in template_data["data_files"]:
            data_file = json.load(open("data/"+file,"r"))
            data.update(data_file)
        for d in template_data["data"]:
            data.update(d)
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