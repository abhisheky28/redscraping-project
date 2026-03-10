<div align="center">

# 🔴 RedScraping

**Turn a 30-minute scraping setup into 4 terminal commands.**

[![PyPI - Version](https://img.shields.io/pypi/v/redscraping?color=red&style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/redscraping/)
[![Python Versions](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://github.com/abhisheky28/redscraping-project/blob/main/LICENSE)
[![License: MIT](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)](https://github.com/abhisheky28/redscraping-project/blob/main/README.md)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-success?style=for-the-badge)](https://github.com/abhisheky28)

</div>

---

## 🛑 The Problem
Let's be honest. Setting up a new Selenium scraping project from scratch is a headache. 
You have to download webdrivers, configure stealth options to avoid getting blocked, fight with Google Cloud Service Accounts, manually share Google Sheets, and write 50 lines of boilerplate code just to open a browser.

## 🟢 The Solution
I got tired of doing that every time I started a new project. So I built **RedScraping**. 

RedScraping is a CLI framework that handles all the boring infrastructure for you. It creates isolated Chrome profiles, handles Google OAuth automatically (no more Service Account JSONs!), and generates plug-and-play boilerplate code. 

**You just write the scraping logic. RedScraping handles the rest.**

---

## ✨ Features

* 🕵️‍♂️ **Stealthy by Default:** Automatically configures Chrome to hide automation flags and bypass basic bot detection.
* 📊 **Zero-Config Google Sheets:** Uses OAuth2 to securely connect to your Google Drive. It even creates the spreadsheet and formats the headers for you automatically.
* 📁 **Excel Support:** Prefer local files? It generates a ready-to-use `.xlsx` template.
* 🤖 **AI-Ready:** Generates a "Context File" that teaches ChatGPT/Claude exactly how your library works, so the AI can write the scraping logic for you.

---

## 🚀 Quick Start

### 1. Install the library
```bash
pip install redscraping
```


## 🤝 Contributing
RedScraping is open-source and I want to make it the ultimate automation hub. Want to add a command for YouTube uploads? Gmail automation? Proxy rotation? PRs are highly encouraged!
How to contribute:
Fork the repository.
Create a new branch (git checkout -b feature/add-proxy-support).
Make your changes.
Commit your changes (git commit -m 'Added proxy rotation feature').
Push to the branch (git push origin feature/add-proxy-support).
Open a Pull Request!


## 📝 License
Distributed under the MIT License. See LICENSE for more information.


<div align="center">
<b>Built with ❤️ by Abhishek Yadav</b>
</div>
