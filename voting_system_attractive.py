
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import hashlib

# Connect to DB (creates file if not exists)
conn = sqlite3.connect("voting.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    fingerprint TEXT UNIQUE,
    has_voted INTEGER DEFAULT 0
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE COLLATE BINARY,
    votes INTEGER DEFAULT 0
)
""")
conn.commit()

# Colors
BG_COLOR = "#f0f8ff"
BTN_COLOR = "#007acc"
BTN_TEXT_COLOR = "white"

# Admin Panel
def open_admin_panel():
    admin = tk.Toplevel(root)
    admin.title("Admin Panel")
    admin.geometry("350x350")
    admin.configure(bg=BG_COLOR)

    def add_candidate():
        name = simpledialog.askstring("Input", "Enter candidate name (Case Sensitive):")
        if name:
            try:
                cursor.execute("INSERT INTO candidates (name) VALUES (?)", (name,))
                conn.commit()
                messagebox.showinfo("Success", f"Candidate '{name}' added!")
            except sqlite3.IntegrityError:
                messagebox.showwarning("Duplicate", f"Candidate '{name}' already exists!")

    def remove_candidate():
        name = simpledialog.askstring("Input", "Enter EXACT name of candidate to remove:")
        if name:
            cursor.execute("SELECT id FROM candidates WHERE name=?", (name,))
            if cursor.fetchone():
                cursor.execute("DELETE FROM candidates WHERE name=?", (name,))
                conn.commit()
                messagebox.showinfo("Removed", f"Candidate '{name}' has been removed.")
            else:
                messagebox.showerror("Not Found", f"No candidate found with name '{name}'.")

    def register_voter():
        name = simpledialog.askstring("Input", "Enter voter's name:")
        fake_fingerprint = simpledialog.askstring("Input", "Enter fingerprint (like password):")
        if name and fake_fingerprint:
            fingerprint_hash = hashlib.sha256(fake_fingerprint.encode()).hexdigest()
            try:
                cursor.execute("INSERT INTO voters (name, fingerprint) VALUES (?, ?)", (name, fingerprint_hash))
                conn.commit()
                messagebox.showinfo("Success", f"Voter '{name}' registered!")
            except sqlite3.IntegrityError:
                messagebox.showwarning("Duplicate", "Fingerprint already registered!")

    tk.Button(admin, text="Add Candidate", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, width=30, command=add_candidate).pack(pady=10)
    tk.Button(admin, text="Remove Candidate", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, width=30, command=remove_candidate).pack(pady=10)
    tk.Button(admin, text="Register Voter", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, width=30, command=register_voter).pack(pady=10)

# Voting Panel
def open_voting_panel():
    voting = tk.Toplevel(root)
    voting.title("Voting Panel")
    voting.geometry("350x250")
    voting.configure(bg=BG_COLOR)

    def scan_fingerprint():
        fake_fp = simpledialog.askstring("Scan", "Enter your fingerprint (password):")
        if fake_fp:
            fingerprint_hash = hashlib.sha256(fake_fp.encode()).hexdigest()
            cursor.execute("SELECT id, name, has_voted FROM voters WHERE fingerprint=?", (fingerprint_hash,))
            result = cursor.fetchone()
            if result:
                voter_id, voter_name, has_voted = result
                if has_voted:
                    messagebox.showinfo("Denied", f"{voter_name}, you have already voted!")
                else:
                    vote_screen(voter_id, voter_name)
            else:
                messagebox.showerror("Error", "Fingerprint not recognized!")

    def vote_screen(voter_id, voter_name):
        vote_win = tk.Toplevel(voting)
        vote_win.title(f"Vote - {voter_name}")
        vote_win.geometry("350x350")
        vote_win.configure(bg=BG_COLOR)

        tk.Label(vote_win, text=f"Welcome, {voter_name}!\nSelect your candidate:", bg=BG_COLOR, font=("Arial", 12)).pack(pady=10)

        cursor.execute("SELECT id, name FROM candidates")
        candidates = cursor.fetchall()

        def cast_vote(candidate_id):
            cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE id=?", (candidate_id,))
            cursor.execute("UPDATE voters SET has_voted = 1 WHERE id=?", (voter_id,))
            conn.commit()
            messagebox.showinfo("Success", "Your vote has been cast!")
            vote_win.destroy()
            voting.destroy()

        for cid, cname in candidates:
            tk.Button(vote_win, text=cname, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, width=30,
                      command=lambda cid=cid: cast_vote(cid)).pack(pady=5)

    tk.Button(voting, text="Scan Fingerprint", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, width=30, command=scan_fingerprint).pack(pady=50)

# Results Panel
def open_result_panel():
    result = tk.Toplevel(root)
    result.title("Voting Results")
    result.geometry("350x350")
    result.configure(bg=BG_COLOR)

    tk.Label(result, text="Election Results", font=('Arial', 14, 'bold'), bg=BG_COLOR).pack(pady=10)

    cursor.execute("SELECT name, votes FROM candidates")
    rows = cursor.fetchall()

    for name, votes in rows:
        tk.Label(result, text=f"{name}: {votes} votes", font=('Arial', 12), bg=BG_COLOR).pack(pady=5)

# Main App Window
root = tk.Tk()
root.title("Simulated Fingerprint Voting System")
root.geometry("400x350")
root.configure(bg=BG_COLOR)

tk.Label(root, text="Welcome to Voting System", font=('Arial', 16, 'bold'), bg=BG_COLOR, fg="#333").pack(pady=20)
tk.Button(root, text="Admin Panel", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, width=30, height=2, command=open_admin_panel).pack(pady=10)
tk.Button(root, text="Voting Panel", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, width=30, height=2, command=open_voting_panel).pack(pady=10)
tk.Button(root, text="View Results", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, width=30, height=2, command=open_result_panel).pack(pady=10)

root.mainloop()
