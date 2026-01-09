#!/bin/bash
# Startup script for Streamlit on Azure App Service

# Run Streamlit with Azure App Service compatible settings
python -m streamlit run src/app.py \
    --server.port=${WEBSITES_PORT:-8000} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
