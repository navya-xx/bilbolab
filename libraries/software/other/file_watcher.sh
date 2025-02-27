#!/bin/bash

WATCH_DIR="/mnt/storage"
TARGET_DIR="/home/admin/copied_files"
STORAGE_IMG="/home/admin/storage.img"
PATTERN="*.bin"  # Adjust this pattern as needed

mkdir -p "$WATCH_DIR"
mkdir -p "$TARGET_DIR"

echo "Monitoring $WATCH_DIR for files matching $PATTERN..."

while true; do
    # Sync: Unmount, Remount, and Sync the Image
    if mount | grep -q "$WATCH_DIR"; then
        sudo umount "$WATCH_DIR"
    fi
    sudo mount -o loop,rw "$STORAGE_IMG" "$WATCH_DIR"
    sync
    sleep 1  # Allow time for sync to complete

    # Check for Existing Files Matching the Pattern
    for file in "$WATCH_DIR"/*; do
        if [[ "$file" == $WATCH_DIR/$PATTERN ]]; then
            echo "File detected: $(basename "$file")"
            cp "$file" "$TARGET_DIR/"
            echo "Copied $(basename "$file") to $TARGET_DIR"
        fi
    done

    # Watch for New Files Matching the Pattern
    inotifywait -m -e create "$WATCH_DIR" --format '%f' |
    while read NEW_FILE; do
        if [[ "$NEW_FILE" == $PATTERN ]]; then
            echo "New file detected: $NEW_FILE"
            cp "$WATCH_DIR/$NEW_FILE" "$TARGET_DIR/"
            echo "Copied $NEW_FILE to $TARGET_DIR"
        fi
    done

    # Allow some delay before checking again
    sleep 10
done

