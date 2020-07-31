import jinja2
import json
import os
from os import listdir
from os.path import isfile, join, splitext
import requests
from functools import reduce
import wget
from PIL import Image

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader,trim_blocks=True)

BLOG_API_URL = "https://blog.haideralipunjabi.com/index.json"
GITHUB_API_URL = "https://api.github.com/users/%s/repos?per_page=100&page=%s"
FOSS_CONTRIBUTIONS_DATA = "data/foss-contributions.json"
BLOG_IMAGE_SIZE = 512,512
ICONS = [32,70,72,96,128,144,150,152,180,192,196,310,384,512]
def get_blog_posts(num):
    data = requests.get(BLOG_API_URL).json()
    os.system("rm -rf assets/img/blogs")
    os.system("mkdir assets/img/blogs")
    for post in data[:num]:
        filepath = f'assets/img/blogs/{post["data"]["image"].split("/")[-1]}'
        wget.download(post["data"]["image"],out=filepath)
        post["data"]["image"] = filepath
        im = Image.open(filepath)
        im.thumbnail(BLOG_IMAGE_SIZE,Image.ANTIALIAS)
        im.save(filepath)
        
    return {"blog_posts":data[:num]}

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
        "data":[get_blog_posts(4),get_github_data("haideralipunjabi"),get_foss_contributions()],
        "output": "index.html"
    },
    {
        "input": "colors.css",
        "data_files": ["settings.json"],
        "data":[],
        "output": "assets/css/colors.css"
    }
]




def gen_og():
    settings = json.load(open("data/settings.json","r"))
    template = templateEnv.get_template("templates/manifest")
    print(template.render(icons=ICONS,**settings),file=open("assets/manifest.json","w"))
    template = templateEnv.get_template("templates/og.html")
    print(template.render(icons=ICONS,**settings),file=open("og.html","w"))
    


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
        %("https://haideralipunjabi.com/"+f.replace("index","").replace(".html","")))
    sitemap_file.write('</urlset>')
    sitemap_file.close()




gen_og()
gen_templates()
# gen_sitemap()