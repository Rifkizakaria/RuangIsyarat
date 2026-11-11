import customtkinter as ctk
from config import (
    COLOR_BG_MAIN,
    COLOR_BG_CARD,
    COLOR_BG_INPUT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_ACCENT,
    COLOR_BTN_PRIMARY,
    COLOR_BTN_PRIMARY_HOVER,
    COLOR_BTN_SECONDARY,
    COLOR_BTN_SECONDARY_HOVER,
    COLOR_BTN_TEXT,
    COLOR_STATUS_SUCCESS,
    COLOR_STATUS_ERROR,
    FONT_TITLE,
    FONT_BODY,
    FONT_BUTTON,
    FONT_INPUT,
    FONT_STATUS,
    BTN_HEIGHT,
    CORNER_RADIUS,
)
from modules.auth import login_user, register_user
from modules.ui_dashboard import DashboardView
from modules.ui_kamus import KamusView
from modules.ui_deteksi import DeteksiView
from modules.ui_kuis import KuisView


class RuangIsyaratApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RuangIsyarat - Edukasi & Deteksi Bahasa Isyarat")
        self.geometry("980x700")
        self.minsize(880, 620)
        self.configure(fg_color=COLOR_BG_MAIN)

        self.active_user = None
        self.current_frame = None

        self.show_login_view()

    def _clear_current_frame(self):
        if self.current_frame is not None:
            if hasattr(self.current_frame, "stop_and_exit"):
                try:
                    self.current_frame.stop_and_exit()
                except Exception:
                    pass
            self.current_frame.destroy()
            self.current_frame = None

    def show_login_view(self):
        self._clear_current_frame()

        self.current_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_CARD,
            corner_radius=CORNER_RADIUS,
            width=500,
        )
        self.current_frame.pack(expand=True, padx=30, pady=30)

        title_label = ctk.CTkLabel(
            self.current_frame,
            text="RuangIsyarat",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_ACCENT,
        )
        title_label.pack(pady=(35, 5), padx=40)

        subtitle_label = ctk.CTkLabel(
            self.current_frame,
            text="Aplikasi Edukasi & Deteksi Bahasa Isyarat",
            font=FONT_BODY,
            text_color=COLOR_TEXT_SECONDARY,
        )
        subtitle_label.pack(pady=(0, 25), padx=40)

        input_container = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        input_container.pack(fill="x", padx=40, pady=5)

        lbl_nick = ctk.CTkLabel(
            input_container,
            text="Nickname:",
            font=FONT_BODY,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        lbl_nick.pack(fill="x", pady=(5, 2))

        self.entry_nickname = ctk.CTkEntry(
            input_container,
            font=FONT_INPUT,
            fg_color=COLOR_BG_INPUT,
            text_color=COLOR_TEXT_PRIMARY,
            height=42,
            placeholder_text="Masukkan nickname Anda",
        )
        self.entry_nickname.pack(fill="x", pady=(0, 15))

        lbl_pwd = ctk.CTkLabel(
            input_container,
            text="Password:",
            font=FONT_BODY,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        lbl_pwd.pack(fill="x", pady=(5, 2))

        self.entry_password = ctk.CTkEntry(
            input_container,
            font=FONT_INPUT,
            fg_color=COLOR_BG_INPUT,
            text_color=COLOR_TEXT_PRIMARY,
            show="*",
            height=42,
            placeholder_text="Masukkan password Anda",
        )
        self.entry_password.pack(fill="x", pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self.current_frame,
            text="",
            font=FONT_STATUS,
            wraplength=400,
        )
        self.status_label.pack(pady=10, padx=40)

        btn_container = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=40, pady=(10, 35))

        btn_login = ctk.CTkButton(
            btn_container,
            text="Masuk",
            font=FONT_BUTTON,
            fg_color=COLOR_BTN_PRIMARY,
            hover_color=COLOR_BTN_PRIMARY_HOVER,
            text_color=COLOR_BTN_TEXT,
            height=BTN_HEIGHT,
            corner_radius=CORNER_RADIUS,
            command=self.handle_login,
        )
        btn_login.pack(fill="x", pady=(0, 10))

        btn_register = ctk.CTkButton(
            btn_container,
            text="Daftar Baru",
            font=FONT_BUTTON,
            fg_color=COLOR_BTN_SECONDARY,
            hover_color=COLOR_BTN_SECONDARY_HOVER,
            text_color=COLOR_BTN_TEXT,
            height=BTN_HEIGHT,
            corner_radius=CORNER_RADIUS,
            command=self.handle_register,
        )
        btn_register.pack(fill="x")

    def handle_login(self):
        nick = self.entry_nickname.get()
        pwd = self.entry_password.get()

        success, msg = login_user(nick, pwd)
        if success:
            self.active_user = nick.strip()
            self.show_dashboard_view()
        else:
            self.status_label.configure(
                text=f"⚠️ {msg}",
                text_color=COLOR_STATUS_ERROR,
            )

    def handle_register(self):
        nick = self.entry_nickname.get()
        pwd = self.entry_password.get()

        success, msg = register_user(nick, pwd)
        if success:
            self.status_label.configure(
                text=f"✅ {msg}",
                text_color=COLOR_STATUS_SUCCESS,
            )
            self.entry_password.delete(0, "end")
        else:
            self.status_label.configure(
                text=f"⚠️ {msg}",
                text_color=COLOR_STATUS_ERROR,
            )

    def show_dashboard_view(self):
        self._clear_current_frame()
        self.current_frame = DashboardView(
            master=self,
            nickname=self.active_user or "Tamu",
            on_kamus=self.show_kamus_view,
            on_deteksi=self.show_deteksi_view,
            on_kuis=self.show_kuis_view,
            on_logout=self.handle_logout,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_kamus_view(self):
        self._clear_current_frame()
        self.current_frame = KamusView(
            master=self,
            on_back=self.show_dashboard_view,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_deteksi_view(self):
        self._clear_current_frame()
        self.current_frame = DeteksiView(
            master=self,
            on_back=self.show_dashboard_view,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_kuis_view(self):
        self._clear_current_frame()
        self.current_frame = KuisView(
            master=self,
            on_back=self.show_dashboard_view,
        )
        self.current_frame.pack(fill="both", expand=True)

    def handle_logout(self):
        self.active_user = None
        self.show_login_view()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = RuangIsyaratApp()
    app.mainloop()
