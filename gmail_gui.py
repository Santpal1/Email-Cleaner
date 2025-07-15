import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from main import authenticate_and_build_service as authenticate
from main import get_top_senders, delete_from_sender
import threading


class ModernGmailCleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gmail Cleaner Pro")
        self.root.geometry("800x900")
        self.root.resizable(True, True)
        
        # Modern color scheme
        self.colors = {
            'bg_primary': '#0d1117',
            'bg_secondary': '#21262d',
            'bg_tertiary': '#30363d',
            'bg_card': '#161b22',
            'accent': '#238636',
            'accent_hover': '#2ea043',
            'accent_secondary': '#1f6feb',
            'accent_secondary_hover': '#409eff',
            'danger': '#da3633',
            'danger_hover': '#f85149',
            'text_primary': '#f0f6fc',
            'text_secondary': '#8b949e',
            'text_muted': '#6e7681',
            'border': '#30363d',
            'border_muted': '#21262d'
        }
        
        self.service = None
        self.senders = []
        
        self.setup_ui()

    def create_modern_button(self, parent, text, command, bg_color, hover_color, width=200, height=50):
        """Create a modern flat button with hover effects"""
        button_frame = tk.Frame(parent, bg=bg_color, height=height, width=width)
        button_frame.pack_propagate(False)
        
        button = tk.Button(
            button_frame,
            text=text,
            command=command,
            bg=bg_color,
            fg=self.colors['text_primary'],
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            borderwidth=0,
            cursor='hand2',
            activebackground=hover_color,
            activeforeground=self.colors['text_primary']
        )
        button.pack(fill='both', expand=True)
        
        # Hover effects
        def on_enter(e):
            button.config(bg=hover_color)
        
        def on_leave(e):
            button.config(bg=bg_color)
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        return button_frame, button

    def create_modern_entry(self, parent, placeholder="", width=200):
        """Create a modern entry field"""
        entry_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'], height=40)
        entry_frame.pack_propagate(False)
        
        entry = tk.Entry(
            entry_frame,
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 10),
            relief='flat',
            borderwidth=0,
            insertbackground=self.colors['text_primary']
        )
        entry.pack(fill='both', expand=True, padx=12, pady=8)
        
        # Placeholder functionality
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=self.colors['text_muted'])
            
            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=self.colors['text_primary'])
            
            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=self.colors['text_muted'])
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
        
        return entry_frame, entry

    def create_modern_spinbox(self, parent, from_=1, to=100, initial=10, width=80):
        """Create a modern spinbox"""
        spinbox_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'], height=40, width=width)
        spinbox_frame.pack_propagate(False)
        
        spinbox = tk.Spinbox(
            spinbox_frame,
            from_=from_,
            to=to,
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 10),
            relief='flat',
            borderwidth=0,
            insertbackground=self.colors['text_primary'],
            buttonbackground=self.colors['bg_secondary'],
            activebackground=self.colors['accent_secondary']
        )
        spinbox.delete(0, tk.END)
        spinbox.insert(0, str(initial))
        spinbox.pack(fill='both', expand=True, padx=12, pady=8)
        
        return spinbox_frame, spinbox

    def create_modern_progress_bar(self, parent, width=600, height=8):
        """Create a modern progress bar"""
        progress_frame = tk.Frame(parent, bg=self.colors['bg_primary'], height=height + 20)
        progress_frame.pack_propagate(False)
        
        # Background bar
        bg_bar = tk.Frame(progress_frame, bg=self.colors['bg_tertiary'], height=height)
        bg_bar.pack(fill='x', pady=10)
        
        # Progress bar
        progress_bar = tk.Frame(bg_bar, bg=self.colors['accent'], height=height)
        progress_bar.place(x=0, y=0, relheight=1, width=0)
        
        def update_progress(current, total):
            if total > 0:
                width = int((current / total) * bg_bar.winfo_width())
                progress_bar.place(width=width)
            self.root.update_idletasks()
        
        progress_frame.update_progress = update_progress
        return progress_frame

    def setup_ui(self):
        # Set window background
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Create main scrollable frame
        main_canvas = tk.Canvas(self.root, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Make main canvas and scrollbar use pack (do not mix grid and pack in self.root)
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Content frame with fixed max width, directly in canvas
        max_content_width = 700
        content_frame = tk.Frame(main_canvas, bg=self.colors['bg_primary'])
        window_id = main_canvas.create_window((main_canvas.winfo_width() // 2, 0), window=content_frame, anchor='n', width=max_content_width)

        def center_and_resize_content(event):
            canvas_width = event.width
            # Responsive width: max 700px or canvas width minus 40px margin
            new_width = min(max_content_width, canvas_width - 40)
            main_canvas.itemconfig(window_id, width=new_width)
            main_canvas.coords(window_id, canvas_width // 2, 0)

        main_canvas.bind('<Configure>', center_and_resize_content)

        # Header Section
        header_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill='x', pady=(30, 40))

        # Logo/Title
        title_label = tk.Label(
            header_frame,
            text="Gmail Cleaner Pro",
            font=('Segoe UI', 28, 'bold'),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="Scan your inbox, filter by sender, keyword, or date, and clean up in bulk!",
            font=('Segoe UI', 12),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary']
        )
        subtitle_label.pack(pady=(5, 0))

        # Filters Card
        filters_card = tk.Frame(content_frame, bg=self.colors['bg_card'], relief='flat')
        filters_card.pack(fill='x', padx=40, pady=(0, 30))

        # Card header
        card_header = tk.Frame(filters_card, bg=self.colors['bg_card'])
        card_header.pack(fill='x', pady=(20, 10))
        
        tk.Label(
            card_header,
            text="🎛️ Filter Options",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).pack(anchor='w', padx=30)
        
        # Filters content
        filters_content = tk.Frame(filters_card, bg=self.colors['bg_card'])
        filters_content.pack(fill='x', padx=30, pady=(0, 30))
        
        # Row 1: Top N and Keyword
        row1 = tk.Frame(filters_content, bg=self.colors['bg_card'])
        row1.pack(fill='x', pady=(0, 20))
        
        # Top N Senders
        top_n_container = tk.Frame(row1, bg=self.colors['bg_card'])
        top_n_container.pack(side='left', padx=(0, 40))
        
        tk.Label(
            top_n_container,
            text="Top N Senders",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        self.top_n_frame, self.top_n_spinbox = self.create_modern_spinbox(
            top_n_container, from_=1, to=50, initial=10, width=100
        )
        self.top_n_frame.pack(anchor='w')
        
        # Keyword
        keyword_container = tk.Frame(row1, bg=self.colors['bg_card'])
        keyword_container.pack(side='left')
        
        tk.Label(
            keyword_container,
            text="Keyword Filter",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        self.keyword_frame, self.keyword_entry = self.create_modern_entry(
            keyword_container, placeholder="Enter keyword...", width=250
        )
        self.keyword_frame.pack(anchor='w')
        
        # Row 2: Older Than
        row2 = tk.Frame(filters_content, bg=self.colors['bg_card'])
        row2.pack(fill='x', pady=(0, 20))
        
        older_than_container = tk.Frame(row2, bg=self.colors['bg_card'])
        older_than_container.pack(side='left')
        
        tk.Label(
            older_than_container,
            text="Older Than (days)",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        self.older_than_frame, self.older_than_spinbox = self.create_modern_spinbox(
            older_than_container, from_=1, to=3650, initial=30, width=100
        )
        self.older_than_frame.pack(anchor='w')
        
        # Row 3: Date Range
        row3 = tk.Frame(filters_content, bg=self.colors['bg_card'])
        row3.pack(fill='x')
        
        # After Date
        after_container = tk.Frame(row3, bg=self.colors['bg_card'])
        after_container.pack(side='left', padx=(0, 40))
        
        tk.Label(
            after_container,
            text="After Date",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        self.after_frame, self.after_entry = self.create_modern_entry(
            after_container, placeholder="YYYY/MM/DD", width=150
        )
        self.after_frame.pack(anchor='w')
        
        # Before Date
        before_container = tk.Frame(row3, bg=self.colors['bg_card'])
        before_container.pack(side='left')
        
        tk.Label(
            before_container,
            text="Before Date",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        self.before_frame, self.before_entry = self.create_modern_entry(
            before_container, placeholder="YYYY/MM/DD", width=150
        )
        self.before_frame.pack(anchor='w')
        
        # Scan Section
        scan_section = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        scan_section.pack(fill='x', pady=(0, 30))
        
        self.scan_button_frame, self.scan_button = self.create_modern_button(
            scan_section, "🔍 Scan Top Senders", self.start_scan_thread,
            self.colors['accent'], self.colors['accent_hover'], width=250, height=50
        )
        self.scan_button_frame.pack()
        
        # Scan Progress
        self.scan_progress_frame = self.create_modern_progress_bar(scan_section, width=600)
        self.scan_progress_frame.pack(pady=(20, 0))
        
        # Senders Selection Card
        senders_card = tk.Frame(content_frame, bg=self.colors['bg_card'], relief='flat')
        senders_card.pack(fill='x', padx=40, pady=(0, 30))
        
        # Card header
        senders_header = tk.Frame(senders_card, bg=self.colors['bg_card'])
        senders_header.pack(fill='x', pady=(20, 10))
        
        tk.Label(
            senders_header,
            text="👥 Select Senders to Delete From",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).pack(anchor='w', padx=30)
        
        # Senders list
        senders_container = tk.Frame(senders_card, bg=self.colors['bg_card'])
        senders_container.pack(fill='both', expand=True, padx=30, pady=(0, 30))
        
        # Scrollable senders list
        self.senders_canvas = tk.Canvas(
            senders_container,
            bg=self.colors['bg_secondary'],
            height=200,
            highlightthickness=0
        )
        self.senders_scrollbar = ttk.Scrollbar(
            senders_container,
            orient="vertical",
            command=self.senders_canvas.yview
        )
        self.senders_scrollable_frame = tk.Frame(self.senders_canvas, bg=self.colors['bg_secondary'])
        
        self.senders_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.senders_canvas.configure(scrollregion=self.senders_canvas.bbox("all"))
        )
        
        self.senders_canvas.create_window((0, 0), window=self.senders_scrollable_frame, anchor="nw")
        self.senders_canvas.configure(yscrollcommand=self.senders_scrollbar.set)
        
        self.senders_canvas.pack(side="left", fill="both", expand=True)
        self.senders_scrollbar.pack(side="right", fill="y")
        
        self.check_vars = []
        
        # Delete Section
        delete_section = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        delete_section.pack(fill='x', pady=(0, 30))
        
        self.delete_button_frame, self.delete_button = self.create_modern_button(
            delete_section, "🗑️ Delete Selected Emails", self.start_delete_thread,
            self.colors['danger'], self.colors['danger_hover'], width=250, height=50
        )
        self.delete_button_frame.pack()
        
        # Delete Progress
        self.delete_progress_frame = self.create_modern_progress_bar(delete_section, width=600)
        self.delete_progress_frame.pack(pady=(20, 0))
        
        # Activity Log Card
        log_card = tk.Frame(content_frame, bg=self.colors['bg_card'], relief='flat')
        log_card.pack(fill='both', expand=True, padx=40, pady=(0, 40))
        
        # Card header
        log_header = tk.Frame(log_card, bg=self.colors['bg_card'])
        log_header.pack(fill='x', pady=(20, 10))
        
        tk.Label(
            log_header,
            text="📋 Activity Log",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).pack(anchor='w', padx=30)
        
        # Log content
        log_container = tk.Frame(log_card, bg=self.colors['bg_card'])
        log_container.pack(fill='both', expand=True, padx=30, pady=(0, 30))
        
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            height=12,
            state="disabled",
            wrap=tk.WORD,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('Consolas', 10),
            borderwidth=0,
            insertbackground=self.colors['text_primary']
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Pack scrollable components
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind("<MouseWheel>", on_mousewheel)

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.root.update_idletasks()

    def start_scan_thread(self):
        self.scan_button.config(state='disabled')
        threading.Thread(target=self.scan_top_senders, daemon=True).start()

    def scan_top_senders(self):
        self.log("🔐 Authenticating...")
        try:
            self.service = authenticate()
        except Exception as e:
            self.log(f"❌ Authentication failed: {e}")
            self.scan_button.config(state='normal')
            return

        self.log("✅ Authenticated. Fetching top senders...")

        def scan_callback(step, total):
            self.scan_progress_frame.update_progress(step, total)

        try:
            top_n = int(self.top_n_spinbox.get())
        except:
            top_n = 10

        self.senders = get_top_senders(self.service, max_messages=1500, top_n=top_n, progress_callback=scan_callback)
        self.check_vars = []

        # Clear previous checkboxes
        for widget in self.senders_scrollable_frame.winfo_children():
            widget.destroy()

        if not self.senders:
            self.log("⚠️ No senders found.")
        else:
            for sender, count in self.senders:
                var = tk.BooleanVar()
                
                # Create modern checkbox
                checkbox_frame = tk.Frame(self.senders_scrollable_frame, bg=self.colors['bg_secondary'])
                checkbox_frame.pack(fill='x', padx=15, pady=5)
                
                cb = tk.Checkbutton(
                    checkbox_frame,
                    text=f"{sender} ({count} emails)",
                    variable=var,
                    bg=self.colors['bg_secondary'],
                    fg=self.colors['text_primary'],
                    font=('Segoe UI', 10),
                    selectcolor=self.colors['bg_tertiary'],
                    activebackground=self.colors['bg_secondary'],
                    activeforeground=self.colors['text_primary'],
                    relief='flat'
                )
                cb.pack(anchor='w', pady=5)
                
                self.check_vars.append((var, sender))

            self.log("📋 Top senders loaded.")

        self.scan_progress_frame.update_progress(0, 1)
        self.scan_button.config(state='normal')

    def start_delete_thread(self):
        self.delete_button.config(state='disabled')
        threading.Thread(target=self.delete_selected, daemon=True).start()

    def delete_selected(self):
        if not self.service:
            messagebox.showerror("Error", "Please scan top senders first.")
            self.delete_button.config(state='normal')
            return

        to_delete = [sender for var, sender in self.check_vars if var.get()]
        if not to_delete:
            messagebox.showinfo("No Selection", "Please select at least one sender.")
            self.delete_button.config(state='normal')
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete emails from {len(to_delete)} senders?")
        if not confirm:
            self.delete_button.config(state='normal')
            return

        keyword = self.keyword_entry.get().strip()
        if keyword == "Enter keyword...":
            keyword = None
        
        try:
            older_than = int(self.older_than_spinbox.get())
        except:
            older_than = None
            
        after = self.after_entry.get().strip()
        if after == "YYYY/MM/DD":
            after = None
            
        before = self.before_entry.get().strip()
        if before == "YYYY/MM/DD":
            before = None

        for sender in to_delete:
            self.log(f"🔄 Deleting from {sender}...")

            def delete_callback(step, total, _sender=sender):
                self.delete_progress_frame.update_progress(step, total)

            delete_from_sender(
                self.service,
                sender,
                log_func=self.log,
                progress_callback=delete_callback,
                keyword=keyword,
                older_than_days=older_than,
                after=after,
                before=before,
            )

        self.log("✅ Deletion completed.")
        self.delete_progress_frame.update_progress(0, 1)
        self.delete_button.config(state='normal')


if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')  # Open window maximized on Windows
    app = ModernGmailCleanerGUI(root)
    root.mainloop()