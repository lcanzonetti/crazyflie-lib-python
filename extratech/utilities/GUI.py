import tkinter as tk
import customtkinter as ctk
from tkinter.messagebox import showinfo
from PIL import Image, ImageTk
import os, time
from test_main import main
import GLOBALS as GB
import stenBaiatore, wakeUppatore
from common_utils import IDFromURI

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def fai_main():
    # GB.available = []
    main()
    for uro in GB.available:
        iddu = IDFromURI(uro)
        ID_trovati = []
        ID_trovati.append(iddu)
    button_1.configure(text="Ho trovato %s radio.\n Specificatamente i droni con ID %s " %(len(GB.available), GB.available))

def all_prop_test():
    for uro in GB.available:
        id = IDFromURI(uro)
        GB.data_d[id].test_manager.single_drone_prop_test()
        
def all_wakeUp():
    for uro in GB.available:
        wakeUppatore.wakeUpSingle(uro)

def all_standBy():
    for uro in GB.available:
        stenBaiatore.standBySingle(uro)        
        
window = ctk.CTk()

textbox = tk.Text(master = window)

button_1 = ctk.CTkButton(
            master = window,
            command=fai_main,
            text = "Connettiti a tutti i droni disponibili",
            width = 100,
            height = 75
        )

button_2 = ctk.CTkButton(
            master = window,
            command=all_prop_test,
            text = "Avvio Test Motori per Tutti",
            width = 100,
            height = 75
        )

button_3 = ctk.CTkButton(
            master = window,
            command=all_wakeUp,
            text = "Wake up, everybody!",
            width = 100,
            height = 75
        )  

button_4 = ctk.CTkButton(
            master = window,
            command=all_standBy,
            text = "Good night, everybody!",
            width = 100,
            height = 75
        )     

textbox.grid(row = 0, column = 1, rowspan=4, columnspan=2, padx=20, pady=20, sticky="nsew")
button_1.grid(row = 0, column = 0, columnspan=1, padx = 20, pady = 20, sticky="w")
button_2.grid(row = 1, column = 0, columnspan=1, padx = 20, pady = 20, sticky="w")
button_3.grid(row = 2, column = 0, columnspan=1, padx = 20, pady = 20, sticky="w")
button_4.grid(row = 3, column = 0, columnspan=1, padx = 20, pady = 20, sticky="w")
window.geometry(f"{500}x{500}")
window.title("Extratech Testing Platform")
window.grid_rowconfigure((0,1,2,3), weight=1)
window.grid_columnconfigure((0, 1), weight=1)

def log_loop():
    f = open(os.path.join(__location__, "log.txt"), mode="r")
    data = f.read()
    textbox.delete(0.0, tk.END)
    textbox.insert(0.0, data)
    window.after(500, log_loop)

log_loop()
window.mainloop()
