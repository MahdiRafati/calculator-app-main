from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
import time
import json
import os
import math


# اگر فونت در کنار فایل برنامه باشد، از آن استفاده می‌شود؛ در غیر این صورت Roboto.
FONT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "DSEG7Classic-Regular.ttf"
)
if os.path.isfile(FONT_PATH):
    LabelBase.register(name="DSEG7", fn_regular=FONT_PATH)
    DISPLAY_FONT = "DSEG7"
else:
    DISPLAY_FONT = "Roboto"


class BatteryGraphic(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = 100.0
        self.installed = True
        self.bind(pos=self.draw_battery, size=self.draw_battery)

    def set_battery(self, level, installed):
        self.level = max(0.0, min(100.0, float(level)))
        self.installed = bool(installed)
        self.draw_battery()

    def draw_battery(self, *args):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size

        if w <= 1 or h <= 1:
            return

        bx = x + w * 0.12
        by = y + h * 0.32
        bw = w * 0.72
        bh = h * 0.36

        with self.canvas:
            # محفظه باتری
            Color(0.16, 0.17, 0.19, 1)
            RoundedRectangle(
                pos=(bx - 4, by - 4),
                size=(bw + 8, bh + 8),
                radius=[bh / 2]
            )

            if self.installed:
                # بدنه نقره‌ای باتری
                Color(0.72, 0.75, 0.78, 1)
                RoundedRectangle(
                    pos=(bx, by),
                    size=(bw, bh),
                    radius=[bh / 2]
                )

                # رنگ نشان‌دهنده شارژ
                if self.level > 30:
                    Color(0.15, 0.75, 0.28, 1)
                elif self.level > 10:
                    Color(0.95, 0.67, 0.12, 1)
                else:
                    Color(0.9, 0.15, 0.12, 1)

                fill_width = bw * 0.84 * (self.level / 100.0)
                if fill_width > 0:
                    RoundedRectangle(
                        pos=(bx + bw * 0.08, by + bh * 0.22),
                        size=(fill_width, bh * 0.56),
                        radius=[bh * 0.2]
                    )

                # سر مثبت باتری
                Color(0.48, 0.50, 0.53, 1)
                RoundedRectangle(
                    pos=(bx + bw, by + bh * 0.3),
                    size=(w * 0.07, bh * 0.4),
                    radius=[bh * 0.15]
                )
            else:
                # محفظه خالی
                Color(0.30, 0.32, 0.35, 1)
                RoundedRectangle(
                    pos=(bx + 5, by + 5),
                    size=(max(0, bw - 10), max(0, bh - 10)),
                    radius=[bh / 3]
                )


class CoinGraphic(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw_coin, size=self.draw_coin)

    def draw_coin(self, *args):
        self.canvas.clear()
        if self.width <= 1 or self.height <= 1:
            return

        with self.canvas:
            Color(0.85, 0.55, 0.08, 1)
            Ellipse(pos=self.pos, size=self.size)

            Color(1, 0.82, 0.25, 1)
            Ellipse(
                pos=(self.x + 4, self.y + 4),
                size=(max(0, self.width - 8), max(0, self.height - 8))
            )


class RaisedButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 0)

        with self.canvas.before:
            Color(0.08, 0.09, 0.11, 1)
            self.shadow = RoundedRectangle(radius=[10])

            if self.text in ["+", "-", "×", "÷"]:
                Color(0.05, 0.75, 0.12, 1)
            elif self.text == "=":
                Color(0.05, 0.40, 0.95, 1)
            elif self.text == "C":
                Color(0.85, 0.08, 0.08, 1)
            else:
                Color(0.38, 0.41, 0.45, 1)

            self.face = RoundedRectangle(radius=[10])
            Color(0.72, 0.75, 0.78, 1)
            self.highlight = Line(width=1.2)

        self.bind(
            pos=self.update_shape,
            size=self.update_shape,
            state=self.update_shape
        )
        self.update_shape()

    def update_shape(self, *args):
        self.shadow.pos = (self.x, self.y - 7)
        self.shadow.size = self.size

        if self.state == "down":
            self.face.pos = (self.x, self.y - 5)
        else:
            self.face.pos = self.pos

        self.face.size = self.size
        self.highlight.points = [
            self.x + 10, self.top - 5,
            self.right - 10, self.top - 5
        ]


