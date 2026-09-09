#!/bin/bash

# Configuration
PLIST_PATH="/Library/LaunchDaemons/com.user.talkingclock.plist"
LABEL="com.user.talkingclock"
SCRIPT_PATH="/var/root/projects/py-talkingclock/src/talkingclock/talkingclock.py"
WORK_DIR="/var/root/projects/py-talkingclock/src/talkingclock"
LOG_OUT="/var/log/talkingclock.log"
LOG_ERR="/var/log/talkingclock_err.log"
PYTHON_BIN="$(which python3 2>/dev/null || echo /usr/bin/python3)"

# Ensure root
if [ "$(id -u)" -ne 0 ]; then
    echo "[-] Please run as root (su -)."
    exit 1
fi

install_clock() {
    echo "[*] Checking prerequisites..."
    if [ ! -f "$SCRIPT_PATH" ]; then
        echo "[-] Error: Python script not found at: $SCRIPT_PATH"
        exit 1
    fi

    if [ ! -x "$PYTHON_BIN" ]; then
        echo "[-] Error: Python3 binary not found at: $PYTHON_BIN"
        exit 1
    fi

    echo "[*] Writing plist configuration to $PLIST_PATH..."
    cat << EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>

    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_BIN}</string>
        <string>${SCRIPT_PATH}</string>
    </array>

    <key>WorkingDirectory</key>
    <string>${WORK_DIR}</string>

    <!-- Every hour from 06:00 to 22:00 -->
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>22</integer><key>Minute</key><integer>0</integer></dict>
    </array>

    <key>StandardOutPath</key>
    <string>${LOG_OUT}</string>
    <key>StandardErrorPath</key>
    <string>${LOG_ERR}</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

    echo "[*] Setting file permissions..."
    chown root:wheel "$PLIST_PATH"
    chmod 644 "$PLIST_PATH"

    # Unload if an old instance exists
    launchctl unload "$PLIST_PATH" 2>/dev/null

    echo "[*] Loading service into launchctl..."
    launchctl load -w "$PLIST_PATH"

    if launchctl list | grep -q "$LABEL"; then
        echo "[+] Successfully installed and scheduled!"
        echo "[*] Logs will be written to ${LOG_OUT}"
    else
        echo "[-] Failed to register with launchctl."
    fi
}

uninstall_clock() {
    echo "[*] Unloading service from launchctl..."
    launchctl unload -w "$PLIST_PATH" 2>/dev/null

    if [ -f "$PLIST_PATH" ]; then
        echo "[*] Removing plist file: $PLIST_PATH"
        rm -f "$PLIST_PATH"
    fi

    if ! launchctl list | grep -q "$LABEL"; then
        echo "[+] Successfully uninstalled and removed."
    else
        echo "[-] Warning: Service still appears active in launchctl list."
    fi
}

check_status() {
    echo "=================================================="
    echo "          Talking Clock Daemon Status             "
    echo "=================================================="

    # 1. Check Plist File
    echo -n "[*] Daemon Configuration File: "
    if [ -f "$PLIST_PATH" ]; then
        echo "PRESENT (${PLIST_PATH})"
    else
        echo "NOT FOUND"
    fi

    # 2. Check Launchctl Registration
    echo -n "[*] Launchd Service Status   : "
    LAUNCH_ENTRY=$(launchctl list | grep "$LABEL")
    if [ -n "$LAUNCH_ENTRY" ]; then
        echo "LOADED & ACTIVE"
        PID=$(echo "$LAUNCH_ENTRY" | awk '{print $1}')
        LAST_STATUS=$(echo "$LAUNCH_ENTRY" | awk '{print $2}')
        echo "    - Last Exit Code: $LAST_STATUS"
        [ "$PID" != "-" ] && echo "    - Currently Running (PID: $PID)"
    else
        echo "NOT LOADED"
    fi

    # 3. Check Target Script
    echo -n "[*] Python Target Script     : "
    if [ -f "$SCRIPT_PATH" ]; then
        echo "FOUND (${SCRIPT_PATH})"
    else
        echo "MISSING (${SCRIPT_PATH})"
    fi

    # 4. Schedule summary
    echo "[*] Configured Schedule      : Every hour from 06:00 to 22:00 (Daily)"

    # 5. Summary Verdict
    echo "--------------------------------------------------"
    if [ -f "$PLIST_PATH" ] && [ -n "$LAUNCH_ENTRY" ]; then
        echo "[+] OVERALL: Talking Clock daemon is fully INSTALLED and RUNNING."
    elif [ -f "$PLIST_PATH" ] && [ -z "$LAUNCH_ENTRY" ]; then
        echo "[!] OVERALL: Plist exists, but daemon is NOT LOADED in launchctl."
    else
        echo "[-] OVERALL: Talking Clock daemon is NOT INSTALLED."
    fi
    echo "--------------------------------------------------"

    # 6. Recent Logs (if any)
    if [ -f "$LOG_OUT" ] && [ -s "$LOG_OUT" ]; then
        echo "[*] Last 3 lines of output log (${LOG_OUT}):"
        tail -n 3 "$LOG_OUT" | sed 's/^/    /'
    fi

    if [ -f "$LOG_ERR" ] && [ -s "$LOG_ERR" ]; then
        echo "[!] Recent errors recorded (${LOG_ERR}):"
        tail -n 3 "$LOG_ERR" | sed 's/^/    /'
    fi
    echo "=================================================="
}

test_clock() {
    echo "[*] Triggering immediate run of $LABEL..."
    launchctl start "$LABEL"
    echo "[*] Command sent. Check audio output and logs (${LOG_OUT})."
}

case "$1" in
    1|install)
        install_clock
        ;;
    2|uninstall)
        uninstall_clock
        ;;
    3|status)
        check_status
        ;;
    test)
        test_clock
        ;;
    *)
        echo "Usage: $0 [1|2|3|test]"
        echo "  1 (or install)   : Install and schedule the talking clock"
        echo "  2 (or uninstall) : Stop and completely remove the service"
        echo "  3 (or status)    : Check daemon installation and runtime state"
        echo "  test             : Fire the service immediately once to test audio"
        exit 1
        ;;
esac
