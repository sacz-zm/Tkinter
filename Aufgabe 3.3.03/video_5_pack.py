

import tkinter as tk

root = tk.Tk()
root.geometry("400x400")

label_1 = tk.Label(root, text="Label 1", bg="green") # bg= ändert die Hintergrundfarbe | Hex oder englische Bezeichnung als String
label_1.pack(side="top", expand=True, fill="y") # side= weist den Platz zu | expand=True versucht so viel Platz wie mögich in fill Richtung zu nutzen| fill=x füllt in x Richtung den kompletten Platz

label_2 = tk.Label (root, text="Label 2", bg="red")
label_2.pack(side="top", expand=True, fill="both") # fill=both nutzt x und y Richtung

root.mainloop()

# Label nutzt immer nur soviel Platz wie es benötigt um den Inhalt darzustellen
# "bottom", "left", "right" 
