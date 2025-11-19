#!/bin/bash

echo "════════════════════════════════════════════════"
echo "🏠 Starting EducApp Main Application"
echo "════════════════════════════════════════════════"
echo ""
echo "📍 URL: http://localhost:8501"
echo ""

cd ~/Desktop/educapp-mvp
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate educapp-mvp
streamlit run app.py --server.port 8501
