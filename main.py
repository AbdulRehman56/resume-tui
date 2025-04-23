# main.py
import json
import random
import threading
import time
import math # Needed for donut
from pathlib import Path

# --- Library Imports ---
try:
    # Pillow might be needed by some terminals or underlying libs, keep for safety
    from PIL import Image
    # Use pygame for sound control (looping/stopping)
    import pygame
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please ensure you have installed all dependencies:")
    print("pip install textual Pillow pygame")
    exit(1)

from textual.app import App, ComposeResult
# --- Import Container ---
from textual.containers import Container, VerticalScroll, Center, Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane, Markdown, Button
# from textual.on import on # <-- Keeping commented out

# --- Configuration ---
RESUME_DATA_PATH = Path(__file__).parent / "resume.json"
SOUNDS_DIR = Path(__file__).parent / "sounds"
RAIN_SOUND_FILENAME = "rain.wav" # User needs to provide this (or change to .ogg)

# --- Pygame Mixer Initialization ---
SOUND_LOADED = False # Default to False
try:
    pygame.mixer.init() # Initialize the mixer
    RAIN_SOUND_PATH = SOUNDS_DIR / RAIN_SOUND_FILENAME
    if RAIN_SOUND_PATH.is_file():
        pygame.mixer.music.load(str(RAIN_SOUND_PATH))
        SOUND_LOADED = True # Set to True only if load succeeds
    else:
        print(f"WARNING: Sound file not found at {RAIN_SOUND_PATH}")
except pygame.error as pg_error:
    print(f"Pygame mixer error: {pg_error}")
    print(f"Could not load sound file: {RAIN_SOUND_PATH}")
    print("Sound effects might not work. Ensure the file is valid (WAV/OGG) and drivers are available.")
except Exception as e:
    print(f"Error initializing sound: {e}")


# --- Sound Playback Helper ---
def toggle_rain_sound(play: bool):
    """Starts or stops the looping rain sound."""
    if not SOUND_LOADED:
        return
    try:
        if play and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(loops=-1) # Loop indefinitely
        elif not play and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    except Exception as e:
        # print(f"Error toggling sound: {e}")
        pass

# --- Load Resume Data ---
# (load_resume_data function remains the same)
def load_resume_data():
    """Loads resume data from the JSON file."""
    if not RESUME_DATA_PATH.is_file():
        return {
            "contact": {"name": "Error", "email": f"{RESUME_DATA_PATH.name} not found"},
            "experience": [{"title": "N/A", "company": "", "details": ["Check resume.json path"]}],
            "education": [{"degree": "N/A", "university": ""}],
            "skills": {"languages": [], "digital": []} }
    try:
        with open(RESUME_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "contact": {"name": "Error", "email": f"Invalid JSON in {RESUME_DATA_PATH.name}"},
            "experience": [{"title": "N/A", "company": "", "details": ["Check resume.json format"]}],
            "education": [{"degree": "N/A", "university": ""}],
            "skills": {"languages": [], "digital": []} }
    except Exception as e:
         return {
            "contact": {"name": "Error", "email": f"Error loading {RESUME_DATA_PATH.name}: {e}"},
            "experience": [{"title": "N/A", "company": "", "details": []}],
            "education": [{"degree": "N/A", "university": ""}],
            "skills": {"languages": [], "digital": []} }

RESUME_DATA = load_resume_data()

# --- Formatting Functions ---
# (format_contact, format_experience, format_education, format_skills remain the same)
def format_contact(data):
    c = data.get("contact", {})
    return f"""
# Contact Information

**Name:** {c.get('name', 'N/A')}
**Email:** {c.get('email', 'N/A')}
**Phone:** {c.get('phone', 'N/A')}
**Address:** {c.get('address', 'N/A')}
**Birthdate:** {c.get('dob', 'N/A')}
**Nationality:** {c.get('nationality', 'N/A')}
"""

def format_experience(data):
    exps = data.get("experience", [])
    output = "# Work Experience\n"
    if not exps: return output + "\nNo experience data found."
    for exp in exps:
        output += f"""
---
## {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}

**Location:** {exp.get('location', 'N/A')}
**Period:** {exp.get('period', 'N/A')}

**Responsibilities / Details:**
"""
        details = exp.get('details', [])
        if details:
            for detail in details: output += f"- {detail}\n"
        else: output += "- N/A\n"
    return output

