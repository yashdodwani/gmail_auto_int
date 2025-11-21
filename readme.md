# Gmail Rule Engine (HappyFox Assignment)

A standalone Python script that integrates with the Gmail API to classify and process emails based on user-defined rules stored in a database.

## 🚀 Features
- **Gmail API Integration:** Securely authenticates using OAuth 2.0.
- **Database Storage:** Stores fetched emails in PostgreSQL (Neon DB) to avoid redundant API calls.
- **Rule Engine:** Supports complex rules with `All` and `Any` predicates.
- **Actions:** Can automatically mark emails as Read/Unread or Move them to labels (Trash, Important, Starred).
- **Date Parsing:** Handles relative date queries (e.g., "emails less than 2 days old").

## 🛠️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yashdodwani/gmail_auto_int
cd gmail_auto_int
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
Create a `.env` file in the root directory and add your database connection string:
```bash
NEON_DATABASE_URL=postgres://user:pass@endpoint/dbname
```

### 4. Google Credentials
Note: `credentials.json` is not included in this repo for security reasons.

Please obtain your OAuth 2.0 Client ID file from the Google Cloud Console.
Rename it to `credentials.json` and place it in the root directory.

## 🏃‍♂️ Usage

### Step 1: Authenticate & Fetch Emails
This script performs the OAuth handshake (first run only), fetches recent emails from Gmail, and stores them in the local database.
```bash
python fetch_emails.py
```

### Step 2: Process Rules
This script reads the rules defined in `rules.json`, queries the local database for matches, and executes the corresponding actions via the Gmail API.
```bash
python process_emails.py
```

## 🧪 Running Tests
To verify the rule engine logic (string and date comparisons) without making external API calls:
```bash
python tests.py
```

## 📂 Project Structure
`auth.py`: Handles Google OAuth 2.0 authentication.

`fetch_emails.py`: Connects to Gmail API and inserts data into Postgres.

`process_emails.py`: Main logic to evaluate rules and execute actions.

`db.py`: Database connection and schema management.

`rules.json`: Configuration file for defining rules.
