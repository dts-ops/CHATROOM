import socket
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import json

def receive(): # Nhận tin nhắn từ server
    while not CLOSE:
        try:
            msg = client.recv(1024).decode(FORMAT)
            if msg == "/n":
                client.send(nickname.encode(FORMAT))
            elif msg == "/nr":
                client.close()
                messagebox.showwarning('Warning',"Nickname của bạn đã tồn tại hoặc không khả dùng.\nVui lòng sử dụng nickname khác")
                window.destroy()
                raise SystemExit(0)
            elif msg == "/r": # Nhận yêu cầu đóng client từ server
                listbox.insert(tk.END,'[SERVER] Server is closing ...')
                listbox.see(tk.END)
                close_client() # Đóng client
            else:
                listbox.insert(tk.END,msg) 
                listbox.see(tk.END)
        except:
            break

def close_client():
    client.send('/r'.encode(FORMAT))
    client.close()
    for widget in window.winfo_children():
        widget.destroy()  # Xóa tất cả widget
    window.quit()
    raise SystemExit(0)

def on_enter_pressed(event):
    message = f'[{nickname}] {entry.get()}'
    if entry.get():
        client.send(message.encode(FORMAT))
        entry.delete(0,tk.END)
        listbox.see(tk.END)

def send_message_by_button():
    message = f'[{nickname}] {entry.get()}'
    if entry.get():
        client.send(message.encode(FORMAT))
        entry.delete(0,tk.END)
        listbox.see(tk.END)

with open('config.json','r') as f:
    p = json.load(f)
    HOST = p['ip']  # Địa chỉ localhost
    PORT = p['port']  # Cổng kết nối

if not HOST and not PORT:
    messagebox.showerror('Config','Vui lòng kiểm tra lại tệp cấu hình')
    raise SystemExit(0)

FORMAT = 'utf-8'
CLOSE = False
ADDRESS = (HOST, PORT)

# Kết nối với server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(ADDRESS)
except:
    messagebox.showerror('Connection','Không thể kết nối đến server')
    raise SystemExit(0)

nickname = simpledialog.askstring("Input", "Vui lòng nhập nickname của bạn?")

# Cửa sổ chính
window = tk.Tk()
window.title(f"Message-{nickname}")

# Tạo Listbox
listbox = tk.Listbox(window, height=10, width=36)
listbox.grid(row = 0, column = 0, columnspan=3, sticky=tk.NSEW)

# Tạo entry
entry = tk.Entry(window)
entry.grid(row = 1, column = 0,sticky = tk.EW)

# Tạo button
button = tk.Button(window,text = "SEND",command=send_message_by_button)
button.grid(row = 1, column = 1)

#Tạo button
bc = tk.Button(window,text = "CLOSE",command=close_client)
bc.grid(row = 1, column = 2)

window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

# Bắt sự kiện phím enter/ return
window.protocol("WM_DELETE_WINDOW", close_client)
entry.bind("<Return>", on_enter_pressed)
thread_receive_msg = threading.Thread(target = receive)
thread_receive_msg.start()

# Chạy ứng dụng
window.mainloop()
