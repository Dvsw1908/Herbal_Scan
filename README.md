# 🌿 Herbal Scan

![Herbal Scan Banner](https://img.shields.io/badge/Status-Active-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20)
![Language](https://img.shields.io/badge/Language-Python%20%7C%20Dart-yellow)
![Framework](https://img.shields.io/badge/Framework-Flutter%20%7C%20Jupyter-cyan)

**Herbal Scan** is an intelligent application designed to help users identify and learn about various herbal leaves. By utilizing machine learning image classification and a seamless mobile interface, the app allows users to scan herbal plants and instantly retrieve relevant information regarding their uses, properties, and benefits.

---

## 📑 Table of Contents
- [Project Overview](#-project-overview)
- [Repository Structure](#-repository-structure)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Mobile App Setup (Flutter)](#mobile-app-setup-flutter)
  - [Backend & Training Setup (Python)](#backend--training-setup-python)
- [Usage](#-usage)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Project Overview

The project is split into three main components:
1. **The Mobile Application:** Built using Flutter, this app provides the user interface for capturing images of herbal leaves and displaying results.
2. **The Backend API:** A server-side application that processes requests and communicates with the machine learning model.
3. **Machine Learning / Training:** Jupyter Notebooks and Python scripts used to train, test, and export the leaf classification model.

---

## 📂 Repository Structure

```text
Herbal_Scan/
├── backend/                             # Python backend API source code
├── herbal_leaf_app/                     # Flutter mobile application source code
├── results/                             # Model evaluation results and output metrics
├── training/                            # Jupyter Notebooks and scripts for model training
├── Instruksi_Claude_Code.docx           # Documentation and prompt instructions
├── herbalscan_product_description.txt   # Detailed product description and features
├── requirements.txt                     # Python dependency file for backend/training
└── README.md                            # Project documentation
