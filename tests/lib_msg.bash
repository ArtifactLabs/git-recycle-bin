#!/usr/bin/env bash
# Common messaging functions and color definitions for test scripts

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
info()    { echo -e "${BLUE}[INFO @ $PWD]${NC} $*" >&2; }
success() { echo -e "${GREEN}[SUCCESS @ $PWD]${NC} $*" >&2; }
error()   { echo -e "${RED}[ERROR @ $PWD]${NC} $*" >&2; exit 1; }
debug()   { echo -e "${BLUE}[DEBUG @ $PWD]${NC} $*" >&2; }