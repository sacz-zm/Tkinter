

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("400x400")

label_1 = tk.Label(root, text="Label 1", bg="green")
label_1.pack()

label_2 = ttk.Label(root, text="Label 2")
label_2.pack()

root.mainloop()

# ttk = Der Code für Widgets wird vom Code fürs Erscheinungsbild soweit wie möglich getrennt 
# Code übersichtlicher
# Schnelle Änderungen möglich
# Mehr Widgets verfügbar
# Besseres plattformübergreifendes Erscheinungsbild -> Themes