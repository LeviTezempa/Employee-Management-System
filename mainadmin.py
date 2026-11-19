# pip install PyMySQL
import pymysql
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import os
import hashlib

from app_utils import DB_CONFIG


# connection for phpmyadmin
def connection():
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
    )
    return conn


def refreshTable():
    for data in my_tree.get_children():
        my_tree.delete(data)

    for array in read():
        my_tree.insert(parent='', index='end', iid=array, text="", values=(array), tag="orow")

    my_tree.tag_configure('orow', background='grey', font=('Arial', 12))
    my_tree.grid(row=16, column=0, columnspan=5, rowspan=11, padx=10, pady=20)


# gui
root = Tk()
root.title("Admin Dashboard")
root.geometry("1300x700")
my_tree = ttk.Treeview(root)

# placeholders for entry
ph1 = tk.StringVar()
ph2 = tk.StringVar()
ph3 = tk.StringVar()
ph4 = tk.StringVar()
ph5 = tk.StringVar()
ph6 = tk.StringVar()
ph7 = tk.StringVar()
ph8 = tk.StringVar()


# placeholder set value function
def setph(word, num):
    if num == 1:
        ph1.set(word)
    if num == 2:
        ph2.set(word)
    if num == 3:
        ph3.set(word)
    if num == 4:
        ph4.set(word)
    if num == 5:
        ph5.set(word)
    if num == 6:
        ph6.set(word)
    if num == 7:
        ph7.set(word)
    if num == 8:
        ph8.set(word)


def read():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    return results


def add():
    # id = str(idEntry.get())
    fn = str(fnEntry.get())
    un = str(unEntry.get())
    pw = hashlib.md5(str(pwEntry.get()).encode())
    em = str(emEntry.get())
    pn = str(pnEntry.get())
    dp = str(dpEntry.get())
    sx = str(sxEntry.get())

    if (fn == "" or fn == " ") or (un == "" or un == " ") or (
            pw == "" or pw == " ") or (em == "" or em == " ") or (pn == "" or pn == " ") or (dp == "" or dp == " ") or (
            sx == "" or sx == " "):
        os.system("py register.py")
        root.destroy()
        os.system("py mainadmin.py")
        # messagebox.showinfo("Error", "Please fill up the blank entry")
        return
    '''else:
        try:
            conn = connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO employees VALUES (null,'" + fn + "','" + un + "','" + pw.hexdigest() + "','" + em + "','" + pn + "','" + dp + "','" + sx + "') ")
            conn.commit()
            conn.close()
        except:
            messagebox.showinfo("Error", "Id already exist")
            return'''


refreshTable()


def reset():
    decision = messagebox.askquestion("Warning!!", "Delete all data?")
    if decision != "yes":
        return
    else:
        try:
            conn = connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees")
            conn.commit()
            conn.close()
        except:
            messagebox.showinfo("Error", "Sorry an error occured")
            return

        refreshTable()


def delete():
    decision = messagebox.askquestion("Warning!!", "Delete the selected data?")
    if decision != "yes":
        return
    else:
        selected_item = my_tree.selection()[0]
        deleteData = str(my_tree.item(selected_item)['values'][0])
        try:
            conn = connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees WHERE employeeID=%s", (deleteData,))
            conn.commit()
            conn.close()
        except:
            messagebox.showinfo("Error", "Sorry an error occured")
            return

        refreshTable()


def select():
    try:
        selected_item = my_tree.selection()[0]
        id = str(my_tree.item(selected_item)['values'][0])
        fn = str(my_tree.item(selected_item)['values'][1])
        un = str(my_tree.item(selected_item)['values'][2])
        pw = str(my_tree.item(selected_item)['values'][3])
        em = str(my_tree.item(selected_item)['values'][4])
        pn = str(my_tree.item(selected_item)['values'][5])
        dp = str(my_tree.item(selected_item)['values'][6])
        sx = str(my_tree.item(selected_item)['values'][7])

        setph(id, 1)
        setph(fn, 2)
        setph(un, 3)
        setph(pw, 4)
        setph(em, 5)
        setph(pn, 6)
        setph(dp, 7)
        setph(sx, 8)
    except:
        messagebox.showinfo("Error", "Please select a data row")


