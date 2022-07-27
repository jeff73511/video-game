from .constants import *
import arcade
from .video_game import TitleView


def main():
    window = arcade.Window(
        width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE
    )
    title_view = TitleView()
    window.show_view(title_view)
    arcade.run()
    
if __name__ == "__main__":
    main()