# Contributing to Clazzy

Thank you for your interest in contributing to **Clazzy** — the AI-Powered Fashion & Outfit Recommendation Companion!

We welcome contributions from developers, designers, fashion technologists, and ML enthusiasts of all experience levels.

---

## 📋 Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone. Please be respectful and constructive in all discussions and pull requests.

---

## 🛠️ Development Setup

### Prerequisites
- **Node.js**: v18.0.0 or higher (v20+ recommended)
- **Python**: 3.10+
- **npm** or **pnpm** / **yarn**
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/mohamedirsath07/Clazzy.git
cd Clazzy
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
> **Security Notice**: Never commit sensitive API keys or database connection strings to git. Ensure `.env` is ignored.

### 3. Install Dependencies
```bash
# Frontend & Node dependencies
npm install

# Python Backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 4. Running the Project Locally
- **Frontend / Client**:
  ```bash
  npm run dev:client
  # Available at http://localhost:5173
  ```
- **Python ML Backend**:
  ```bash
  cd backend
  python main.py
  # ML server runs at http://localhost:8000
  ```

---

## 🧪 Running Tests

Always verify tests pass before opening a Pull Request:

```bash
# Run Frontend Unit Tests
npm test

# Run Python Backend Unit Tests
npm run test:backend
# or
python -m pytest backend/tests
```

---

## 🌿 Git Workflow & Conventional Commits

We follow standard GitHub flow and conventional commit standards:

### Commit Message Format
```
<type>(<scope>): <short description>
```

**Types:**
- `feat`: A new feature (e.g., `feat(recommender): add seasonal weather weighting`)
- `fix`: A bug fix (e.g., `fix(color): correct HSL boundary for split-complementary`)
- `docs`: Documentation updates (e.g., `docs(readme): add architecture diagram`)
- `refactor`: Code reorganization with no behavior changes
- `test`: Adding or updating test suites
- `chore`: Dependency updates, tooling, or config changes

### Branch Naming Convention
- `feature/<feature-name>`
- `fix/<bug-description>`
- `docs/<doc-topic>`

---

## 🚀 Submitting a Pull Request

1. Fork the repository and create your branch from `main`.
2. Ensure your changes adhere to project style and all tests pass.
3. Open a Pull Request against `main` with:
   - A clear title following conventional commit naming.
   - A concise summary of changes and rationale.
   - Any relevant screenshots or test results.
4. Respond to review feedback constructively.

Thank you for helping make Clazzy even better!