def search():
    # id = str(idEntry.get())
    fn = str(fnEntry.get())
    un = str(unEntry.get())
    pw = str(pwEntry.get())
    em = str(emEntry.get())
    pn = str(pnEntry.get())
    dp = str(dpEntry.get())
    sx = str(sxEntry.get())

    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM employees WHERE employeeFullName=%s OR employeeUsername=%s "
        "OR employeePassword=%s OR employeeEmail=%s OR employeePhone=%s "
        "OR employeeDepartment=%s OR employeeSex=%s",
        (fn, un, pw, em, pn, dp, sx),
    )

    try:
        result = cursor.fetchall()

        for num in range(0, 8):
            setph(result[0][num], (num + 1))

        conn.commit()
        conn.close()
    except:
        messagebox.showinfo("Error", "No data found")


def update():
    selectedid = ""

    try:
        selected_item = my_tree.selection()[0]
        selectedid = str(my_tree.item(selected_item)['values'][0])
    except:
        messagebox.showinfo("Error", "Please select a data row")

    # id = str(idEntry.get())
    fn = str(fnEntry.get())
    un = str(unEntry.get())
    pw = hashlib.md5(str(pwEntry.get()).encode())
    em = str(emEntry.get())
    pn = str(pnEntry.get())
    dp = str(dpEntry.get())
    sx = str(sxEntry.get())

    if (fn == "" or fn == " ") or (un == "" or un == " ") or (
            pw == "" or pw == " ") or (em == "" or em == " ") or (pn == "" or pn == " ") or (dp == "" or dp == " ") or (
            sx == "" or sx == " "):
        messagebox.showinfo("Error", "Please fill up the blank entry")
        return
    else:
        try:
            conn = connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE employees SET employeeFullName=%s, employeeUsername=%s, "
                "employeePassword=%s, employeeEmail=%s, employeePhone=%s, "
                "employeeDepartment=%s, employeeSex=%s WHERE employeeID=%s",
                (fn, un, pw.hexdigest(), em, pn, dp, sx, selectedid),
            )
            conn.commit()
            conn.close()
        except:
            messagebox.showinfo("Error", "ID already exist")
            return

    refreshTable()


# GUI
label = Label(root, text="ADMIN DASHBOARD", font=('Arial Bold', 30))
label.grid(row=0, column=0, columnspan=8, rowspan=2, padx=70, pady=20)

# idLabel = Label(root, text="ID", font=('Arial ', 20))
fnLabel = Label(root, text="Fullname", font=('Arial', 20))
unLabel = Label(root, text="Username", font=('Arial', 20))
pwLabel = Label(root, text="Password", font=('Arial', 20))
emLabel = Label(root, text="Email", font=('Arial', 20))
pnLabel = Label(root, text="Phone number", font=('Arial', 20))
dpLabel = Label(root, text="Department", font=('Arial', 20))
sxLabel = Label(root, text="Sex", font=('Arial', 20))

# idLabel.grid(row=2, column=1, columnspan=1, padx=50, pady=5)
fnLabel.grid(row=3, column=2, columnspan=1, padx=50, pady=5)
unLabel.grid(row=4, column=1, columnspan=1, padx=50, pady=5)
pwLabel.grid(row=4, column=3, columnspan=1, padx=50, pady=5)
emLabel.grid(row=6, column=1, columnspan=1, padx=50, pady=5)
pnLabel.grid(row=6, column=3, columnspan=1, padx=50, pady=5)
dpLabel.grid(row=8, column=1, columnspan=1, padx=50, pady=5)
sxLabel.grid(row=8, column=3, columnspan=1, padx=50, pady=5)

