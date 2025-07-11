from PIL import Image, ImageDraw, ImageFont
import re
import requests
import json

class ContestImageGenerator:
    def __init__(self, contestId, descText, imageSelected, regex=r"^(2023|2024|2022).{9}$", overrideContestName=False, overrideText=""):
        self.imageList = ["dark.png", "brown.png", "purple.png", "blue.png"]
        self.textColour = ["#e1e1de", "#ffe5c0", "#e4caf4", "#cbdcfd"]
        self.regex = regex
        self.contestId = contestId
        self.descText = descText
        self.imageSelected = imageSelected % len(self.textColour)
        self.overrideContestName = overrideContestName
        self.overrideText = overrideText
        self.background = None
        self.width = None
        self.height = None
        self.draw = None
        self.titleFont = None
        self.lineFont = None
        self.titleBoldFont = None

    def fetchDatabase(self):
        url = "https://algoxxx.onrender.com/database"
        req = requests.get(url)
        data = req.json()
        data.append({"_id":"123","name":"Meet Parmar","bitsid":"2023A7PS0406G","cfid":"meeeet"})
        return data

    def filterEntries(self, dataa):
        return [
            [entry.get("name", "").title(), entry.get("cfid", "").lower()]
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
                handle = row["party"]["members"][0]["handle"].lower()
                rank = row["rank"]
                name = cfidToName.get(handle, None)
                if name:
                    data.append([name, handle, rank])
        with open("t.json", "w") as f:
            json.dump(data, f, indent=2);
        return data

    def getTop6(self, data):
        return sorted([entry for entry in data if entry[2] != 0], key=lambda x: x[2])[:min(6, len(data))]

    def truncate(self, text):
        return text if len(text) <= 17 else text[:14] + "..."

    def setupImage(self):
        self.background = Image.open(f"./BGCL/{self.imageList[self.imageSelected]}")
        self.width, self.height = self.background.size
        self.draw = ImageDraw.Draw(self.background)
        fontPath = "./fonts/Montserrat-Light.ttf"
        boldFontPath = "./fonts/Montserrat-Bold.ttf"
        self.titleFont = ImageFont.truetype(fontPath, 123)
        self.lineFont = ImageFont.truetype(fontPath, 52)
        self.titleBoldFont = ImageFont.truetype(boldFontPath, 80)

    def drawTitle(self, contestName):
        self.draw.text(
            (self.width // 2, 750),
            contestName.upper(),
            font=self.titleBoldFont,
            fill=self.textColour[self.imageSelected],
            anchor="mm"
        )
        self.draw.text(
            (self.width // 2, 950),
            self.descText,
            font=self.titleFont,
            fill=self.textColour[self.imageSelected],
            anchor="mm"
        )

    def drawTable(self, top5):
        startY = 1250
        gap = 110
        xName = 120
        xHandle = 700
        xPoints = 1430
        for idx, (name, handle, points) in enumerate(top5):
            y = startY + idx * gap
            nameTrunc = self.truncate(name)
            handleTrunc = self.truncate(handle)
            self.draw.text((xName, y), f"{nameTrunc}", font=self.lineFont, fill=self.textColour[self.imageSelected])
            self.draw.text((xHandle, y), f"{handleTrunc}", font=self.lineFont, fill=self.textColour[self.imageSelected])
            self.draw.text((xPoints, y), f"{int(points)}", font=self.lineFont, fill=self.textColour[self.imageSelected])

    def saveImage(self):
        self.background.save(f"{self.descText}.png")

    def generate(self):
        dataa = self.fetchDatabase()
        filteredEntries = self.filterEntries(dataa)
        resp = self.fetchContestStandings()
        contestName = self.getContestName(resp)
        cfidToName = self.mapCfidToName(filteredEntries)
        data = self.extractStandings(resp, cfidToName)
        top6 = self.getTop6(data)
        self.setupImage()
        self.drawTitle(contestName)
        self.drawTable(top6)
        self.saveImage()
