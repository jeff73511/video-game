from video_game import *


if __name__ == "__main__":
    window = arcade.Window(
        width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE
    )
    title_view = TitleView()
    window.show_view(title_view)
    arcade.run()