#!/bin/bash

echo "════════════════════════════════════════════════"
echo "🚀 Opening VS Code with all EducApp services"
echo "════════════════════════════════════════════════"
echo ""

cd ~/Desktop/educapp-mvp

# Open VS Code
code .

# Wait for VS Code to open
sleep 3

# Launch all services in separate Terminal windows
osascript <<'APPLESCRIPT'
tell application "Terminal"
    do script "cd ~/Desktop/educapp-mvp && source /opt/anaconda3/etc/profile.d/conda.sh && conda activate educapp-mvp && streamlit run app.py --server.port 8501"
    do script "cd ~/Desktop/educapp-mvp && source /opt/anaconda3/etc/profile.d/conda.sh && conda activate educapp-mvp && streamlit run admin_dashboard.py --server.port 8502"
    do script "cd ~/Desktop/educapp-mvp && source /opt/anaconda3/etc/profile.d/conda.sh && conda activate educapp-mvp && streamlit run admin_users.py --server.port 8503"
end tell
APPLESCRIPT

echo ""
echo "✅ All services launched!"
echo ""
echo "�� Your URLs:"
echo "   🏠 Main: http://localhost:8501"
echo "   💰 Financial: http://localhost:8502"
echo "   👥 Users: http://localhost:8503"