class calcApp(App):
    def build(self):
        root = FloatLayout()

        self.flip_button = Button(
            text="ROTATE",
            font_size=18,
            size_hint=(0.12, 0.07),
            pos_hint={"right": 0.95, "top": 0.98}
        )
        self.is_back = False
        self.flip_button.bind(on_press=self.flip_view)

        # نمای جلوی ماشین‌حساب
        body = BoxLayout(orientation="vertical")
        self.body = body
        body.size_hint = (0.94, 0.85)
        body.pos_hint = {"center_x": 0.5, "center_y": 0.43}
        body.padding = 20
        body.spacing = 10

        with body.canvas.before:
            Color(0.18, 0.20, 0.23, 1)
            self.body_shape = RoundedRectangle(
                pos=body.pos,
                size=body.size,
                radius=[20]
            )
        with body.canvas.after:
            Color(0.65, 0.68, 0.72, 1)
            self.body_border = Line(
                rounded_rectangle=(0, 0, 100, 100, 20),
                width=2
            )
        body.bind(pos=self.update_body, size=self.update_body)

        # صفحه‌نمایش
        self.display_area = BoxLayout(orientation="horizontal")
        self.display_area.spacing = 0
        self.display_area.size_hint_y = 0.20

        self.display = Label(
            text="0",
            color=(0.2, 1, 0.3, 1),
            font_name=DISPLAY_FONT,
            font_size=42,
            size_hint_x=1,
            halign="center",
            valign="middle"
        )

        self.operator_display = Label(
            text="",
            color=(1, 1, 1, 1),
            font_size=48,
            size_hint_x=0
        )

        self.second_display = Label(
            text="",
            color=(0.2, 1, 0.3, 1),
            font_name=DISPLAY_FONT,
            font_size=42,
            size_hint_x=0
        )

        self.display.bind(text=self.fit_display, width=self.fit_display)
        self.second_display.bind(text=self.fit_display, width=self.fit_display)

        self.display_area.add_widget(self.display)
        self.display_area.add_widget(self.operator_display)
        self.display_area.add_widget(self.second_display)

        with self.display_area.canvas.before:
            # قاب مشکی بیرونی
            Color(0.02, 0.02, 0.02, 1)
            self.display_frame = RoundedRectangle(
                pos=self.display_area.pos,
                size=self.display_area.size,
                radius=[12]
            )

            # صفحه سبز تیره داخل قاب
            Color(0.02, 0.04, 0.03, 1)
            self.display_rect = RoundedRectangle(
                pos=(self.display_area.x + 9, self.display_area.y + 9),
                size=(
                    self.display_area.width - 18,
                    self.display_area.height - 18
                ),
                radius=[8]
            )
        self.display_area.bind(
            pos=self.update_display,
            size=self.update_display
        )

        self.first_number = None
        self.operator = None
        body.add_widget(self.display_area)

        layout = GridLayout(rows=5, cols=4)
        layout.padding = 4
        layout.spacing = 7

        buttons = [
            "7", "8", "9", "÷",
            "4", "5", "6", "×",
            "1", "2", "3", "-",
            "C", "0", "DEL", "+",
            ".", "x²", "√", "="
        ]

        for key in buttons:
            button = RaisedButton(text=key, font_size=42)
            button.bind(on_press=self.button_click)
            layout.add_widget(button)

        body.add_widget(layout)

        # اطلاعات باتری و سکه
        self.battery_level = 100.0
        self.battery_installed = True
        self.powered = True
        self.solar_enabled = False
        self.solar_coin_progress = 0.0

        self.battery_file = os.path.join(self.user_data_dir, "battery.json")
        self.coins_file = os.path.join(self.user_data_dir, "coins.json")
        self.daily_file = os.path.join(self.user_data_dir, "daily.json")
        self.history_file = os.path.join(self.user_data_dir, "history.json")
        self.upgrades_file = os.path.join(self.user_data_dir, "upgrades.json")
        self.coins = 0
        self.history = []
        self.owned_upgrades = set()
        self.load_coins()
        self.load_history()
        self.load_upgrades()

        # نمای پشت ماشین‌حساب؛ تا زمان چرخش به root اضافه نمی‌شود.
        self.back_view = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=20
        )
        self.back_view.size_hint = (0.94, 0.85)
        self.back_view.pos_hint = {"center_x": 0.5, "center_y": 0.43}

        with self.back_view.canvas.before:
            Color(0.18, 0.20, 0.23, 1)
            self.back_shape = RoundedRectangle(
                pos=self.back_view.pos,
                size=self.back_view.size,
                radius=[20]
            )
        self.back_view.bind(pos=self.update_back, size=self.update_back)

        self.battery_visual = BatteryGraphic(size_hint=(1, 0.34))
        self.back_view.add_widget(self.battery_visual)

        self.battery_status = Label(
            text="AA Battery | Charge: 100%",
            font_size=20
        )
        self.back_view.add_widget(self.battery_status)

        self.coins_row = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=55,
            spacing=10
        )
        self.coins_label = Label(
            text=f"Coins: {self.coins}",
            font_size=22
        )
        self.coins_row.add_widget(self.coins_label)

        self.coin_visual = CoinGraphic(size_hint=(None, 1), width=45)
        self.coins_row.add_widget(self.coin_visual)
        self.back_view.add_widget(self.coins_row)

        self.battery_action = Button(
            text="Remove Battery",
            size_hint=(1, None),
            height=48
        )
        self.battery_action.bind(on_press=self.toggle_battery)
        self.back_view.add_widget(self.battery_action)

        self.solar_button = Button(
            text="Solar Charging",
            size_hint=(1, None),
            height=48
        )
        self.solar_button.bind(on_press=self.solar_charge)
        self.back_view.add_widget(self.solar_button)

        self.shop_button = Button(
            text="SHOP",
            size_hint=(1, None),
            height=48
        )
        self.shop_button.bind(on_press=self.open_shop)
        self.back_view.add_widget(self
        .shop_button)

        self.history_button = Button(
            text="HISTORY",
            size_hint=(1, None),
            height=48
        )
        self.history_button.bind(on_press=self.open_history)
        self.back_view.add_widget(self.history_button)

        # نمای پشت در شروع مخفی است و روی دکمه‌های جلو قرار نمی‌گیرد.
        self.back_view.opacity = 0
        self.back_view.disabled = True

        self.load_battery()

        self.solar_button.text = (
            "Solar: ON" if self.solar_enabled else "Solar: OFF"
        )
        self.update_battery_panel()

        # جایزه روزانه بعد از ساخته‌شدن برچسب سکه بررسی می‌شود.
        self.daily_reward()

        # مصرف یا شارژ باتری هر ۱۰ ثانیه
        Clock.schedule_interval(self.battery_time_tick, 10)

        root.add_widget(self.body)
        root.add_widget(self.flip_button)
        self.root_layout = root
        return root

    def update_body(self, instance, value):
        self.body_shape.pos = instance.pos
        self.body_shape.size = instance.size
        self.body_border.rounded_rectangle = (
            instance.x, instance.y,
            instance.width, instance.height, 20
        )

    def update_back(self, instance, value):
        self.back_shape.pos = instance.pos
        self.back_shape.size = instance.size

    def update_display(self, instance, value):
        self.display_frame.pos = instance.pos
        self.display_frame.size = instance.size

        self.display_rect.pos = (
            instance.x + 9,
            instance.y + 9
        )
        self.display_rect.size = (
            instance.width - 18,
            instance.height - 18
        )

    def fit_display(self, instance, value):
        base_size = 42
        length = max(1, len(instance.text))
        available_width = max(1, instance.width - 12)
        instance.font_size = min(
            base_size,
            max(14, available_width / (length * 0.65))
        )

    def restore_display_layout(self):
        self.display.size_hint_x = 1
        self.operator_display.size_hint_x = 0
        self.second_display.size_hint_x = 0

    def update_battery_panel(self):
        self.battery_level = max(0.0, min(100.0, float(self.battery_level)))
        self.powered = self.battery_installed and self.battery_level > 0

        self.battery_visual.set_battery(
            self.battery_level,
            self.battery_installed
        )

        if not self.battery_installed:
            self.battery_status.text = "NO BATTERY INSTALLED"
            self.battery_action.text = "Install New Battery"
        elif self.battery_level <= 0:
            self.battery_status.text = "LOW BATTERY | 0%"
            self.battery_action.text = "Remove Empty Battery"
        else:
            self.battery_status.text = (
                f"AA Battery | Charge: {self.battery_level:.1f}%"
            )
            self.battery_action.text = "Remove Battery"

        self.body.opacity = 1 if self.powered else 0.25

        if self.battery_level > 0:
            self.battery_popup_shown = False

        if self.battery_installed and self.battery_level <= 0:
            if not getattr(self, "battery_popup_shown", False):
                self.battery_popup_shown = True
                Clock.schedule_once(
                    lambda dt: self.show_battery_popup(),
                    0.5
                )
    def show_battery_popup(self):
        if hasattr(self, "battery_popup") and self.battery_popup:
            return

        panel = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=15
        )

        message = Label(
            text=(
                "Your battery is empty.\n"
                "Please purchase a new AA battery "
                "from the Store to continue."
            ),
            halign="center",
            valign="middle",
            font_size=17
        )
        message.bind(
            size=lambda widget, value: setattr(
                widget, "text_size", value
            )
        )
        panel.add_widget(message)

        store_button = Button(
            text="OPEN STORE",
            size_hint_y=None,
            height=48
        )

        later_button = Button(
            text="LATER",
            size_hint_y=None,
            height=44
        )

        panel.add_widget(store_button)
        panel.add_widget(later_button)

        popup = Popup(
            title="LOW BATTERY",
            content=panel,
            size_hint=(0.88, 0.42),
            auto_dismiss=False
        )

        self.battery_popup = popup

        def open_store(button):
            popup.dismiss()
            self.battery_popup = None

            if not self.is_back:
                self.flip_view(None)

            self.open_shop(None)

        def close_popup(button):
            popup.dismiss()
            self.battery_popup = None

        store_button.bind(on_press=open_store)
        later_button.bind(on_press=close_popup)

        popup.open()

    def toggle_battery(self, instance):
        if self.battery_installed:
            self.battery_installed = False
        else:
            self.battery_installed = True
            self.battery_popup_shown = False
            self.display.text = "0"
            self.operator_display.text = ""
            self.second_display.text = ""
            self.first_number = None
            self.operator = None
            self.restore_display_layout()

        self.update_battery_panel()
        self.save_battery()

    def spend_battery(self, amount):
        if not self.powered:
            return

        drain_multiplier = 0.75 if "battery_saver" in self.owned_upgrades else 1.0
        actual_amount = amount * drain_multiplier
        self.battery_level = max(0.0, self.battery_level - actual_amount)
        self.update_battery_panel()

    def process_solar_gain(self, gained_amount):
        """هر ۱۰ درصد شارژ واقعی خورشیدی، ۵ سکه جایزه می‌دهد."""
        if gained_amount <= 0:
            return

        self.solar_coin_progress += gained_amount
        while self.solar_coin_progress >= 10.0:
            self.solar_coin_progress -= 10.0
            self.add_coins(5)

    def battery_time_tick(self, dt):
        if self.battery_installed:
            if self.solar_enabled:
                old_level = self.battery_level
                solar_multiplier = 2.0 if "solar_boost" in self.owned_upgrades else 1.0
                self.battery_level = min(
                    100.0,
                    self.battery_level + (0.25 / 6.0) * solar_multiplier
                )
                gained = self.battery_level - old_level
                self.process_solar_gain(gained)
                self.update_battery_panel()
            elif self.powered:
                self.spend_battery(0.05)

        self.save_battery()

    def solar_charge(self, instance):
        self.solar_enabled = not self.solar_enabled
        self.solar_button.text = (
            "Solar: ON" if self.solar_enabled else "Solar: OFF"
        )
        self.save_battery()

    def save_battery(self):
        data = {
            "level": self.battery_level,
            "installed": self.battery_installed,
            "solar": self.solar_enabled,
            "solar_coin_progress": self.solar_coin_progress,
            "saved_at": time.time()
        }
        try:
            with open(self.battery_file, "w", encoding="utf-8") as file:
                json.dump(data, file)
        except OSError as error:
            print("Battery save error:", error)

    def load_battery(self):
        if not os.path.exists(self.battery_file):
            return

        try:
            with open(self.battery_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.battery_level = float(data.get("level", 100.0))
            self.battery_level = max(0.0, min(100.0, self.battery_level))
            self.battery_installed = bool(data.get("installed", True))
            self.solar_enabled = bool(data.get("solar", False))
            self.solar_coin_progress = float(
                data.get("solar_coin_progress", 0.0)
            )
            self.solar_coin_progress = max(0.0, self.solar_coin_progress)

            saved_at = float(data.get("saved_at", time.time()))
            elapsed = max(0.0, time.time() - saved_at)

            if self.battery_installed:
                if self.solar_enabled:
                    old_level = self.battery_level
                    solar_multiplier = 2.0 if "solar_boost" in self.owned_upgrades else 1.0
                    self.battery_level = min(
                        100.0,
                        self.battery_level + elapsed * (0.25 / 60.0) * solar_multiplier
                    )
                    gained = self.battery_level - old_level
                    self.process_solar_gain(gained)
                else:
                    self.battery_level = max(
                        0.0,
                        self.battery_level - elapsed * 0.005
                    )

        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            print("Battery load error:", error)

    def save_coins(self):
        try:
            with open(self.coins_file, "w", encoding="utf-8") as file:
                json.dump({"coins": self.coins}, file)
        except OSError as error:
            print("Coins save error:", error)

    def load_coins(self):
        if not os.path.exists(self.coins_file):
            return

        try:
            with open(self.coins_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.coins = max(0, int(data.get("coins", 0)))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.coins = 0

    def load_history(self):
        if not os.path.exists(self.history_file):
            self.history = []
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.history = data if isinstance(data, list) else []
            self.history = [
                item for item in self.history
                if isinstance(item, dict)
                and "expression" in item
                and "result" in item
            ][:100]
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.history = []

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as file:
                json.dump(self.history[:100], file, ensure_ascii=False)
        except OSError as error:
            print("History save error:", error)

    def add_history_entry(self, expression, result):
        entry = {
            "expression": str(expression),
            "result": str(result),
            "time": time.strftime("%Y-%m-%d %H:%M")
        }
        self.history.insert(0, entry)
        self.history = self.history[:100]
        self.save_history()

    def open_history(self, instance):
        panel = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=12
        )

        scroll = ScrollView(do_scroll_x=False)
        rows = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=6
        )
        rows.bind(minimum_height=rows.setter("height"))

        if not self.history:
            rows.add_widget(Label(
                text="No calculations yet.",
                size_hint_y=None,
                height=55
            ))
        else:
            for item in self.history:
                text = (
                    f"{item.get('time', '')}\n"
                    f"{item.get('expression', '')} = {item.get('result', '')}"
                )
                line = Label(
                    text=text,
                    size_hint_y=None,
                    height=64,
                    halign="left",
                    valign="middle"
                )
                line.bind(size=lambda widget, size: setattr(widget, "text_size", size))
                rows.add_widget(line)

        scroll.add_widget(rows)
        panel.add_widget(scroll)

        actions = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=48,
            spacing=8
        )
        clear_button = Button(text="Clear history")
        close_button = Button(text="Close")
        actions.add_widget(clear_button)
        actions.add_widget(close_button)
        panel.add_widget(actions)

        popup = Popup(
            title="CALCULATION HISTORY",
            content=panel,
            size_hint=(0.92, 0.82)
        )
        self.history_popup = popup
        clear_button.bind(on_press=self.confirm_clear_history)
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def confirm_clear_history(self, instance):
        panel = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=12
        )
        panel.add_widget(Label(text="Delete all saved calculations?"))
        actions = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=48,
            spacing=8
        )
        yes_button = Button(text="Delete")
        no_button = Button(text="Cancel")
        actions.add_widget(yes_button)
        actions.add_widget(no_button)
        panel.add_widget(actions)

        confirm = Popup(
            title="CONFIRM",
            content=panel,
            size_hint=(0.82, 0.32)
        )
        no_button.bind(on_press=confirm.dismiss)

        def delete_all(button):
            self.history = []
            self.save_history()
            confirm.dismiss()
            if hasattr(self, "history_popup"):
                self.history_popup.dismiss()
            self.open_history(None)

        yes_button.bind(on_press=delete_all)
        confirm.open()

    def load_upgrades(self):
        if not os.path.exists(self.upgrades_file):
            self.owned_upgrades = set()
            return

        try:
            with open(self.upgrades_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            allowed = {"solar_boost", "battery_saver"}
            saved = data.get("owned", []) if isinstance(data, dict) else []
            self.owned_upgrades = set(saved) & allowed
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.owned_upgrades = set()

    def save_upgrades(self):
        try:
            with open(self.upgrades_file, "w", encoding="utf-8") as file:
                json.dump({"owned": sorted(self.owned_upgrades)}, file)
        except OSError as error:
            print("Upgrade save error:", error)

    def daily_reward(self):
        today = time.strftime("%Y-%m-%d")
        last_reward = ""

        if os.path.exists(self.daily_file):
            try:
                with open(self.daily_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                last_reward = data.get("last_reward", "")
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                pass

        if last_reward != today:
            self.add_coins(50)
            try:
                with open(self.daily_file, "w", encoding="utf-8") as file:
                    json.dump({"last_reward": today}, file)
            except OSError as error:
                print("Daily reward save error:", error)
            Clock.schedule_once(lambda dt: self.show_daily_popup(), 0.5)

    def show_daily_popup(self):
        content = BoxLayout(
            orientation="vertical",
            spacing=15,
            padding=15
        )
        content.add_widget(Label(text="+50 Coins!", font_size=28))

        ok_button = Button(text="OK", size_hint=(1, 0.4))
        content.add_widget(ok_button)

        popup = Popup(
            title="Daily Reward!",
            content=content,
            size_hint=(0.7, 0.35),
            auto_dismiss=False
        )
        ok_button.bind(on_press=popup.dismiss)
        popup.open()

    def open_shop(self, instance):
        self.shop_products = {
            "Batteries": [
                {
                    "id": "aa_battery",
                    "name": "AA Battery",
                    "price": 50,
                    "description": "Restores the battery to 100%. Repeatable purchase.",
                    "kind": "consumable"
                }
            ],
            "Energy": [
                {
                    "id": "solar_boost",
                    "name": "Solar Boost",
                    "price": 120,
                    "description": "Permanently doubles the solar charging speed.",
                    "kind": "upgrade"
                }
            ],
            "Upgrades": [
                {
                    "id": "battery_saver",
                    "name": "Battery Saver",
                    "price": 150,
                    "description": "Permanently reduces battery drain by 25%.",
                    "kind": "upgrade"
                }
            ]
        }

        panel = BoxLayout(
            orientation="vertical",
            spacing=9,
            padding=12
        )
        self.shop_balance_label = Label(
            text=f"COINS: {self.coins}",
            font_size=23,
            size_hint_y=None,
            height=42
        )
        panel.add_widget(self.shop_balance_label)

        self.shop_message = Label(
            text="Choose a category, then open a product.",
            size_hint_y=None,
            height=30
        )
        panel.add_widget(self.shop_message)

        categories = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=45,
            spacing=6
        )
        for category in ["Batteries", "Energy", "Upgrades"]:
            category_button = Button(text=category, font_size=15)
            category_button.bind(
                on_press=lambda button, selected=category: self.show_shop_category(selected)
            )
            categories.add_widget(category_button)
        panel.add_widget(categories)

        scroll = ScrollView(do_scroll_x=False)
        self.shop_grid = GridLayout(
            cols=2,
            spacing=9,
            padding=4,
            size_hint_y=None
        )
        self.shop_grid.bind(minimum_height=self.shop_grid.setter("height"))
        scroll.add_widget(self.shop_grid)
        panel.add_widget(scroll)

        close_button = Button(
            text="Close",
            size_hint_y=None,
            
            height=46
        )
        panel.add_widget(close_button)

        popup = Popup(
            title="CALCULATOR STORE",
            content=panel,
            size_hint=(1.00, 1.01)
        )
        self.shop_popup = popup
        close_button.bind(on_press=popup.dismiss)
        self.show_shop_category("Batteries")
        popup.open()

    def show_shop_category(self, category):
        if not hasattr(self, "shop_grid"):
            return
        self.shop_grid.clear_widgets()
        products = self.shop_products.get(category, [])
        self.shop_grid.cols = 1 if len(products) <= 1 else 2

        for product in products:
            card = BoxLayout(
                orientation="vertical",
                spacing=5,
                padding=8,
                size_hint_y=None,
                height=165
            )
            with card.canvas.before:
                Color(0.22, 0.25, 0.29, 1)
                card_background = RoundedRectangle(
                    pos=card.pos,
                    size=card.size,
                    radius=[10]
                )
            card.bind(
                pos=lambda widget, value, shape=card_background: setattr(shape, "pos", value),
                size=lambda widget, value, shape=card_background: setattr(shape, "size", value)
            )

            title = Label(
                text=product["name"],
                font_size=18,
                bold=True,
                size_hint_y=None,
                height=34
            )
            description = Label(
                text=product["description"],
                font_size=12,
                halign="center",
                valign="middle"
            )
            description.bind(
                size=lambda widget, value: setattr(widget, "text_size", value)
            )
            owned = product["id"] in self.owned_upgrades
            if owned:
                price_text = "OWNED"
            else:
                price_text = f"{product['price']} COINS"
            details_button = Button(
                text=f"{price_text}  |  DETAILS",
                size_hint_y=None,
                height=40,
                font_size=13
            )
            details_button.bind(
                on_press=lambda button, product_id=product["id"]: self.show_product_details(product_id)
            )

            card.add_widget(title)
            card.add_widget(description)
            card.add_widget(details_button)
            self.shop_grid.add_widget(card)

        self.shop_message.text = f"{category} — select a product for details."

    def show_product_details(self, product_id):
        product = None
        for items in self.shop_products.values():
            for item in items:
                if item["id"] == product_id:
                    product = item
                    break
            if product is not None:
                break
        if product is None:
            return

        panel = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=15
        )
        panel.add_widget(Label(
            text=product["name"],
            font_size=23,
            size_hint_y=None,
            height=44
        ))
        description = Label(
            text=product["description"],
            halign="center",
            valign="middle"
        )
        description.bind(size=lambda widget, value: setattr(widget, "text_size", value))
        panel.add_widget(description)
        panel.add_widget(Label(
            text=f"Price: {product['price']} coins",
            font_size=18,
            size_hint_y=None,
            height=38
        ))

        self.shop_detail_message = Label(text="", size_hint_y=None, height=32)
        panel.add_widget(self.shop_detail_message)

        owned = product["id"] in self.owned_upgrades
        buy_button = Button(
            text="Already owned" if owned else f"BUY — {product['price']} COINS",
            size_hint_y=None,
            height=48,
            disabled=owned
        )
        close_button = Button(
            text="Close",
            size_hint_y=None,
            height=44
        )
        panel.add_widget(buy_button)
        panel.add_widget(close_button)

        detail_popup = Popup(
            title="PRODUCT DETAILS",
            content=panel,
            size_hint=(0.88, 0.58)
        )
        self.shop_detail_popup = detail_popup
        self.shop_detail_buy_button = buy_button
        buy_button.bind(
            on_press=lambda button, selected=product_id: self.buy_product(selected)
        )
        close_button.bind(on_press=detail_popup.dismiss)
        detail_popup.open()

    def buy_product(self, product_id):
        product = None
        for items in self.shop_products.values():
            for item in items:
                if item["id"] == product_id:
                    product = item
                    break
            if product is not None:
                break
        if product is None:
            return

        if product["kind"] == "upgrade" and product_id in self.owned_upgrades:
            self.shop_message.text = "You already own this upgrade."
            self.shop_detail_message.text = "Already owned."
            return

        if self.coins < product["price"]:
            self.shop_message.text = "Not enough coins. Keep calculating or collect your daily reward."
            self.shop_detail_message.text = "Not enough coins."
            return

        self.coins -= product["price"]
        self.coins_label.text = f"Coins: {self.coins}"
        self.shop_balance_label.text = f"COINS: {self.coins}"

        if product_id == "aa_battery":
            self.battery_level = 100.0
            self.battery_installed = True
            self.update_battery_panel()
            self.save_battery()
            self.shop_detail_message.text = "Battery restored to 100%."
        else:
            self.owned_upgrades.add(product_id)
            self.save_upgrades()
            self.shop_detail_message.text = "Upgrade activated permanently!"
            self.shop_detail_buy_button.text = "Already owned"
            self.shop_detail_buy_button.disabled = True

        self.save_coins()
        self.show_shop_category(next(
            category for category, items in self.shop_products.items()
            if product in items
        ))
        self.shop_message.text = f"Purchased: {product['name']}"

    def buy_battery(self):
        # سازگاری با نسخه قبلی فروشگاه
        self.buy_product("aa_battery")

    def add_coins(self, amount):
        self.coins += int(amount)
        self.coins_label.text = f"Coins: {self.coins}"
        if hasattr(self, "shop_balance_label"):
            self.shop_balance_label.text = f"COINS: {self.coins}"
        self.save_coins()

    def on_stop(self):
        self.save_battery()
        self.save_coins()

    def show_error(self):
        self.display.text = "EROR"
        self.operator_display.text = ""
        self.second_display.text = ""
        self.first_number = None
        self.operator = None
        self.restore_display_layout()

    @staticmethod
    def format_result(value):
        if not math.isfinite(value):
            return "EROR"
        if value.is_integer():
            return str(int(value))
        return str(value)

    def button_click(self, instance):
        if not self.powered:
            return

        key = instance.text

        if key.isdigit():
            if self.operator is None:
                if self.display.text in ["0", "EROR"]:
                    self.display.text = key
                else:
                    self.display.text += key
            else:
                if self.second_display.text in ["", "0"]:
                    self.second_display.text = key
                else:
                    self.second_display.text += key

        elif key == ".":
            target = (
                self.display if self.operator is None
                else self.second_display
            )
            if target.text in ["", "EROR"]:
                target.text = "0."
            elif "." not in target.text:
                target.text += "."

        elif key in ["+", "-", "×", "÷"]:
            if self.operator is None:
                try:
                    self.first_number = float(self.display.text)
                except ValueError:
                    return
                if not math.isfinite(self.first_number):
                    return
                self.operator = key
                self.operator_display.text = key
                self.second_display.text = ""
                self.display.size_hint_x = 0.4
                self.operator_display.size_hint_x = 0.2
                self.second_display.size_hint_x = 0.4
            elif self.second_display.text == "":
                # اگر هنوز عدد دوم وارد نشده، عملگر قابل تغییر است.
                self.operator = key
                self.operator_display.text = key

        elif key == "=":
            if self.operator is None or self.second_display.text == "":
                return

            try:
                second_number = float(self.second_display.text)
            except ValueError:
                self.show_error()
                return

            if not math.isfinite(second_number):
                self.show_error()
                return

            if self.operator == "÷" and second_number == 0:
                self.show_error()
                return

            if self.operator == "+":
                result = self.first_number + second_number
            elif self.operator == "-":
                result = self.first_number - second_number
            elif self.operator == "×":
                result = self.first_number * second_number
            else:
                result = self.first_number / second_number

            if not math.isfinite(result):
                self.show_error()
                return

            expression = (
                f"{self.display.text} {self.operator} {self.second_display.text}"
            )
            result_text = self.format_result(result)
            self.add_history_entry(expression, result_text)
            self.display.text = result_text
            self.operator_display.text = ""
            self.second_display.text = ""
            self.first_number = None
            self.operator = None
            self.restore_display_layout()
            self.spend_battery(1.0)
            self.add_coins(2)

        elif key == "C":
            self.display.text = "0"
            self.operator_display.text = ""
            self.second_display.text = ""
            self.first_number = None
            self.operator = None
            self.restore_display_layout()

        elif key == "DEL":
            target = (
                self.display if self.operator is None
                else self.second_display
            )
            if target.text == "EROR":
                target.text = "0" if self.operator is None else ""
            elif target.text:
                target.text = target.text[:-1]
            if target.text == "":
                target.text = "0" if self.operator is None else ""

        elif key in ["x²", "√"]:
            target = (
                self.display if self.operator is None
                else self.second_display
            )
            if target.text in ["", "EROR"]:
                return

            try:
                number = float(target.text)
                if not math.isfinite(number):
                    self.show_error()
                    return
                if key == "x²":
                    result = number ** 2
                else:
                    if number < 0:
                        self.show_error()
                        return
                    result = math.sqrt(number)

                if not math.isfinite(result):
                    self.show_error()
                    return

                expression = (
                    f"{target.text}²" if key == "x²"
                    else f"√({target.text})"
                )
                result_text = self.format_result(result)
                self.add_history_entry(expression, result_text)
                target.text = result_text
                self.spend_battery(1.0)
                self.add_coins(2)
            except (ValueError, OverflowError):
                self.show_error()

    def flip_view(self, instance):
        self.is_back = not self.is_back

        if self.is_back:
            self.root_layout.remove_widget(self.body)
            self.back_view.disabled = False
            self.back_view.opacity = 1
            self.root_layout.add_widget(self.back_view)
        else:
            self.root_layout.remove_widget(self.back_view)
            self.back_view.disabled = True
            self.back_view.opacity = 0
            self.root_layout.add_widget(self.body)


if __name__ == "__main__":
    calcApp().run()
