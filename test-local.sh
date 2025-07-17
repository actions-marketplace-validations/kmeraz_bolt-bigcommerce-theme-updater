#!/bin/bash

# Test script for local GitHub Action testing with act

echo "🧪 Testing BigCommerce Theme Updater Action locally..."
echo "================================================="

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ act is not installed. Please install it with: brew install act"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one with the required INPUT_* variables."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Clean up any previous test artifacts
echo "🧹 Cleaning up previous test artifacts..."
rm -rf bolt-modified-theme
rm -f bolt-modified-theme.zip
rm -f BOLT_INSTALLATION_GUIDE.md
rm -f bolt_integration_summary.json
rm -rf theme

echo "🚀 Running GitHub Action locally..."
echo ""

# Run the action with act
if act --env-file .env; then
    echo ""
    echo "✅ GitHub Action executed successfully!"
    echo ""
    echo "📁 Generated files:"
    if [ -f "bolt-modified-theme.zip" ]; then
        echo "  ✅ bolt-modified-theme.zip ($(du -h bolt-modified-theme.zip | cut -f1))"
    else
        echo "  ❌ bolt-modified-theme.zip not found"
    fi

    if [ -f "BOLT_INSTALLATION_GUIDE.md" ]; then
        echo "  ✅ BOLT_INSTALLATION_GUIDE.md ($(du -h BOLT_INSTALLATION_GUIDE.md | cut -f1))"
    else
        echo "  ❌ BOLT_INSTALLATION_GUIDE.md not found"
    fi

    if [ -f "bolt_integration_summary.json" ]; then
        echo "  ✅ bolt_integration_summary.json ($(du -h bolt_integration_summary.json | cut -f1))"
        echo ""
        echo "📋 Integration Summary:"
        cat bolt_integration_summary.json | jq . 2>/dev/null || cat bolt_integration_summary.json
    else
        echo "  ❌ bolt_integration_summary.json not found"
    fi
else
    echo "❌ GitHub Action failed to execute"
    exit 1
fi

echo ""
echo "🎉 Local testing completed successfully!"
echo "💡 To use with a real OpenAI API key, update the INPUT_OPENAI_API_KEY in .env"
