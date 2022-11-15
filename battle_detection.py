import pyautogui
import win32gui

def screenshot(window_title=None):

    if window_title:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            x, y, x1, y1 = win32gui.GetClientRect(hwnd)
            x, y = win32gui.ClientToScreen(hwnd, (x, y))
            x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
            im = pyautogui.screenshot(region=(x, y, x1, y1))
            return im
        else:
            print('Window not found!')
    else:
        im = pyautogui.screenshot()
        return im
# def winEnumHandler( hwnd, ctx ):
#     if win32gui.IsWindowVisible( hwnd ):
#         print (win32gui.GetWindowText( hwnd ))
#         if "DeSmuMe" in win32gui.GetWindowText(hwnd):
#             return win32gui.GetWindowText(hwnd)
#
# win32gui.EnumWindows( winEnumHandler, None )
# im = screenshot('pokemon – battle_detection.py')
# im.save("test_fotos/pycharm.png")
# if im:
#     im.show()


