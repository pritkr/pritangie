#!/usr/bin/env bash
# ==============================================================================
# publish_projects_to_github.sh
# Automates preparing and publishing the 4 standalone frontier projects to GitHub:
# 1. sentinel-mcp -> https://github.com/pritkr/sentinel-mcp
# 2. dhvani-eval   -> https://github.com/pritkr/dhvani-eval
# 3. pebble-sync   -> https://github.com/pritkr/pebble-sync
# 4. spec-forge    -> https://github.com/pritkr/spec-forge
# ==============================================================================

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/projects"
PROJECTS=("sentinel-mcp" "dhvani-eval" "pebble-sync" "spec-forge")

echo "========================================================================"
echo "  FRONTIER PROJECTS GITHUB PUBLISHING HELPER"
echo "========================================================================"
echo "Base Directory: $BASE_DIR"
echo

publish_project() {
    local proj="$1"
    local dir="$BASE_DIR/$proj"

    if [ ! -d "$dir" ]; then
        echo "[-] Project directory not found: $dir"
        return 1
    fi

    echo "------------------------------------------------------------------------"
    echo "[+] Preparing standalone repository for: $proj"
    echo "    Path: $dir"
    echo "------------------------------------------------------------------------"

    cd "$dir"

    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        echo "    Initializing git repo..."
        git init -b main
    fi

    git add .
    git commit -m "feat: initial commit of $proj ($proj core, benchmarks, tests, CI/CD)" || true

    echo "    Ready to publish with GitHub CLI:"
    echo "    Run: cd \"$dir\" && gh repo create \"pritkr/$proj\" --public --source=. --remote=origin --push"
    echo
}

if [ "${1:-all}" == "all" ]; then
    for p in "${PROJECTS[@]}"; do
        publish_project "$p"
    done
else
    publish_project "$1"
fi

echo "========================================================================"
echo "  All 4 project repositories are prepared with standalone Git history!"
echo "========================================================================"
