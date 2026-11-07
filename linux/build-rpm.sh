#!/usr/bin/env bash
# ==============================================================================
# Powertool Extended Edition — RPM Package Builder
# Developed by En-Dhiaa (https://github.com/En-Dhiaa)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VERSION="0.88.0"
RPM_TOP="${SCRIPT_DIR}/build/rpmbuild"
OUTPUT_DIR="${ROOT_DIR}/release"

echo "=== Building Powertool RPM Package (${VERSION}) ==="
mkdir -p "${OUTPUT_DIR}"
rm -rf "${RPM_TOP}"
mkdir -p "${RPM_TOP}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Copy spec file
cp "${SCRIPT_DIR}/powertool.spec" "${RPM_TOP}/SPECS/"

# Create source tarball
TAR_NAME="powertool-${VERSION}"
TMP_TAR_DIR="/tmp/${TAR_NAME}"
rm -rf "${TMP_TAR_DIR}"
mkdir -p "${TMP_TAR_DIR}"

cp -r "${ROOT_DIR}/src" "${TMP_TAR_DIR}/"
cp -r "${ROOT_DIR}/linux" "${TMP_TAR_DIR}/"
cp -r "${ROOT_DIR}/assets" "${TMP_TAR_DIR}/"

tar -czf "${RPM_TOP}/SOURCES/${TAR_NAME}.tar.gz" -C /tmp "${TAR_NAME}"
rm -rf "${TMP_TAR_DIR}"

# Build RPM
echo "[*] Running rpmbuild..."
rpmbuild --define "_topdir ${RPM_TOP}" -ba "${RPM_TOP}/SPECS/powertool.spec"

cp "${RPM_TOP}"/RPMS/*/*.rpm "${OUTPUT_DIR}/"
echo "=== RPM Package Successfully Created ==="
echo "Output in ${OUTPUT_DIR}"