def format_education(data):
    edus = data.get("education", [])
    output = "# Education\n"
    if not edus: return output + "\nNo education data found."
    for edu in edus:
        output += f"""
---
## {edu.get('degree', 'N/A')} - {edu.get('university', 'N/A')}

**Location:** {edu.get('location', 'N/A')}
**Period:** {edu.get('period', 'N/A')}
"""
        website = edu.get('website')
        if website:
             if website.startswith(('http://', 'https://')):
                 output += f"**Website:** [{website}]({website})\n"
             else: output += f"**Website:** {website}\n"
    return output

def format_skills(data):
    skills = data.get("skills", {})
    langs = skills.get("languages", [])
    digital = skills.get("digital", [])
    output = "# Skills\n"
    output += "\n## Languages\n"
    if langs:
        for lang in langs: output += f"- {lang}\n"
    else: output += "- N/A\n"
    output += "\n## Digital Skills\n"
    if digital:
        for skill in digital: output += f"- {skill}\n"
    else: output += "- N/A\n"
    return output

# --- Rain Effect Widget ---
# (RainWidget class remains the same)
class RainWidget(Widget):
    """A widget to display a simple rain effect."""
    rain_lines = reactive([])

    def on_mount(self) -> None:
        self.update_rain()
        self.set_interval(0.2, self.update_rain) # Adjust interval for speed

    def update_rain(self) -> None:
        width, height = self.size
        if width <= 0 or height <= 0: return

        new_lines = [""] * height
        # Only use visible lines from previous state
        old_lines = self.rain_lines[:height]

        # Move existing rain down
        for r in range(height - 1, 0, -1):
            if r - 1 < len(old_lines):
                line_content = old_lines[r-1]
                new_lines[r] = line_content.ljust(width)[:width]

        # Add new drops at the top randomly
        top_line = list(" " * width)
        density = 0.05 # Adjust density
        for i in range(width):
            if random.random() < density:
                top_line[i] = random.choice(['|', '.', ':', '*']) # Rain characters
        new_lines[0] = "".join(top_line)

        # Pad lines to ensure consistent width
        for i in range(len(new_lines)):
            new_lines[i] = new_lines[i].ljust(width)[:width]

        self.rain_lines = new_lines
        self.refresh() # Request repaint

    def render(self) -> str:
        """Render the current state of the rain."""
        width, height = self.size
        if height <= 0: return ""
        # Only return the number of lines that fit the widget's height
        return "\n".join(self.rain_lines[:height])

# --- Spinning Donut Widget ---
# (DonutWidget class remains the same)
class DonutWidget(Static):
    """A widget to display the spinning ASCII donut."""
    donut_frame = reactive("")
    _A = 0.0
    _B = 0.0

    def on_mount(self) -> None:
        self.update_donut()
        self.set_interval(1 / 30, self.update_donut)

    def update_donut(self) -> None:
        output = [' '] * 1760
        zbuffer = [0.0] * 1760
        A = self._A
        B = self._B
        cosA = math.cos(A)
        sinA = math.sin(A)
        cosB = math.cos(B)
        sinB = math.sin(B)

        for j in range(0, 628, 7):
            cosj = math.cos(j * 0.01)
            sinj = math.sin(j * 0.01)
            for i in range(0, 628, 2):
                cosp = math.cos(i * 0.01)
                sinp = math.sin(i * 0.01)
                h = cosj + 2
                D = 1 / (sinp * h * sinA + sinj * cosA + 5)
                t = sinp * h * cosA - sinj * sinA
                x = int(40 + 30 * D * (cosp * h * cosB - t * sinB))
                y = int(12 + 15 * D * (cosp * h * sinB + t * cosB))
                o = x + 80 * y
                N = int(8 * ((sinj * sinA - sinp * cosj * cosA) * cosB - sinp * cosj * sinA - sinj * cosA - cosp * cosj * sinB))
                if 0 <= y < 22 and 0 <= x < 80 and D > zbuffer[o]:
                    zbuffer[o] = D
                    output[o] = ".,-~:;=!*#$@"[max(0, N)]
        for k in range(80 - 1, 1760, 80):
             output[k] = "\n"
        self.donut_frame = "".join(output)
        self._A += 0.05
        self._B += 0.03

    def render(self) -> str:
        # Wrap in code block for monospace and styling
        return f"```\n{self.donut_frame}\n```"


