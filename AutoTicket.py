import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import keyboard
import json
import os
from typing import Dict, Optional

CONFIG_FILE: str = "skroty.json"
shortcuts: Dict[str, str] = {}
currently_edited_shortcut: Optional[str] = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def load_shortcuts() -> None:
    global shortcuts
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                shortcuts = json.load(f)
        except json.JSONDecodeError:
            shortcuts = {}
    else:
        shortcuts = {}

def save_shortcuts() -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(shortcuts, f, ensure_ascii=False, indent=4)

def apply_shortcuts() -> None:
    keyboard.unhook_all()
    for shortcut, text in shortcuts.items():
        keyboard.add_abbreviation(shortcut, text)

def clear_form() -> None:
    global currently_edited_shortcut
    currently_edited_shortcut = None
    entry_shortcut.delete(0, tk.END)
    text_content.delete("1.0", tk.END)
    listbox.selection_clear(0, tk.END)

def load_for_editing(event) -> None:
    global currently_edited_shortcut
    selection = listbox.curselection()
    if not selection:
        return

    index: int = selection[0]
    selected_text: str = listbox.get(index)
    shortcut: str = selected_text.split(" ➔ ")[0].strip()

    if shortcut in shortcuts:
        currently_edited_shortcut = shortcut

        entry_shortcut.delete(0, tk.END)
        text_content.delete("1.0", tk.END)

        entry_shortcut.insert(0, shortcut)
        text_content.insert("1.0", shortcuts[shortcut])

def add_shortcut() -> None:
    global currently_edited_shortcut
    shortcut: str = entry_shortcut.get().strip()
    text: str = text_content.get("1.0", tk.END).strip()

    if shortcut and text:
        if not shortcut.startswith("--"):
            shortcut = f"--{shortcut}"

        if currently_edited_shortcut and currently_edited_shortcut != shortcut:
            if currently_edited_shortcut in shortcuts:
                del shortcuts[currently_edited_shortcut]

        shortcuts[shortcut] = text
        save_shortcuts()
        apply_shortcuts()
        refresh_list()

        clear_form()
        messagebox.showinfo("Sukces", f"Zapisano skrót: {shortcut}")
    else:
        messagebox.showwarning("Błąd", "Wypełnij oba pola przed zapisaniem!")

def delete_shortcut() -> None:
    selection = listbox.curselection()
    if not selection:
        messagebox.showwarning("Błąd", "Najpierw kliknij na liście skrót, który chcesz usunąć.")
        return

    index: int = selection[0]
    selected_text: str = listbox.get(index)
    shortcut: str = selected_text.split(" ➔ ")[0].strip()

    if shortcut in shortcuts:
        confirmed = messagebox.askyesno("Usuwanie", f"Czy na pewno chcesz usunąć skrót {shortcut}?")
        if confirmed:
            del shortcuts[shortcut]
            save_shortcuts()
            apply_shortcuts()
            refresh_list()
            clear_form()
            messagebox.showinfo("Usunięto", f"Skrót {shortcut} został trwale usunięty.")

def refresh_list() -> None:
    listbox.delete(0, tk.END)
    for shortcut, text in shortcuts.items():
        short_text: str = f"{text[:45]}..." if len(text) > 45 else text
        listbox.insert(tk.END, f"{shortcut} ➔ {short_text}")


load_shortcuts()
apply_shortcuts()


app = ctk.CTk()
app.title("AutoTicket")
app.geometry("550x740")
app.resizable(False, False)

FONT_TITLE = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
FONT_MAIN = ctk.CTkFont(family="Segoe UI", size=13)

ctk.CTkLabel(app, text="Nazwa skrótu:", font=FONT_TITLE).pack(pady=(20, 5))
entry_shortcut = ctk.CTkEntry(app, width=450, height=40, font=FONT_MAIN, placeholder_text="Wpisz skrót...")
entry_shortcut.pack(pady=5)

ctk.CTkLabel(app, text="Pełny tekst do wklejenia:", font=FONT_TITLE).pack(pady=(15, 5))
text_content = ctk.CTkTextbox(app, width=450, height=130, font=FONT_MAIN, corner_radius=8)
text_content.pack(pady=5)

ctk.CTkLabel(app, text="Twoje skróty (kliknij, aby edytować):", font=FONT_TITLE).pack(pady=(20, 5))

list_frame = ctk.CTkFrame(app, width=450, height=220, corner_radius=8)
list_frame.pack(pady=5, padx=50, fill="both", expand=True)
list_frame.pack_propagate(False)

listbox = tk.Listbox(list_frame, font=("Segoe UI", 11), bg="#1c1c1e", fg="#d1d1d6",
                     selectbackground="#1f6feb", selectforeground="white",
                     relief="flat", highlightthickness=0, borderwidth=0)
listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)

scrollbar = ctk.CTkScrollbar(list_frame, command=listbox.yview)
scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))
listbox.config(yscrollcommand=scrollbar.set)

listbox.bind("<<ListboxSelect>>", load_for_editing)

refresh_list()

button_frame = ctk.CTkFrame(app, fg_color="transparent")
button_frame.pack(pady=20, padx=50, fill="x")

btn_save = ctk.CTkButton(button_frame, text="Zapisz / Edytuj", command=add_shortcut,
                         height=40, font=FONT_TITLE, fg_color="#238636", hover_color="#2EA043")
btn_save.pack(side="left", padx=5, expand=True, fill="x")

btn_clear = ctk.CTkButton(button_frame, text="Wyczyść", command=clear_form,
                          height=40, font=FONT_MAIN, fg_color="#30363D", hover_color="#484F58")
btn_clear.pack(side="left", padx=5, expand=True, fill="x")

btn_delete = ctk.CTkButton(button_frame, text="Usuń", command=delete_shortcut,
                           height=40, font=FONT_TITLE, fg_color="#DA3633", hover_color="#F85149")
btn_delete.pack(side="left", padx=5, expand=True, fill="x")

ctk.CTkLabel(app, text="Wskazówka: Minimalizuj okno, aby aplikacja działała w tle.",
             font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"), text_color="gray").pack(pady=(0, 15))

app.mainloop()