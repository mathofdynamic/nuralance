<!-- Banner -->
<p align="center">
  <img src="media/banner.png" alt="Nuralance Banner" style="max-width: 100%; height: auto;">
</p>

# Nuralance: AI-Powered Financial Data Analysis Web App

## Overview
Nuralance is a next-generation, AI-powered web application for financial data analysis. Upload your CSV files, store and analyze them securely, and interact with your data using a conversational AI assistant. Nuralance is designed for finance professionals, analysts, and anyone who wants to explore, query, and gain insights from their financial data interactively and intuitively.

---

## 🚀 Features
- **Intelligent CSV Upload & Parsing:** Upload financial data in CSV format. The app automatically parses, validates, and stores your data securely in a session-specific SQLite database.
- **AI Chatbot (OpenAI-Powered):** Ask complex questions about your data in natural language. The chatbot understands context, generates SQL queries, and provides clear, actionable answers.
- **Automated Data Analysis:** The backend analyzes your data structure and generates a custom system prompt for the AI, enabling deep, context-aware insights.
- **Secure Session Management:** Each user session is isolated, with its own database and state, ensuring privacy and data separation.
- **Modern, Responsive UI:** Clean, user-friendly interface with real-time chat, file upload, and status updates. Built with FastAPI, Jinja2, and custom JS/CSS.
- **Extensible Architecture:** Modular codebase with clear separation of concerns (routers, services, state, static, templates).
- **Rich Output:** Supports markdown-formatted answers, tables, and summaries in chat.
- **Error Handling & Validation:** Robust error messages and validation for file uploads, queries, and API usage.

---

## 🏗️ Architecture & Technology Stack
- **Backend:** Python 3.10+, FastAPI, SQLite, OpenAI API, python-dotenv
- **Frontend:** Jinja2 templates, Vanilla JS, marked.js (for markdown rendering), CSS3
- **Session & State:** In-memory session management (can be extended to Redis/DB for production)
- **File Storage:** Uploaded CSVs and generated SQLite DBs are stored per session (and git-ignored for privacy)
- **API Structure:**
  - `/` — Main chat UI
  - `/upload-csv` — CSV upload endpoint
  - `/message` — Chatbot message endpoint (via router)

---

## 📂 Project Structure
```
Nuralance/
├── app/
│   ├── main.py                # FastAPI app entry point, UI, upload logic
│   ├── state.py               # Session and thread state management
│   ├── routers/
│   │   └── chatbot_router.py  # API endpoints for chat
│   ├── services/
│   │   ├── db_analysis_service.py      # CSV→SQLite, schema analysis, prompt gen
│   │   ├── openai_service.py          # OpenAI API integration, thread mgmt
│   │   └── query_execution_service.py # Secure SQL query execution
│   ├── csv_uploads/           # Uploaded CSVs (per session, git-ignored)
│   └── db_storage/            # SQLite DBs (per session, git-ignored)
├── static/
│   ├── script.js              # Frontend logic (chat, upload, UI)
│   └── style.css              # Custom styles
├── templates/
│   └── index.html             # Main UI template
├── media/
│   └── banner.png             # Project banner for README
├── requirements.txt           # Python dependencies
├── sample_finance.csv         # Example CSV (git-ignored)
└── .gitignore                 # Ignore rules
```

---

## ⚙️ Installation & Setup
### Prerequisites
- Python 3.10+
- [pip](https://pip.pypa.io/en/stable/)

### 1. Clone the Repository
```bash
git clone <repo-url>
cd Nuralance
```

### 2. Create a Virtual Environment
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
ASSISTANT_ID=your_openai_assistant_id_here
```

### 5. Run the Application
```bash
uvicorn app.main:app --reload
```
Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🖥️ Usage Guide
1. **Open the app** in your browser.
2. **Upload a CSV file** with your financial data.
3. **Wait for analysis:** The app parses your file, creates a session database, and prepares the AI assistant.
4. **Chat with the AI:** Ask questions like:
   - "What was my highest expense in Q1 2024?"
   - "Show total sales by category."
   - "Which customer spent the most?"
5. **View results:** Answers are shown in chat, with tables and summaries as needed.

> **Tip:** Try the included `sample_finance.csv` for a quick demo!

---

## 🧩 API Endpoints
| Endpoint         | Method | Description                                 |
|------------------|--------|---------------------------------------------|
| `/`              | GET    | Main chat UI (HTML)                         |
| `/upload-csv`    | POST   | Upload CSV, initialize session, analyze data|
| `/message`       | POST   | Send chat message, get AI response          |

---

## 🛠️ Customization & Extensibility
- **Change AI Model:** Edit `ANALYZER_MODEL` in `db_analysis_service.py` or update OpenAI settings in `.env`.
- **Production Session Storage:** Swap in Redis or a DB for `USER_SESSIONS` in `state.py`.
- **UI/UX:** Modify `static/style.css` and `templates/index.html` for branding.
- **Add More Tools:** Extend `openai_service.py` and `query_execution_service.py` for new AI or DB features.

---

## 🧪 Example CSV Format
```csv
sale_id,customer_name,product_name,category,sale_date,quantity_sold,unit_price,total_sale_amount
1,"John Doe","Accounting Pro Subscription","Software","2024-03-10",12,49.99,599.88
2,"Jane Smith","Premium Wireless Keyboard","Electronics","2024-05-21",2,79.99,159.98
```

---

## 🧱 Technologies Used
- **FastAPI** — High-performance Python web framework
- **OpenAI API** — Natural language understanding and code generation
- **SQLite** — Lightweight, session-based data storage
- **Jinja2** — HTML templating
- **Vanilla JS & marked.js** — Dynamic frontend, markdown rendering
- **python-dotenv** — Secure environment variable management

---

## 🔒 Security & Privacy
- Uploaded files and databases are stored locally and ignored by git.
- API keys and sensitive data are kept in `.env` (never commit this file).
- Only SELECT SQL queries are allowed for safety.

---

## 🧑‍💻 Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes.
4. Push to your fork and submit a pull request.

---

## 📄 License
[MIT License](LICENSE)

---

## 📬 Contact & Support
For questions, feature requests, or support, open an issue or contact the maintainer.

---

## 🙋 FAQ
**Q: Can I use this with other data types?**  
A: The app is optimized for financial CSVs, but you can upload any tabular CSV. For best results, use clear headers.

**Q: How do I deploy this in production?**  
A: Use a production server (e.g., Gunicorn), secure your `.env`, and use persistent session storage (like Redis).

**Q: Is my data private?**  
A: Yes. All uploads and databases are local and never committed to git.

---

<p align="center"><sub>Made with ❤️ by the Nuralance Team</sub></p>
