

import tkinter as tk

root = tk.Tk()
root.title("Hier steht der Titel") # Ändert den Titel
root.geometry("400x400") # Ändert die Größre des Fensters
root.minsize(width=250, height=250) # Gibt die minimale Größe des Fensters vor
root.maxsize(width=600, height=600) # Gibt die maximale Größe des Fensters vor
root.resizable(width=False, height=True) # Gibt vor ob die Größe geändert werden kann | False = Kann nicht, True = kann | min und maxsize gelten noch
label_1 = tk.Label(root, text="Hallo Welt")
label_1.pack()

root.mainloop()
