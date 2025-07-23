import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from dataclasses import dataclass
import subprocess
import ctypes
import sys
import asyncio
import aiohttp
import threading
import winreg

@dataclass
class Configuration:
    name: str
    primary: str
    secondary: str
    comment: str = ""

CONFIG_FILE = "dns_config.json"
HISTORY_FILE = "url_history.json"

configuration_list = [
    Configuration(name="Shecan", primary="178.22.122.100", secondary="185.51.200.2"),
    Configuration(name="Begzar", primary="185.55.226.26", secondary="185.55.225.25"),
    Configuration(name="Radar Game", primary="10.202.10.10", secondary="10.202.10.11"),
    Configuration(name="Electrot", primary="78.157.42.100", secondary="78.157.42.101"),
    Configuration(name="403 DNS", primary="10.202.10.202", secondary="10.202.10.102", comment="[In Memories]"),
    Configuration(name="Sheltertm", primary="94.103.125.157", secondary="94.103.125.158"),
    Configuration(name="Beshkanapp", primary="181.41.194.177", secondary="181.41.194.186"),
    Configuration(name="Pishgaman", primary="5.202.100.100", secondary="5.202.100.101"),
    Configuration(name="Shatel", primary="85.15.1.14", secondary="85.15.1.15", comment="[Shatel ADSL Only]"),
    Configuration(name="Level3", primary="209.244.0.3", secondary="209.244.0.4"),
    Configuration(name="Cloudflare", primary="1.1.1.1", secondary="1.0.0.1"),
    Configuration(name="Google DNS", primary="8.8.8.8", secondary="4.2.2.4"),
]

default_urls = [
    "https://developer.android.com",
    "https://repo.maven.apache.org",
    "https://jcenter.bintray.com",
    "https://dl.google.com",
]

def load_config():
    global configuration_list
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            custom_configs = json.load(f)
            configuration_list.extend([Configuration(**config) for config in custom_configs])

def save_config():
    custom_configs = [config.__dict__ for config in configuration_list if config not in configuration_list[:12]]
    with open(CONFIG_FILE, 'w') as f:
        json.dump(custom_configs, f, indent=4)

def load_url_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_url_history(url):
    history = load_url_history()
    if url and url not in history:
        history.append(url)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)

def flush_dns_cache():
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True)

def get_current_dns():
    try:
        command = ["netsh", "interface", "ip", "show", "dns", "Wi-Fi"]
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        primary = secondary = None
        for line in output.splitlines():
            if "DNS Servers" in line and ":" in line:
                primary = line.split(":")[1].strip()
            elif "DNS Servers" in line and primary and ":" in line:
                secondary = line.split(":")[1].strip()
        return primary, secondary
    except subprocess.CalledProcessError:
        return None, None

async def test_dns(index, config, url, loop, app):
    try:
        command = ["netsh", "interface", "ip", "set", "dns", "Wi-Fi", "static", config.primary]
        subprocess.run(command, check=True, capture_output=True)
        command = ["netsh", "interface", "ip", "add", "dns", "Wi-Fi", config.secondary, "index=2"]
        subprocess.run(command, check=True, capture_output=True)
        
        flush_dns_cache()
        
        async with aiohttp.ClientSession() as session:
            app.update_status(index, "Testing...")
            async with session.get(url, timeout=5, headers={"Cache-Control": "no-cache"}) as response:
                status = response.status
                app.update_status(index, str(status))
                return (index, status)
    except (aiohttp.ClientError, subprocess.CalledProcessError, asyncio.TimeoutError):
        app.update_status(index, "Failed")
        return (index, None)

def apply_dns(primary_dns, secondary_dns):
    try:
        command = ["netsh", "interface", "ip", "set", "dns", "Wi-Fi", "static", primary_dns]
        subprocess.run(command, check=True, capture_output=True)
        command = ["netsh", "interface", "ip", "add", "dns", "Wi-Fi", secondary_dns, "index=2"]
        subprocess.run(command, check=True, capture_output=True)
        flush_dns_cache()
        messagebox.showinfo("Success", f"DNS set to {primary_dns} and {secondary_dns}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to set DNS: {e}")

def clear_dns():
    try:
        command = ["netsh", "interface", "ip", "set", "dns", "Wi-Fi", "dhcp"]
        subprocess.run(command, check=True, capture_output=True)
        flush_dns_cache()
        messagebox.showinfo("Success", "DNS settings cleared (set to DHCP)")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to clear DNS: {e}")

def run_as_admin(func):
    if ctypes.windll.shell32.IsUserAnAdmin():
        func()
    else:
        script = sys.argv[0]
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
        sys.exit(0)

class DNSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FuckDNS")
        self.root.geometry("800x600")
        
        self.url_history = load_url_history()
        load_config()
        
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(pady=5, padx=10, fill="x")
        self.current_dns_label = ttk.Label(self.status_frame, text="Current DNS: Not set")
        self.current_dns_label.pack(side="left")
        
        self.url_frame = ttk.Frame(self.root)
        self.url_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(self.url_frame, text="Test URL:").pack(side="left")
        self.url_combo = ttk.Combobox(self.url_frame, values=self.url_history + default_urls)
        self.url_combo.pack(side="left", fill="x", expand=True, padx=5)
        self.url_combo.bind("<<ComboboxSelected>>", self.on_url_select)
        
        self.test_button = ttk.Button(self.url_frame, text="Test DNS", command=self.start_test_dns_servers)
        self.test_button.pack(side="left", padx=5)
        
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("Name", "Primary", "Secondary", "Status", "Comment"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Primary", text="Primary DNS")
        self.tree.heading("Secondary", text="Secondary DNS")
        self.tree.heading("Status", text="Status Code")
        self.tree.heading("Comment", text="Comment")
        self.tree.pack(fill="both", expand=True)
        
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10, padx=10, fill="x")
        
        self.apply_button = ttk.Button(self.button_frame, text="Apply Selected DNS", command=self.apply_selected_dns)
        self.apply_button.pack(side="left", padx=5)
        
        self.auto_apply_button = ttk.Button(self.button_frame, text="Apply First 200 DNS", command=self.auto_apply_first_200)
        self.auto_apply_button.pack(side="left", padx=5)
        
        self.clear_button = ttk.Button(self.button_frame, text="Clear DNS", command=self.clear_dns_with_status)
        self.clear_button.pack(side="left", padx=5)
        
        self.add_dns_button = ttk.Button(self.button_frame, text="Add DNS", command=self.open_add_dns_window)
        self.add_dns_button.pack(side="left", padx=5)
        
        self.populate_tree()
        self.loop = asyncio.get_event_loop()
        self.update_current_dns_status()

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, config in enumerate(configuration_list):
            self.tree.insert("", "end", values=(config.name, config.primary, config.secondary, "", config.comment))

    def update_status(self, index, status):
        self.root.after(0, lambda: self.tree.set(self.tree.get_children()[index], "Status", status))

    def update_current_dns_status(self):
        primary, secondary = get_current_dns()
        if primary and secondary:
            for config in configuration_list:
                if config.primary == primary and config.secondary == secondary:
                    self.current_dns_label.config(text=f"Current DNS: {config.name} ({primary}, {secondary})")
                    return
            self.current_dns_label.config(text=f"Current DNS: Custom ({primary}, {secondary})")
        else:
            self.current_dns_label.config(text="Current DNS: DHCP")

    def start_test_dns_servers(self):
        url = self.url_combo.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter or select a URL")
            return
        
        save_url_history(url)
        self.url_history = load_url_history()
        self.url_combo["values"] = self.url_history + default_urls
        
        self.test_button["state"] = "disabled"
        self.auto_apply_button["state"] = "disabled"
        threading.Thread(target=self.run_async_tests, args=(url, False), daemon=True).start()

    def auto_apply_first_200(self):
        url = self.url_combo.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter or select a URL")
            return
        
        save_url_history(url)
        self.url_history = load_url_history()
        self.url_combo["values"] = self.url_history + default_urls
        
        self.test_button["state"] = "disabled"
        self.auto_apply_button["state"] = "disabled"
        threading.Thread(target=self.run_async_tests, args=(url, True), daemon=True).start()

    def run_async_tests(self, url, auto_apply):
        async def run_tests():
            results = []
            for i, config in enumerate(configuration_list):
                self.update_status(i, "Testing...")
                result = await test_dns(i, config, url, self.loop, self)
                results.append(result)
                if auto_apply and result[1] == 200:
                    self.root.after(0, lambda: run_as_admin(lambda: apply_dns(config.primary, config.secondary)))
                    self.root.after(0, self.update_current_dns_status)
                    self.root.after(0, lambda: self.test_button.configure(state="normal"))
                    self.root.after(0, lambda: self.auto_apply_button.configure(state="normal"))
                    return
            
            results.sort(key=lambda x: x[1] if x[1] is not None else 9999)
            self.root.after(0, lambda: self.test_button.configure(state="normal"))
            self.root.after(0, lambda: self.auto_apply_button.configure(state="normal"))

        self.loop.run_until_complete(run_tests())

    def apply_selected_dns(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a DNS configuration")
            return
        
        index = self.tree.index(selected[0])
        config = configuration_list[index]
        run_as_admin(lambda: apply_dns(config.primary, config.secondary))
        self.update_current_dns_status()

    def clear_dns_with_status(self):
        run_as_admin(clear_dns)
        self.update_current_dns_status()

    def open_add_dns_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add DNS")
        add_window.geometry("400x300")
        
        ttk.Label(add_window, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(add_window)
        name_entry.pack(pady=5, padx=10, fill="x")
        
        ttk.Label(add_window, text="Primary DNS:").pack(pady=5)
        primary_entry = ttk.Entry(add_window)
        primary_entry.pack(pady=5, padx=10, fill="x")
        
        ttk.Label(add_window, text="Secondary DNS:").pack(pady=5)
        secondary_entry = ttk.Entry(add_window)
        secondary_entry.pack(pady=5, padx=10, fill="x")
        
        ttk.Label(add_window, text="Comment:").pack(pady=5)
        comment_entry = ttk.Entry(add_window)
        comment_entry.pack(pady=5, padx=10, fill="x")
        
        def save_new_dns():
            name = name_entry.get()
            primary = primary_entry.get()
            secondary = secondary_entry.get()
            comment = comment_entry.get()
            
            if name and primary and secondary:
                configuration_list.append(Configuration(name=name, primary=primary, secondary=secondary, comment=comment))
                save_config()
                self.populate_tree()
                add_window.destroy()
            else:
                messagebox.showwarning("Warning", "Please fill in all required fields")
        
        ttk.Button(add_window, text="Save", command=save_new_dns).pack(pady=10)

    def on_url_select(self, event):
        pass

if __name__ == "__main__":
    run_as_admin(lambda: DNSApp(tk.Tk()).root.mainloop())
