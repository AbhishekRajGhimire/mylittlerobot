import os
import sys
import json
import re
import threading
import urllib.request
import subprocess

REPO = "AbhishekRajGhimire/mylittlerobot"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"

def version_tuple(v):
    return tuple(map(int, re.findall(r'\d+', v)))

def get_latest_release():
    try:
        req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Update check failed: {e}")
        return None

def download_file(url, dest_path):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as response, open(dest_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def updater_thread(current_version):
    release = get_latest_release()
    if release and 'tag_name' in release:
        latest_version = release['tag_name']
        try:
            if version_tuple(latest_version) > version_tuple(current_version):
                print(f"New version found: {latest_version}")
                for asset in release.get('assets', []):
                    if asset['name'].endswith('.exe'):
                        download_url = asset['browser_download_url']
                        
                        # Only proceed if we are running as an exe
                        if getattr(sys, 'frozen', False):
                            current_exe = sys.executable
                            exe_dir = os.path.dirname(current_exe)
                            new_exe_path = os.path.join(exe_dir, "MyLittleRobot_update.exe")
                            old_exe_path = os.path.join(exe_dir, "MyLittleRobot.old.exe")
                            
                            if download_file(download_url, new_exe_path):
                                try:
                                    # Rename current running executable
                                    if os.path.exists(old_exe_path):
                                        os.remove(old_exe_path)
                                    os.rename(current_exe, old_exe_path)
                                    
                                    # Rename downloaded file to original name
                                    os.rename(new_exe_path, current_exe)
                                    
                                    # Restart
                                    subprocess.Popen([current_exe] + sys.argv[1:])
                                    os._exit(0)
                                except Exception as e:
                                    print(f"Failed to replace executable: {e}")
                        break
        except Exception as e:
            print(f"Version comparison failed: {e}")

def start_updater(current_version):
    t = threading.Thread(target=updater_thread, args=(current_version,), daemon=True)
    t.start()
