from PIL import Image, ImageDraw, ImageFont
import re
import json
import requests

imageList = ["dark.png", "brown.png", "purple.png", "blue.png"]
textColour = ["#e1e1de", "#ffe5c0", "#e4caf4", "#cbdcfd"]

contestId = 2109
regex = r"^(2023|2024|2022).{9}$"
descText = "TOP 5 - Overall"
imageSelected = 1
overrideContestName = False
overrideText = "CODEFORCES Div. 2 Round 1025"

imageSelected %=4


# with open("database.json", "r") as f:
#     dataa = json.load(f)

url = "https://algoxxx.onrender.com/database"
req = requests.get(url)
dataa = req.json()

# [{"_id":"677f9c5e23c75525f713eb4a","name":"Guranurag Singh Tung","bitsid":"2023A7PS0412G","cfid":"woyeta","__v":0},{"_id":"677f9c5f23c75525f713eb4e","name":"Jayanth","bitsid":"2023A7PS0399G","cfid":"Jayanth_2006","__v":0},
filtered_entries = [
    [entry.get("name", ""), entry.get("cfid", "")]
    for entry in dataa
    if re.search(regex, entry.get("bitsid", ""))
]

# https://codeforces.com/api/contest.standings?contestId=2109&showUnofficial=true
url = f"https://codeforces.com/api/contest.standings?contestId={contestId}&showUnofficial=true"
req = requests.get(url)
resp = req.json()

contestName = resp["result"]["contest"]["name"] if resp["status"] == "OK" else "Unknown Contest"
if (overrideContestName == True): contestName = overrideText

# Map cfid to name for quick lookup
cfid_to_name = {cfid: name for name, cfid in filtered_entries}

# Extract standings
data = []
if resp["status"] == "OK":
    for row in resp["result"]["rows"]:
        handle = row["party"]["members"][0]["handle"]
        points = row["points"]
        name = cfid_to_name.get(handle, None)
        if name:
            data.append([name, handle, points])
else:
    data = []

# If not enough data, fill with sample data
if len(data) < 5:
    data += [
        ["Alice", "alice_cf", 2100],
        ["Bob", "bob_the_coder", 2500],
        ["Charlie", "chaz123", 1800],
        ["Diana", "didi_the_challenger_of_worlds", 2600],
        ["Eve", "eve_hacks", 2400],
        ["Franklin Longname", "frankie_the_l33t_programmer", 2300],
    ][:5-len(data)]

# Sort top 5 by points descending
top_5 = sorted(data, key=lambda x: x[2], reverse=True)[:5]

# Utility to truncate strings > 20 characters
def truncate(text):
    return text if len(text) <= 20 else text[:17] + "..."

# Image setup
# width, height = 1080, 1920
background = Image.open(f"./BGCL/{imageList[imageSelected]}")
width, height = background.size
draw = ImageDraw.Draw(background)

# Load font
font_path = "./fonts/Montserrat-Light.ttf"
title_font = ImageFont.truetype(font_path, 123)
line_font = ImageFont.truetype(font_path, 52)

# Title
# draw.text((width // 2, 100), "Top 5 Coders", font=title_font, fill=textColour[imageSelected], anchor="mm")

# To make text bold, use a bold font variant
bold_font_path = "./fonts/Montserrat-Bold.ttf"
title_bold_font = ImageFont.truetype(bold_font_path, 80)
draw.text((width//2, 750), contestName.upper(), font=title_bold_font, fill=textColour[imageSelected], anchor="mm")

draw.text((width//2, 950), descText, font = title_font, fill = textColour[imageSelected], anchor="mm")

# Table start
start_y = 1250
gap = 110
x_name = 120
x_handle = 700
x_points = 1430

for idx, (name, handle, points) in enumerate(reversed(top_5)):
    y = start_y + idx * gap
    name_trunc = truncate(name)
    handle_trunc = truncate(handle)

    draw.text((x_name, y), f"{name_trunc}", font=line_font, fill=textColour[imageSelected])
    draw.text((x_handle, y), f"{handle_trunc}", font=line_font, fill=textColour[imageSelected])
    draw.text((x_points, y), f"{int(points)}", font=line_font, fill=textColour[imageSelected], anchor="ra")

# Save and show
background.save(f"{descText}.png")
