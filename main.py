import functions as fn

def my_bot():
    while fn.is_paused():
        fn.time.sleep(0.1)

    if not fn.should_run():
        return

    # --- Your BOT CODE ---
    fn.close_window_by_title_part("Calc")
    fn.find_and_click("start_windows")
    fn.random_sleep(1, 2)
    fn.type_text("calc")
    fn.random_sleep(0.5, 1)
    fn.press_key("enter")
    fn.random_sleep(0.5, 1)
    fn.focus_window("calc")
    fn.type_text("1337")
    fn.log("✅ Run complete.")

# Just call the universal controller
if __name__ == "__main__":
    fn.run_hotkey_bot(my_bot)
