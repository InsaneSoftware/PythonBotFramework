import functions as fn


def open_website():
    fn.log("Opening website")
    fn.key_down('win')
    fn.press_key('r')
    fn.key_up('win')
    fn.random_sleep(0.5, 1)
    fn.type_text('chrome.exe --profile-directory="Default"')
    fn.press_key('enter')

    fn.random_sleep(2, 3)
    fn.log("Visiting website")
    fn.type_text('insane.software')
    fn.press_key('enter')


if __name__ == "__main__":
    fn.run_hotkey_bot(open_website)
