import json, os, csv, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from tkcalendar import Calendar
import datetime
import threading
import time

APP_TITLE = "Meine To-Do-Liste"
SAVE_FILE = "todo_tasks.json"
tasks = []
PRIO_COLORS = {"Niedrig": "#fff58c", "Mittel": "#ffb84d", "Hoch": "#ff6666"}

def current_date_str(): return date.today().strftime("%d/%m/%y")
def parse_date(s):
    try: d,m,y = map(int,s.split("/")); y += 2000 if y<100 else 0; return date(y,m,d)
    except: return None

def save_tasks(): open(SAVE_FILE,"w",encoding="utf-8").write(json.dumps(tasks,ensure_ascii=False,indent=2))
def load_tasks():
    if os.path.exists(SAVE_FILE):
        data=json.load(open(SAVE_FILE,"r",encoding="utf-8"))
        for t in data: t.setdefault("prio","Mittel"); t.setdefault("created",current_date_str()); t.setdefault("due",""); t.setdefault("done",False)
        tasks.extend(data)

def refresh_views():
    for v in (tree_prio, tree_data): [v.delete(i) for i in v.get_children()]
    today = date.today()
    visible_indices = []
    for i, t in enumerate(tasks):
        flt = filter_var.get()
        due = parse_date(t["due"]) if t["due"] else None
        show = (
            flt == "Alle"
            or (flt == "Offen" and not t["done"])
            or (flt == "Heute" and due == today and not t["done"])
            or (flt == "Überfällig" and due and due < today and not t["done"])
            or (flt == "Erledigt" and t["done"])
        )
        if not show:
            continue
        visible_indices.append(i)
    for row, i in enumerate(visible_indices):
        t = tasks[i]
        tag_prio = "done" if t["done"] else t["prio"]
        tree_prio.insert("", "end", iid=str(row), values=(" ",), tags=(tag_prio,))
        tag_data = "default"
        # Status: Häkchen für erledigt, "Überfällig" für überfällige offene Aufgaben, "Offen" für offene Aufgaben
        due = parse_date(t["due"]) if t["due"] else None
        if t["done"]:
            status = "✔"
        elif due and due < today:
            status = "Überfällig"
        else:
            status = "Offen"
        # Löschen-Spalte: Papierkorb-Symbol
        tree_data.insert("", "end", iid=str(row),
                         values=(row + 1, t["text"], t["created"], t["due"], status, "🗑"),
                         tags=("bold",))
    for p, c in PRIO_COLORS.items():
        tree_prio.tag_configure(p, background=c)
    tree_prio.tag_configure("done", background="#5a885a")
    tree_data.tag_configure("default", background=style.lookup("Treeview", "background"),
                            foreground=style.lookup("Treeview", "foreground"))
    tree_data.tag_configure("done", background="#355a35", foreground="white")
    tree_data.tag_configure("bold", font=("Arial", 10, "bold"))

def add_task():
    text=entry_task.get().strip(); prio=prio_var.get(); due=entry_due.get().strip()
    if not text: return messagebox.showwarning("Hinweis","Aufgabe darf nicht leer sein.")
    if due and not parse_date(due): return messagebox.showwarning("Hinweis","Datum TT/MM/JJ.")
    tasks.append({"text":text,"prio":prio,"created":current_date_str(),"due":due,"done":False})
    entry_task.delete(0,tk.END); entry_due.delete(0,tk.END)
    save_tasks(); refresh_views()

def get_visible_indices():
    visible_indices = []
    today = date.today()
    for i, t in enumerate(tasks):
        flt = filter_var.get()
        due = parse_date(t["due"]) if t["due"] else None
        show = (flt == "Alle" or (flt == "Heute" and due == today and not t["done"]) or
                (flt == "Überfällig" and due and due < today and not t["done"]) or
                (flt == "Erledigt" and t["done"]))
        if not show:
            continue
        visible_indices.append(i)
    return visible_indices

def delete_selected(idx=None):
    visible_indices = get_visible_indices()
    # idx ist der Index in der sichtbaren Liste
    idx = int(idx) if idx is not None else int(tree_data.selection()[0])
    if idx >= len(visible_indices):
        return
    real_idx = visible_indices[idx]
    if messagebox.askyesno("Löschen", f"Aufgabe '{tasks[real_idx]['text']}' löschen?"):
        tasks.pop(real_idx)
        save_tasks()
        refresh_views()

