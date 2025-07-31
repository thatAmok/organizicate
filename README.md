# Organizicate (Beta v0.9.6)

![image](https://github.com/user-attachments/assets/4d9a344b-4825-4f34-9e11-04e81d4ff7e7)

Organizicate is a smart, user-friendly file and folder organizer for Windows. It helps you keep your digital workspace tidy by automatically sorting files and folders into customizable categories based on their extensions. With a modern interface, drag-and-drop support, undo, system tray minimization, and theme switching, Organizicate makes digital organization effortless.

---

![image](https://github.com/user-attachments/assets/d9723b54-210a-4fff-b095-80c02d274f0a)

## ✨ Features

- **Automatic Organization:** Sort files and folders into categories by extension.
- **Custom Categories:** Add, edit, delete, import, and export your own categories.
- **Drag & Drop:** Quickly drop files or folders into the app to set the path.
- **Undo:** Revert the last organization action.
- **System Tray:** Minimize to tray and restore easily.
- **Theme Support:** Switch between multiple light and dark themes.
- **Recent Folders:** Quick access to recently used folders.
- **No Recursion:** Only top-level files/folders are moved (no subfolder recursion).
- **Modern UI:** Built with [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) for a clean, modern look.

---

## 🚀 Getting Started

### Requirements

>Note!
>Those requirements are only for **source-code** use, you can use the full app by downloading the .zip file from this Github.

- Python 3.8+
- [ttkbootstrap](https://pypi.org/project/ttkbootstrap/)
- [pystray](https://pypi.org/project/pystray/) (optional, for tray support)
- [Pillow](https://pypi.org/project/Pillow/) (optional, for tray icon)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourAmok/organizicate-beta.git
   cd organizicate-beta
   ```

2. **Install dependencies:**
   ```sh
   pip install ttkbootstrap pystray Pillow tkinterdnd2
   ```

3. **Run the app:**
   ```sh
   python organizicate.py
   ```

---

![image](https://github.com/user-attachments/assets/7f28a72c-4827-466e-8085-27202dddaa4a)

## 🛠️ Usage

1. **Select an operation:**  
   - Organize a folder
   - Organize a file
   - Organize all files in a folder
   - Organize all folders in a folder

2. **Set the path:**  
   Enter or drag-and-drop a file/folder, or use the Browse button.

3. **Click "Run Operation"** to organize.

4. **Manage categories:**  
   Use the category manager to add, edit, or delete user categories.

5. **Undo:**  
   Click "Undo Last Action" to revert the last move.

6. **Minimize to tray:**  
   Close the window to minimize; restore from the tray icon.

---

## 📂 Category Management

- **Default Categories:**  
  Predefined, cannot be deleted or edited (except for renaming).
- **User Categories:**  
  Fully customizable. Import/export your own sets.

---

## 📝 License

This project is licensed under the MIT License.

---

## 👤 Author

Developed by [@yourAmok](https://github.com/yourAmok) 
>Note!
>[@Hotmountain](https://github.com/Hotmountain) was my main account before I got locked out of it. [@yourAmok](https://github.com/yourAmok) is my new account.*

> Note!
> Please contact me for any bugs or unusual behaviour: kerogergesazmy@gmail.com

---

## 🌐 Links

- [GitHub Repo](https://github.com/yourAmok/organizicate-beta)
- [ttkbootstrap Documentation](https://ttkbootstrap.readthedocs.io/)

---

## 💡 Contributing

Pull requests and suggestions are welcome! Please open an issue to discuss your ideas.

---

## 🛡️ Disclaimer

Organizicate is in beta. Please back up important files before using.

---

## 💸 100% Free & Open-Source

Organizicate is **completely free forever** and open source. There are no hidden fees, subscriptions, or paid features—ever. Enjoy and share!
