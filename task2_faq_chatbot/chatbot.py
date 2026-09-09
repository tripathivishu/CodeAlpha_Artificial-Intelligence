import tkinter as tk
from tkinter import scrolledtext
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ----------------- FAQ KNOWLEDGE BASE -----------------
faq_data = [
    {
        "q": "hello hi hey good morning greetings",
        "a": "Hello there! 👋 How can I help you with your CodeAlpha internship today?"
    },
    {
        "q": "how many tasks do i need to complete submission requirements",
        "a": "You need to complete at least 2 or 3 tasks to successfully pass the internship."
    },
    {
        "q": "how to submit tasks where to submit project link submission form",
        "a": "Upload your code to GitHub, share a LinkedIn video demo tagging CodeAlpha, and submit the links via the official submission form."
    },
    {
        "q": "when will i get certificate completion certificate criteria",
        "a": "You will receive a QR-verified completion certificate after submitting at least 2 or 3 tasks successfully."
    },
    {
        "q": "what is the name format for github repository",
        "a": "Your GitHub repository name should follow this format: 'CodeAlpha_ProjectName'."
    },
    {
        "q": "bye goodbye see you take care exit",
        "a": "Goodbye! Best of luck with your internship project. Keep coding! 🚀"
    }
]

questions = [item["q"] for item in faq_data]
answers = [item["a"] for item in faq_data]

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(questions)

def get_bot_response(user_text):
    clean_text = user_text.lower().strip()
    if not clean_text:
        return ""

    user_vec = vectorizer.transform([clean_text])
    scores = cosine_similarity(user_vec, tfidf_matrix).flatten()
    best_idx = scores.argmax()

    # Agar confidence match threshold se kam ho
    if scores[best_idx] < 0.20:
        return "I'm not quite sure about that one yet! 🤔 Try checking the internship PDF instructions or rephrase your question."

    return answers[best_idx]


# ----------------- UI SETUP (TKINTER) -----------------
root = tk.Tk()
root.title("CodeAlpha Support Assistant")
root.geometry("480x620")
root.configure(bg="#F0F2F5")
root.resizable(False, False)

# 1. Header Bar (Google/Fintech Clean Minimal Look)
header_frame = tk.Frame(root, bg="#1A73E8", height=60)
header_frame.pack(fill="x")

lbl_title = tk.Label(
    header_frame, 
    text="CodeAlpha AI Assistant", 
    font=("Segoe UI", 13, "bold"), 
    bg="#1A73E8", 
    fg="white"
)
lbl_title.pack(pady=(12, 0))

lbl_subtitle = tk.Label(
    header_frame, 
    text="● Online | Instant FAQ Help", 
    font=("Segoe UI", 9), 
    bg="#1A73E8", 
    fg="#D2E3FC"
)
lbl_subtitle.pack(pady=(0, 10))

# 2. Chat History Area
chat_area = scrolledtext.ScrolledText(
    root, 
    wrap=tk.WORD, 
    state='disabled', 
    bg="#FFFFFF", 
    fg="#202124", 
    font=("Segoe UI", 10),
    padx=12,
    pady=12,
    bd=0,
    highlightthickness=1,
    highlightbackground="#DADCE0"
)
chat_area.pack(padx=14, pady=(12, 6), fill="both", expand=True)

# Custom text tags styling
chat_area.tag_config("user", foreground="#1A73E8", font=("Segoe UI", 10, "bold"))
chat_area.tag_config("bot", foreground="#1E8E3E", font=("Segoe UI", 10, "bold"))
chat_area.tag_config("msg", foreground="#3C4043")

def display_message(sender, message, tag_name):
    chat_area.configure(state='normal')
    chat_area.insert(tk.END, f"{sender}: ", tag_name)
    chat_area.insert(tk.END, f"{message}\n\n", "msg")
    chat_area.configure(state='disabled')
    chat_area.yview(tk.END)

# 3. Quick Suggestion Pills (Helpful clickable buttons)
quick_frame = tk.Frame(root, bg="#F0F2F5")
quick_frame.pack(fill="x", padx=14, pady=(0, 6))

def send_query(query_text):
    if not query_text.strip():
        return
    
    display_message("You", query_text, "user")
    
    bot_reply = get_bot_response(query_text)
    if bot_reply:
        root.after(300, lambda: display_message("Bot", bot_reply, "bot"))

def on_send_click():
    text = entry_box.get().strip()
    if text:
        entry_box.delete(0, tk.END)
        send_query(text)

btn_style = {
    "bg": "#E8F0FE", 
    "fg": "#1A73E8", 
    "activebackground": "#D2E3FC", 
    "font": ("Segoe UI", 8, "bold"),
    "bd": 0,
    "padx": 8,
    "pady": 3,
    "cursor": "hand2"
}

btn_q1 = tk.Button(quick_frame, text="📌 Required Tasks", command=lambda: send_query("How many tasks do I need to complete?"), **btn_style)
btn_q1.pack(side="left", padx=(0, 4))

btn_q2 = tk.Button(quick_frame, text="📤 How to Submit", command=lambda: send_query("Where should I submit the task?"), **btn_style)
btn_q2.pack(side="left", padx=4)

btn_q3 = tk.Button(quick_frame, text="📜 Certificate", command=lambda: send_query("When will I get the certificate?"), **btn_style)
btn_q3.pack(side="left", padx=4)

# 4. Bottom Input Bar
input_frame = tk.Frame(root, bg="#F0F2F5")
input_frame.pack(fill="x", padx=14, pady=(4, 14))

entry_box = tk.Entry(
    input_frame, 
    font=("Segoe UI", 10), 
    bd=1, 
    relief="solid", 
    highlightthickness=0
)
entry_box.pack(side="left", fill="both", expand=True, ipady=8, padx=(0, 8))
entry_box.bind("<Return>", lambda event: on_send_click())

btn_send = tk.Button(
    input_frame, 
    text="Send", 
    font=("Segoe UI", 10, "bold"), 
    bg="#1A73E8", 
    fg="white", 
    activebackground="#1557B0",
    bd=0, 
    padx=16, 
    cursor="hand2",
    command=on_send_click
)
btn_send.pack(side="right")

# Welcome message on launch
display_message("Bot", "Hi! I am your CodeAlpha Assistant. You can type a question below or click on the suggestion buttons.", "bot")

root.mainloop()