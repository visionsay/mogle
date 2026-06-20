#!/bin/bash

set -e

echo "======================================"
echo " Mac 앱 자동 설치 스크립트"
echo "======================================"
echo ""

# Homebrew 설치 확인 및 설치
if ! command -v brew &> /dev/null; then
    echo "[1/2] Homebrew 설치 중..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Apple Silicon Mac의 경우 PATH 설정
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    echo "Homebrew 설치 완료!"
else
    echo "[1/2] Homebrew 이미 설치되어 있음. 업데이트 중..."
    brew update
fi

echo ""
echo "[2/2] 앱 설치 시작..."
echo ""

APPS=(
    "rectangle"
    "raycast"
    "alt-tab"
    "iterm2"
    "visual-studio-code"
    "lm-studio"
    "keka"
    "appcleaner"
    "shottr"
    "keycastr"
)

for app in "${APPS[@]}"; do
    echo "설치 중: $app"
    brew install --cask "$app" 2>/dev/null || echo "  -> $app 설치 실패 또는 이미 설치됨"
done

echo ""
echo "======================================"
echo " 자동 설치 완료!"
echo "======================================"
echo ""
echo "아래 앱은 수동으로 설치해야 합니다:"
echo ""
echo "  [App Store에서 설치]"
echo "  - ScreenBrush  : 화면 판서/필기 (강의용 최추천)"
echo "  - Presentify   : 커서 강조, 화면 판서"
echo ""
echo "  [공식 웹사이트에서 설치]"
echo "  - MacWhisper   : https://goodsnooze.gumroad.com/l/macwhisper"
echo "  - Superwhisper : https://superwhisper.com"
echo "  - Epic Pen     : https://epicpen.com"
echo ""
echo "  [App Store 또는 웹사이트]"
echo "  - Cursor Pro   : 마우스 커서 강조 효과"
echo ""
echo "설치된 앱들은 /Applications 폴더에서 확인하세요."
