#!/usr/bin/env python3
import sys
import os
import time
import argparse
import ctypes

# 1. Load native dynamic libraries
objc = ctypes.cdll.LoadLibrary('/usr/lib/libobjc.A.dylib')
ctypes.cdll.LoadLibrary('/System/Library/Frameworks/AVFoundation.framework/AVFoundation')

objc.objc_getClass.restype = ctypes.c_void_p
objc.objc_getClass.argtypes = [ctypes.c_char_p]

objc.sel_registerName.restype = ctypes.c_void_p
objc.sel_registerName.argtypes = [ctypes.c_char_p]

objc.objc_msgSend.restype = ctypes.c_void_p
objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

def setup_audio_session():
    """Sets AVAudioSession to Playback mode to bypass low ringer limits."""
    AVAudioSession = objc.objc_getClass(b'AVAudioSession')
    NSString = objc.objc_getClass(b'NSString')

    sel_sharedInstance = objc.sel_registerName(b'sharedInstance')
    sel_stringWithUTF8 = objc.sel_registerName(b'stringWithUTF8String:')
    sel_setCategory_error = objc.sel_registerName(b'setCategory:error:')
    sel_setActive_error = objc.sel_registerName(b'setActive:error:')

    # [AVAudioSession sharedInstance]
    session = objc.objc_msgSend(AVAudioSession, sel_sharedInstance)

    # NSString *category = @"AVAudioSessionCategoryPlayback";
    func_stringWithUTF8 = ctypes.cast(
        objc.objc_msgSend,
        ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p)
    )
    category_ns = func_stringWithUTF8(NSString, sel_stringWithUTF8, b'AVAudioSessionCategoryPlayback')

    # [session setCategory:category error:nil]
    func_setCategory = ctypes.cast(
        objc.objc_msgSend,
        ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
    )
    func_setCategory(session, sel_setCategory_error, category_ns, None)

    # [session setActive:YES error:nil]
    func_setActive = ctypes.cast(
        objc.objc_msgSend,
        ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p)
    )
    func_setActive(session, sel_setActive_error, True, None)

def play_audio(file_path, software_volume=1.0):
    abs_path = os.path.abspath(file_path)
    if not os.path.isfile(abs_path):
        print(f"[-] File not found: {abs_path}", file=sys.stderr)
        sys.exit(1)

    # Activate maximum media gain channel
    setup_audio_session()

    NSString = objc.objc_getClass(b'NSString')
    NSURL = objc.objc_getClass(b'NSURL')
    AVAudioPlayer = objc.objc_getClass(b'AVAudioPlayer')

    sel_stringWithUTF8 = objc.sel_registerName(b'stringWithUTF8String:')
    sel_fileURLWithPath = objc.sel_registerName(b'fileURLWithPath:')
    sel_alloc = objc.sel_registerName(b'alloc')
    sel_init = objc.sel_registerName(b'initWithContentsOfURL:error:')
    sel_play = objc.sel_registerName(b'play')
    sel_stop = objc.sel_registerName(b'stop')
    sel_isPlaying = objc.sel_registerName(b'isPlaying')
    sel_setVolume = objc.sel_registerName(b'setVolume:')

    # Build path and URL
    func_stringWithUTF8 = ctypes.cast(
        objc.objc_msgSend,
        ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p)
    )
    ns_path = func_stringWithUTF8(NSString, sel_stringWithUTF8, abs_path.encode('utf-8'))

    func_fileURLWithPath = ctypes.cast(
        objc.objc_msgSend,
        ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
    )
    ns_url = func_fileURLWithPath(NSURL, sel_fileURLWithPath, ns_path)

    # Init player
    alloc_player = objc.objc_msgSend(AVAudioPlayer, sel_alloc)
    func_init = ctypes.cast(
        objc.objc_msgSend,
        ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
    )
    player = func_init(alloc_player, sel_init, ns_url, None)

    if not player:
        print("[-] Failed to initialize audio.", file=sys.stderr)
        sys.exit(1)

    # Force full player volume (float 1.0)
    func_setVolume = ctypes.cast(
        objc.objc_msgSend,
        ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_float)
    )
    func_setVolume(player, sel_setVolume, ctypes.c_float(software_volume))

    # Playback
    objc.objc_msgSend(player, sel_play)
    print(f"[+] Playing at full gain: {os.path.basename(abs_path)}")

    func_isPlaying = ctypes.cast(
        objc.objc_msgSend,
        ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    )

    try:
        while func_isPlaying(player, sel_isPlaying):
            time.sleep(0.3)
    except KeyboardInterrupt:
        objc.objc_msgSend(player, sel_stop)
        print("\n[*] Stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play audio files on iOS with full volume.")
    parser.add_argument("file", help="Audio file path")
    parser.add_argument("-v", "--volume", type=float, default=1.0, help="Volume 0.0 to 1.0 (default: 1.0)")
    args = parser.parse_args()

    play_audio(args.file, args.volume)
