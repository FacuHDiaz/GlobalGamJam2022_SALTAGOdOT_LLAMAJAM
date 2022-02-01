import arcade
import math
import os
import random

# Constantes
ANCHO_PANTALLA = 1000
ALTO_PANTALLA = 650
TITULO_PANTALLA = "Llama Jam"

#Constantes usadas para escalar nuestros sprites de su tamaño original
ESCALA_PERSONAJE = 1
ESCALA_BALDOZA = 1.5
ESCALA_MONEDA = 0.5
TAMANIO_PIXEL_SPRITE = 128
TAMANIO_PIXEL_CUADRICULA = TAMANIO_PIXEL_SPRITE * ESCALA_BALDOZA

# Velocidad de movimiento del jugador, en pixeles por cuadro
VELOCIDAD_MOVIMIENTO_JUGADOR = 7
GRAVEDAD = 1.5
VELOCIDAD_SALTO_JUGADOR = 20

# Posición de inicio del jugador
JUGADOR_INICIO_X = 64
JUGADOR_INICIO_Y = 225

# Constantes usadas para seguir si el jugador esta mirando a la derecha o izquierda
RIGHT_FACING = 0
LEFT_FACING = 1

# Capas de nuestro mapas tilemap
#CAPA_NOMBRE_PLATAFORMA = "Platforms"
#CAPA_NOMBRE_MONEDA = "Coins"
#CAPA_NOMBRE_PRIMER_PLANO = "Foreground"
CAPA_NOMBRE_FONDO = "Fondo"
#LAYER_NAME_DONT_TOUCH = "Don't Touch"
#LAYER_NAME_LADDERS = "Ladders"
#LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_PLAYER = "Player"
CAPA_NOMBRE_SUELO = "Suelo"
LAYER_NAME_ENEMIES = "Enemigo"


