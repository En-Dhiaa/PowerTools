#!/usr/bin/env bash
# ==============================================================================
# Powertool Extended Edition — Debian (.deb) Package Builder
# Developed by En-Dhiaa (https://github.com/En-Dhiaa)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VERSION="0.88.0"
BUILD_DIR="${SCRIPT_DIR}/build/deb"
PKG_DIR="${BUILD_DIR}/powertool_${VERSION}_all"
OUTPUT_DIR="${ROOT_DIR}/release"

echo "=== Building Powertool Debian Package (${VERSION}) ==="
mkdir -p "${OUTPUT_DIR}"
rm -rf "${BUILD_DIR}"
mkdir -p "${PKG_DIR}/DEBIAN"
mkdir -p "${PKG_DIR}/usr/bin"
mkdir -p "${PKG_DIR}/usr/share/powertool/src/modules"
mkdir -p "${PKG_DIR}/usr/share/applications"
mkdir -p "${PKG_DIR}/usr/share/metainfo"
mkdir -p "${PKG_DIR}/usr/share/icons/hicolor/256x256/apps"

# 1. Control file
cp "${SCRIPT_DIR}/debian/control" "${PKG_DIR}/DEBIAN/control"

# 2. Main script and launcher
cp "${SCRIPT_DIR}/powertool-linux.py" "${PKG_DIR}/usr/share/powertool/"
chmod +x "${PKG_DIR}/usr/share/powertool/powertool-linux.py"

# Symlink to /usr/bin/powertool
cat << 'EOF' > "${PKG_DIR}/usr/bin/powertool"
#!/usr/bin/env bash
exec python3 /usr/share/powertool/powertool-linux.py "$@"
EOF
chmod +x "${PKG_DIR}/usr/bin/powertool"

# 3. Copy modules
cp -r "${ROOT_DIR}/src/modules/OfflineTranslator" "${PKG_DIR}/usr/share/powertool/src/modules/"
cp -r "${ROOT_DIR}/src/modules/KeyboardLayoutConverter" "${PKG_DIR}/usr/share/powertool/src/modules/"
cp -r "${ROOT_DIR}/src/modules/LinuxModules" "${PKG_DIR}/usr/share/powertool/src/modules/"

# 4. Copy desktop integration & metadata
cp "${SCRIPT_DIR}/powertool.desktop" "${PKG_DIR}/usr/share/applications/"
cp "${SCRIPT_DIR}/org.endhiaa.Powertool.metainfo.xml" "${PKG_DIR}/usr/share/metainfo/"
if [ -f "${ROOT_DIR}/assets/powertool_branding/PowerTool_256.png" ]; then
    cp "${ROOT_DIR}/assets/powertool_branding/PowerTool_256.png" "${PKG_DIR}/usr/share/icons/hicolor/256x256/apps/powertool.png"
fi

# 5. Build package
echo "[*] Creating Debian package with dpkg-deb..."
dpkg-deb --build --root-owner-group "${PKG_DIR}" "${OUTPUT_DIR}/powertool_${VERSION}_all.deb"

echo "=== Debian Package Successfully Created ==="
echo "Output: ${OUTPUT_DIR}/powertool_${VERSION}_all.deb"

