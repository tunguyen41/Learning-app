# 📚 Spaced-Repetition Vocabulary App

A simple Tkinter-based app that uses **Spaced Repetition** to help you remember vocabulary longer. Data is stored in **PostgreSQL** with automatic scheduling via triggers.

---

## 🚀 Features
- Add, edit, delete, and search vocabulary.
- Day-based review (Day 2, 4, 7, 12, 21).
- Auto-move words between review days.
- Track progress automatically.

---

## 🛠 Tech Stack
- Python 3 + Tkinter
- PostgreSQL + psycopg2
- SQL triggers & functions

---

## ⚙️ Setup
1. **Create database & tables**  
   Run `schema.sql` in PostgreSQL.
2. **Install dependencies**  
   ```bash
   pip install psycopg2
