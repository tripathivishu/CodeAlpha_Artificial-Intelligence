import tkinter as tk
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator
import pyttsx3
import threading

# Language Dictionary
LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Russian": "ru",
    "Arabic": "ar",
    "Bengali": "bn",
    "Korean": "ko"
}

# Text to Speech in a separate thread (UI freeze nahi hoga)
def speak_text(text):
    def run_voice():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 145)
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=run_voice, daemon=True).start()

def perform_translation():
    content = txt_input.get("1.0", tk.END).strip()
    if not content:
        status_var.set("⚠️ Please enter some text first!")
        return

    src = combo_src.get()
    tgt = combo_tgt.get()

    src_code = 'auto' if src == "Auto Detect" else LANGUAGES.get(src, 'auto')
    tgt_code = LANGUAGES.get(tgt, 'hi')

    status_var.set("⚡ Translating...")
    root.update_idletasks()

    try:
        translated = GoogleTranslator(source=src_code, target=tgt_code).translate(content)
        txt_output.delete("1.0", tk.END)
        txt_output.insert(tk.END, translated)
        status_var.set("✅ Translation Completed!")
    except Exception as e:
        status_var.set("❌ Error: Check internet connection")

def swap_languages():
    src_val = combo_src.get()
    tgt_val = combo_tgt.get()
    if src_val != "Auto Detect":
        combo_src.set(tgt_val)
        combo_tgt.set(src_val)
        status_var.set("🔄 Languages swapped")

def copy_result():
    output = txt_output.get("1.0", tk.END).strip()
    if output:
        root.clipboard_clear()
        root.clipboard_append(output)
        status_var.set("📋 Copied to clipboard!")

def update_counts(event=None):
    text = txt_input.get("1.0", tk.END).strip()
    chars = len(text)
    words = len(text.split()) if text else 0
    lbl_counter.config(text=f"Words: {words} | Characters: {chars}")

# --- UI Theme Configuration ---
BG_DARK = "#0f172a"       # Slate 900
CARD_BG = "#1e293b"       # Slate 800
TEXT_COLOR = "#f8fafc"    # Slate 50
ACCENT_BLUE = "#3b82f6"   # Neon Blue
ACCENT_GREEN = "#10b981"  # Emerald
ACCENT_PURPLE = "#8b5cf6" # Violet

root = tk.Tk()
root.title("AI PolyGlot - Smart Translator")
root.geometry("640x670")
root.configure(bg=BG_DARK)
root.resizable(False, False)

# Header Banner
header_frame = tk.Frame(root, bg=CARD_BG, pady=12)
header_frame.pack(fill="x", padx=15, pady=(15, 10))

tk.Label(header_frame, text="✨ AI Language Translator", font=("Segoe UI", 16, "bold"), fg="#38bdf8", bg=CARD_BG).pack()
tk.Label(header_frame, text="Real-time Multi-Language Processing Engine", font=("Segoe UI", 9), fg="#94a3b8", bg=CARD_BG).pack()

# Dropdown Control Bar
bar = tk.Frame(root, bg=BG_DARK)
bar.pack(fill="x", padx=25, pady=8)

combo_src = ttk.Combobox(bar, values=["Auto Detect"] + list(LANGUAGES.keys()), state="readonly", width=14, font=("Segoe UI", 10))
combo_src.set("Auto Detect")
combo_src.pack(side="left", padx=5)

btn_swap = tk.Button(bar, text="⇄", command=swap_languages, bg="#334155", fg="#38bdf8", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2", padx=10)
btn_swap.pack(side="left", padx=10)

combo_tgt = ttk.Combobox(bar, values=list(LANGUAGES.keys()), state="readonly", width=14, font=("Segoe UI", 10))
combo_tgt.set("Hindi")
combo_tgt.pack(side="left", padx=5)

# Input Box Card
in_card = tk.Frame(root, bg=CARD_BG, padx=12, pady=10)
in_card.pack(fill="x", padx=20, pady=5)

tk.Label(in_card, text="SOURCE TEXT", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg=CARD_BG).pack(anchor="w")
txt_input = tk.Text(in_card, height=5, bg="#0b1120", fg=TEXT_COLOR, insertbackground="white", font=("Segoe UI", 11), relief="flat", bd=0, padx=8, pady=8)
txt_input.pack(fill="x", pady=5)
txt_input.bind("<KeyRelease>", update_counts)

lbl_counter = tk.Label(in_card, text="Words: 0 | Characters: 0", font=("Segoe UI", 8), fg="#64748b", bg=CARD_BG)
lbl_counter.pack(anchor="e")

# Main Action Button
btn_translate = tk.Button(root, text="⚡ Translate Now", command=perform_translation, bg=ACCENT_BLUE, fg="white", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2", pady=7)
btn_translate.pack(fill="x", padx=20, pady=10)

# Output Box Card
out_card = tk.Frame(root, bg=CARD_BG, padx=12, pady=10)
out_card.pack(fill="x", padx=20, pady=5)

tk.Label(out_card, text="TRANSLATION RESULT", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg=CARD_BG).pack(anchor="w")
txt_output = tk.Text(out_card, height=5, bg="#0b1120", fg="#38bdf8", insertbackground="white", font=("Segoe UI", 11, "bold"), relief="flat", bd=0, padx=8, pady=8)
txt_output.pack(fill="x", pady=5)

# Feature Controls (Copy & Audio TTS)
action_bar = tk.Frame(out_card, bg=CARD_BG)
action_bar.pack(fill="x", pady=(5, 0))

btn_copy = tk.Button(action_bar, text="📋 Copy", command=copy_result, bg="#059669", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10)
btn_copy.pack(side="left", padx=5)

btn_listen = tk.Button(action_bar, text="🔊 Listen Output", command=lambda: speak_text(txt_output.get("1.0", tk.END).strip()), bg=ACCENT_PURPLE, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10)
btn_listen.pack(side="left", padx=5)

# Status Footer
status_var = tk.StringVar(value="Ready")
lbl_status = tk.Label(root, textvariable=status_var, font=("Segoe UI", 9), fg="#94a3b8", bg=BG_DARK)
lbl_status.pack(side="bottom", pady=10)

root.mainloop()