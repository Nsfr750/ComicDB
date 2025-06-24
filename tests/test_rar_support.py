"""Test script to verify RAR file support."""
import sys
import os
import ctypes

def test_rar_support():
    print("=== Testing RAR Support ===")
    
    # Try to import rarfile
    try:
        import rarfile
        print("✓ rarfile module is installed")
    except ImportError:
        print("❌ rarfile module is not installed. Install with: pip install rarfile")
        return False
    
    # Try to find UnRAR
    unrar_path = None
    unrar_paths = [
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
        r"C:\Program Files\UnrarDLL\UnRAR.exe",
        r"C:\Program Files (x86)\UnrarDLL\UnRAR.exe",
        r"C:\Windows\System32\UnRAR.dll"
    ]
    
    for path in unrar_paths:
        if os.path.exists(path):
            unrar_path = path
            print(f"✓ Found UnRAR at: {unrar_path}")
            break
    
    if not unrar_path:
        print("❌ Could not find UnRAR executable. Please install WinRAR or UnRAR.")
        return False
    
    # Set up rarfile
    rarfile.UNRAR_TOOL = unrar_path
    
    # For DLLs, try to load it directly
    if unrar_path.lower().endswith('.dll'):
        try:
            ctypes.WinDLL(unrar_path)
            print("✓ Successfully loaded UnRAR DLL")
        except Exception as e:
            print(f"❌ Failed to load UnRAR DLL: {e}")
            print("This might be a 32/64-bit architecture mismatch.")
            return False
    
    # Test rarfile setup
    try:
        if rarfile.tool_setup():
            print("✓ rarfile.tool_setup() successful")
            return True
        else:
            print("❌ rarfile.tool_setup() returned False")
            return False
    except Exception as e:
        print(f"❌ rarfile.tool_setup() failed: {e}")
        return False

if __name__ == "__main__":
    success = test_rar_support()
    if success:
        print("\n✅ RAR support is working correctly!")
    else:
        print("\n❌ There were issues with RAR support. See above for details.")
    
    input("\nPress Enter to exit...")
