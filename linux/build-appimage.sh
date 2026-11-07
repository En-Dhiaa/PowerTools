#!/usr/bin/env bash
# ==============================================================================
# Powertool Extended Edition — Linux AppImage Builder
# Developed by En-Dhiaa (https://github.com/En-Dhiaa)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VERSION="0.88.0"
APPDIR="${SCRIPT_DIR}/build/AppDir"
OUTPUT_DIR="${ROOT_DIR}/release"

echo "=== Building Powertool AppImage (${VERSION}) ==="
mkdir -p "${OUTPUT_DIR}"
rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/share/powertool/src/modules"

# Copy AppRun
cp "${SCRIPT_DIR}/AppRun" "${APPDIR}/AppRun"
chmod +x "${APPDIR}/AppRun"

# Copy Desktop file & Icon
cp "${SCRIPT_DIR}/powertool.desktop" "${APPDIR}/powertool.desktop"
if [ -f "${ROOT_DIR}/assets/powertool_branding/PowerTool_256.png" ]; then
    cp "${ROOT_DIR}/assets/powertool_branding/PowerTool_256.png" "${APPDIR}/powertool.png"
    cp "${ROOT_DIR}/assets/powertool_branding/PowerTool_256.png" "${APPDIR}/.DirIcon"
fi

# Copy script and modules
cp "${SCRIPT_DIR}/powertool-linux.py" "${APPDIR}/usr/share/powertool/"
chmod +x "${APPDIR}/usr/share/powertool/powertool-linux.py"

cat << 'EOF' > "${APPDIR}/usr/bin/powertool"
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec python3 "${HERE}/../share/powertool/powertool-linux.py" "$@"
EOF
chmod +x "${APPDIR}/usr/bin/powertool"

cp -r "${ROOT_DIR}/src/modules/OfflineTranslator" "${APPDIR}/usr/share/powertool/src/modules/"
cp -r "${ROOT_DIR}/src/modules/KeyboardLayoutConverter" "${APPDIR}/usr/share/powertool/src/modules/"
cp -r "${ROOT_DIR}/src/modules/LinuxModules" "${APPDIR}/usr/share/powertool/src/modules/"

# AppImage packaging tool
if ! command -v appimagetool &> /dev/null; then
    echo "[*] Downloading appimagetool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O /tmp/appimagetool
    chmod +x /tmp/appimagetool
    APPIMAGETOOL="/tmp/appimagetool"
else
    APPIMAGETOOL="appimagetool"
fi

echo "[*] Generating AppImage bundle..."
ARCH=x86_64 "${APPIMAGETOOL}" "${APPDIR}" "${OUTPUT_DIR}/Powertool-${VERSION}-x86_64.AppImage"

echo "=== AppImage Successfully Created ==="
echo "Output: ${OUTPUT_DIR}/Powertool-${VERSION}-x86_64.AppImage"

