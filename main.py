# Tkinter → membuat GUI
import tkinter as tk
from tkinter import ttk, messagebox

# Import class & fungsi dari logic.py (backend)
from logic import (
    Queue, Account, VaultManager, get_master_password, update_master_password
)


# KONFIGURASI WARNA TEMA
PAGE_BG = "#E0F7FA"
DASHBOARD_BG = "#EBD4FF"
CARD_BG = "#E5CCFF"
TREE_BG = "#DAB6FF"
TITLE_FG = "#2E1A47"


# MODERN CUSTOM BUTTON (ROUND CORNERS)
def rounded_button(parent, text, command, fill_color="#00BCD4"):

    # Membuat tombol berbentuk rounded rectangle menggunakan Canvas.
    canvas = tk.Canvas(parent, width=200, height=40,
                       bg=parent["bg"] if "bg" in parent.keys() else PAGE_BG,
                       highlightthickness=0)

    # Koordinat dan radius
    x1, y1, x2, y2, r = 10, 5, 190, 35, 8

    # Membentuk sisi + sudut oval
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill_color, outline=fill_color, tags=("btn",))
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill_color, outline=fill_color, tags=("btn",))
    canvas.create_oval(x1, y1, x1 + 2 * r, y1 + 2 * r, fill=fill_color, outline=fill_color, tags=("btn",))
    canvas.create_oval(x2 - 2 * r, y1, x2, y1 + 2 * r, fill=fill_color, outline=fill_color, tags=("btn",))
    canvas.create_oval(x1, y2 - 2 * r, x1 + 2 * r, y2, fill=fill_color, outline=fill_color, tags=("btn",))
    canvas.create_oval(x2 - 2 * r, y2 - 2 * r, x2, y2, fill=fill_color, outline=fill_color, tags=("btn",))

    # Text pada tombol
    canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                       text=text, fill="white", font=("Segoe UI", 10, "bold"), tags=("btn",))

    # Bind event klik
    canvas.tag_bind("btn", "<Button-1>", lambda e: command())
    return canvas


# LOGIN WINDOW → Halaman Masuk Awal
class LoginWindow(tk.Frame):
    # Halaman login untuk memasukkan master password.Terdapat gradient background + card login.
    def __init__(self, master, login_queue, switch_page):
        super().__init__(master)
        self.switch_page = switch_page
        self.queue = login_queue

        # Area gradient
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        # Card login pusat
        self.card = tk.Frame(self.canvas, bg="#E0CCFF", bd=5,
                             highlightbackground="#bfc8d8", highlightthickness=1)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=300, height=200)
        self.card.pack_propagate(False)

        # Judul
        tk.Label(self.card, text="🔐 Simple Password Vault",
                 bg="#E0CCFF", fg="#2E1A47", font=("Segoe UI", 14, "bold")).pack(pady=(20, 15))

        # Input master password
        tk.Label(self.card, text="Master Password:",
                 bg="#E0CCFF", fg="#2E1A47", font=("Segoe UI", 11)).pack(pady=(0, 5))

        self.entry = ttk.Entry(self.card, show="*", font=("Segoe UI", 12))
        self.entry.pack(pady=(0, 15), padx=30, fill="x")
        self.entry.bind("<Return>", lambda e: self.check())

        ttk.Button(self.card, text="LOGIN", command=self.check).pack(pady=(0, 20), ipadx=10, ipady=5)
        self.entry.focus_set()

    # Gradient background
    def draw_gradient(self, width, height):
        self.canvas.delete("gradient")
        # Warna gradasi ungu → pink
        r1, g1, b1 = (64, 0, 128)
        r2, g2, b2 = (255, 0, 255)

        for i in range(height):
            r = int(r1 + (r2 - r1) * i / max(1, height))
            g = int(g1 + (g2 - g1) * i / max(1, height))
            b = int(b1 + (b2 - b1) * i / max(1, height)) 
            color = f"#{r:02x}{g:02x}{b:02x}"

            self.canvas.create_line(0, i, width, i, fill=color, tags="gradient")

    # Resize event → menyesuaikan gradient + card
    def on_resize(self, event):
        self.draw_gradient(event.width, event.height)
        w = max(event.width * 0.3, 300)
        h = max(event.height * 0.2, 200)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=w, height=h)

    # Validasi master password
    def check(self):
        pw = self.entry.get().strip()
        if pw == get_master_password():
            self.queue.enqueue("Login berhasil")
            self.switch_page("main")
        else:
            messagebox.showerror("Error", "Master Password salah!")



