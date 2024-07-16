from slack_bolt import App
from .app_home_update import app_home_update_button_click_callback
from .create_pr import action_button_click_no_callback, action_button_click_yes_callback


def register(app: App):
    app.action("app_home_update_button_click")(app_home_update_button_click_callback)
    app.action("button_click_no")(action_button_click_no_callback)
    app.action("button_click_yes")(action_button_click_yes_callback)
