#!/bin/bash
# Script to help with documentation translation

# Exit on error
set -e

# Check for required commands
for cmd in sphinx-build sphinx-intl; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is not installed. Please install it first."
        exit 1
    fi
done

# Configuration
LOCALE_DIR="locale"
LANGUAGES=("it")  # Add more languages as needed

# Function to display usage
usage() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  extract    - Extract translatable strings"
    echo "  update     - Update translation files"
    echo "  compile    - Compile translations"
    echo "  build      - Build documentation in all languages"
    echo "  clean      - Clean build files"
    echo "  all        - Run extract, update, compile, and build"
    exit 1
}

# Function to extract translatable strings
extract_strings() {
    echo "Extracting translatable strings..."
    make gettext
    echo "Done extracting strings to _build/locale/"
}

# Function to update translation files
update_translations() {
    echo "Updating translation files..."
    for lang in "${LANGUAGES[@]}"; do
        echo "Updating $lang..."
        sphinx-intl update -p _build/locale -l $lang -d $LOCALE_DIR
    done
    echo "Translation files updated in $LOCALE_DIR/"
}

# Function to compile translations
compile_translations() {
    echo "Compiling translations..."
    for lang in "${LANGUAGES[@]}"; do
        echo "Compiling $lang..."
        sphinx-intl build --locale-dir $LOCALE_DIR
    done
    echo "Translations compiled"
}

# Function to build documentation in all languages
build_docs() {
    echo "Building documentation..."
    
    # Build English (default)
    echo "Building English documentation..."
    make html
    
    # Build other languages
    for lang in "${LANGUAGES[@]}"; do
        echo "Building $lang documentation..."
        make -e SPHINXOPTS="-D language=$lang" html
    done
    
    echo "Documentation built in _build/html/"
}

# Function to clean build files
clean_build() {
    echo "Cleaning build files..."
    make clean
    echo "Build files cleaned"
}

# Main script
case "$1" in
    extract)
        extract_strings
        ;;
    update)
        update_translations
        ;;
    compile)
        compile_translations
        ;;
    build)
        build_docs
        ;;
    clean)
        clean_build
        ;;
    all)
        extract_strings
        update_translations
        compile_translations
        build_docs
        ;;
    *)
        usage
        ;;
esac

exit 0
