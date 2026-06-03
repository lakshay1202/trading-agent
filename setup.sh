#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  AI Backtesting Agent — One-click Git + VS Code setup
#  Run this from inside the trading-agent folder:
#    bash setup.sh
# ─────────────────────────────────────────────────────────────

set -e   # stop on any error

echo ""
echo "════════════════════════════════════════"
echo "  AI Backtesting Agent — Setup Script  "
echo "════════════════════════════════════════"
echo ""

# ── 1. Collect GitHub info ────────────────────────────────────
read -p "Enter your GitHub username: " GH_USER
read -p "Enter your GitHub email: " GH_EMAIL
read -p "Enter your new GitHub repo name (e.g. trading-agent): " GH_REPO

echo ""
echo "You'll need a GitHub Personal Access Token to push."
echo "Create one at: https://github.com/settings/tokens/new"
echo "  → Scopes needed: ✅ repo"
echo ""
read -s -p "Paste your GitHub Personal Access Token (hidden): " GH_TOKEN
echo ""

# ── 2. Initialize git ─────────────────────────────────────────
echo ""
echo "▶ Initializing git repository..."
git init
git config user.name  "$GH_USER"
git config user.email "$GH_EMAIL"
git branch -M main

# ── 3. First commit ───────────────────────────────────────────
echo "▶ Staging and committing all files..."
git add .
git commit -m "Initial commit — AI Backtesting Agent MVP"

# ── 4. Link remote and push ───────────────────────────────────
echo "▶ Connecting to GitHub..."
REMOTE="https://${GH_USER}:${GH_TOKEN}@github.com/${GH_USER}/${GH_REPO}.git"
git remote add origin "$REMOTE"

echo "▶ Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Code pushed to: https://github.com/${GH_USER}/${GH_REPO}"

# ── 5. Set up Python virtual environment ─────────────────────
echo ""
echo "▶ Creating Python virtual environment..."
python3 -m venv venv

echo "▶ Activating venv and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt

echo ""
echo "════════════════════════════════════════"
echo "  ✅ All done! Here's what to do next:  "
echo "════════════════════════════════════════"
echo ""
echo "  1. Open VS Code:"
echo "     code ."
echo ""
echo "  2. In VS Code: Ctrl+Shift+P → 'Python: Select Interpreter'"
echo "     → choose the one inside ./venv"
echo ""
echo "  3. Run the app:"
echo "     source venv/bin/activate && streamlit run app.py"
echo ""
echo "  4. Deploy free to Streamlit Cloud:"
echo "     → https://share.streamlit.io"
echo "     → Connect your GitHub repo: ${GH_USER}/${GH_REPO}"
echo "     → Main file: app.py → Deploy!"
echo ""
