# main.py
import json
from pathlib import Path

# --- NEW IMPORTS for Image Handling ---
try:
    from PIL import Image # Check if Pillow is installed
    import ascii_magic
except ImportError:
    # Set flags to indicate missing libraries
    Image = None
    ascii_magic = None
# --- End New Imports ---

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll, Center
from textual.reactive import var
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane, Markdown

# --- Configuration ---
RESUME_DATA_PATH = Path(__file__).parent / "resume.json"
PROFILE_IMAGE_FILENAME = "me.png"
PROFILE_IMAGE_PATH = Path(__file__).parent / PROFILE_IMAGE_FILENAME
# --- ADJUSTED: Reduce ASCII width significantly ---
ASCII_ART_WIDTH = 45 # Width in characters for the final ASCII output (Reduced from 60)
# --- ADJUSTED: Reduce max pixel height slightly ---
# This helps ensure consistency regardless of original image size.
# Adjust these pixel dimensions as needed for your desired output size/detail.
TARGET_IMAGE_MAX_DIMENSION = (100, 100) # Max width, Max height in pixels (Reduced height from 120)

# --- Load Resume Data ---
# (load_resume_data function remains the same as before)
def load_resume_data():
    """Loads resume data from the JSON file."""
    if not RESUME_DATA_PATH.is_file():
        return {
            "contact": {"name": "Error", "email": "resume.json not found"},
            "experience": [{"title": "N/A", "company": "", "details": ["Check resume.json path"]}],
            "education": [{"degree": "N/A", "university": ""}],
            "skills": {"languages": [], "digital": []}
        }
    try:
        with open(RESUME_DATA_PATH, 'r', encoding='utf-8') as f: # Specify encoding
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "contact": {"name": "Error", "email": "Invalid JSON in resume.json"},
            "experience": [{"title": "N/A", "company": "", "details": ["Check resume.json format"]}],
            "education": [{"degree": "N/A", "university": ""}],
            "skills": {"languages": [], "digital": []}
        }
    except Exception as e:
         return {
            "contact": {"name": "Error", "email": f"Error loading resume.json: {e}"},
            "experience": [{"title": "N/A", "company": "", "details": []}],
            "education": [{"degree": "N/A", "university": ""}],
            "skills": {"languages": [], "digital": []}
        }

RESUME_DATA = load_resume_data()

# --- Formatting Functions (Enhanced) ---
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
    if not exps:
        return output + "\nNo experience data found."
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
            for detail in details:
                output += f"- {detail}\n"
        else:
            output += "- N/A\n"
    return output

def format_education(data):
    edus = data.get("education", [])
    output = "# Education\n"
    if not edus:
        return output + "\nNo education data found."
    for edu in edus:
        output += f"""
---
## {edu.get('degree', 'N/A')} - {edu.get('university', 'N/A')}

**Location:** {edu.get('location', 'N/A')}
**Period:** {edu.get('period', 'N/A')}
"""
        if edu.get('website'):
             if edu['website'].startswith(('http://', 'https://')):
                 output += f"**Website:** [{edu['website']}]({edu['website']})\n"
             else:
                 output += f"**Website:** {edu['website']}\n"
    return output

def format_skills(data):
    skills = data.get("skills", {})
    langs = skills.get("languages", [])
    digital = skills.get("digital", [])
    output = "# Skills\n"
    output += "\n## Languages\n"
    if langs:
        for lang in langs:
            output += f"- {lang}\n"
    else:
        output += "- N/A\n"
    output += "\n## Digital Skills\n"
    if digital:
        for skill in digital:
             output += f"- {skill}\n"
    else:
        output += "- N/A\n"
    return output

# --- MODIFIED: Function to Format Profile Image as ASCII ---
def format_profile_image():
    """Loads profile image, resizes it, and converts it to ASCII art."""
    # Check if required libraries are installed
    if Image is None or ascii_magic is None:
        return ("# Profile Image\n\n"
                "```\nPlease install 'Pillow' and 'ascii_magic' to view image:\n"
                "pip install Pillow ascii_magic\n```")

    # Check if the image file exists
    if not PROFILE_IMAGE_PATH.is_file():
        return f"# Profile Image\n\nImage file not found at:\n{PROFILE_IMAGE_PATH}"

    try:
        # --- Load and Resize Image using Pillow ---
        img = Image.open(PROFILE_IMAGE_PATH)
        # Resize the image while maintaining aspect ratio to fit within TARGET dimensions
        img.thumbnail(TARGET_IMAGE_MAX_DIMENSION) # Uses the updated tuple
        # --- End Resize ---

        # --- Generate ASCII from the resized Pillow image object ---
        my_art = ascii_magic.AsciiArt.from_pillow_image(img)
        # Convert the object to a terminal-ready string
        ascii_art_string = my_art.to_terminal(columns=ASCII_ART_WIDTH) # Uses the updated width
        # --- End ASCII Generation ---

        # Wrap in Markdown code block for monospace rendering
        return f"# Profile Image\n\n```\n{ascii_art_string}\n```"
    except Exception as e:
        # Provide more specific error feedback
        return f"# Profile Image\n\nCould not load/convert image '{PROFILE_IMAGE_FILENAME}':\n{e}"

# --- Main Application ---
# (ResumeApp class remains the same as the previous version)
class ResumeApp(App):
    """A Textual resume viewer app."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+t", "next_tab", "Next Tab"),
        ("ctrl+p", "previous_tab", "Prev Tab")
    ]

    CSS = """
    Screen {
        background: #0d0d0d;
        color: #00ff00;
    }
    TabbedContent > TabPane {
        padding: 1 2;
    }
    Markdown {
        link-color: cyan;
        link-style: underline;
    }
    Markdown BlockCode { /* Style for the ``` block containing ASCII */
        background: #111;
        color: #ccc;
        border: thick #222;
        padding: 1;
        width: auto; /* Let content determine width up to container */
        height: auto; /* Let content determine height */
        text-align: center;
        overflow: hidden; /* Hide overflow instead of scrolling */
    }
    Header {
        background: #004d00;
        color: white;
    }
    Footer {
        background: #003300;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with TabbedContent(initial="about_me"):
            with TabPane("About Me", id="about_me"):
                 # Removed VerticalScroll here, relying on content fitting
                 # or being hidden by Markdown BlockCode overflow style
                 yield Markdown(format_profile_image(), id="profile-image")
            with TabPane("Contact", id="contact"):
                with VerticalScroll(): # Keep scroll for potentially long text
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
        yield Footer()

    def action_quit(self) -> None:
        self.exit()

    def action_next_tab(self) -> None:
         try:
            self.query_one(TabbedContent).action_next_tab()
         except Exception:
            pass

    def action_previous_tab(self) -> None:
         try:
            self.query_one(TabbedContent).action_previous_tab()
         except Exception:
            pass


if __name__ == "__main__":
    if not RESUME_DATA_PATH.is_file():
         print(f"ERROR: Cannot find {RESUME_DATA_PATH}")
         print("Please create this file with your resume data in JSON format.")
         exit(1)

    if not PROFILE_IMAGE_PATH.is_file():
        print(f"WARNING: Profile image '{PROFILE_IMAGE_FILENAME}' not found at {PROFILE_IMAGE_PATH}")
        print("The 'About Me' tab will show an error message.")

    app = ResumeApp()
    app.run()