# DASHBOARD PAGE → Halaman utama setelah login
class MainApp(tk.Frame):
    """
    Dashboard utama:
    - menampilkan list akun
    - tombol tambah, hapus, lihat password
    - log aktivitas
    - ubah master password
    """

    def __init__(self, master, vault, login_queue):
        super().__init__(master)
        self.vault = vault
        self.login_queue = login_queue

        # Layout grid
        self.configure(bg=DASHBOARD_BG)
        self.switch_page = master.switch
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Judul dashboard
        tk.Label(self, text="🔑 Password Vault Dashboard",
                 bg=DASHBOARD_BG, fg=TITLE_FG, font=("Segoe UI", 16, "bold")
                 ).grid(row=0, column=0, pady=(10, 0), sticky="ew")

        # Card daftar akun
        card = tk.Frame(self, bg=CARD_BG, bd=0,
                        highlightbackground="#C59CFF", highlightthickness=1)
        card.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")

        tk.Label(card, text="Daftar Akun",
                 bg=CARD_BG, fg=TITLE_FG, font=("Segoe UI", 12, "bold")).pack(pady=5)

        # Treeview daftar akun
        tree_frame = tk.Frame(card, bg=CARD_BG)
        tree_frame.pack(pady=5, padx=10, fill="both", expand=True)

        style = ttk.Style()
        style.configure("Dashboard.Treeview",
                        background=TREE_BG,
                        fieldbackground=TREE_BG,
                        foreground="#000")
        style.configure("Dashboard.Treeview.Heading",
                        font=('Segoe UI', 10, 'bold'),
                        background="#A45BFF",
                        foreground='white')
        style.map("Dashboard.Treeview", background=[('selected', '#B57BFF')])

        self.tree = ttk.Treeview(tree_frame,
                                 columns=("platform", "username"),
                                 show="headings",
                                 height=8,
                                 style="Dashboard.Treeview")
        self.tree.heading("platform", text="Platform")
        self.tree.heading("username", text="Username")
        self.tree.column("platform", width=100, anchor="w")
        self.tree.column("username", width=150, anchor="w")
        self.tree.pack(side='left', fill="both", expand=True)

        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        # Tombol aksi
        btn_container = tk.Frame(self, bg=DASHBOARD_BG)
        btn_container.grid(row=2, column=0, pady=(0, 5), sticky="ew")
        btn_frame = tk.Frame(btn_container, bg=DASHBOARD_BG)
        btn_frame.pack()

        rounded_button(btn_frame, "Tambah Akun", self.add_account,
                       fill_color="#7D3CFF").pack(pady=5)
        rounded_button(btn_frame, "Show Password", self.show_password,
                       fill_color="#7D3CFF").pack(pady=5)
        rounded_button(btn_frame, "Hapus Akun", self.delete_account,
                       fill_color="#7D3CFF").pack(pady=5)
        rounded_button(btn_frame, "Activity Log", self.show_logs,
                       fill_color="#7D3CFF").pack(pady=5)
        rounded_button(btn_frame, "Ubah Master Password", self.change_master_password,
                       fill_color="#7D3CFF").pack(pady=5)

        # Tombol Logout
        logout_container = tk.Frame(self, bg=DASHBOARD_BG)
        logout_container.grid(row=3, column=0, pady=(5, 20))
        rounded_button(logout_container, "Logout",
                       self.logout, fill_color="#FF5722").pack()

        self.refresh()

    # Refresh daftar akun di treeview
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for acc in self.vault.get_all_accounts():
            self.tree.insert("", "end",
                             values=(acc.get_platform(), acc.get_username()))

    # CRUD: Tambah akun
    def add_account(self):
        """
        Form tambah akun baru (Toplevel window).
        """

        win = tk.Toplevel(self)
        win.title("Tambah Akun Baru")
        win.configure(bg=DASHBOARD_BG)
        win.geometry("350x300")
        win.resizable(False, False)
        win.grab_set()
        win.transient(self.master)

        frame = tk.Frame(win, bg=DASHBOARD_BG)
        frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(frame, text="Platform (e.g., Google, Twitter)",
                 bg=DASHBOARD_BG, fg=TITLE_FG).pack(pady=(5, 0), anchor='w')
        e1 = ttk.Entry(frame)
        e1.pack(fill="x", pady=2)

        tk.Label(frame, text="Username/Email",
                 bg=DASHBOARD_BG, fg=TITLE_FG).pack(pady=(5, 0), anchor='w')
        e2 = ttk.Entry(frame)
        e2.pack(fill="x", pady=2)

        tk.Label(frame, text="Password",
                 bg=DASHBOARD_BG, fg=TITLE_FG).pack(pady=(5, 0), anchor='w')
        e3 = ttk.Entry(frame, show="*")
        e3.pack(fill="x", pady=2)

        def save():
            platform = e1.get().strip()
            username = e2.get().strip()
            password = e3.get()
            if not (platform and username and password):
                return messagebox.showerror("Error", "Semua kolom harus diisi!")
            self.vault.add(Account(platform, username, password))
            self.login_queue.enqueue(f"Tambah akun: {platform} ({username})")
            self.refresh()
            win.destroy()

        ttk.Button(frame, text="Save Account", command=save).pack(pady=10, side='right')
        ttk.Button(frame, text="Cancel", command=win.destroy).pack(pady=10, side='left')
        win.wait_window()

    # Show password
    def show_password(self):
        item = self.tree.selection()
        if not item:
            return messagebox.showerror("Error", "Pilih akun dulu!")

        index = self.tree.index(item)
        acc = self.vault.get_account(index)

        self.login_queue.enqueue(f"Lihat password: {acc.get_platform()} ({acc.get_username()})")


        messagebox.showinfo("Password",
                            f"Platform: {acc.get_platform()}\n"
                            f"Username: {acc.get_username()}\n\n"
                            f"Password: {acc.get_password()}")
    
    # Hapus akun
    def delete_account(self):
        item = self.tree.selection()
        if not item:
            return messagebox.showerror("Error", "Pilih akun dulu!")

        index = self.tree.index(item)
        acc = self.vault.get_account(index)

        if messagebox.askyesno("Konfirmasi",
                               f"Yakin ingin menghapus {acc.get_platform()} ({acc.get_username()})?"):
            self.login_queue.enqueue(f"Hapus akun: {acc.get_platform()} ({acc.get_username()})")
            self.vault.delete(index)
            self.refresh()

    # Log aktivitas
    def show_logs(self):
        logs = self.login_queue.get_all()
        msg = "--- Activity Log (max 10) ---\n" + "\n".join(logs)
        messagebox.showinfo("Login Log", msg)

    # Logout
    def logout(self):
        self.login_queue.enqueue("Logout pengguna")
        messagebox.showinfo("Logout", "Anda telah keluar.")
        self.switch_page("login")

    # Ubah master password
    def change_master_password(self):
        win = tk.Toplevel(self)
        win.title("Ubah Master Password")
        win.configure(bg=DASHBOARD_BG)
        win.geometry("350x250")
        win.resizable(False, False)
        win.grab_set()

        frame = tk.Frame(win, bg=DASHBOARD_BG)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(frame, text="Password Lama:", bg=DASHBOARD_BG, fg=TITLE_FG).pack(anchor="w")
        old_entry = ttk.Entry(frame, show="*")
        old_entry.pack(fill="x", pady=5)

        tk.Label(frame, text="Password Baru:", bg=DASHBOARD_BG, fg=TITLE_FG).pack(anchor="w")
        new_entry = ttk.Entry(frame, show="*")
        new_entry.pack(fill="x", pady=5)

        def update_pw():
            old = old_entry.get().strip()
            new = new_entry.get().strip()

            ok, msg = update_master_password(old, new)

            if ok:
                messagebox.showinfo("Sukses", msg)
                self.login_queue.enqueue("Master password diperbarui")
                win.destroy()
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(frame, text="Update", command=update_pw).pack(pady=10)



# MAIN WINDOW → Frame utama yang mengatur halaman login & dashboard
class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Vault Modern UI")
        self.geometry("800x600")
        self.configure(bg=PAGE_BG)

        style = ttk.Style(self)
        style.theme_use("clam")

        # Queue log dan vault akun
        self.login_queue = Queue()
        self.vault = VaultManager()

        # Tambah 2 akun demo
        self.vault.add(Account("DemoApp", "user_demo", "password123"))
        self.vault.add(Account("SocialMedia", "jane_doe", "mysecretpwd"))

        # Halaman
        self.pages = {
            "login": LoginWindow(self, self.login_queue, self.switch),
            "main": MainApp(self, self.vault, self.login_queue)
        }

        self.pages["login"].pack(fill="both", expand=True)

    def switch(self, name):
        """
        Mengganti halaman antara login <-> dashboard.
        """
        for p in self.pages.values():
            p.pack_forget()
        self.pages[name].pack(fill="both", expand=True)


# RUN PROGRAM
if __name__ == "__main__":
    Window().mainloop()