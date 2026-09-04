# 😄 Face Attendance System

> 🎯 **AI-powered facial recognition attendance system built with Python + Streamlit**

A modern, batch-wise attendance management system that uses **face recognition** to automatically detect students from a class photo and record their attendance.

## ✨ Features

- 📁 **Batch Management**
- 👤 **Student Registration**
- 📸 **Multi-face Recognition**
- ✅ **Automatic Attendance**
- 📅 **Date-wise Reports**
- 👨‍🎓 **Student-wise Reports**
- 📊 **Batch Attendance Summary**
- 📥 **CSV Export**
- 🎨 **Modern Streamlit UI**
- 💾 **SQLite Database**

## 🧠 How It Works

```text
📷 Student Photo
       ↓
🧠 Face Detection
       ↓
🔢 Face Encoding
       ↓
💾 Student Profile
       ↓
📸 Class / Group Photo
       ↓
🔍 Face Matching
       ↓
✅ Present / ❌ Absent
       ↓
📊 Attendance Report
```

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| 🐍 Python | Core programming |
| 🎈 Streamlit | Web application |
| 🧠 face_recognition | Face recognition |
| 👁️ OpenCV | Image processing |
| 🔢 NumPy | Numerical operations |
| 🐼 Pandas | Data & reports |
| 🖼️ Pillow | Image processing |
| 🗄️ SQLite | Database |

## 🚀 Run Locally

### 1️⃣ Clone

```bash
git clone https://github.com/Pareshprajapati-777/FACE-ATTENDANCE-SYSTEM.git
cd FACE-ATTENDANCE-SYSTEM
```

### 2️⃣ Install Dependencies

Use **Python 3.9–3.11** for better compatibility with `dlib` and `face_recognition`.

```bash
pip install -r requirements.txt
```

### 3️⃣ Run

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## 📂 Project Structure

```text
FACE-ATTENDANCE-SYSTEM/
│
├── 📄 app.py
├── 🗄️ database.py
├── 🧠 face_utils.py
├── 📦 requirements.txt
├── 🎨 .streamlit/
│   └── config.toml
└── 📖 README.md
```

## 🎯 Workflow

**👤 Register → 📸 Capture Class Photo → 🧠 Recognize → ✅ Mark Attendance → 📊 View Report**

### 👤 Register Students
Create a batch and register each student using a clear, front-facing photo.

### 📸 Take Attendance
Upload or capture a class/group photo. The system detects visible faces and compares them with registered students.

### 📊 View Reports
Check date-wise attendance, student history, attendance percentage, and downloadable CSV reports.

## 🎯 Recognition Tips

- 💡 Use good lighting
- 🙂 Keep faces clearly visible
- 📷 Avoid blurry images
- 👓 Avoid sunglasses or face coverings
- 👥 Keep faces large enough in group photos
- 🎚️ Adjust **Match Strictness** when required

## 🔐 Data & Privacy

Face encodings and attendance information are stored in the application's **SQLite database**.

> ⚠️ For real-world/public use, add authentication and use a production database before storing real student data.

## 🌐 Live Demo

🚀 **Streamlit App:** https://face-attendance-system-on.streamlit.app/

## 🔮 Future Improvements

- 🔐 Faculty authentication
- ☁️ Cloud database
- 📱 Mobile optimization
- 📧 Attendance notifications
- 📈 Advanced analytics
- ✏️ Manual attendance correction
- 👥 Multiple photos per student
- 🗂️ Admin dashboard

## 👨‍💻 Author

**Paresh Prajapati**

🎓 B.Sc. Information Technology Student  
🤖 AI & ML Enthusiast  
📊 Data & Machine Learning Projects

⭐ **If you like this project, give the repository a star!**

---

### 💡 Built with Python • Streamlit • AI
