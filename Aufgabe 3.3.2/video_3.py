

import tkinter as tk

root = tk.Tk()
label_1 = tk.Label(root, text="Hallo Welt")
label_1.pack()

root.mainloop() # Emdlosschleife die permanent prüft, ob ein Event auftritt
                # Mithilfe von Programmcode kann auf beliebige Events reagiert werden

print("Testausgabe")