def load_texture_pair(filename):
    """
    Cargue un par de texturas, siendo el segundo una imagen especular.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]

class Entity(arcade.Sprite):
    def __init__(self, name_folder, name_file):
        super().__init__()

        # Default to facing right
        self.facing_direction = RIGHT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = ESCALA_PERSONAJE
        self.character_face_direction = RIGHT_FACING

        main_path = f"recursos/sprites/{name_folder}/{name_file}"

        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        #self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        #self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # Load textures for walking
        #self.walk_textures = []
        #for i in range(8):
        #    texture = load_texture_pair(f"{main_path}_walk{i}.png")
        #    self.walk_textures.append(texture)

        # Load textures for climbing
        #self.climbing_textures = []
        #texture = arcade.load_texture(f"{main_path}_climb0.png")
        #self.climbing_textures.append(texture)
        #texture = arcade.load_texture(f"{main_path}_climb1.png")
        #self.climbing_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # set_hit_box = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

class Enemigo(Entity):
    def __init__(self, name_folder, name_file):

        # Setup parent class
        super().__init__(name_folder, name_file)

class Soldado(Enemigo):
    def __init__(self):

        # Set up parent class
        super().__init__("soldados", "soldado")

class Tanque(Enemigo):
    def __init__(self):

        # Set up parent class
        super().__init__("tanque", "tanque")


class PlayerCharacter(Entity):
    """Player Sprite"""

    def __init__(self):

        # conf. clase padre
        super().__init__("llama_blanca","llama_blanca")

        # Seguimiento de nuestro estado
        self.jumping = False
        #self.climbing = False
        #self.is_on_ladder = False


    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Climbing animation
        #if self.is_on_ladder:
        #    self.climbing = True
        #if not self.is_on_ladder and self.climbing:
        #    self.climbing = False
        #if self.climbing and abs(self.change_y) > 1:
        #    self.cur_texture += 1
        #    if self.cur_texture > 7:
        #        self.cur_texture = 0
        #if self.climbing:
        #    self.texture = self.climbing_textures[self.cur_texture // 4]
        #    return

        ## Jumping animation
        #if self.change_y > 0 and not self.is_on_ladder:
        #    self.texture = self.jump_texture_pair[self.character_face_direction]
        #    return
        #elif self.change_y < 0 and not self.is_on_ladder:
        #    self.texture = self.fall_texture_pair[self.character_face_direction]
        #    return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        #self.cur_texture += 1
        #if self.cur_texture > 2:
        #    self.cur_texture = 0
        #self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Llama a las clases padre y configura la ventana
        super().__init__(ANCHO_PANTALLA, ALTO_PANTALLA, TITULO_PANTALLA)

        # Establecer la ruta para comenzar con este programa
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Seguimiento del estado actual de qué tecla se presiona
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # Nuestro objeto de Tilemap
        self.tile_map = None

        # Nuestro objeto escena
        self.scene = None

        # Variable separada que contiene el sprite del jugador
        self.player_sprite = None

        #Nuestro motor de fisicas
        self.physics_engine = None

        # Una camara que se puede usar para desplazar la pantalla.
        self.camera = None

        # Donde esta el borde derecho del mapa
        #self.end_of_map = 0

        # Level
        #self.level = 1

        # Cargar sonidos
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")


        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """La configuracion del juego va aqui. Llama a esta funcion para reiniciar el juego."""

        # Conf de la camara
        self.camera = arcade.Camera(self.width, self.height)

        # Nombre del mapa
        map_name = "recursos/maps/llama finaltmx.tmx"

        # Opciones específicas de capa para el Tilemap
        layer_options = {
            #CAPA_NOMBRE_PLATAFORMA: {
            #    "use_spatial_hash": True,
            #},
            #CAPA_NOMBRE_MONEDA: {
            #    "use_spatial_hash": True,
            #},
            #LAYER_NAME_DONT_TOUCH: {
            #    "use_spatial_hash": True,
            #},
            #LAYER_NAME_LADDERS: {
            #    "use_spatial_hash": True,
            #},
            CAPA_NOMBRE_SUELO: {
                "use_spatial_hash": True
            },
        }

        # Cargar en TileMap
        self.tile_map = arcade.load_tilemap(map_name, ESCALA_BALDOZA, layer_options)

        # Inicie una nueva capa con nuestro TileMap, esto agregará automaticamente todas las capas
        # del mapa como SpriteLists en la escena en el orden correcto.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Agregue la lista de Sprites del jugador antes de la capa "Primer plano". Esto hará que el primer plano 
        # dibujarse detrás del jugador, haciendo que parezca estar frente al jugador. 
        # La configuración antes de usar scene.add_sprite nos permite definir dónde está SpriteList 
        # estará en el orden de sorteo. Si solo usamos add_sprite, se agregará al # fin del pedido.
        #self.scene.add_sprite_list_after("Player", CAPA_NOMBRE_PRIMER_PLANO)

        # Config. del jugador, especificamente colocandolo en esas coordenadas.
        #image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        #self.player_sprite = arcade.Sprite(image_source, ESCALA_PERSONAJE)
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = JUGADOR_INICIO_X
        self.player_sprite.center_y = JUGADOR_INICIO_Y 
        self.scene.add_sprite(LAYER_NAME_PLAYER,self.player_sprite)

        # --- Cargar en un mapa desde el tiled editor ---

        # -- Enemies
        #enemies_layer = self.tile_map.object_lists[LAYER_NAME_ENEMIES]

        enemylist = ["soldado","tanque"]

        enemy_type = random.choice(enemylist)



        if enemy_type == "soldado":
            enemy = Soldado()
        elif enemy_type == "tanque":
                enemy = Tanque()
        else:
            raise Exception(f"Unknown enemy type {enemy_type}.")
        for x in range(0, 1250, 64):
            enemy.center_x = x
            enemy.center_y = JUGADOR_INICIO_Y 

        self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)

        # Calcule el borde derecho de my_map en píxeles
        self.end_of_map = self.tile_map.width * TAMANIO_PIXEL_CUADRICULA

        # --- Otras cosas
        # Conf el color del fondo
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Creamos el 'motor de fisicas'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVEDAD, #ladders=self.scene[LAYER_NAME_LADDERS],walls=self.scene[CAPA_NOMBRE_PLATAFORMA],
            walls=self.scene[CAPA_NOMBRE_SUELO],)


    def on_draw(self):
        """Renderiza la pantalla."""

        self.clear()

        # Activamos nuestra camara
        self.camera.use()
 
        # Dinujar nuestros sprite
        self.scene.draw()

    #def process_keychange(self):
    #    """
    #    Called when we change a key up/down or we move on/off a ladder.
    #    """
    #    # Process up/down
    #    if self.up_pressed and not self.down_pressed:
    #        if self.physics_engine.is_on_ladder():
    #            self.player_sprite.change_y = VELOCIDAD_MOVIMIENTO_JUGADOR
    #        elif (
    #            self.physics_engine.can_jump(y_distance=10)
    #            and not self.jump_needs_reset
    #        ):
    #            self.player_sprite.change_y = VELOCIDAD_SALTO_JUGADOR
    #            self.jump_needs_reset = True
    #            arcade.play_sound(self.jump_sound)
    #    elif self.down_pressed and not self.up_pressed:
    #        if self.physics_engine.is_on_ladder():
    #            self.player_sprite.change_y = -VELOCIDAD_MOVIMIENTO_JUGADOR
