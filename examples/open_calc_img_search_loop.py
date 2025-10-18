import functions as fn


def my_bot():
    """
    Example bot using the Python Bot Framework.

    - Waits if paused (F3)
    - Only runs when the user presses Start (F2)
    - Searches for a Windows Start button (dark/light version)
    - Opens Calculator
    - Types '1337' in the Calculator
    """

    while 1:
        # If paused (F3), wait until resumed
        while fn.is_paused():
            fn.time.sleep(0.1)

        # Only run if the user pressed Start (F2)
        if not fn.should_run():
            return

        # --- Your BOT CODE STARTS HERE ---
        fn.log("Starting my awesome bot in 3-5 seconds!")
        fn.random_sleep(3, 5)
        fn.close_window_by_title_part("Calc")  # Close any open Calculator window

        # Loop until one of the two Start button images is found and clicked
        while True:
            if fn.find_and_click("start_windows", breaking=False):  # Searches for img/start_windows.png
                break
            if fn.find_and_click("start_windows_light", breaking=False):  # Searches for img/start_windows_light.png
                break
            if fn.find_and_click("start_windows_11", breaking=False):  # Searches for img/start_windows_11.png
                break
            if fn.find_and_click("start_windows_11_light",
                                 breaking=False):  # Searches for img/start_windows_11_light.png
                break
            fn.random_sleep(1, 2)  # Wait 1–2 seconds between tries to reduce CPU usage

        # Launch Calculator via Start menu
        fn.type_text("calc")
        fn.random_sleep(0.5, 1)
        fn.press_key("enter")

        # Wait for Calculator to appear and bring it to focus
        fn.random_sleep(0.5, 1)
        fn.focus_window("calc")

        # Type "1337" into the Calculator
        fn.type_text("1337")

        # Log success in the console
        fn.log("✅ Run complete.")
        fn.random_sleep(3, 5)

        # Comment this line to execute code just once
        #break


if __name__ == "__main__":
    fn.run_hotkey_bot(my_bot)
