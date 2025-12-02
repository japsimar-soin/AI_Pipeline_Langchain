#!/bin/bash

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your API keys!"
fi

if [ ! -f "pdf_doc.pdf" ]; then
    echo "Warning: pdf_doc.pdf not found. Please add a PDF file to the project root."
fi

echo "Setup complete!"

