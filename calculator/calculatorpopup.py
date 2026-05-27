import tkinter as tk
root = tk.Tk()
root.title("Calculator")
root.resizable(False,False)

display = tk.Entry(root, font=("Arial", 20),justify="right",bd = 5) 
display.grid(row=0,column = 0, columnspan = 4)

def click(value):
    display.insert(tk.END, value)
def clear():
    display.delete(0, tk.END)
def calculate():
    try:
        result = eval(display.get())
        clear()
        display.insert(0, result)
    except:
        clear()
        display.insert(0,"Error")
buttons = [["7","8","9","/"],
           ["4","5","6","*"],
           ["1","2","3","-"],
           ["0",".","=","+"],
           ]
for r, row in enumerate(buttons, start=1):
    for c, label in enumerate(row):
        cmd = calculate if label == "=" else lambda v=label: click(v)
        tk.Button(root, text=label, width=5, height=2,
                  font=("Arial", 14), command=cmd).grid(row=r, column=c)

tk.Button(root, text="C", width=23, height=2,
          font=("Arial", 14), command=clear).grid(row=5, column=0, columnspan=4)

root.mainloop()