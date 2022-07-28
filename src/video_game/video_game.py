"""
Video Game

Demonstrating the capabilities of arcade in a platformer game
Support the Arcade Platformer article
at https://realpython.com/platformer-python-arcade/

All game art work from www.kenney.nl
Game sounds and tile maps bu author
"""

import arcade
import pathlib
from .constants import *


# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent / "assets"


class Enemy(arcade.AnimatedWalkingSprite):
    """An enemy sprite with basic walking movement"""

    def __init__(self, pos_x: int, pos_y: int) -> None:
        super().__init__(center_x=pos_x, center_y=pos_y)

        # Where are the enemy images store?
        texture_path = ASSETS_PATH / "images" / "enemies"

        # Set up the appropriate textures
        walking_texture_path = [
            texture_path / "slimePurple.png",
            texture_path / "slimePurple_move.png"
        ]
        standing_texture_path = texture_path / "slimePurple.png"

        # Load them all now
        self.walk_left_textures = [
            arcade.load_texture(texture) for texture in walking_texture_path
        ]
        self.walk_right_textures = [
            arcade.load_texture(texture, mirrored=True)
            for texture in walking_texture_path
        ]
        self.stand_left_textures = [
            arcade.load_texture(standing_texture_path, mirrored=True)
        ]
        self.stand_right_textures = [
            arcade.load_texture(standing_texture_path)
        ]

        # Set the enemy defaults
        self.state = arcade.FACE_LEFT
        self.change_x = -PLAYER_MOVE_SPEED // 2

        # Set the initial texture
        self.texture = self.stand_left_textures[0]


class TitleView(arcade.View):
    """Display a title screen and prompts the user to begin the game.
    Provides a way to show instructions and start the game.
    """

    def __init__(self) -> None:
        super().__init__()

        # Find the title image
        title_imgae_path = ASSETS_PATH / "images" / "title_image.png"

        # Load our title image
        self.title_image = arcade.load_texture(title_imgae_path)

        # Set our display timer
        self.display_timer = 3.0

        # Are we showing the instructions?
        self.show_instructions = False

    def on_update(self, delta_time: float) -> None:
        """Manages the timer to toggle the instructions

        :param delta_time {float}: Time passes since last update
        """

        # First count down the time
        self.display_timer -= delta_time

        # If the timer has run out, we toggle the instructions
        if self.display_timer < 0:

            # Toggle whether to show the instructions
            self.show_instructions = not self.show_instructions

            # And reset the timer so the instructions flash slowly
            self.display_timer = 1.0

    def on_draw(self) -> None:
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with our title image
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=self.title_image
        )

        # Should we show our instructions?
        if self.show_instructions:
            arcade.draw_text(
                "Enter to start | I for Instructions",
                start_x=100,
                start_y=220,
                color=arcade.color.INDIGO,
                font_size=40
            )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Resume the game when the user presses ESC again

        :param key {int}: Which key was pressed
        :param modifiers {int}: What modifiers were active
        """
        if key == arcade.key.RETURN:
            game_view = PlatformerView()
            game_view.setup()
            self.window.show_view(game_view)

        elif key == arcade.key.I:
            instructions_view = InstructionsView()
            self.window.show_view(instructions_view)


class InstructionsView(arcade.View):
    """Show instructions to the player"""

    def __init__(self) -> None:
        """Create instructions screen"""
        super().__init__()

        # Find the instructions imgae
        instructions_image_path = (
            ASSETS_PATH / "images" / "instructions_image.png"
        )

        # Load our title image
        self.instructions_image = arcade.load_texture(instructions_image_path)

    def on_draw(self) -> None:
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with the instructions image
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=self.instructions_image
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Start the game when the user presses Enter

        :param key {int}: Which key was pressed
        :param modifiers {int}: What modifiers were active
        """
        if key == arcade.key.RETURN:
            game_view = PlatformerView()
            game_view.setup()
            self.window.show_view(game_view)

        elif key == arcade.key.ESCAPE:
            title_view = TitleView()
            self.window.show_view(title_view)


