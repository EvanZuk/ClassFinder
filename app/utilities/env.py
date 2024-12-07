import platform, sys
devmode = not (platform.uname()[1] == 'classfinder' or 'pytest' in sys.modules)