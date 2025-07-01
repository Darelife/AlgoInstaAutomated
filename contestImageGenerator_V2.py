from PIL import Image, ImageDraw, ImageFont
import re
import requests
import random
import math
import numpy as np

class ContestImageGeneratorV2:
    def __init__(self, contestId, descText, imageSelected=0, regex=r"^(2023|2024|2022).{9}$", overrideContestName=False, overrideText=""):
        self.contestId = contestId
        self.descText = descText
        self.imageSelected = imageSelected
        self.regex = regex
        self.overrideContestName = overrideContestName
        self.overrideText = overrideText
        
        # Image dimensions for Instagram story (9:16 aspect ratio)
        self.width = 1080
        self.height = 1920
        
        # Colors
        self.bg_color = "#1a1a1a"  # Dark background
        self.axis_color = "#404040"  # Dark gray for axes
        self.text_color = "#e1e1de"  # Light gray for main text
        self.subtext_color = "#A0A0A0"  # Gray for subtext
        self.marker_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD", "#D4A5A5"]
        
        # Initialize drawing objects
        self.image = None
        self.draw = None
        self.fonts = {}
        
    def setup_fonts(self):
        """Initialize fonts with different sizes for various text elements"""
        font_path = "./fonts/Montserrat-Light.ttf"
        bold_font_path = "./fonts/Montserrat-Bold.ttf"
        
        self.fonts = {
            'title': ImageFont.truetype(bold_font_path, 80),
            'subtitle': ImageFont.truetype(font_path, 60),
            'name': ImageFont.truetype(bold_font_path, 40),
            'subtext': ImageFont.truetype(font_path, 30)
        }
    
    def add_wobble(self, points, amplitude=2, frequency=0.1):
        """Add a wobble effect to a line of points"""
        wobbled = []
        for i, (x, y) in enumerate(points):
            # Add random noise with controlled amplitude
            noise_x = amplitude * math.sin(frequency * i + random.random() * 2 * math.pi)
            noise_y = amplitude * math.sin(frequency * i + random.random() * 2 * math.pi)
            wobbled.append((x + noise_x, y + noise_y))
        return wobbled
    
    def draw_wobbly_line(self, points, color, width=2):
        """Draw a line with wobble effect"""
        wobbled_points = self.add_wobble(points)
        for i in range(len(wobbled_points) - 1):
            self.draw.line([wobbled_points[i], wobbled_points[i + 1]], 
                         fill=color, width=width)
    
    def draw_axes(self):
        """Draw XKCD-style axes"""
        # Define graph area
        margin = 200
        graph_width = self.width - 2 * margin
        graph_height = self.height - 2 * margin
        
        # Draw axes with wobble
        x_axis_points = [(margin, self.height - margin), 
                        (self.width - margin, self.height - margin)]
        y_axis_points = [(margin, margin), 
                        (margin, self.height - margin)]
        
        self.draw_wobbly_line(x_axis_points, self.axis_color, width=3)
        self.draw_wobbly_line(y_axis_points, self.axis_color, width=3)
        
        return margin, graph_width, graph_height
    
    def draw_participant_marker(self, x, y, name, handle, rank, color):
        """Draw a participant marker with annotation"""
        # Draw marker
        marker_radius = 8
        self.draw.ellipse([x - marker_radius, y - marker_radius,
                          x + marker_radius, y + marker_radius],
                         fill=color)
        
        # Calculate annotation position
        annotation_x = x + 50
        annotation_y = y - 40
        
        # Draw annotation line
        self.draw_wobbly_line([(x, y), (annotation_x, annotation_y)], color)
        
        # Draw name
        self.draw.text((annotation_x, annotation_y),
                      name,
                      font=self.fonts['name'],
                      fill=self.text_color)
        
        # Draw handle and rank
        self.draw.text((annotation_x, annotation_y + 45),
                      f"{handle} • Rank {rank}",
                      font=self.fonts['subtext'],
                      fill=self.subtext_color)
    
    def draw_title(self, contest_name):
        """Draw the contest title and description"""
        # Draw contest name
        self.draw.text((self.width // 2, 200),
                      contest_name.upper(),
                      font=self.fonts['title'],
                      fill=self.text_color,
                      anchor="mm")
        
        # Draw description
        self.draw.text((self.width // 2, 300),
                      self.descText,
                      font=self.fonts['subtitle'],
                      fill=self.text_color,
                      anchor="mm")
    
    def fetch_database(self):
        """Fetch participant data from the database"""
        url = "https://algoxxx.onrender.com/database"
        req = requests.get(url)
        data = req.json()
        data.append({"_id":"123","name":"Meet Parmar","bitsid":"2023A7PS0406G","cfid":"meeeet"})
        return data
    
    def filter_entries(self, data):
        """Filter entries based on regex pattern"""
        return [
            [entry.get("name", ""), entry.get("cfid", "")]
            for entry in data
            if re.search(self.regex, entry.get("bitsid", ""))
        ]
    
    def fetch_contest_standings(self):
        """Fetch contest standings from Codeforces API"""
        url = f"https://codeforces.com/api/contest.standings?contestId={self.contestId}&showUnofficial=true"
        req = requests.get(url)
        if req.status_code != 200:
            raise Exception(f"Failed to fetch contest standings: {req.status_code}")
        return req.json()
    
    def get_contest_name(self, resp):
        """Get contest name from API response"""
        if resp["status"] == "OK":
            contest_name = resp["result"]["contest"]["name"]
        else:
            contest_name = "Unknown Contest"
        if self.overrideContestName:
            contest_name = self.overrideText
        return contest_name
    
    def map_cfid_to_name(self, filtered_entries):
        """Create mapping from Codeforces ID to name"""
        return {cfid: name for name, cfid in filtered_entries}
    
    def extract_standings(self, resp, cfid_to_name):
        """Extract standings data from API response"""
        data = []
        if resp["status"] == "OK":
            for row in resp["result"]["rows"]:
                handle = row["party"]["members"][0]["handle"]
                rank = row["rank"]
                name = cfid_to_name.get(handle, None)
                if name:
                    data.append([name, handle, rank])
        return data
    
    def get_top_6(self, data):
        """Get top 6 participants"""
        return sorted([entry for entry in data if entry[2] != 0], 
                     key=lambda x: x[2])[:min(6, len(data))]
    
    def generate(self):
        """Generate the contest image"""
        # Create new image
        self.image = Image.new('RGB', (self.width, self.height), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)
        self.setup_fonts()
        
        # Fetch and process data
        data = self.fetch_database()
        filtered_entries = self.filter_entries(data)
        resp = self.fetch_contest_standings()
        contest_name = self.get_contest_name(resp)
        cfid_to_name = self.map_cfid_to_name(filtered_entries)
        standings = self.extract_standings(resp, cfid_to_name)
        top_6 = self.get_top_6(standings)
        
        # Draw title and axes
        self.draw_title(contest_name)
        margin, graph_width, graph_height = self.draw_axes()
        
        # Draw participant markers
        for i, (name, handle, rank) in enumerate(top_6):
            # Calculate position based on rank and some randomness
            x = margin + (i + 1) * (graph_width / 7)
            y = margin + graph_height - (rank * (graph_height / 10))
            
            # Add some randomness to positions
            x += random.uniform(-20, 20)
            y += random.uniform(-20, 20)
            
            # Draw marker with annotation
            self.draw_participant_marker(x, y, name, handle, rank, 
                                       self.marker_colors[i % len(self.marker_colors)])
        
        # Save the image
        self.image.save(f"{self.descText}_xkcd.png") 