#
    #    # Process up/down when on a ladder and no movement
    #    if self.physics_engine.is_on_ladder():
    #        if not self.up_pressed and not self.down_pressed:
    #            self.player_sprite.change_y = 0
    #        elif self.up_pressed and self.down_pressed:
    #            self.player_sprite.change_y = 0
#
        # Process left/right
        #if self.right_pressed and not self.left_pressed:
        #    self.player_sprite.change_x = VELOCIDAD_MOVIMIENTO_JUGADOR
        #elif self.left_pressed and not self.right_pressed:
        #    self.player_sprite.change_x = -VELOCIDAD_MOVIMIENTO_JUGADOR
        #else:
        #    self.player_sprite.change_x = 0


    def on_key_press(self, key, modifiers):
        """Se llama cada vez que se presiona una tecla."""

        if key == arcade.key.UP or key == arcade.key.W:
            #if self.physics_engine.is_on_ladder():
            #    self.player_sprite.change_y = VELOCIDAD_MOVIMIENTO_JUGADOR
            #elif self.physics_engine.can_jump():
            #    self.player_sprite.change_y = VELOCIDAD_SALTO_JUGADOR
            #    arcade.play_sound(self.jump_sound)
            if self.physics_engine.can_jump():
               self.player_sprite.change_y = VELOCIDAD_SALTO_JUGADOR
               arcade.play_sound(self.jump_sound)
        #elif key == arcade.key.DOWN or key == arcade.key.S:
        #    if self.physics_engine.is_on_ladder():
        #        self.player_sprite.change_y = -VELOCIDAD_MOVIMIENTO_JUGADOR
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -VELOCIDAD_MOVIMIENTO_JUGADOR
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = VELOCIDAD_MOVIMIENTO_JUGADOR

    def on_key_release(self, key, modifiers):
        """Se llama cuando el usario suelta la tecla."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )

        # No permite que la camara viaje mas de 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered,0.2)

    def on_update(self, delta_time):
        """Movimiento y logica del juego"""

        # Mueve al jugador con el motor de fisicas
        self.physics_engine.update()

        ## Actualizacion de las animaciones
        #if self.physics_engine.can_jump():
        #    self.player_sprite.can_jump = False
        #else:
        #    self.player_sprite.can_jump = True
#
        #if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
        #    self.player_sprite.is_on_ladder = True
        #    self.process_keychange()
        #else:
        #    self.player_sprite.is_on_ladder = False
        #    self.process_keychange()

        # Update animations
        #self.scene.update_animation(
        #    delta_time, [#CAPA_NOMBRE_MONEDA,
        #     CAPA_NOMBRE_FONDO]
        #)

        # Update Animations
        #self.scene.update_animation(
        #    delta_time,
        #    [
                #LAYER_NAME_COINS,
                #LAYER_NAME_BACKGROUND,
        #        LAYER_NAME_PLAYER,
                #LAYER_NAME_ENEMIES,
        #    ],
        #)

        # Update walls, used with moving platforms
        #self.scene.update([LAYER_NAME_MOVING_PLATFORMS])

        ## Ve si golpeamos alguna moneda
        #coin_hit_list = arcade.check_for_collision_with_list(
        #    self.player_sprite, self.scene["Coins"]
        #)
#
        ## Recorre cada moneda que golpeamos (si hay) y las remueve
        #for coin in coin_hit_list:
        #    # Remueve la moneda
        #    coin.remove_from_sprite_lists()
        #    # Reproduce un sonido
        #    arcade.play_sound(self.collect_coin_sound)
#
        ## El jugador se callo del mapa?
        #if self.player_sprite.center_y < -100:
        #    self.player_sprite.center_x = JUGADOR_INICIO_Y
        #    self.player_sprite.center_y = JUGADOR_INICIO_Y
        #    arcade.play_sound(self.game_over)
#
        ## El jugador toco algo que no deberia?
        #if arcade.check_for_collision_with_list(
        #    self.player_sprite, self.scene[LAYER_NAME_DONT_TOUCH]
        #):
        #    self.player_sprite.change_x = 0
        #    self.player_sprite.change_y = 0
        #    self.player_sprite.center_x = JUGADOR_INICIO_X
        #    self.player_sprite.center_y = JUGADOR_INICIO_Y
#
        #    arcade.play_sound(self.game_over)

        # Ver si el usuario llego al final del nivel
        #if self.player_sprite.center_x >= self.end_of_map:
        #    # Advance to the next level
        #    self.level += 1
#
        #    # Load the next level
        #    self.setup()

        # coloca la camara
        self.center_camera_to_player()

def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()