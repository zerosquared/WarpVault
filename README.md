# WarpVault v3.0 | Ultimate Edition
### The High-Speed Prefix & Save Game Archiver for Linux Gamers

![WarpVault Ultimate Edition Screenshot](https://github.com/zerosquared/WarpVault/blob/main/WarpVaultScreen.png)

**WarpVault** is a specialized, GUI-driven backup engine designed specifically for Linux power users and gamers on distributions like **CachyOS** and **Arch**. It solves the "bloat" problem of modern Linux gaming by allowing you to easily warp (compress) and reconstitute (recover) game prefixes, compatdata, and save folders without the manual overhead of terminal commands.

This is my first attempt at making an app.  Yes, I used A.I. (Gemini) for something that I personally needed and I thought someone else might find this useful as well.  Please be kind.  Any suggestions are welcome but it's just a python script so you can customize however you like.

You WILL have to edit the script to point it to your directories where your prefix folders live and where you want to back them up to.  There are 3 lines at the top that are commented that you will need to change.

This is a free tool that can be customized for use on your own system so please use at your own risk!  I will NOT be responsible for any lost data due to the use of this python script.

---

## 🚀 Core Functionality
Unlike generic backup tools, WarpVault is built to understand how Linux gaming works:

* **Targeted Compression:** It targets the specific `compatdata` (Steam) and local game folders (Faugus/Standalone) where prefixes and saves live.
* **High-Efficiency Engine:** Utilizes `pigz` (Parallel Implementation of GZip) to leverage your full CPU for lightning-fast compression.
* **Smart Exclusions:** Automatically ignores "junk" data like `shadercache` and `Temp` folders to keep your vault lean.
* **Steam Integration:** Uses `protontricks` logic to map cryptic Steam AppIDs (e.g., `2882001120`) to actual game titles (e.g., *Baldur's Gate 3*).

## 🖥️ Under the Hood (The Interface)
The UI is designed for "at-a-glance" management of your local and archived libraries:

* **Dual-Vault System:** Dedicated tabs for **Faugus/Standalone** games and **Steam/Proton** compatdata.
* **Live Status Tracking:**
    * `[LIVE]`: Installed on system; not yet backed up.
    * `[VAULT ONLY]`: Safely archived; not currently on local drive.
    * `[SYNCED]`: Matching copies exist in both active library and vault.
* **Size Transparency:** Displays exact compressed archive sizes to help manage storage.
* **Bulk Operations:** "Select All" and "Clear All" for massive migrations, or select individual folders.
* **Real-Time Feedback:** Monospace "Engine Log" and storage meter for live status and drive space tracking.

## 🛠️ Technical Specs
| Component | Requirement |
| :--- | :--- |
| **OS** | Optimized for **CachyOS** / **Arch Linux** (Works on most distros) |
| **Language** | Python |
| **UI Framework** | PySide6 (Qt) |
| **Dependencies** | `tar`, `pigz`, `protontricks` |
| **Storage Support**| Btrfs, Ext4, and Network Mounts (fstab) |

## 👤 Who Is This For?
* **Distro Hoppers:** Effortlessly move prefixes between installs (e.g., Mint to CachyOS).
* **SSD Minimalists:** Keep active games on NVMe; move "resting" prefixes to HDDs or Network Mounts without losing progress.
* **Power Users:** For those who want the speed of Arch/CachyOS with a professional KDE-friendly GUI.

---

## 🛠️ Installation & Setup

### 1. Install System Dependencies
WarpVault requires `pigz` for high-speed compression and `protontricks` to identify Steam games.

**For Arch / CachyOS (Bash or Fish):**
```bash
sudo pacman -Syu pigz protontricks

**Once system tools are installed, install the GUI framework:**
```bash
pip install -r requirements.txt

---

**WarpVault 3.0: Because your saves shouldn't be left behind.**
