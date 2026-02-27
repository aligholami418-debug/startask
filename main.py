"""
Star Task - Task Manager with Sky Theme
Complete English version – corrected star calculations
"""

import os
import json
import random
from datetime import datetime, timedelta

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget

# ----------------------------------------------------------------------
# Font setup (Arial is used – works on Windows)
# ----------------------------------------------------------------------
FONT_NAME = "Arial"   # Change if you have a custom font

Window.size = (400, 700)
Window.clearcolor = (0.05, 0.05, 0.1, 1)   # Dark blue background

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def week_of_year(date):
    return date.isocalendar()[1]

# ----------------------------------------------------------------------
# Database class
# ----------------------------------------------------------------------
class Database:
    def __init__(self):
        self.data_file = "database/user_data.json"
        os.makedirs("database", exist_ok=True)
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.create_default_data()
        else:
            self.create_default_data()

    def create_default_data(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.data = {
            "user": {
                "name": "User",
                "streak": 0,
                "total_stars": 0,
                "last_active_date": today_str
            },
            "tasks": {
                "fixed": [
                    {"id": 1, "title": "📚 1 hour study", "completed": False, "stars": 1},
                    {"id": 2, "title": "🏃 30 min exercise", "completed": False, "stars": 1},
                    {"id": 3, "title": "🧹 Tidy up room", "completed": False, "stars": 1},
                    {"id": 4, "title": "💧 Drink 8 glasses of water", "completed": False, "stars": 1},
                    {"id": 5, "title": "📝 Do homework", "completed": False, "stars": 1},
                    {"id": 6, "title": "📖 Read 30 min", "completed": False, "stars": 1},
                    {"id": 7, "title": "🎨 Artistic activity", "completed": False, "stars": 1},
                    {"id": 8, "title": "📱 Less than 1h gaming", "completed": False, "stars": 1},
                    {"id": 9, "title": "👨‍👩‍👧 Help family", "completed": False, "stars": 1},
                    {"id": 10, "title": "😴 Sleep before 11 PM", "completed": False, "stars": 1}
                ],
                "custom": [],
                "special": {
                    "title": self._get_special_task(),
                    "completed": False,
                    "stars": 3
                }
            },
            "stats": {
                "daily": {},
                "moods": [],
                "monthly_stars": {}
            }
        }
        self.save_data()

    def _get_special_task(self):
        specials = [
            "✨ Plant a flower at home",
            "✨ Watch a scientific documentary",
            "✨ Learn a simple craft",
            "✨ Help a classmate",
            "✨ Write a short story",
            "✨ Cook or bake something",
            "✨ Walk in nature"
        ]
        week = week_of_year(datetime.now())
        return specials[week % len(specials)]

    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except:
            pass

    def complete_task(self, task_type, task_id=None, title=None):
        today = datetime.now().strftime("%Y-%m-%d")
        stars_earned = 1
        if task_type == "fixed" and task_id:
            for task in self.data["tasks"]["fixed"]:
                if task["id"] == task_id and not task["completed"]:
                    task["completed"] = True
                    stars_earned = task["stars"]
                    break
        elif task_type == "custom" and title:
            for task in self.data["tasks"]["custom"]:
                if task["title"] == title and not task["completed"]:
                    task["completed"] = True
                    stars_earned = task["stars"]
                    break
        elif task_type == "special":
            if not self.data["tasks"]["special"]["completed"]:
                self.data["tasks"]["special"]["completed"] = True
                stars_earned = self.data["tasks"]["special"]["stars"]
                self.data["tasks"]["special"]["title"] = self._get_special_task()

        total_tasks = len(self.data["tasks"]["fixed"]) + len(self.data["tasks"]["custom"])
        if today not in self.data["stats"]["daily"]:
            self.data["stats"]["daily"][today] = {
                "completed_tasks": 0,
                "total_tasks": total_tasks,
                "stars_earned": 0,
                "mood": None
            }
        self.data["stats"]["daily"][today]["completed_tasks"] += 1
        self.data["stats"]["daily"][today]["stars_earned"] += stars_earned
        self.data["user"]["total_stars"] += stars_earned
        self.update_streak()
        self.save_data()
        return stars_earned

    def update_streak(self):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if yesterday in self.data["stats"]["daily"] and self.data["stats"]["daily"][yesterday]["completed_tasks"] > 0:
            self.data["user"]["streak"] += 1
        else:
            self.data["user"]["streak"] = 1
        self.data["user"]["last_active_date"] = today

    def add_custom_task(self, title):
        self.data["tasks"]["custom"].append({"title": title, "completed": False, "stars": 1})
        # Update today's total tasks count
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.data["stats"]["daily"]:
            self.data["stats"]["daily"][today]["total_tasks"] += 1
        self.save_data()

    def save_mood(self, mood):
        today = datetime.now().strftime("%Y-%m-%d")
        total_tasks = len(self.data["tasks"]["fixed"]) + len(self.data["tasks"]["custom"])
        if today in self.data["stats"]["daily"]:
            self.data["stats"]["daily"][today]["mood"] = mood
        else:
            self.data["stats"]["daily"][today] = {
                "completed_tasks": 0,
                "total_tasks": total_tasks,
                "stars_earned": 0,
                "mood": mood
            }
        self.data["stats"]["moods"].append({"date": today, "mood": mood})
        self.save_data()

    def end_day(self):
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        if month not in self.data["stats"]["monthly_stars"]:
            self.data["stats"]["monthly_stars"][month] = 0
        if today in self.data["stats"]["daily"]:
            self.data["stats"]["monthly_stars"][month] += self.data["stats"]["daily"][today]["stars_earned"]

        # Reset tasks
        for task in self.data["tasks"]["fixed"]:
            task["completed"] = False
        for task in self.data["tasks"]["custom"]:
            task["completed"] = False
        self.data["tasks"]["special"]["completed"] = False
        self.data["tasks"]["special"]["title"] = self._get_special_task()
        self.save_data()

# ----------------------------------------------------------------------
# PieChart widget
# ----------------------------------------------------------------------
class PieChart(Widget):
    def __init__(self, percentage, **kwargs):
        super().__init__(**kwargs)
        self.percentage = percentage
        self.bind(pos=self.update, size=self.update)

    def update(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 0.2)
            Line(circle=(self.center_x, self.center_y, min(self.width, self.height)/2), width=2)
            angle = 360 * self.percentage
            if angle > 0:
                Color(1, 0.8, 0.2, 1)
                Line(circle=(self.center_x, self.center_y, min(self.width, self.height)/2, 0, angle), width=10)

# ----------------------------------------------------------------------
# Home Screen
# ----------------------------------------------------------------------
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.mood_popup = None
        self.motivation_label = None
        self.custom_layout = None
        self.build_ui()
        Clock.schedule_interval(self.update_stars, 5)

    def build_ui(self):
        main = BoxLayout(orientation='vertical', padding=20, spacing=10)
        with main.canvas.before:
            Color(0.05, 0.05, 0.15, 1)
            self.rect = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=self._update_rect, size=self._update_rect)

        # Date
        date_label = Label(
            text=datetime.now().strftime("%A - %Y/%m/%d"),
            font_size=18,
            color=(1,1,0.8,1),
            font_name=FONT_NAME,
            halign='center',
            valign='middle',
            size_hint_y=0.1,
            size_hint_x=1
        )
        date_label.bind(size=lambda *x: setattr(date_label, 'text_size', (date_label.width, None)))
        main.add_widget(date_label)

        # Title
        title = Label(
            text="✨ Star Task ✨",
            font_size=32,
            color=(1,0.9,0.2,1),
            font_name=FONT_NAME,
            halign='center',
            valign='middle',
            size_hint_y=0.1,
            size_hint_x=1
        )
        title.bind(size=lambda *x: setattr(title, 'text_size', (title.width, None)))
        main.add_widget(title)

        # Fixed tasks
        fixed_title = Label(
            text="📋 Daily Tasks",
            font_size=20,
            color=(0.7,0.8,1,1),
            font_name=FONT_NAME,
            halign='center',
            valign='middle',
            size_hint_y=0.05,
            size_hint_x=1
        )
        fixed_title.bind(size=lambda *x: setattr(fixed_title, 'text_size', (fixed_title.width, None)))
        main.add_widget(fixed_title)

        fixed_scroll = ScrollView(size_hint_y=0.3)
        fixed_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        fixed_layout.bind(minimum_height=fixed_layout.setter('height'))

        for task in self.db.data["tasks"]["fixed"]:
            box = BoxLayout(size_hint_y=None, height=40, spacing=10)
            cb = CheckBox(active=task["completed"])
            if not task["completed"]:
                cb.bind(active=lambda ch, val, t=task: self.on_task_complete(t, "fixed"))
            lbl = Label(
                text=task["title"],
                font_name=FONT_NAME,
                color=(1,1,1,0.8 if not task["completed"] else 0.3),
                halign='left',
                valign='middle',
                size_hint_x=0.8,
                size_hint_y=1
            )
            lbl.bind(size=lambda *x, l=lbl: setattr(l, 'text_size', (l.width, None)))
            box.add_widget(cb)
            box.add_widget(lbl)
            fixed_layout.add_widget(box)

        fixed_scroll.add_widget(fixed_layout)
        main.add_widget(fixed_scroll)

        # Custom tasks
        custom_title = Label(
            text="✨ My Custom Tasks",
            font_size=20,
            color=(0.8,0.9,1,1),
            font_name=FONT_NAME,
            halign='center',
            valign='middle',
            size_hint_y=0.05,
            size_hint_x=1
        )
        custom_title.bind(size=lambda *x: setattr(custom_title, 'text_size', (custom_title.width, None)))
        main.add_widget(custom_title)

        add_btn = Button(
            text="+ Add New Task",
            size_hint_y=0.06,
            background_normal='',
            background_color=(0.2,0.4,0.8,1),
            font_name=FONT_NAME
        )
        add_btn.bind(on_press=self.show_add_task_popup)
        main.add_widget(add_btn)

        custom_scroll = ScrollView(size_hint_y=0.2)
        self.custom_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.custom_layout.bind(minimum_height=self.custom_layout.setter('height'))
        self.update_custom_tasks()
        custom_scroll.add_widget(self.custom_layout)
        main.add_widget(custom_scroll)

        # Special task
        special_box = BoxLayout(size_hint_y=0.1, spacing=5)
        with special_box.canvas.before:
            Color(0.3, 0.1, 0.3, 0.7)
            self.special_rect = Rectangle(pos=special_box.pos, size=special_box.size)
        special_box.bind(pos=self._update_special_rect, size=self._update_special_rect)

        special_check = CheckBox(active=self.db.data["tasks"]["special"]["completed"])
        if not self.db.data["tasks"]["special"]["completed"]:
            special_check.bind(active=lambda ch, val: self.on_task_complete(None, "special"))
        special_title = Label(
            text=self.db.data["tasks"]["special"]["title"],
            color=(1,0.8,0,1),
            font_size=14,
            font_name=FONT_NAME,
            halign='left',
            valign='middle',
            size_hint_x=1
        )
        special_title.bind(size=lambda *x: setattr(special_title, 'text_size', (special_title.width, None)))
        special_box.add_widget(special_check)
        special_box.add_widget(special_title)
        main.add_widget(special_box)

        # Motivational sentence
        self.motivation_label = Label(
            text="🌟 Ready to start today?",
            size_hint_y=0.08,
            color=(0.8,1,0.8,1),
            font_size=14,
            font_name=FONT_NAME,
            halign='center',
            valign='middle',
            size_hint_x=1
        )
        self.motivation_label.bind(size=lambda *x: setattr(self.motivation_label, 'text_size', (self.motivation_label.width, None)))
        main.add_widget(self.motivation_label)

        # Navigation
        nav = BoxLayout(size_hint_y=0.1, spacing=10)
        report_btn = Button(
            text="📊 Report",
            background_normal='',
            background_color=(0.3,0.2,0.5,1),
            font_name=FONT_NAME
        )
        report_btn.bind(on_press=self.go_to_report)
        sky_btn = Button(
            text="🌌 Sky",
            background_normal='',
            background_color=(0.2,0.3,0.6,1),
            font_name=FONT_NAME
        )
        sky_btn.bind(on_press=self.go_to_sky)
        nav.add_widget(report_btn)
        nav.add_widget(sky_btn)
        main.add_widget(nav)

        self.add_widget(main)
        Clock.schedule_once(self.draw_initial_stars, 0.1)

    def _update_rect(self, inst, val):
        if hasattr(self, 'rect'):
            self.rect.pos = inst.pos
            self.rect.size = inst.size

    def _update_special_rect(self, inst, val):
        if hasattr(self, 'special_rect'):
            self.special_rect.pos = inst.pos
            self.special_rect.size = inst.size

    def draw_initial_stars(self, dt):
        self.draw_stars()

    def update_stars(self, dt):
        self.draw_stars()

    def draw_stars(self):
        try:
            self.canvas.after.clear()
            with self.canvas.after:
                stars_count = min(self.db.data["user"]["total_stars"] % 30 + 10, 50)
                for i in range(stars_count):
                    Color(1, 1, 0.8, random.uniform(0.3, 0.8))
                    x = random.randint(0, Window.width)
                    y = random.randint(0, Window.height)
                    s = random.randint(2, 4)
                    Ellipse(pos=(x, y), size=(s, s))
        except:
            pass

    def on_task_complete(self, task, task_type):
        if task_type == "fixed" and task:
            stars = self.db.complete_task("fixed", task_id=task["id"])
        elif task_type == "special":
            stars = self.db.complete_task("special")
        elif task_type == "custom" and task:
            stars = self.db.complete_task("custom", title=task["title"])
        else:
            return

        self.draw_stars()

        streak = self.db.data["user"]["streak"]
        if streak >= 3:
            msg = random.choice(["Great! A star added to your sky 🌟",
                                 "Awesome! Keep going 💪",
                                 "You're shining! ✨",
                                 "Closer to your goals... 🌙",
                                 "Your star lit up! ⭐"])
        elif streak == 0:
            msg = random.choice(["Don't worry, tomorrow is a new day ☁️",
                                 "Every day is a fresh start",
                                 "Slow and steady wins the race",
                                 "Maybe not today, but tomorrow for sure"])
        else:
            msg = f"🔥 {streak} days in a row! You're doing great"
        self.motivation_label.text = msg

        self.show_mood_popup()

    def show_mood_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(
            text="How are you feeling?",
            font_size=18,
            font_name=FONT_NAME,
            halign='center',
            size_hint_y=None,
            height=30
        ))
        moods = ["😊 Happy", "😴 Tired", "💪 Energetic", "🤔 Unmotivated", "😌 Calm"]
        grid = GridLayout(cols=2, spacing=10, size_hint_y=0.6)
        for m in moods:
            btn = Button(
                text=m,
                background_normal='',
                background_color=(0.3,0.3,0.6,1),
                font_name=FONT_NAME
            )
            btn.bind(on_press=lambda x, mood=m: self.save_mood_and_close(mood))
            grid.add_widget(btn)
        content.add_widget(grid)
        close_btn = Button(
            text="Later",
            size_hint_y=0.2,
            background_color=(0.5,0.1,0.1,1),
            font_name=FONT_NAME
        )
        close_btn.bind(on_press=self.close_mood_popup)
        content.add_widget(close_btn)

        self.mood_popup = Popup(
            title="🌟 Today's Mood",
            content=content,
            size_hint=(0.8,0.5),
            auto_dismiss=False,
            title_font=FONT_NAME
        )
        self.mood_popup.open()

    def save_mood_and_close(self, mood):
        self.db.save_mood(mood)
        self.mood_popup.dismiss()

    def close_mood_popup(self, inst):
        self.mood_popup.dismiss()

    def show_add_task_popup(self, inst):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(
            text="New task title:",
            font_name=FONT_NAME,
            halign='center',
            size_hint_y=None,
            height=30
        ))
        txt = TextInput(
            multiline=False,
            hint_text="e.g., Buy groceries",
            font_name=FONT_NAME
        )
        content.add_widget(txt)
        btns = BoxLayout(size_hint_y=0.3, spacing=10)
        add_btn = Button(
            text="Add",
            background_color=(0.2,0.7,0.2,1),
            font_name=FONT_NAME
        )
        cancel_btn = Button(
            text="Cancel",
            background_color=(0.7,0.2,0.2,1),
            font_name=FONT_NAME
        )
        btns.add_widget(add_btn)
        btns.add_widget(cancel_btn)
        content.add_widget(btns)

        popup = Popup(
            title="➕ New Task",
            content=content,
            size_hint=(0.8,0.4),
            title_font=FONT_NAME
        )
        add_btn.bind(on_press=lambda x: self.add_custom_task_and_close(txt.text, popup))
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def add_custom_task_and_close(self, title, popup):
        if title.strip():
            self.db.add_custom_task(title)
            self.update_custom_tasks()
            popup.dismiss()

    def update_custom_tasks(self):
        self.custom_layout.clear_widgets()
        for task in self.db.data["tasks"]["custom"]:
            box = BoxLayout(size_hint_y=None, height=40, spacing=10)
            cb = CheckBox(active=task["completed"])
            if not task["completed"]:
                cb.bind(active=lambda ch, val, t=task: self.on_task_complete(t, "custom"))
            lbl = Label(
                text=task["title"],
                font_name=FONT_NAME,
                color=(1,1,1,0.8 if not task["completed"] else 0.3),
                halign='left',
                valign='middle',
                size_hint_x=0.8,
                size_hint_y=1
            )
            lbl.bind(size=lambda *x, l=lbl: setattr(l, 'text_size', (l.width, None)))
            box.add_widget(cb)
            box.add_widget(lbl)
            self.custom_layout.add_widget(box)

    def go_to_report(self, inst):
        self.manager.current = 'report'

    def go_to_sky(self, inst):
        self.manager.current = 'sky'

