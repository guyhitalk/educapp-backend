#!/bin/bash

echo "════════════════════════════════════════════════"
echo "💰 Starting Financial Dashboard"
echo "════════════════════════════════════════════════"
echo ""
echo "📍 URL: http://localhost:8502"
echo "🔐 Password: educapp2024"
echo ""

cd ~/Desktop/educapp-mvp
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate educapp-mvp
streamlit run admin_dashboard.py --server.port 8502
