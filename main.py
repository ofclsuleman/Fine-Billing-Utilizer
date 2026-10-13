# -*- coding: utf-8 -*-
# main.py - Fine Billing Utilizer (entry point: splash -> login -> main app)

import tkinter as tk
from tkinter import ttk, messagebox

try:
    import customtkinter as ctk
except ImportError:
    raise SystemExit(
        "CustomTkinter is required.\nInstall it with:  pip install customtkinter")

import database as db
from pages import (DashboardPage, CustomersPage, SuppliersPage, ProductsPage,
                   InvoicePage, RecordsPage, SettingsPage)

APP_NAME = "Fine Billing Utilizer"
COMPANY = "Fine Tech's Fine Group Of Companies"
DEVELOPER = "M.Suleman Raghib"
CONTACT = "ofclsuleman@gmail.com"
VERSION = "1.0.0"

ctk.set_default_color_theme("blue")

# Global appearance mode ("light" / "dark") shared by all windows
MODE = ["light"]

THEMES = {
    "light": {
        "bg": "#eef1f6", "sidebar": "#12325b", "sidebar_hover": "#1b4a85",
        "card": "#ffffff", "text": "#16202e", "subtext": "#5c6b7a",
        "accent": "#1f6aa5", "accent_hover": "#2b83c4",
        "entry": "#f2f5f9", "tree_bg": "#ffffff", "tree_head": "#1f6aa5",
        "tree_head_fg": "#ffffff", "border": "#d5dde5",
        "success": "#1e9e5a", "danger": "#d64545", "warn": "#c77d1d",
    },
    "dark": {
        "bg": "#0f141b", "sidebar": "#0c1a2e", "sidebar_hover": "#14304f",
        "card": "#171e27", "text": "#e6ecf2", "subtext": "#8fa0b0",
        "accent": "#3b8ed0", "accent_hover": "#5aa3dc",
        "entry": "#1e2630", "tree_bg": "#141b23", "tree_head": "#1c3d5a",
        "tree_head_fg": "#e6ecf2", "border": "#2a3542",
        "success": "#2fbf71", "danger": "#e06060", "warn": "#e0a13c",
    },
}

FONT = "Segoe UI"

PAGES = ["🏠  Dashboard", "👥  Customers", "🏭  Suppliers", "📦  Products",
         "🧾  Sales Invoice", "🛒  Purchase Invoice", "📚  Records", "⚙️  Settings"]


def style_treeview(mode):
    t = THEMES[mode]
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Treeview",
                    background=t["tree_bg"], foreground=t["text"],
                    fieldbackground=t["tree_bg"], rowheight=30,
                    font=(FONT, 11), borderwidth=0)
    style.configure("Treeview.Heading",
                    background=t["tree_head"], foreground=t["tree_head_fg"],
                    font=(FONT, 11, "bold"), relief="flat", padding=6)
    style.map("Treeview",
              background=[("selected", t["accent"])],
              foreground=[("selected", "#ffffff")])


# ----------------------------------------------------------------------
# Splash screen
# ----------------------------------------------------------------------
class SplashWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        w, h = 560, 340
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+%d+%d" % (w, h, (sw - w) // 2, (sh - h) // 2))
        self.configure(fg_color="#0d2242")

        ctk.CTkLabel(self, text="⚡", font=(FONT, 46)).pack(pady=(30, 0))
        ctk.CTkLabel(self, text=APP_NAME, font=(FONT, 30, "bold"),
                     text_color="#ffffff").pack()
        ctk.CTkLabel(self, text=COMPANY, font=(FONT, 14),
                     text_color="#9db8d2").pack(pady=(4, 0))
        self.pb = ctk.CTkProgressBar(self, width=380, height=10,
                                     progress_color="#3b8ed0",
                                     fg_color="#1a3a63", corner_radius=5)
        self.pb.set(0)
        self.pb.pack(pady=(30, 10))
        self.status = ctk.CTkLabel(self, text="Starting...",
                                   font=(FONT, 12), text_color="#9db8d2")
        self.status.pack()
        self._step = 0.0
        self.after(150, self._animate)

    def _animate(self):
        self._step += 0.025
        self.pb.set(min(self._step, 1.0))
        if self._step < 0.4:
            self.status.configure(text="Loading database...")
        elif self._step < 0.8:
            self.status.configure(text="Preparing interface...")
        else:
            self.status.configure(text="Almost ready...")
        if self._step < 1.0:
            self.after(45, self._animate)
        else:
            self.after(400, self.destroy)


