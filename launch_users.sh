#!/bin/bash

echo "════════════════════════════════════════════════"
echo "👥 Starting User Management Dashboard"
echo "════════════════════════════════════════════════"
echo ""
echo "📍 URL: http://localhost:8503"
echo "🔐 Password: educapp2024"
echo ""

cd ~/Desktop/educapp-mvp
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate educapp-mvp
streamlit run admin_users.py --server.port 8503
