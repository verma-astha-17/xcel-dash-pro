#!/bin/bash
# Quick Start Guide for AI Use Case Portfolio Dashboard

echo "================================"
echo "AI Use Case Portfolio Dashboard"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null
then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python --version)"
echo ""

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🚀 Starting Streamlit app..."
    echo ""
    streamlit run app.py
else
    echo "❌ Failed to install dependencies."
    exit 1
fi
