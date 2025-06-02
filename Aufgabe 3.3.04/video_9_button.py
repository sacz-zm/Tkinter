

import tkinter as tk
from tkinter import ttk

def say_hello():
    print("Hallo, danke das du mich geklickt hast!") # Funktion für den Button

root = tk.Tk()
root.geometry("400x400")

button_1 = ttk.Button(root, text="Klick mich!", padding=10, command=say_hello, state=tk.DISABLED) # command=bezeichner macht die Funktion nutzbar | state=tk.DISABLED deaktiviert einen Button
button_1.pack()

quit_button = ttk.Button(root, text="Programm beenden", command=root.destroy) # root.destroy beendet das Programm
quit_button.pack()
for item in button_1.keys():
    print(item, ": ", button_1[item])

root.mainloop()