# --- Main Application ---
class ResumeApp(App):
    """A Textual resume viewer app."""
    is_raining = reactive(False)

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+t", "next_tab", "Next Tab"),
        ("ctrl+p", "previous_tab", "Prev Tab"),
        ("r", "toggle_rain", "Toggle Rain Sound")
    ]

    CSS = """
    Screen {
        /* Layers not needed if rain is contained */
        background: #0d0d0d;
        color: #00ff00;
    }
    /* Container for the rain effect at the bottom */
    #rain-container {
        dock: bottom; /* Dock it at the bottom */
        height: 4; /* Set a fixed small height (e.g., 4 lines) */
        width: 100%;
        overflow: hidden; /* Hide any overflow from the rain */
        border-top: thick #003300; /* Optional border above rain */
        background: #050505; /* Slightly different background for rain area */
    }
    /* Rain widget itself, now inside the container */
    RainWidget {
        /* layer removed, it's contained now */
        color: #006600; /* Darker green for rain */
        width: 100%;
        height: 100%; /* Fill its container */
    }
    Header { background: #004d00; color: white; }
    Footer { background: #003300; }
    TabbedContent { /* This will fill the space between Header and rain-container/Footer */
        /* No layer needed */
    }
    TabbedContent > TabPane {
        padding: 1 2;
        background: #0d0d0d;
    }
    Markdown {
        link-color: cyan;
        link-style: underline;
    }
    DonutWidget > Static {
         background: #111;
         color: #ccc;
         border: thick #222;
         padding: 0 1;
         width: auto;
         height: auto;
         text-align: center;
         overflow: hidden;
         /* font-family removed */
    }
    Markdown BlockCode {
        background: #111;
        color: #ccc;
        border: thick #222;
        padding: 1;
        width: auto;
        height: auto;
        text-align: left;
        overflow: hidden;
    }
    Footer Button {
        width: auto;
        height: 1;
        min-width: 10;
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # Header first
        yield Header()
        # Main content area
        with TabbedContent(initial="about_me"):
            with TabPane("About Me", id="about_me"):
                 with Container():
                     yield DonutWidget()
            with TabPane("Contact", id="contact"):
                with VerticalScroll():
                    yield Markdown(format_contact(RESUME_DATA))
            with TabPane("Experience", id="experience"):
                 with VerticalScroll():
                    yield Markdown(format_experience(RESUME_DATA))
            with TabPane("Education", id="education"):
                 with VerticalScroll():
                    yield Markdown(format_education(RESUME_DATA))
            with TabPane("Skills", id="skills"):
                 with VerticalScroll():
                    yield Markdown(format_skills(RESUME_DATA))
        # Rain container docked above the footer
        with Container(id="rain-container"):
            yield RainWidget()
        # Footer last
        yield Footer()
        # Mount button after footer is composed
        try:
            footer = self.query_one(Footer)
            self.mount(
                Button("Rain Sound: OFF", id="rain-button", variant="default"),
                after=footer
            )
        except Exception:
             pass

    # --- Event Handlers & Actions ---
    def on_mount(self) -> None:
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "rain-button":
            self.is_raining = not self.is_raining

    def watch_is_raining(self, raining: bool) -> None:
        try:
            button = self.query_one("#rain-button", Button)
            if raining:
                toggle_rain_sound(True)
                button.label = "Rain Sound: ON"
                button.variant = "success"
            else:
                toggle_rain_sound(False)
                button.label = "Rain Sound: OFF"
                button.variant = "default"
        except Exception:
            pass

    def action_next_tab(self) -> None:
         try:
            self.query_one(TabbedContent).action_next_tab()
         except Exception: pass

    def action_previous_tab(self) -> None:
         try:
            self.query_one(TabbedContent).action_previous_tab()
         except Exception: pass

    def action_toggle_rain(self) -> None:
        self.is_raining = not self.is_raining

    def action_quit(self) -> None:
        if SOUND_LOADED:
            pygame.mixer.music.stop()
        self.exit()


if __name__ == "__main__":
    if not RESUME_DATA_PATH.is_file():
         print(f"ERROR: Cannot find {RESUME_DATA_PATH}")
         exit(1)

    if not SOUNDS_DIR.is_dir():
        print(f"WARNING: Sounds directory not found at {SOUNDS_DIR}")
    elif not (SOUNDS_DIR / RAIN_SOUND_FILENAME).is_file():
         print(f"WARNING: Rain sound file '{RAIN_SOUND_FILENAME}' not found in {SOUNDS_DIR}")

    app = ResumeApp()
    app.run()
