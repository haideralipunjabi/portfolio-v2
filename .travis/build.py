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

NO_DOWNLOAD = False

BLOG_API_URL = "https://blog.haideralipunjabi.com/index.json"
GITHUB_API_URL = "https://api.github.com/users/%s/repos?per_page=100&page=%s"
FOSS_CONTRIBUTIONS_DATA = "data/foss-contributions.json"
BLOG_IMAGE_SIZE = 512,512

def get_blog_posts(num):
    data = requests.get(BLOG_API_URL).json()
    if not NO_DOWNLOAD:
        os.system("rm -rf assets/img/blogs")
        os.system("mkdir assets/img/blogs")
    for post in data[:num]:
        filein = f'assets/img/blogs/{post["data"]["image"].split("/")[-1]}'
        fileout1 = filein.rsplit(".",1)[0] + ".webp"
        fileout2 = filein.rsplit(".",1)[0] + ".jpg"
        if not NO_DOWNLOAD:
            wget.download(post["data"]["image"],out=filein)
        post["data"]["image"] = [fileout1,fileout2]
        im = Image.open(filein)
        im.thumbnail(BLOG_IMAGE_SIZE,Image.ANTIALIAS)
        im.save(fileout1)
        im.save(fileout2)
        
    return {"blog_posts":data[:num]}

def get_press_posts(num):
    data = json.load(open("data/press.json","r"))
    if not NO_DOWNLOAD:
        os.system("rm -rf assets/img/press")
        os.system("mkdir assets/img/press")
    for i,post in enumerate(data["press"]):
        if "title" not in post.keys() or post["title"] == "":
            r = requests.get(f"https://api.urlmeta.org/?url={post['link']}", headers={
                "Authorization": f"Basic {os.getenv('URLMETA_API')}"
            }).json()
            post["title"] = r["meta"]["title"]
            post["description"]=r["meta"]["description"]
            post["image_src"] = r["meta"]["image"]
            post["site"] = r["meta"]["site"]["name"]
        if num > i:    
            filein = f'assets/img/press/{i}.{post["image_src"].split(".")[-1].split("?")[0]}'
            fileout1 = filein.rsplit(".",1)[0] + ".webp"
            fileout2 = filein.rsplit(".",1)[0] + ".jpg"
            if not NO_DOWNLOAD:
                wget.download(post["image_src"],out=filein)
            im = Image.open(filein)
            im.thumbnail(BLOG_IMAGE_SIZE,Image.ANTIALIAS)
            im.save(fileout1)
            im.save(fileout2)
            post["images"] = [fileout1,fileout2]
    json.dump(data,fp=open("data/press.json","w"))
    return {"press":data["press"]}

def get_github_data(username,num):
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
    most_popular = list(sorted(repos, key=lambda repo: repo['stargazers_count'],reverse=True))[:num]
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
        "data":[get_blog_posts(4),get_github_data("haideralipunjabi",4),get_foss_contributions(),get_press_posts(4)],
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
    print(template.render(**settings),file=open("assets/manifest.json","w"))
    template = templateEnv.get_template("templates/og.html")
    print(template.render(**settings),file=open("og.html","w"))
    
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


def gen_redirects():
    redirects_file = open("_redirects","a")
    redirects_file.write("\n%s %s 200"%("/contact/*", f"https://api.telegram.org/bot{os.getenv('TELEGRAM_API')}/sendMessage?chat_id={os.getenv('TELEGRAM_CHAT_ID')}&text=:splat"))
    redirects_file.close()


gen_og()
gen_templates()
gen_redirects()