def toggle_done(event):
    row_id = tree_data.identify_row(event.y)
    if not row_id:
        return
    idx = int(row_id)
    visible_indices = get_visible_indices()
    if idx >= len(visible_indices):
        return
    real_idx = visible_indices[idx]
    col = tree_data.identify_column(event.x)
    if col == "#6":  # Spalte "Aktion" (Nr=1, Aufgabe=2, ... Aktion=6)
        delete_selected(idx)
    else:
        tasks[real_idx]["done"] = not tasks[real_idx]["done"]
        save_tasks()
        refresh_views()

def get_german_holidays(year):
    # Feste Feiertage
    holidays = {
        "Neujahr": f"{year}-01-01",
        "Tag der Arbeit": f"{year}-05-01",
        "Tag der Deutschen Einheit": f"{year}-10-03",
        "1. Weihnachtstag": f"{year}-12-25",
        "2. Weihnachtstag": f"{year}-12-26"
    }
    # Bewegliche Feiertage (Ostern, Pfingsten, etc.)
    easter = calc_easter(year)
    holidays["Karfreitag"] = (easter - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    holidays["Ostermontag"] = (easter + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    holidays["Ostersonntag"] = easter.strftime("%Y-%m-%d")
    holidays["Christi Himmelfahrt"] = (easter + datetime.timedelta(days=39)).strftime("%Y-%m-%d")
    holidays["Pfingstsonntag"] = (easter + datetime.timedelta(days=49)).strftime("%Y-%m-%d")
    holidays["Pfingstmontag"] = (easter + datetime.timedelta(days=50)).strftime("%Y-%m-%d")
    holidays["Fronleichnam"] = (easter + datetime.timedelta(days=60)).strftime("%Y-%m-%d")
    return holidays

def calc_easter(year):
    # Gaußsche Osterformel
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)

def get_theme_colors():
    theme = theme_var.get()
    if theme == "Hell":
        return {"bg": "#f0f0f0", "fg": "#000", "entry_bg": "#fff", "entry_fg": "#000"}
    elif theme == "Blau":
        return {"bg": "#dce6f9", "fg": "#000", "entry_bg": "#eef3ff", "entry_fg": "#000"}
    else:
        return {"bg": "#1e1e1e", "fg": "#fff", "entry_bg": "#2b2b2b", "entry_fg": "#fff"}

def open_calendar(event=None):
    win = tk.Toplevel(root)
    win.title("Datum wählen")
    win.geometry("350x320")  # Feste Startgröße
    c = get_theme_colors()
    win.configure(bg=c["bg"])
    theme = theme_var.get()
    if theme == "Hell":
        cal_colors = {"background": "#fff", "foreground": "#000", "selectbackground": "#ddd", "selectforeground": "#000"}
        holiday_color = "#ffcccc"
    elif theme == "Blau":
        cal_colors = {"background": "#eef3ff", "foreground": "#000", "selectbackground": "#c9d8f4", "selectforeground": "#000"}
        holiday_color = "#ffd6d6"
    else:
        cal_colors = {"background": "#2b2b2b", "foreground": "#fff", "selectbackground": "#3a3a3a", "selectforeground": "#fff"}
        holiday_color = "#a94442"
    cal = Calendar(win, date_pattern="dd/mm/yy", **cal_colors)
    cal.pack(padx=10, pady=10)
    start_year = datetime.date.today().year
    for year in range(start_year, start_year + 3):
        holidays = get_german_holidays(year)
        for name, date_str in holidays.items():
            try:
                cal.calevent_create(datetime.datetime.strptime(date_str, "%Y-%m-%d"), name, "feiertag")
            except Exception:
                pass
    cal.tag_config("feiertag", background=holiday_color, foreground="#000")
    ttk.Button(win, text="OK", command=lambda: (entry_due.delete(0, tk.END), entry_due.insert(0, cal.get_date()), win.destroy())).pack(pady=(0, 10))
    # Passe Button und Kalender-Fenster an Theme an
    for child in win.winfo_children():
        if isinstance(child, tk.Label) or isinstance(child, tk.Entry) or isinstance(child, tk.Text):
            child.configure(bg=c["bg"], fg=c["fg"])
        if isinstance(child, ttk.Button):
            style = ttk.Style()
            style.configure("TButton", background=c["bg"], foreground=c["fg"])

def export_list():
    p = filedialog.asksaveasfilename(title="Liste Speichern", defaultextension=".txt",
                                     filetypes=[("Textdatei", "*.txt"), ("Alle Dateien", "*.*")])
    if not p: return
    # Tabellenähnliche Formatierung mit festen Spaltenbreiten und Rahmen
    header = ["Nr.", "Aufgabe", "Priorität", "Erstellt am", "Fällig am", "Status"]
    widths = [5, 30, 10, 14, 14, 10]
    def fmt_row(row):
        return "| " + " | ".join(str(col).ljust(width)[:width] for col, width in zip(row, widths)) + " |"
    line = "+"+ "+".join("-"*(w+2) for w in widths) + "+"
    with open(p, "w", encoding="utf-8") as f:
        f.write(line + "\n")
        f.write(fmt_row(header) + "\n")
        f.write(line + "\n")
        for idx, t in enumerate(tasks, 1):
            status = "Erledigt" if t["done"] else ("Überfällig" if t["due"] and parse_date(t["due"]) and parse_date(t["due"]) < date.today() else "Offen")
            row = [
                idx,
                t["text"],
                t["prio"],
                t["created"],
                t["due"],
                status
            ]
            f.write(fmt_row(row) + "\n")
        f.write(line + "\n")
    messagebox.showinfo("Export", "Liste als Tabelle gespeichert.")

def apply_theme(event=None):
    theme=theme_var.get()
    if theme=="Hell": c={"bg":"#f0f0f0","fg":"#000","tree_bg":"#fff","tree_fg":"#000","head_bg":"#ddd","head_fg":"#000"}
    elif theme=="Blau": c={"bg":"#dce6f9","fg":"#000","tree_bg":"#eef3ff","tree_fg":"#000","head_bg":"#c9d8f4","head_fg":"#000"}
    else: c={"bg":"#1e1e1e","fg":"#fff","tree_bg":"#2b2b2b","tree_fg":"#fff","head_bg":"#3a3a3a","head_fg":"#fff"}

    root.configure(bg=c["bg"])
    style.configure("TFrame", background=c["bg"])
    for w in frame_main.winfo_children():
        if isinstance(w,ttk.Label): w.configure(background=c["bg"],foreground=c["fg"])
    style.configure("TEntry", fieldbackground=c["tree_bg"], foreground=c["fg"])
    style.configure("Treeview", background=c["tree_bg"], fieldbackground=c["tree_bg"],
                    foreground=c["tree_fg"], borderwidth=1, relief="solid")  # Umrandung hinzugefügt
    style.map("Treeview", background=[('selected', c["head_bg"])])
    style.configure("Treeview.Heading",background=c["head_bg"],foreground=c["head_fg"],relief="solid", font=("Arial", 10, "bold"))  # Fett und Umrandung
    # Buttons einfärben
    style.configure("TButton", background=c["head_bg"], foreground=c["head_fg"])
    style.map("TButton",
        background=[("active", c["tree_bg"]), ("!active", c["head_bg"])],
        foreground=[("active", c["tree_fg"]), ("!active", c["head_fg"])]
    )
    # Combobox einfärben
    style.configure("TCombobox", fieldbackground=c["tree_bg"], background=c["head_bg"], foreground=c["fg"])
    style.map("TCombobox",
        fieldbackground=[("readonly", c["tree_bg"])],
        background=[("readonly", c["head_bg"])],
        foreground=[("readonly", c["fg"])]
    )
    # Fett für die wichtigsten Spalten in der Tabelle
    tree_data.tag_configure("bold", font=("Arial", 10, "bold"))
    refresh_views()

def update_prio_color(*args):
    prio = prio_var.get()
    prio_color_label.config(bg=PRIO_COLORS.get(prio, "#fff"))

def check_reminders():
    while True:
        now = date.today()
        due_tasks = []
        overdue_tasks = []
        for idx, t in enumerate(tasks):
            if not t.get("done") and t.get("due"):
                due = parse_date(t["due"])
                if due == now:
                    nr = idx + 1
                    due_tasks.append(f"{nr}. {t['text']} (Fällig: {t['due']})")
                elif due and due < now:
                    nr = idx + 1
                    overdue_tasks.append(f"{nr}. {t['text']} (Überfällig seit: {t['due']})")
        if due_tasks or overdue_tasks:
            def show_due_window():
                c = get_theme_colors()
                win = tk.Toplevel(root)
                win.title("Fällige Aufgaben heute")
                win.geometry("420x380")
                win.configure(bg=c["bg"])
                tk.Label(win, text="Diese Aufgaben sind heute fällig:", font=("Arial", 12, "bold"), bg=c["bg"], fg=c["fg"]).pack(pady=10)
                txt = tk.Text(win, wrap="word", height=14, bg=c["entry_bg"], fg=c["entry_fg"])
                txt.pack(fill="both", expand=True, padx=10, pady=10)
                if due_tasks:
                    txt.insert("end", "\n".join(due_tasks) + "\n\n")
                if overdue_tasks:
                    txt.insert("end", "Überfällige Aufgaben:\n", "overdue_title")
                    for line in overdue_tasks:
                        txt.insert("end", line + "\n", "overdue")
                txt.config(state="disabled")
                txt.tag_configure("overdue_title", foreground="#b22222", font=("Arial", 10, "bold"))
                txt.tag_configure("overdue", foreground="#b22222", font=("Arial", 10, "bold"))
                ttk.Button(win, text="OK", command=win.destroy).pack(pady=10)
                style = ttk.Style()
                style.configure("TButton", background=c["bg"], foreground=c["fg"])
            root.after(0, show_due_window)
        time.sleep(3600)  # prüfe jede Stunde

def start_reminder_thread():
    thread = threading.Thread(target=check_reminders, daemon=True)
    thread.start()

root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1000x540")
style = ttk.Style()
style.theme_use("clam")

frame_main = ttk.Frame(root)
frame_main.pack(fill=tk.X, padx=10, pady=10)
entry_task = ttk.Entry(frame_main)
entry_task.grid(row=0, column=0, padx=(0,8), sticky="ew")
prio_var = tk.StringVar(value="Mittel")
prio_cb = ttk.Combobox(frame_main, textvariable=prio_var, values=list(PRIO_COLORS.keys()), width=10, state="readonly")
prio_cb.grid(row=0, column=1, padx=(4,0))
# Farbakzent-Label neben der Combobox
prio_color_label = tk.Label(frame_main, width=2, height=1, bg=PRIO_COLORS[prio_var.get()], relief="ridge")
prio_color_label.grid(row=0, column=2, padx=(2,8))
prio_var.trace_add("write", update_prio_color)
entry_due = ttk.Entry(frame_main, width=12)
entry_due.grid(row=0, column=3, padx=4)
entry_due.bind("<Button-1>", open_calendar)
ttk.Button(frame_main, text="Hinzufügen", command=add_task).grid(row=0, column=4, padx=8)
ttk.Label(frame_main, text="Aufgabe").grid(row=1, column=0, sticky="w")
ttk.Label(frame_main, text="Priorität").grid(row=1, column=1, sticky="w")
ttk.Label(frame_main, text="Fälligkeitsdatum").grid(row=1, column=3, sticky="w")
frame_main.columnconfigure(0, weight=1)

frame_list = ttk.Frame(root)
frame_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

# Neue Spalte "Nr." für die Nummerierung in tree_data
tree_prio = ttk.Treeview(frame_list, columns=("color",), show="headings", height=15)
tree_prio.heading("color", text="Priorität")
tree_prio.column("color", width=80, anchor="center")
tree_prio.pack(side=tk.LEFT, fill=tk.Y)

# Passe die Spaltenüberschriften und Reihenfolge in tree_data an:
tree_data = ttk.Treeview(frame_list, columns=("nr", "task", "created", "due", "status", "delete"), show="headings")
for t, h, w in [
    ("nr", "Nr.", 40),
    ("task", "Aufgabe", 340),
    ("created", "Erstellt am", 120),
    ("due", "Fällig am", 100),
    ("status", "Status", 60),
    ("delete", "Aktion", 60)  # Spalte für Löschen wieder hinzugefügt
]:
    tree_data.heading(t, text=h)
    tree_data.column(t, width=w, anchor="center" if t != "task" else "w")
tree_data.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll=ttk.Scrollbar(frame_list,orient="vertical",command=lambda *a:(tree_prio.yview(*a),tree_data.yview(*a)))
scroll.pack(side=tk.RIGHT,fill=tk.Y)
tree_prio.configure(yscrollcommand=scroll.set); tree_data.configure(yscrollcommand=scroll.set)
tree_data.bind("<Button-1>", toggle_done)

frame_bottom = ttk.Frame(root)
frame_bottom.pack(fill=tk.X, padx=10, pady=(0,10))

# Filter alphabetisch sortieren
filter_options = sorted(["Alle", "Offen", "Heute", "Überfällig", "Erledigt"])
filter_var = tk.StringVar(value="Alle")
filter_cb = ttk.Combobox(
    frame_bottom,
    textvariable=filter_var,
    values=filter_options,
    width=12,
    state="readonly"
)
filter_cb.grid(row=0, column=0, padx=(0,8))
filter_cb.bind("<<ComboboxSelected>>", lambda e: refresh_views())
theme_var=tk.StringVar(value="Dunkel")
theme_cb=ttk.Combobox(frame_bottom,textvariable=theme_var,values=["Hell","Dunkel","Blau"],width=14,state="readonly")
theme_cb.grid(row=0,column=1,padx=8); theme_cb.bind("<<ComboboxSelected>>",apply_theme)
ttk.Button(frame_bottom,text="Liste Speichern",command=export_list).grid(row=0,column=2,padx=8)

def edit_task(idx):
    t = tasks[idx]
    c = get_theme_colors()
    edit_win = tk.Toplevel(root)
    edit_win.title("Aufgabe bearbeiten")
    edit_win.geometry("350x220")  # Feste Startgröße
    edit_win.configure(bg=c["bg"])
    tk.Label(edit_win, text="Aufgabe:", bg=c["bg"], fg=c["fg"]).pack(anchor="w", padx=10, pady=(10,0))
    entry_text = tk.Entry(edit_win, bg=c["entry_bg"], fg=c["entry_fg"])
    entry_text.pack(fill="x", padx=10)
    entry_text.insert(0, t["text"])
    tk.Label(edit_win, text="Priorität:", bg=c["bg"], fg=c["fg"]).pack(anchor="w", padx=10, pady=(10,0))
    prio_edit = ttk.Combobox(edit_win, values=list(PRIO_COLORS.keys()), state="readonly")
    prio_edit.pack(fill="x", padx=10)
    prio_edit.set(t["prio"])
    tk.Label(edit_win, text="Fälligkeitsdatum:", bg=c["bg"], fg=c["fg"]).pack(anchor="w", padx=10, pady=(10,0))
    entry_due = tk.Entry(edit_win, bg=c["entry_bg"], fg=c["entry_fg"])
    entry_due.pack(fill="x", padx=10)
    entry_due.insert(0, t["due"])
    def save_edit():
        t["text"] = entry_text.get().strip()
        t["prio"] = prio_edit.get()
        t["due"] = entry_due.get().strip()
        save_tasks()
        refresh_views()
        edit_win.destroy()
    ttk.Button(edit_win, text="Speichern", command=save_edit).pack(pady=10)
    # Passe Combobox an Theme an
    style = ttk.Style()
    style.configure("TCombobox", fieldbackground=c["entry_bg"], background=c["bg"], foreground=c["fg"])

def show_context_menu(event):
    row_id = tree_data.identify_row(event.y)
    if not row_id:
        return
    idx = int(row_id)
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Bearbeiten", command=lambda: edit_task(idx))
    menu.post(event.x_root, event.y_root)

tree_data.bind("<Button-3>", show_context_menu)

load_tasks(); apply_theme(); refresh_views()
start_reminder_thread()
root.mainloop()








