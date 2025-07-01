import re
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class ContestImageGeneratorV2:
    def __init__(self, contestId, descText, imageSelected, regex=r"^(2023|2024|2022).{9}$", overrideContestName=False, overrideText="", highlightHandle=None):
        self.regex = regex
        self.contestId = contestId
        self.descText = descText
        self.imageSelected = imageSelected
        self.overrideContestName = overrideContestName
        self.overrideText = overrideText
        self.highlightHandle = highlightHandle
        self.colours = ["#22223b", "#9a8c98", "#4a4e69", "#22223b"]
        self.dot_colours = ["#e07a5f", "#3d405b", "#81b29a", "#f2cc8f"]

    def fetchDatabase(self):
        url = "https://algoxxx.onrender.com/database"
        req = requests.get(url)
        data = req.json()
        data.append({"_id":"123","name":"Meet Parmar","bitsid":"2023A7PS0406G","cfid":"meeeet"})
        return data

    def filterEntries(self, dataa):
        return [
            [entry.get("name", ""), entry.get("cfid", "")]
            for entry in dataa
            if re.search(self.regex, entry.get("bitsid", ""))
        ]

    def fetchContestStandings(self):
        url = f"https://codeforces.com/api/contest.standings?contestId={self.contestId}&showUnofficial=true"
        req = requests.get(url)
        if req.status_code != 200:
            raise Exception(f"Failed to fetch contest standings: {req.status_code}")
        return req.json()

    def getContestName(self, resp):
        if resp["status"] == "OK":
            contestName = resp["result"]["contest"]["name"]
        else:
            contestName = "Unknown Contest"
        if self.overrideContestName:
            contestName = self.overrideText
        return contestName

    def mapCfidToName(self, filteredEntries):
        return {cfid: name for name, cfid in filteredEntries}

    def extractStandings(self, resp, cfidToName):
        data = []
        if resp["status"] == "OK":
            for row in resp["result"]["rows"]:
                handle = row["party"]["members"][0]["handle"]
                rank = row["rank"]
                points = row["points"] if "points" in row else 0
                name = cfidToName.get(handle, None)
                if name:
                    data.append([name, handle, rank, points])
        return data

    def generate(self):
        dataa = self.fetchDatabase()
        filteredEntries = self.filterEntries(dataa)
        resp = self.fetchContestStandings()
        contestName = self.getContestName(resp)
        cfidToName = self.mapCfidToName(filteredEntries)
        data = self.extractStandings(resp, cfidToName)
        data = [entry for entry in data if entry[2] != 0]
        data.sort(key=lambda x: x[2])
        ranks = [entry[2] for entry in data]
        points = [entry[3] for entry in data]
        handles = [entry[1] for entry in data]
        names = [entry[0] for entry in data]

        fig, ax = plt.subplots(figsize=(12, 7))
        color = self.dot_colours[self.imageSelected % len(self.dot_colours)]
        ax.plot(points, ranks, "-", color=color, alpha=0.3, linewidth=2)
        ax.scatter(points, ranks, s=120, color=color, edgecolor="#22223b", zorder=3, alpha=0.8)

        # Highlight the user's rank if provided
        if self.highlightHandle and self.highlightHandle in handles:
            idx = handles.index(self.highlightHandle)
            ax.scatter([points[idx]], [ranks[idx]], s=300, color="#f94144", edgecolor="#22223b", zorder=4, label="You", marker="o")
            ax.annotate(f"{names[idx]} ({handles[idx]})", (points[idx], ranks[idx]), textcoords="offset points", xytext=(0,15), ha='center', fontsize=13, fontweight='bold', color="#f94144")

        # Aesthetic improvements
        ax.set_facecolor(self.colours[self.imageSelected % len(self.colours)])
        fig.patch.set_facecolor(self.colours[self.imageSelected % len(self.colours)])
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_xlabel("Points", fontsize=18, fontweight='bold')
        ax.set_ylabel("Rank", fontsize=18, fontweight='bold')
        ax.set_title(f"{contestName}\n{self.descText}", fontsize=22, fontweight='bold', pad=20)
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.invert_yaxis()  # Lower rank is better
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(loc='upper right', fontsize=14)

        # Save
        plt.tight_layout()
        plt.savefig(f"{self.descText}_xkcd.png", dpi=300)
        plt.close()

        # Use PIL to style the image for Instagram
        img = Image.open(f"{self.descText}_xkcd.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("./fonts/Montserrat-Bold.ttf", 40)
        draw.text((20, 20), "Instagram Post", font=font, fill="#ffffff")
        img.save(f"{self.descText}_instagram.png") 