# Text variable entry
# idEntry = Entry(root, width=40, bd=3, font=('Arial', 13), textvariable=ph1)
fnEntry = Entry(root, width=40, bd=3, font=('Arial', 13), textvariable=ph2)
unEntry = Entry(root, width=40, bd=3, font=('Arial', 13), textvariable=ph3)
pwEntry = Entry(root, width=40, bd=3, font=('Arial', 13), textvariable=ph4)
emEntry = Entry(root, width=40, bd=3, font=('Arial', 13), textvariable=ph5)
pnEntry = Entry(root, width=40, bd=3, font=('Arial', 13), textvariable=ph6)
dpEntry = Entry(root, width=40, bd=3, font=('Arial', 13), textvariable=ph7)
sxEntry = Entry(root, width=40, bd=3, font=('Arial', 13), textvariable=ph8)

# idEntry.grid(row=3, column=1, columnspan=1, padx=5, pady=0)
fnEntry.grid(row=3, column=1, columnspan=1, padx=5, pady=0)
unEntry.grid(row=5, column=1, columnspan=1, padx=5, pady=0)
pwEntry.grid(row=5, column=3, columnspan=1, padx=5, pady=0)
emEntry.grid(row=7, column=1, columnspan=1, padx=5, pady=0)
pnEntry.grid(row=7, column=3, columnspan=1, padx=5, pady=0)
dpEntry.grid(row=9, column=1, columnspan=1, padx=5, pady=0)
sxEntry.grid(row=9, column=3, columnspan=1, padx=5, pady=0)

addBtn = Button(
    root, text="Register", padx=65, pady=5, width=10,
    bd=5, font=('Arial', 15), bg="#84F894", command=add)
updateBtn = Button(
    root, text="Update", padx=65, pady=5, width=10,
    bd=5, font=('Arial', 15), bg="#84E8F8", command=update)
deleteBtn = Button(
    root, text="Delete", padx=65, pady=5, width=10,
    bd=5, font=('Arial', 15), bg="#FF9999", command=delete)
searchBtn = Button(
    root, text="Search", padx=65, pady=5, width=10,
    bd=5, font=('Arial', 15), bg="#F4FE82", command=search)
resetBtn = Button(
    root, text="Reset", padx=65, pady=5, width=10,
    bd=5, font=('Arial', 15), bg="#F398FF", command=reset)
selectBtn = Button(
    root, text="Generate", padx=65, pady=5, width=10,
    bd=5, font=('Arial', 15), bg="#EEEEEE", command=select)

addBtn.grid(row=1, column=4, columnspan=1, rowspan=2)
updateBtn.grid(row=3, column=4, columnspan=1, rowspan=2)
deleteBtn.grid(row=5, column=4, columnspan=1, rowspan=2)
searchBtn.grid(row=7, column=4, columnspan=1, rowspan=2)
resetBtn.grid(row=9, column=4, columnspan=1, rowspan=2)
selectBtn.grid(row=11, column=4, columnspan=1, rowspan=2)

style = ttk.Style()
style.configure("Treeview.Heading", font=('Arial Bold', 15))

my_tree['columns'] = (
    "employeeID", "employeeFullName", "employeeUsername", "employeePassword", "employeeEmail", "employeePhone",
    "employeeDepartment", "employeeSex")

my_tree.column("#0", width=0, stretch=NO)
my_tree.column("employeeID", anchor=W, width=50)
my_tree.column("employeeFullName", anchor=W, width=250)
my_tree.column("employeeUsername", anchor=W, width=180)
my_tree.column("employeePassword", anchor=W, width=150)
my_tree.column("employeeEmail", anchor=W, width=170)
my_tree.column("employeePhone", anchor=W, width=150)
my_tree.column("employeeDepartment", anchor=W, width=160)
my_tree.column("employeeSex", anchor=W, width=40)

my_tree.heading("employeeID", text="Id")
my_tree.heading("employeeFullName", text="Fullname", anchor=W)
my_tree.heading("employeeUsername", text="Username", anchor=W)
my_tree.heading("employeePassword", text="Password", anchor=W)
my_tree.heading("employeeEmail", text="Email", anchor=W)
my_tree.heading("employeePhone", text="Phonenumber", anchor=W)
my_tree.heading("employeeDepartment", text="Department", anchor=W)
my_tree.heading("employeeSex", text="Sex", anchor=W)

refreshTable()

root.mainloop()