# ----------------------------------------------------------------------
# Report Screen
# ----------------------------------------------------------------------
class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.build_ui()

    def build_ui(self):
        main = BoxLayout(orientation='vertical', padding=20, spacing=15)
        with main.canvas.before:
            Color(0.05, 0.05, 0.15, 1)
            self.rect = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=self._update_rect, size=self._update_rect)

        title = Label(
            text="📊 Performance Report",
            font_size=28,
            color=(1,0.9,0.2,1),
            font_name=FONT_NAME,
            halign='center',
            valign='middle',
            size_hint_y=0.1,
            size_hint_x=1
        )
        title.bind(size=lambda *x: setattr(title, 'text_size', (title.width, None)))
        main.add_widget(title)

        today = datetime.now().strftime("%Y-%m-%d")
        total_tasks = len(self.db.data["tasks"]["fixed"]) + len(self.db.data["tasks"]["custom"])
        if today in self.db.data["stats"]["daily"]:
            stats = self.db.data["stats"]["daily"][today]
            completed = stats.get("completed_tasks", 0)
            total = stats.get("total_tasks", total_tasks)
            stars_today = stats.get("stars_earned", 0)
        else:
            completed = 0
            total = total_tasks
            stars_today = 0
        percentage = completed / total if total > 0 else 0

        chart = PieChart(percentage, size_hint=(None,None), size=(200,200))
        chart.pos_hint = {'center_x': 0.5}
        main.add_widget(chart)

        stats_grid = GridLayout(cols=2, spacing=10, size_hint_y=0.3)
        # Today's stars
        lbl1 = Label(text="⭐ Today's stars:", font_name=FONT_NAME, halign='left', valign='middle', size_hint_x=1)
        lbl1.bind(size=lambda *x: setattr(lbl1, 'text_size', (lbl1.width, None)))
        lbl2 = Label(text=str(stars_today), font_name=FONT_NAME, halign='right', valign='middle', size_hint_x=1)
        lbl2.bind(size=lambda *x: setattr(lbl2, 'text_size', (lbl2.width, None)))
        stats_grid.add_widget(lbl1)
        stats_grid.add_widget(lbl2)

        # Streak
        lbl3 = Label(text="🔥 Streak:", font_name=FONT_NAME, halign='left', valign='middle', size_hint_x=1)
        lbl3.bind(size=lambda *x: setattr(lbl3, 'text_size', (lbl3.width, None)))
        lbl4 = Label(text=str(self.db.data["user"]["streak"]), font_name=FONT_NAME, halign='right', valign='middle', size_hint_x=1)
        lbl4.bind(size=lambda *x: setattr(lbl4, 'text_size', (lbl4.width, None)))
        stats_grid.add_widget(lbl3)
        stats_grid.add_widget(lbl4)

        # This month's stars
        month = datetime.now().strftime("%Y-%m")
        month_stars = self.db.data["stats"]["monthly_stars"].get(month, 0)
        lbl5 = Label(text="🌙 This month's stars:", font_name=FONT_NAME, halign='left', valign='middle', size_hint_x=1)
        lbl5.bind(size=lambda *x: setattr(lbl5, 'text_size', (lbl5.width, None)))
        lbl6 = Label(text=str(month_stars), font_name=FONT_NAME, halign='right', valign='middle', size_hint_x=1)
        lbl6.bind(size=lambda *x: setattr(lbl6, 'text_size', (lbl6.width, None)))
        stats_grid.add_widget(lbl5)
        stats_grid.add_widget(lbl6)

        main.add_widget(stats_grid)

        end_day_btn = Button(
            text="End Day",
            size_hint_y=0.1,
            background_color=(0.8,0.2,0.2,1),
            font_name=FONT_NAME
        )
        end_day_btn.bind(on_press=self.end_day)
        main.add_widget(end_day_btn)

        back_btn = Button(
            text="🔙 Back to Home",
            size_hint_y=0.1,
            background_color=(0.3,0.2,0.5,1),
            font_name=FONT_NAME
        )
        back_btn.bind(on_press=self.go_back)
        main.add_widget(back_btn)

        self.add_widget(main)

    def _update_rect(self, inst, val):
        if hasattr(self, 'rect'):
            self.rect.pos = inst.pos
            self.rect.size = inst.size

    def end_day(self, inst):
        self.db.end_day()
        self.manager.current = 'home'

    def go_back(self, inst):
        self.manager.current = 'home'

