from cairosvg import svg2png
from PIL import Image

ICONS = [32,70,72,96,128,144,150,152,180,192,196,310,384,512]

def gen_icons():
    os.system("mkdir assets/favicons")
    icon_svg = "assets/icon.svg"    
    for icon in ICONS:
        svg2png(url=icon_svg, write_to=f"assets/favicons/icon-{icon}x{icon}.png", parent_width=icon,parent_height=icon)
    Image.open("assets/favicons/icon-512x512.png").save("assets/favicons/favicon.ico")