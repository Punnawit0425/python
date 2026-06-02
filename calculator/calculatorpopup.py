import tkinter as tk
tkin = tk.Tk()
tkin.geometry("400x500")

for i in range(4):
    tkin.grid_columnconfigure(i, weight=1)

for i in range(5):
    tkin.grid_rowconfigure(i, weight=1)
tkin.title("Calculator")

entry = tk.Entry(tkin, font=("Arial", 24))

entry.grid(row=0,column=0,columnspan=4, sticky="nsew")

def display(number):
    entry.insert(tk.END,number)

def clear():
    entry.delete(0,tk.END)

def calculate():
    result = eval(entry.get())
    entry.delete(0,tk.END)
    entry.insert(tk.END,result)

    
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", "C", "=", "+"]
]
for row_num, rows in enumerate(buttons):
    for col_num, column in enumerate(rows):
        if column == "C":
            button = tk.Button(tkin,text="C",font=("Arial", 20),command=clear)
            button.grid(row=row_num + 1, column=col_num, sticky="nsew")
        elif column == "=":
            button = tk.Button(tkin,text="=",font=("Arial", 20),command=calculate)
            button.grid(row=row_num + 1, column=col_num, sticky="nsew")
        else:
            button = tk.Button(tkin,text=column,font=("Arial", 20),command=lambda value=column: display(value))
            button.grid(row=row_num + 1, column=col_num, sticky="nsew")

tkin.mainloop()