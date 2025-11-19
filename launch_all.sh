#!/bin/bash

echo "════════════════════════════════════════════════"
echo "🚀 Launching All EducApp Services"
echo "════════════════════════════════════════════════"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Launch Main App
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && source /opt/anaconda3/etc/profile.d/conda.sh && conda activate educapp-mvp && streamlit run app.py --server.port 8501\""

sleep 2

# Launch Financial Dashboard
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && source /opt/anaconda3/etc/profile.d/conda.sh && conda activate educapp-mvp && streamlit run admin_dashboard.py --server.port 8502\""

sleep 2

# Launch User Management
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && source /opt/anaconda3/etc/profile.d/conda.sh && conda activate educapp-mvp && streamlit run admin_users.py --server.port 8503\""

echo ""
echo "✅ All services launched!"
echo ""
echo "📌 Your URLs:"
echo "   🏠 Main: http://localhost:8501"
echo "   💰 Financial: http://localhost:8502"
echo "   👥 Users: http://localhost:8503"