class PauseView(arcade.View):
    """Shown when the game is paused"""

    def __init__(self, game_view: arcade.View) -> None:
        """Create the pause screen"""
        # Initialize the parent
        super().__init__()

        # Store a reference to the underlying view
        self.game_view = game_view

        # Store a semitransparent color to use as an overlay
        self.fill_color = arcade.make_transparent_color(
            arcade.color.WHITE, transparency=150
        )

    def on_draw(self) -> None:
        """Draw the underlying screen, blurred, then the Pause text"""

        # First, draw the underlying view
        # This also calls start_render(), so no need to do it again
        self.game_view.on_draw()

        # Now create a filled rect that covers the current viewport
        # We get the viewport size from the game view
        arcade.draw_lrtb_rectangle_filled(
            left=self.game_view.view_left,
            right=self.game_view.view_left + SCREEN_WIDTH,
            top=self.game_view.view_bottom + SCREEN_HEIGHT,
            bottom=self.game_view.view_bottom,
            color=self.fill_color
        )

        # Now shoe the Pause text
        arcade.draw_text(
            "PAUSED - ESC TO CONTINUE",
            start_x=self.game_view.view_left + 180,
            start_y=self.game_view.view_bottom + 300,
            color=arcade.color.INDIGO,
            font_size=40
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Resume the game when the user presses ESC again

        :param key {int}: Which key was pressed
        :param modifiers {int}: What modifiers were active
        """
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)


class PlatformerView(arcade.View):
    def __init__(self) -> None:
        super().__init__()

        # These lists will hold different sets of sprites
        self.coins = None
        self.background = None
        self.walls = None
        self.ladders = None
        self.goals = None
        self.enemies = None

        # One sprite for the player, no more is needed
        self.player = None

        # We need a physics engine as well
        self.physics_engine = None

        # Someplace to keep score
        self.score = 0

        # Which level are we on?
        self.level = 1

        # Load up our sounds here
        self.coin_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "coin.wav")
        )
        self.jump_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "jump.wav")
        )
        self.victory_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "victory.wav")
        )

        # Check if a joystick is connected
        joysticks = arcade.get_joysticks()

        if joysticks:
            # If so, get the first one
            self.joystick = joysticks[0]
            self.joystick.open()
        else:
            # If not, flag it so we won't use it
            print("No joysticks detected")
            self.joystick = None

    def setup(self) -> None:
        """Sets up the game for the current level"""

        # Get the current map based on the level
        map_name = f"platform_level_{self.level:02}.tmx"
        map_path = ASSETS_PATH / map_name

        # What are the names of the layers
        wall_layer = "ground"
        ladders_layer = "ladders"
        background_layer = "background"
        goal_layer = "goal"
        coin_layer = "coins"

        # Load the current map
        game_map = arcade.tilemap.read_tmx(str(map_path))

        # Load the layers
        self.walls = arcade.tilemap.process_layer(
            game_map, layer_name=wall_layer, scaling=MAP_SCALING
        )

        self.ladders = arcade.tilemap.process_layer(
            game_map, layer_name=ladders_layer, scaling=MAP_SCALING
        )

        self.background = arcade.tilemap.process_layer(
            game_map, layer_name=background_layer, scaling=MAP_SCALING
        )

        self.goals = arcade.tilemap.process_layer(
            game_map, layer_name=goal_layer, scaling=MAP_SCALING
        )

        self.coins = arcade.tilemap.process_layer(
            game_map, layer_name=coin_layer, scaling=MAP_SCALING
        )

        # Process moving platforms
        moving_platforms_layer_name = "moving_platforms"
        moving_platforms = arcade.tilemap.process_layer(
            game_map,
            layer_name=moving_platforms_layer_name,
            scaling=MAP_SCALING
        )
        for sprite in moving_platforms:
            self.walls.append(sprite)

        # Set the background color
        background_color = arcade.color.FRESH_AIR
        if game_map.background_color:
            background_color = game_map.background_color
        arcade.set_background_color(background_color)

        # Find the edge of the map to control viewport scrolling
        self.map_width = (
            game_map.map_size.width - 1
        ) * game_map.tile_size.width

        # Create the player sprite if they are not already set up
        if not self.player:
            self.player = self.create_player_sprite()

        # Move the player sprite back to the beginning
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.player.change_x = 0
        self.player.change_y = 0

        # Set up our enemies
        self.enemies = self.create_enemy_sprites()

        # Reset the viewport
        self.view_left = 0
        self.view_bottom = 0

        # Load the physics engine for this map
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            platforms=self.walls,
            gravity_constant=GRAVITY,
            ladders=self.ladders
        )

    def create_enemy_sprites(self) -> arcade.SpriteList:
        """Creates enemy sprites appropriate for the current level

        :return: A sprite list of enemies
        """
        enemies = arcade.SpriteList()

        # Only enemies on level 2
        if self.level == 2:
            enemies.append(Enemy(1464, 320))

        return enemies

    def create_player_sprite(self) -> arcade.AnimatedWalkingSprite:
        """Creates the animated player sprite

        :return: The properly set up player sprite
        """
        # Where are the player images stored?
        texture_path = ASSETS_PATH / "images" / "player"

        # Set up the appropriate textures
        walking_paths = [
            texture_path / f"alienGreen_walk{x}.png" for x in (1, 2)
        ]
        climbing_paths = [
            texture_path / f"alienGreen_climb{x}.png" for x in (1, 2)
        ]
        standing_path = texture_path / "alienGreen_stand.png"

        # Load them all now
        walking_right_textures = [
            arcade.load_texture(texture) for texture in walking_paths
        ]
        walking_left_textures = [
            arcade.load_texture(texture, mirrored=True)
            for texture in walking_paths
        ]

        walking_up_textures = [
            arcade.load_texture(texture) for texture in climbing_paths
        ]
        walking_down_textures = [
            arcade.load_texture(texture) for texture in climbing_paths
        ]

        standing_right_textures = [arcade.load_texture(standing_path)]

        standing_left_textures = [
            arcade.load_texture(standing_path, mirrored=True)
        ]

        # Create the sprite
        player = arcade.AnimatedWalkingSprite()

        # Add the proper textures
        player.stand_left_textures = standing_left_textures
        player.stand_right_textures = standing_right_textures
        player.walk_left_textures = walking_left_textures
        player.walk_right_textures = walking_right_textures
        player.walk_up_textures = walking_up_textures
        player.walk_down_textures = walking_down_textures

        # Set the player defaults
        player.center_x = PLAYER_START_X
        player.center_y = PLAYER_START_Y
        player.state = arcade.FACE_RIGHT

        # Set the initial texture
        player.texture = player.stand_right_textures[0]

        return player

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Processes key releases

        :param key {int}: Which key was pressed
        :param modifiers {int}: Which modifiers were down at the time
        """

        # Check for player left or right movement
        if key in [arcade.key.LEFT, arcade.key.J]:
            self.player.change_x = -PLAYER_MOVE_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.L]:
            self.player.change_x = PLAYER_MOVE_SPEED

        # Check if player can climb up or down
        elif key in [arcade.key.UP, arcade.key.I]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = PLAYER_MOVE_SPEED
        elif key in [arcade.key.DOWN, arcade.key.K]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = -PLAYER_MOVE_SPEED

        # Check if player can jump
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
                # Play the jump sound
                arcade.play_sound(self.jump_sound)

        # Did the user want to pause?
        elif key == arcade.key.ESCAPE:
            # Pass the current view to preserve this view's state
            pause = PauseView(self)
            self.window.show_view(pause)

    def on_key_release(self, key: int, modifiers: int):
        """Processes key releases

        :param key {int}: Which key was released
        :param modifiers {int}: Which modifiers were down at the time
        """

        # Check for player left or right movement
        if key in [
            arcade.key.LEFT,
            arcade.key.J,
            arcade.key.RIGHT,
            arcade.key.L,
        ]:
            self.player.change_x = 0

        # Check if player can climb or down
        elif key in [
            arcade.key.UP,
            arcade.key.I,
            arcade.key.DOWN,
            arcade.key.K,
        ]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = 0

    def on_update(self, delta_time: float) -> None:
        """Updates the position of all game objects

        :param delta_time {float}: How much time since the last call
        """

        # First, check for joystick movement
        if self.joystick:
            # Check if we are in the dead zone
            if abs(self.joystick.x) > DEAD_ZONE:
                self.player.change_x = self.joystick.x * PLAYER_MOVE_SPEED
            else:
                self.player.change_x = 0

            if abs(self.joystick.y) > DEAD_ZONE:
                if self.physics_engine.is_on_ladder():
                    self.player.change_y = self.joystick.y * PLAYER_MOVE_SPEED
                else:
                    self.player.change_y = 0

            # Did the user press the jump button?
            if self.joystick.button[0]:
                if self.physics_engine.can_jump():
                    self.player.change_y = PLAYER_JUMP_SPEED
                    # Play the jump sound
                    arcade.play_sound(self.jump_sound)


        # Update the player animation
        self.player.update_animation(delta_time)

        # Are there enemies? Update them as well
        self.enemies.update_animation(delta_time)
        for enemy in self.enemies:
            enemy.center_x += enemy.change_x
            walls_hit = arcade.check_for_collision_with_list(
                sprite=enemy, sprite_list=self.walls
            )
            if walls_hit:
                enemy.change_x *= -1

        # Update player movement based on the physics engine
        self.physics_engine.update()

        # Restrict user movement so they cannot walk off screen
        if self.player.left < 0:
            self.player.left = 0

        # Check if we have picked up a coin
        coins_hit = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.coins
        )

        for coin in coins_hit:
            # Add the coin sore to our score
            self.score += int(coin.properties["point_value"])

            # Play the coin sound
            arcade.play_sound(self.coin_sound)

             # Remove the coin
            coin.remove_from_sprite_lists()

        # Has Roz collided with an enemy?
        enemies_hit = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.enemies
        )

        if enemies_hit:
            self.setup()
            title_view = TitleView()
            self.window.show_view(title_view)

        # Now check if we are at the ending goal
        goals_hit = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.goals
        )

        if goals_hit:
            # Play the victory sound
            self.victory_sound.play()

            # Set up the next level
            self.level += 1
            self.setup()

        # Set the viewport, scrolling if necessary
        self.scroll_viewport()

    def scroll_viewport(self) -> None:
        """Scrolls the viewport when the player gets close to the edges"""
        # Scroll left
        # Find the current left boundary
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN

        # Are we to the left of this boundary? Then we should scroll left
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            # But don't scroll past the left edge of the map
            if self.view_left < 0:
                self.view_left = 0

        # Scroll right
        # Find the current right boundary
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN

        # Are we to the right of this boundary? Then we should scroll right
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            # Don't scroll past the right edge of the map
            if self.view_left > self.map_width - SCREEN_WIDTH:
                self.view_left = self.map_width - SCREEN_WIDTH

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom

        # Only scroll to integers. Otherwise we end up with pixels that
        # don't line up on the screen
        self.view_bottom = int(self.view_bottom)
        self.view_left = int(self.view_left)

        # Do the scrolling
        arcade.set_viewport(
            left=self.view_left,
            right=SCREEN_WIDTH + self.view_left,
            bottom=self.view_bottom,
            top=SCREEN_WIDTH + self.view_bottom
        )

    def on_draw(self) -> None:
        arcade.start_render()

        # Draw all the sprites
        self.background.draw()
        self.walls.draw()
        self.coins.draw()
        self.goals.draw()
        self.ladders.draw()
        self.enemies.draw()
        self.player.draw()

        # Draw the score in the lower left
        score_text = f"Score: {self.score}"

        # First a black background for a shadow effect
        arcade.draw_text(
            score_text,
            start_x=10 + self.view_left,
            start_y=10 + self.view_bottom,
            color=arcade.csscolor.BLACK,
            font_size=40
        )
        # Now in white, slightly shifted
        arcade.draw_text(
            score_text,
            start_x=15 + self.view_left,
            start_y=15 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=40
        )
