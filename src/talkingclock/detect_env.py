import os
import sys
import platform

def is_ios():
    """Check if the underlying platform is iOS (Darwin kernel + mobile OS)."""
    if sys.platform != "darwin":
        return False
    # Check for iOS-specific kernel release or device architecture
    machine = platform.machine() # e.g., 'iPad4,4', 'arm64', 'iPhone6,1'
    return any(machine.startswith(prefix) for prefix in ("iPad", "iPhone", "iPod", "arm64", "armv7"))

def is_jailbroken():
    """Detect presence of common jailbreak filesystem paths and Cydia artifacts."""
    jailbreak_indicators = [
        "/Applications/Cydia.app",
        "/Library/MobileSubstrate/MobileSubstrate.dylib",
        "/var/lib/cydia",
        "/etc/apt",
        "/bin/bash",
        "/usr/libexec/cydia",
    ]
    return any(os.path.exists(path) for path in jailbreak_indicators)

def is_terminal_session():
    """Check if standard output is an interactive terminal or an active SSH shell."""
    is_tty = sys.stdout.isatty()
    has_ssh = "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ
    has_term = bool(os.environ.get("TERM"))
    return is_tty or has_ssh or has_term

def detect_cydia_terminal():
    ios = is_ios()
    jb = is_jailbroken()
    term = is_terminal_session()

    print(f"[*] iOS Platform       : {ios} ({platform.machine()})")
    print(f"[*] Jailbreak Detected : {jb}")
    print(f"[*] Terminal/SSH Active: {term}")

    if ios and jb and term:
        print("\n[+] SUCCESS: Running inside an iOS Jailbreak / Cydia Terminal session.")
        return True
    elif ios and jb and not term:
        print("\n[-] Running on a jailbroken iOS device, but NOT in a terminal (e.g., launchd daemon).")
        return False
    else:
        print("\n[-] Standard host environment (Not an iOS Jailbroken terminal).")
        return False

if __name__ == "__main__":
    detect_cydia_terminal()
