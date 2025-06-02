

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

root = tk.Tk()
root.geometry("400x400")

image = Image.open("bild.jpg").resize((300, 300)) # Öffnet ein Bild | Absoluter Pfad oder Bild in den Projektordner
photo = ImageTk.PhotoImage(image) # Intergriert das Bild 

label_1 = ttk.Label(root, text="Das ist unser Logo", image=photo, compound="top", pady=20)
label_1.pack()

label_1.configure(font=("Courier", 30)) # Ändert die Schriftart | Nur Schriftarten die man auf dem System hat | Zahl ändert die Schriftgröße 

for item in label_1.keys():
    print(item, ": ", label_1[item]) # Zeigt alle Optionen eines Widgets auf welchen Wert diese gesetzt sind


root.mainloop()