# ----------------------------------------------------------------------
# Sky Screen
# ----------------------------------------------------------------------
class SkyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.stars_label = None
        self.build_ui()

    def build_ui(self):
        main = BoxLayout(orientation='vertical', padding=20, spacing=15)
        with main.canvas.before:
            Color(0.05, 0.05, 0.15, 1)
            self.rect = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=self._update_rect, size=self._update_rect)

        title = Label(
            text="🌌 My Sky",
            font_size=28,
            color=(1, 0.9, 0.2, 1),
            font_name=FONT_NAME,
            halign='center',
            valign='middle',
            size_hint_y=0.1,
            size_hint_x=1
        )
        title.bind(size=lambda *x: setattr(title, 'text_size', (title.width, None)))
        main.add_widget(title)

        month = datetime.now().strftime("%Y-%m")
        month_stars = self.db.data["stats"]["monthly_stars"].get(month, 0)
        self.stars_label = Label(
            text=f"You have {month_stars} stars this month ⭐",
            font_size=20,
            color=(0.8, 0.9, 1, 1),
            font_name=FONT_NAME,
            halign='center',
            valign='middle',
            size_hint_y=0.2,
            size_hint_x=1
        )
        self.stars_label.bind(size=lambda *x: setattr(self.stars_label, 'text_size', (self.stars_label.width, None)))
        main.add_widget(self.stars_label)

        new_month_btn = Button(
            text="Start New Month",
            size_hint_y=0.1,
            background_color=(0.2, 0.6, 0.2, 1),
            font_name=FONT_NAME
        )
        new_month_btn.bind(on_press=self.start_new_month)
        main.add_widget(new_month_btn)

        back_btn = Button(
            text="🔙 Back to Home",
            size_hint_y=0.1,
            background_color=(0.2, 0.3, 0.6, 1),
            font_name=FONT_NAME
        )
        back_btn.bind(on_press=self.go_back)
        main.add_widget(back_btn)

        self.add_widget(main)
        self.draw_stars(month_stars)

    def _update_rect(self, inst, val):
        if hasattr(self, 'rect'):
            self.rect.pos = inst.pos
            self.rect.size = inst.size

    def draw_stars(self, count):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.05, 0.05, 0.15, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            for i in range(min(count, 100)):
                Color(1, 1, 0.8, random.uniform(0.5, 1))
                x = random.randint(50, Window.width - 50)
                y = random.randint(50, Window.height - 50)
                s = random.randint(3, 6)
                Ellipse(pos=(x, y), size=(s, s))
            if count >= 20:
                Color(1, 0.8, 0.2, 0.3)
                for _ in range(5):
                    x1 = random.randint(50, Window.width - 50)
                    y1 = random.randint(50, Window.height - 50)
                    x2 = random.randint(50, Window.width - 50)
                    y2 = random.randint(50, Window.height - 50)
                    Line(points=[x1, y1, x2, y2], width=1)

    def on_pre_enter(self, *args):
        month = datetime.now().strftime("%Y-%m")
        month_stars = self.db.data["stats"]["monthly_stars"].get(month, 0)
        self.stars_label.text = f"You have {month_stars} stars this month ⭐"
        self.stars_label.text_size = (self.stars_label.width, None)
        self.draw_stars(month_stars)
        return super().on_pre_enter(*args)

    def start_new_month(self, inst):
        self.db.save_data()
        self.manager.current = 'home'

    def go_back(self, inst):
        self.manager.current = 'home'

# ----------------------------------------------------------------------
# Main App
# ----------------------------------------------------------------------
class StarTaskApp(App):
    def build(self):
        self.title = 'Star Task ✨'
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ReportScreen(name='report'))
        sm.add_widget(SkyScreen(name='sky'))
        return sm

if __name__ == '__main__':
    StarTaskApp().run()