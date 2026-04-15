#!/bin/bash
set -e

# This script downloads the argocd CLI.

OS="$(uname | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

if [[ "$ARCH" == "x86_64" ]]; then
    ARCH="amd64"
elif [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    ARCH="arm64"
fi

if [[ "$OS" == "linux" || "$OS" == "darwin" ]]; then
    VERSION=$(curl -L -s https://raw.githubusercontent.com/argoproj/argo-cd/stable/VERSION)
    if [[ -z "$VERSION" ]]; then
        echo "Failed to get ArgoCD version."
        exit 1
    fi
    echo "Downloading ArgoCD version v$VERSION for $OS-$ARCH..."
    curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/download/v$VERSION/argocd-$OS-$ARCH
    chmod +x argocd
    echo "Installed argocd in the current directory."
    echo "You can move it to your PATH: sudo mv argocd /usr/local/bin/"
else
    echo "Unsupported OS: $OS"
    exit 1
fi
