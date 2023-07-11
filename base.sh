unameOut="$(uname -s)"
is_macos=false

# https://stackoverflow.com/a/3466183
case "${unameOut}" in
    Linux*) is_macos=false;;
    Darwin*) is_macos=true;;
    *) is_macos=false;;
esac

if [ "$is_macos" = true ]; then
    echo "Installing Brew..."
    curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | bash
    echo "Installing Python..."
    brew install python3
else
    echo "Installing Python..."
    sudo apt-get install -y python3
fi