import os
import sys

if getattr(sys, "frozen", False):
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        os.chdir(bundle_root)
