#!/bin/bash
# Install Nerd Fonts for better provider icons

set -e

echo "=========================================="
echo "Installing Nerd Fonts"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    FONTS_DIR="$HOME/.local/share/fonts"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    FONTS_DIR="$HOME/Library/Fonts"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

# Create fonts directory
mkdir -p "$FONTS_DIR"

# Download and install JetBrains Mono Nerd Font (popular choice)
FONT_NAME="JetBrainsMono"
FONT_URL="https://github.com/ryanoasis/nerd-fonts/releases/latest/download/${FONT_NAME}.zip"

echo "📦 Downloading $FONT_NAME Nerd Font..."
cd /tmp
curl -fLo "${FONT_NAME}.zip" "$FONT_URL"

echo "📂 Extracting fonts..."
unzip -o "${FONT_NAME}.zip" -d "$FONT_NAME"

echo "💾 Installing fonts to $FONTS_DIR..."
cp "$FONT_NAME"/*.ttf "$FONTS_DIR/" 2>/dev/null || true

# Update font cache (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔄 Updating font cache..."
    fc-cache -f "$FONTS_DIR"
fi

# Cleanup
rm -rf "${FONT_NAME}.zip" "$FONT_NAME"

echo ""
echo "✅ Nerd Font installed successfully!"
echo ""
echo "📝 Next steps:"
echo "   1. Restart your terminal"
echo "   2. Set your terminal font to 'JetBrainsMono Nerd Font'"
echo "   3. Run: ./agent chat"
echo ""
echo "Terminal-specific instructions:"
echo ""
echo "  GNOME Terminal:"
echo "    Preferences → Profiles → Text → Font → Select 'JetBrainsMono Nerd Font'"
echo ""
echo "  iTerm2 (macOS):"
echo "    Preferences → Profiles → Text → Font → Select 'JetBrainsMono Nerd Font'"
echo ""
echo "  Windows Terminal:"
echo "    Settings → Profiles → Appearance → Font face → 'JetBrainsMono Nerd Font'"
echo ""
echo "  Alacritty:"
echo "    Edit ~/.config/alacritty/alacritty.yml:"
echo "    font:"
echo "      normal:"
echo "        family: JetBrainsMono Nerd Font"
echo ""
