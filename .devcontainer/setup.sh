#!/usr/bin/env bash
# Per-create setup for the RDL Plugin Sandbox devcontainer.
#
# Runs once after container create (see devcontainer.json postCreateCommand).
# The /home/node/.claude directory is a named volume, so it starts empty on
# first boot — this script seeds it with skill symlinks, runs lefthook install,
# and pre-builds asctl into ~/.local/bin for the interactive shell.
set -euo pipefail

REPO=/workspace
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
LOCAL_BIN="$HOME/.local/bin"

mkdir -p "$CLAUDE_DIR/skills" "$LOCAL_BIN"

echo "==> Linking skills into $CLAUDE_DIR/skills"
for skill in "$REPO"/skills/*/; do
  name=$(basename "$skill")
  target="$CLAUDE_DIR/skills/$name"
  if [ -L "$target" ] || [ -e "$target" ]; then
    rm -rf "$target"
  fi
  ln -s "$skill" "$target"
done

echo "==> Installing pixi environments"
cd "$REPO"
pixi install

echo "==> Installing lefthook git hooks"
lefthook install

echo "==> Building asctl → $LOCAL_BIN/asctl"
cd "$REPO/tools/asctl"
go build -o "$LOCAL_BIN/asctl" .

case ":$PATH:" in
  *":$LOCAL_BIN:"*) ;;
  *) echo "export PATH=\"$LOCAL_BIN:\$PATH\"" >> "$HOME/.zshrc" ;;
esac

echo "==> Setup complete. Skills linked: $(find "$CLAUDE_DIR/skills" -maxdepth 1 -type l | wc -l)"
