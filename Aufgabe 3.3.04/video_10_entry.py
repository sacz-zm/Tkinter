
import tkinter as tk
from tkinter import ttk

#def print_entry_input():
    # print(entry_1.get()) Funktion zur Textausgabe
    #ttk.Label(root, text=entry_1.get()).pack() # erstellt ein neues Label aus der Texteingabe und zeigt diese an

def delete_input():
    entry_1.delete(0, tk.END) # tk.END löscht bis zum letzten Zeichen


root = tk.Tk()
root.geometry("400x400")

entry_1 = ttk.Entry(root, width=40)
entry_1.pack()

#entry_1.insert(0, "Hier kannst du schreiben!") # Gibt einen Anfangstext aus | 0 = Die Stelle an, an die der Text startet

button_1 = ttk.Button(root, text="Input löschen!", command=delete_input) #command=print_entry_input | command=delete_input löscht den Text nach Button  
button_1.pack()


for item in entry_1.keys():
    print(item, ": ", entry_1[item])

root.mainloop()

