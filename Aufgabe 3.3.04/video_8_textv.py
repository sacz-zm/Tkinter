

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("400x400")

text_variable = tk.StringVar() # Erstellt ein Objekt der StringVar() Variable | IntVar() Ganzzahlen, DoubleVar() Kommazahlen, Boolean() Wahrheitswerte
text_variable.set("Das ist der neue Text") # Text kann als Variable gespeichert werden

label_1 = ttk.Label(root, textvariable=text_variable) # textvarible=text_variable zeigt den Text an
label_1.pack()

text_variable.set("Aktualisierter Text") # Text kann später im Code geändert werden (wird dynamisch)

# label_1.configure(text="Neuer Text")
# label_1["text"] = "Neuer Text"      # Beide Varianten ändern den Text, manuell, in label_1 = tk.Label

root.mainloop()
