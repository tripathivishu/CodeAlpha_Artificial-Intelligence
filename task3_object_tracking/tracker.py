import os
import time
import threading
from datetime import datetime
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
from ultralytics import YOLO

class ProObjectTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeAlpha AI Studio - Vision Tracking & Assistant")
        self.root.geometry("1240x740")
        self.root.minsize(1050, 650)
        self.root.configure(bg="#F1F3F4")

        # ----------------- Core Variables -----------------
        self.is_running = False
        self.cap = None
        self.thread = None
        self.current_frame = None
        self.annotated_frame = None
        self.detected_items = {}       # { "person": 2, "cell phone": 1 }
        self.total_tracked_count = 0
        self.fps = 0.0
        self.prev_time = time.time()
        self.confidence_thresh = 0.35

        # Initialize YOLOv8 Model
        try:
            self.model = YOLO("yolov8n.pt")
        except Exception as e:
            messagebox.showerror("Model Error", f"Model load nahi ho paya: {e}")
            self.model = None

        self._build_interface()

    # ----------------- UI Layout Construction -----------------
    def _build_interface(self):
        # 1. Navigation / Top Bar
        top_bar = tk.Frame(self.root, bg="#0F172A", height=55)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)

        title_lbl = tk.Label(
            top_bar, 
            text="◈ CodeAlpha Vision Engine | Object Detection & Deep Tracker", 
            font=("Segoe UI", 13, "bold"), 
            fg="#F8FAFC", 
            bg="#0F172A"
        )
        title_lbl.pack(side=tk.LEFT, padx=20)

        self.lbl_system_clock = tk.Label(
            top_bar, 
            font=("Segoe UI", 10), 
            fg="#94A3B8", 
            bg="#0F172A"
        )
        self.lbl_system_clock.pack(side=tk.RIGHT, padx=20)
        self._update_clock()

        # 2. Main Workspace
        workspace = tk.Frame(self.root, bg="#F1F3F4")
        workspace.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        # ---------------- LEFT COLUMN: Vision & Controls ----------------
        left_col = tk.Frame(workspace, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Metrics Ribbon (Google / Fin-Tech Dashboard Style)
        metrics_bar = tk.Frame(left_col, bg="#F8FAFC", height=50, bd=1, relief=tk.GROOVE)
        metrics_bar.pack(fill=tk.X, padx=10, pady=8)

        self.lbl_metric_fps = tk.Label(metrics_bar, text="FPS: 0.0", font=("Segoe UI", 11, "bold"), bg="#F8FAFC", fg="#2563EB")
        self.lbl_metric_fps.pack(side=tk.LEFT, padx=15)

        self.lbl_metric_objects = tk.Label(metrics_bar, text="Active Objects: 0", font=("Segoe UI", 11, "bold"), bg="#F8FAFC", fg="#0F172A")
        self.lbl_metric_objects.pack(side=tk.LEFT, padx=20)

        self.lbl_metric_status = tk.Label(metrics_bar, text="● Camera Idle", font=("Segoe UI", 11, "bold"), bg="#F8FAFC", fg="#DC2626")
        self.lbl_metric_status.pack(side=tk.RIGHT, padx=15)

        # Video Viewport
        self.video_viewport = tk.Label(
            left_col, 
            text="VIDEO FEED OFFLINE\nClick 'Start Camera' below to launch real-time AI tracking", 
            font=("Segoe UI", 12, "bold"), 
            bg="#E2E8F0", 
            fg="#475569"
        )
        self.video_viewport.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Interactive Controls Panel
        controls_panel = tk.Frame(left_col, bg="#FFFFFF")
        controls_panel.pack(fill=tk.X, padx=10, pady=10)

        self.btn_start = tk.Button(
            controls_panel, text="▶ Start Camera", font=("Segoe UI", 10, "bold"), 
            bg="#16A34A", fg="white", activebackground="#15803D", activeforeground="white",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2", command=self.start_tracking
        )
        self.btn_start.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_stop = tk.Button(
            controls_panel, text="⏹ Stop Camera", font=("Segoe UI", 10, "bold"), 
            bg="#DC2626", fg="white", activebackground="#B91C1C", activeforeground="white",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2", state=tk.DISABLED, command=self.stop_tracking
        )
        self.btn_stop.pack(side=tk.LEFT, padx=6)

        self.btn_snap = tk.Button(
            controls_panel, text="📸 Snapshot", font=("Segoe UI", 10, "bold"), 
            bg="#0284C7", fg="white", activebackground="#0369A1", activeforeground="white",
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2", command=self.take_snapshot
        )
        self.btn_snap.pack(side=tk.LEFT, padx=6)

        # Confidence Slider
        slider_box = tk.Frame(controls_panel, bg="#FFFFFF")
        slider_box.pack(side=tk.RIGHT, padx=5)

        tk.Label(slider_box, text="Confidence:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(side=tk.LEFT, padx=4)
        self.conf_slider = ttk.Scale(slider_box, from_=0.20, to=0.85, value=0.35, orient=tk.HORIZONTAL, length=110, command=self._update_confidence)
        self.conf_slider.pack(side=tk.LEFT)

        self.lbl_conf_val = tk.Label(slider_box, text="0.35", font=("Segoe UI", 9), bg="#FFFFFF", fg="#334155", width=4)
        self.lbl_conf_val.pack(side=tk.LEFT)

        # ---------------- RIGHT COLUMN: Support Bot & Diagnostics ----------------
        right_col = tk.Frame(workspace, bg="#FFFFFF", width=380, bd=1, relief=tk.SOLID)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_col.pack_propagate(False)

        chat_header = tk.Frame(right_col, bg="#F8FAFC", height=45, bd=1, relief=tk.GROOVE)
        chat_header.pack(fill=tk.X)
        tk.Label(chat_header, text="TrackBot | Intelligent Support", font=("Segoe UI", 11, "bold"), bg="#F8FAFC", fg="#0F172A").pack(pady=10)

        # Message History
        self.chat_area = tk.Text(right_col, bg="#F8FAFC", font=("Segoe UI", 10), wrap=tk.WORD, state=tk.DISABLED, relief=tk.FLAT, padx=8, pady=8)
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Quick Action Chips (Reference: Modern Support Bots)
        chip_bar = tk.Frame(right_col, bg="#FFFFFF")
        chip_bar.pack(fill=tk.X, padx=8, pady=2)

        chips = [
            ("Explain Architecture", lambda: self._trigger_prompt("Explain Architecture")),
            ("Telemetry Status", lambda: self._trigger_prompt("Telemetry Status")),
            ("Fix Camera Issues", lambda: self._trigger_prompt("Fix Camera Issues"))
        ]
        for label, cmd in chips:
            b = tk.Button(chip_bar, text=label, font=("Segoe UI", 8), bg="#EFF6FF", fg="#1D4ED8", relief=tk.FLAT, cursor="hand2", command=cmd)
            b.pack(side=tk.LEFT, padx=2, pady=2)

        # Input & Dispatch Bar
        input_container = tk.Frame(right_col, bg="#FFFFFF")
        input_container.pack(fill=tk.X, padx=8, pady=8)

        self.chat_entry = tk.Entry(input_container, font=("Segoe UI", 10), bg="#F1F5F9", relief=tk.FLAT, bd=4)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), ipady=3)
        self.chat_entry.bind("<Return>", lambda event: self.send_message())

        btn_send = tk.Button(input_container, text="Send", font=("Segoe UI", 9, "bold"), bg="#2563EB", fg="white", relief=tk.FLAT, padx=12, pady=4, cursor="hand2", command=self.send_message)
        btn_send.pack(side=tk.RIGHT)

        # Initial Welcome
        self._append_chat("TrackBot", "Welcome! I monitor your YOLOv8 inference pipeline and tracking telemetry. Ask a query or use the chips above.")

    # ----------------- Vision Thread & Inference -----------------
    def start_tracking(self):
        if self.is_running:
            return
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Device Error", "Unable to open webcam. Please verify connection and permissions.")
            return

        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.lbl_metric_status.config(text="● Camera Live", fg="#16A34A")

        # Spawn background capture/inference thread to prevent GUI lockup
        self.thread = threading.Thread(target=self._run_inference_loop, daemon=True)
        self.thread.start()

    def _run_inference_loop(self):
        while self.is_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            # Calculate FPS
            curr_time = time.time()
            self.fps = 1.0 / max((curr_time - self.prev_time), 0.0001)
            self.prev_time = curr_time

            # YOLO Track Inference
            results = self.model.track(frame, persist=True, conf=self.confidence_thresh, verbose=False)
            self.annotated_frame = results[0].plot()

            # Inspect and aggregate detected classes
            current_counts = {}
            if results[0].boxes is not None:
                for cls_idx in results[0].boxes.cls.cpu().numpy():
                    class_name = self.model.names[int(cls_idx)]
                    current_counts[class_name] = current_counts.get(class_name, 0) + 1
            
            self.detected_items = current_counts
            self.total_tracked_count = sum(current_counts.values())

            # Convert frame to PIL for display
            rgb_img = cv2.cvtColor(self.annotated_frame, cv2.COLOR_BGR2RGB)
            rgb_img = cv2.resize(rgb_img, (670, 470))
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(rgb_img))

            # Push image to UI safely
            self.root.after(0, self._render_frame, img_tk)

        if self.cap:
            self.cap.release()

    def _render_frame(self, img_tk):
        self.video_viewport.imgtk = img_tk
        self.video_viewport.configure(image=img_tk)
        self.lbl_metric_fps.config(text=f"FPS: {self.fps:.1f}")
        self.lbl_metric_objects.config(text=f"Active Objects: {self.total_tracked_count}")

    def stop_tracking(self):
        self.is_running = False
        self.video_viewport.config(image="", text="VIDEO FEED OFFLINE\nClick 'Start Camera' below to launch real-time AI tracking")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_metric_status.config(text="● Camera Idle", fg="#DC2626")
        self.lbl_metric_fps.config(text="FPS: 0.0")
        self.lbl_metric_objects.config(text="Active Objects: 0")

    def take_snapshot(self):
        if self.annotated_frame is None:
            messagebox.showinfo("Snapshot Info", "No live frame to capture. Start the camera first.")
            return

        os.makedirs("captures", exist_ok=True)
        filename = f"captures/track_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(filename, self.annotated_frame)
        self._append_chat("TrackBot", f"Snapshot successfully archived to: `{filename}`")

    def _update_confidence(self, val):
        self.confidence_thresh = float(val)
        self.lbl_conf_val.config(text=f"{self.confidence_thresh:.2f}")

    # ----------------- Support Chatbot Logic -----------------
    def _trigger_prompt(self, text):
        self.chat_entry.delete(0, tk.END)
        self.chat_entry.insert(0, text)
        self.send_message()

    def send_message(self):
        user_text = self.chat_entry.get().strip()
        if not user_text:
            return

        self._append_chat("You", user_text)
        self.chat_entry.delete(0, tk.END)

        reply = self._get_bot_reply(user_text.lower())
        self.root.after(150, lambda: self._append_chat("TrackBot", reply))

    def _get_bot_reply(self, q):
        if "explain architecture" in q or "how it works" in q:
            return (
                "Architecture Overview:\n"
                "1. OpenCV reads video streams frame-by-frame.\n"
                "2. YOLOv8 detects bounding boxes and object classes.\n"
                "3. Deep tracking assigns persistent IDs across frames to maintain movement continuity."
            )
        elif "telemetry" in q or "status" in q or "count" in q:
            if not self.is_running:
                return "The camera pipeline is inactive. Start the stream to record real-time telemetry."
            item_details = ", ".join([f"{k}: {v}" for k, v in self.detected_items.items()]) or "None"
            return f"Current Pipeline Metrics:\n- Real-time FPS: {self.fps:.1f}\n- Objects In Frame: {self.total_tracked_count}\n- Detected Classes: {item_details}"
        elif "camera" in q or "fix" in q or "error" in q:
            return "Troubleshooting Guide:\n- If index 0 fails, verify if another app is using your webcam.\n- On macOS, confirm terminal camera permissions in System Settings."
        elif "confidence" in q or "threshold" in q:
            return f"Current confidence threshold is {self.confidence_thresh:.2f}. Lowering it increases sensitivity, while raising it reduces false positives."
        elif "hi" in q or "hello" in q:
            return "Greetings! How can I assist with your model detections and tracking telemetry today?"
        else:
            return "I monitor model pipeline health, explain tracking architecture, and diagnose camera connectivity. Try using the quick chips above!"

    def _append_chat(self, sender, message):
        self.chat_area.config(state=tk.NORMAL)
        if sender == "You":
            self.chat_area.insert(tk.END, f"\n🧑 You:\n{message}\n")
        else:
            self.chat_area.insert(tk.END, f"\n🤖 TrackBot:\n{message}\n")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _update_clock(self):
        now = datetime.now().strftime("%d %b %Y | %H:%M:%S")
        self.lbl_system_clock.config(text=now)
        self.root.after(1000, self._update_clock)

    def close_app(self):
        self.stop_tracking()
        self.root.destroy()

if __name__ == "__main__":
    app_root = tk.Tk()
    app = ProObjectTrackerApp(app_root)
    app_root.protocol("WM_DELETE_WINDOW", app.close_app)
    app_root.mainloop()