# ----------------------------------------------------------------------
# Login / registration
# ----------------------------------------------------------------------
class LoginWindow:
    def __init__(self):
        self.success = False
        self.win = ctk.CTk()
        self.win.title(APP_NAME)
        w, h = 480, 600
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry("%dx%d+%d+%d" % (w, h, (sw - w) // 2, (sh - h) // 2))
        self.win.resizable(False, False)
        ctk.set_appearance_mode(MODE[0])
        style_treeview(MODE[0])
        theme = THEMES[MODE[0]]
        self.win.configure(fg_color=theme["bg"])

        card = ctk.CTkFrame(self.win, fg_color=theme["card"], corner_radius=18,
                            border_width=1, border_color=theme["border"])
        card.place(relx=0.5, rely=0.5, relwidth=0.88, relheight=0.92, anchor="center")

        ctk.CTkLabel(card, text="⚡", font=(FONT, 46)).pack(pady=(26, 0))
        ctk.CTkLabel(card, text=APP_NAME, font=(FONT, 24, "bold"),
                     text_color=theme["text"]).pack()
        ctk.CTkLabel(card, text=COMPANY, font=(FONT, 13),
                     text_color=theme["subtext"],
                     wraplength=360).pack(pady=(2, 16))

        biz = db.get_business()
        if biz:
            # Returning user: quick, efficient login
            ctk.CTkLabel(card, text="Welcome back 👋", font=(FONT, 16),
                         text_color=theme["text"]).pack()
            ctk.CTkLabel(card, text=biz["name"], font=(FONT, 22, "bold"),
                         text_color=theme["accent"],
                         wraplength=360).pack(pady=(2, 24))
            ctk.CTkButton(card, text="Continue  ➜", width=250, height=46,
                          font=(FONT, 15, "bold"),
                          fg_color=theme["accent"],
                          hover_color=theme["accent_hover"],
                          command=self._continue).pack(pady=6)
        else:
            # First run: register by entering a business name only
            ctk.CTkLabel(card, text="Register your business", font=(FONT, 16),
                         text_color=theme["text"]).pack()
            ctk.CTkLabel(card, text="Just enter your business name to get started",
                         font=(FONT, 12),
                         text_color=theme["subtext"]).pack(pady=(2, 12))
            self.entry = ctk.CTkEntry(card, placeholder_text="Business name",
                                      width=310, height=46, justify="center",
                                      font=(FONT, 14), fg_color=theme["entry"],
                                      text_color=theme["text"],
                                      border_color=theme["border"])
            self.entry.pack(pady=6)
            self.entry.bind("<Return>", lambda e: self._register())
            ctk.CTkButton(card, text="Create & Continue  ➜", width=250, height=46,
                          font=(FONT, 15, "bold"),
                          fg_color=theme["accent"],
                          hover_color=theme["accent_hover"],
                          command=self._register).pack(pady=10)

        ctk.CTkLabel(card, text="Developed by %s\n%s" % (DEVELOPER, CONTACT),
                     font=(FONT, 11), text_color=theme["subtext"],
                     justify="center").pack(side="bottom", pady=16)

    def _register(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showwarning("Required", "Please enter your business name.")
            return
        db.create_business(name)
        self.success = True
        self.win.destroy()

    def _continue(self):
        self.success = True
        self.win.destroy()


# ----------------------------------------------------------------------
# Main application window
# ----------------------------------------------------------------------
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.should_exit = False
        self.mode = MODE[0]
        self.current_page = PAGES[0]
        self.title("%s  —  %s" % (APP_NAME, COMPANY))
        self.geometry("1280x720")
        self.minsize(1100, 650)
        ctk.set_appearance_mode(self.mode)
        style_treeview(self.mode)
        self._build()

    # ---- UI construction ----
    def _build(self):
        theme = THEMES[self.mode]
        self.configure(fg_color=theme["bg"])

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=theme["sidebar"],
                                    corner_radius=0, width=225)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="⚡ Fine Billing\nUtilizer",
                     font=(FONT, 18, "bold"), text_color="#ffffff",
                     justify="left", anchor="w",
                     wraplength=190).pack(pady=(22, 2), padx=16, anchor="w")
        biz = db.get_business()
        ctk.CTkLabel(self.sidebar, text=biz["name"] if biz else "",
                     font=(FONT, 12), text_color="#9db8d2",
                     anchor="w", wraplength=190).pack(padx=16, pady=(0, 14), anchor="w")

        self.nav_buttons = {}
        for p in PAGES:
            btn = ctk.CTkButton(self.sidebar, text=p, anchor="w", height=42,
                                font=(FONT, 14), corner_radius=10,
                                fg_color="transparent", text_color="#e8eef5",
                                hover_color=theme["sidebar_hover"],
                                command=lambda name=p: self.show_page(name))
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[p] = btn

        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=12, pady=14)
        toggle_text = "☀️  Light Mode" if self.mode == "dark" else "🌙  Dark Mode"
        ctk.CTkButton(bottom, text=toggle_text, height=36, font=(FONT, 13),
                      fg_color=theme["sidebar_hover"],
                      hover_color=theme["accent"],
                      command=self.toggle_theme).pack(fill="x", pady=3)
        ctk.CTkButton(bottom, text="🚪  Logout", height=36, font=(FONT, 13),
                      fg_color=theme["sidebar_hover"],
                      hover_color=theme["warn"],
                      command=self.logout).pack(fill="x", pady=3)
        ctk.CTkButton(bottom, text="✖  Exit", height=36, font=(FONT, 13),
                      fg_color=theme["sidebar_hover"],
                      hover_color=theme["danger"],
                      command=self.quit_app).pack(fill="x", pady=3)

        # Content container
        self.container = ctk.CTkFrame(self, fg_color=theme["bg"], corner_radius=0)
        self.container.pack(side="left", fill="both", expand=True)
        self._render_page()

    def _render_page(self):
        theme = THEMES[self.mode]
        for w in self.container.winfo_children():
            w.destroy()
        name = self.current_page
        if name == PAGES[4]:
            page = InvoicePage(self.container, theme, "sale", app=self)
        elif name == PAGES[5]:
            page = InvoicePage(self.container, theme, "purchase", app=self)
        else:
            cls = {PAGES[0]: DashboardPage, PAGES[1]: CustomersPage,
                   PAGES[2]: SuppliersPage, PAGES[3]: ProductsPage,
                   PAGES[6]: RecordsPage, PAGES[7]: SettingsPage}[name]
            page = cls(self.container, theme, app=self)
        page.pack(fill="both", expand=True, padx=18, pady=18)
        # highlight active nav button
        for p, btn in self.nav_buttons.items():
            if p == name:
                btn.configure(fg_color=theme["accent"])
            else:
                btn.configure(fg_color="transparent")

    def show_page(self, name):
        self.current_page = name
        self._render_page()

    def toggle_theme(self):
        MODE[0] = "dark" if MODE[0] == "light" else "light"
        self.mode = MODE[0]
        ctk.set_appearance_mode(self.mode)
        style_treeview(self.mode)
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def logout(self):
        if messagebox.askyesno("Logout", "Log out and return to the login screen?"):
            self.destroy()

    def quit_app(self):
        if messagebox.askyesno("Exit", "Exit %s?" % APP_NAME):
            self.should_exit = True
            self.destroy()


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
def run():
    db.init_db()
    splash = SplashWindow()
    splash.mainloop()          # exits when the splash destroys itself

    while True:
        login = LoginWindow()
        login.win.mainloop()
        if not login.success:  # user closed the login window
            break
        app = MainApp()
        app.mainloop()
        if app.should_exit:
            break


if __name__ == "__main__":
    run()
