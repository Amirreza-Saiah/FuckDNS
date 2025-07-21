import subprocess
from ping3 import ping, verbose_ping
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes
from dataclasses import dataclass

@dataclass
class Configuration():
    name: str
    primary: str
    secondary: str
    comment:str = ""

configuration_list = [
    Configuration(name = "Shecan", primary ="178.22.122.100", secondary= "185.51.200.2"),
    Configuration(name = "Begzar", primary ="185.55.226.26", secondary= "185.55.225.25"),
    Configuration(name = "Radar Game", primary ="10.202.10.10", secondary= "10.202.10.11"),
    Configuration(name = "Electrot", primary ="78.157.42.100", secondary= "78.157.42.101"),
    Configuration(name = "403 DNS", primary ="10.202.10.202", secondary= "10.202.10.102", comment = "[In Memories]"),
    Configuration(name = "Sheltertm", primary ="94.103.125.157", secondary= "94.103.125.158"),
    Configuration(name = "Beshkanapp", primary ="181.41.194.177", secondary= "181.41.194.186"),
    Configuration(name = "Pishgaman", primary ="5.202.100.100", secondary= "5.202.100.101"),
    Configuration(name = "Shatel", primary ="85.15.1.14", secondary= "85.15.1.15", comment = "[Shatel ADSL Only]"),
    Configuration(name = "Level3", primary ="209.244.0.3", secondary= "209.244.0.4"),
    Configuration(name = "Cloudflare", primary ="1.1.1.1", secondary= "1.0.0.1"),
    Configuration(name = "Google DNS", primary ="8.8.8.8", secondary= "4.2.2.4"),
]

def selection():

    with ThreadPoolExecutor() as executor:
        sorted_configs = []
        futures = [executor.submit(ping_config, i, config) for i, config in enumerate(configuration_list)]
        for future in as_completed(futures):
            sorted_configs.append(future.result())
            
    sorted_configs.sort(key=lambda x: x[1])
    indx = 0
    for config in sorted_configs:
        indx += 1
        if config[1] != 9999:
            print(f"[{indx}][{int(config[1] * 1000)}ms] {configuration_list[config[0]].name} {configuration_list[config[0]].comment}")
        else:
            print(f"[{indx}][TIME OUT] {configuration_list[config[0]].name} {configuration_list[config[0]].comment}")


    output = int(input("~> "))
    primary(configuration_list[sorted_configs[output-1][0]].primary)
    secondary(configuration_list[sorted_configs[output-1][0]].secondary)
    done()
    
def ping_config(index, config: Configuration):
    try:
        result = ping(config.primary, timeout=1)
        if result is not None:
            return (index, result)
        else:
            return (index, 9999)
    except Exception as e:
        return  (index, 9999)
  
def primary(primary_dns):
    try:
        command = [
            "netsh", "interface", "ip", "set", "dns",
            "Wi-Fi", "static", primary_dns
        ]

        subprocess.run(command, check=True)
        print(f"Primary DNS for Wi-Fi set to {primary_dns}.")
    except subprocess.CalledProcessError as error:
        print("An error occurred while setting the DNS:")
        print("Return code:", error.returncode)
        print("Error output:", error.stderr)
        sys.exit(1)

def secondary(secondary_dns):
    try:
        command = [
            "netsh", "interface", "ip", "add", "dns",
            "Wi-Fi", secondary_dns, "index=2"
        ]
        subprocess.run(command, check=True)
        print(f"Secondary DNS for Wi-Fi added as {secondary_dns}.")
        done()
    except subprocess.CalledProcessError as error:
        print("An error occurred while adding the secondary DNS:", error)
        sys.exit(1)
        
def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        selection()
    else:
        script = sys.argv[0]
        params = " ".join(sys.argv[1:])
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            sys.exit(0)
        except Exception as e:
            print("Failed to elevate privileges:", e)
            sys.exit(1)

def done():
    print("[+] Done.")
    time.sleep(1)
    sys.exit(0)

def clear_dns():
    command = ["netsh", "interface", "ip", "set", "dns", f'name="Wi-Fi"', "dhcp"]
    print("Clearing current DNS settings...")
    subprocess.run(command, check=True)
    print(f"DNS settings for Wi-Fi have been cleared (set to DHCP).")

if "__main__" == __name__:
    run_as_admin()