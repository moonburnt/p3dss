import logging
from panda3d.core import CardMaker, TextureStage, Texture
from p3dss import spritesheet_processor

log = logging.getLogger(__name__)

DEFAULT_ANIMATIONS_SPEED = 0.1

class SpritesheetObject:
    '''Create 2D CardMaker node out of provided spritesheet and sprite data. Can
    be then used to show various animations and static sprites from provided sheet'''
    def __init__(self, name:str, spritesheet, sprites: list, sprite_size:int,
                 parent = None, default_sprite:int = 0, default_action = None):

        if not parent:
            parent = render
        #name of animated object
        self.name = name
        self.size = sprite_size
        self.spritesheet = spritesheet

        size_x, size_y = self.size
        log.debug(f"{self.name}'s size has been set to {size_x}x{size_y}")

        #the magic that allows textures to be mirrored. With that thing being
        #there, its possible to use values in range 1-2 to get versions of sprites
        #that will face the opposite direction, removing the requirement to draw
        #them with hands. Without thing thing being there, 0 and 1 will be threated
        #as same coordinates, coz "out of box" texture wrap mode is "repeat"
        self.spritesheet.set_wrap_u(Texture.WM_mirror)
        self.spritesheet.set_wrap_v(Texture.WM_mirror)

        sprite_data = spritesheet_processor.get_offsets(self.spritesheet, self.size)

        horizontal_scale, vertical_scale = sprite_data.step_sizes
        offsets = sprite_data.offsets

        #entity2d used to create this with category. Idk
        entity_frame = CardMaker(self.name)
        #setting frame's size. Say, for 32x32 sprite all of these need to be 16
        entity_frame.set_frame(-(size_x/2), (size_x/2), -(size_y/2), (size_y/2))

        #settings this to base.render wont work - I tried
        self.node = parent.attach_new_node(entity_frame.generate())
        self.node.set_texture(self.spritesheet)

        #okay, this does the magic
        #basically, to show the very first sprite of 2 in row, we set tex scale
        #to half (coz half is our normal char's size). If we will need to use it
        #with sprites other than first - then we also should adjust offset accordingly
        #entity_object.set_tex_offset(TextureStage.getDefault(), 0.5, 0)
        #entity_object.set_tex_scale(TextureStage.getDefault(), 0.5, 1)
        self.node.set_tex_scale(TextureStage.getDefault(),
                                    horizontal_scale, vertical_scale)

        #now, to use the stuff from cut_spritesheet function.
        #lets say, we need to use second sprite from sheet. Just do:
        #entity_object.set_tex_offset(TextureStage.getDefault(), *offsets[1])
        self.node.set_tex_offset(TextureStage.getDefault(),
                                     *offsets[default_sprite])

        #enable support for alpha channel. This is a float, e.g making it non-100%
        #will require values between 0 and 1
        self.node.set_transparency(1)

        #setting this to None may cause crashes on few rare cases, but going
        #for "idle_right" wont work for projectiles... So I technically add it
        #there for anims updater, but its meant to be overwritten at 100% cases
        self.currently_shown = None

        self.default_action = default_action

        self.items = {}
        #this can be a bit complicated to tweak later, because sprites become
        #offsets and offsets become sprites... Idk what Im typing anymore lol
        for sprite in sprites:
            #this may crash on incorrect length
            if isinstance(sprites[sprite]['sprites'], int):
                data = Sprite(
                        name = sprite,
                        sprites = offsets,
                        offset = sprites[sprite]['sprites'],
                        parent = self,
                        length = sprites[sprite].get('length', 0),
                        reset_on_complete = sprites[sprite].get('reset_on_complete',
                                                                        False),
                             )

            elif ((len(sprites[sprite]['sprites']) == 1) or
                (sprites[sprite]['sprites'][0] == sprites[sprite]['sprites'][1])):
                data = Sprite(
                        name = sprite,
                        sprites = offsets,
                        offset = sprites[sprite]['sprites'][0],
                        parent = self,
                        length = sprites[sprite].get('length', 0),
                        reset_on_complete = sprites[sprite].get('reset_on_complete',
                                                                        False),
                             )

            else:
                data = Animation(
                        name = sprite,
                        sprites = offsets,
                        animation_offsets = sprites[sprite]['sprites'],
                        parent = self,
                        loop = sprites[sprite].get('loop', False),
                        speed = sprites[sprite].get('speed', DEFAULT_ANIMATIONS_SPEED),
                        length = sprites[sprite].get('length', 0),
                        reset_on_complete = sprites[sprite].get('reset_on_complete',
                                                                        False),
                             )

            self.items[sprite] = data

        # if default_action and (default_action in self.items):
            # self.default_action = default_action
        # else:
            # self.default_action = None

        # print(self.default_action)

    def show(self, item_name:str):
        '''Make node switch to showcase of selected spritesheet's item instead
        of whatever else plays'''
        #safety check to ensure that we wont crash everything with exception by
        #trying to play animation that doesnt exist
        if not item_name in self.items:
            log.warning(f"{self.name} has no item named {item_name}!")
            return

        self.stop()

        self.currently_shown = self.items[item_name]
        self.currently_shown.show()
        log.debug(f"{self.name} currently playing {self.currently_shown.name}")

    def switch(self, item_name: str):
        '''Play new item, but only if its different from current one'''
        if (not self.currently_shown or ((self.currently_shown.name != item_name)
           and not self.currently_shown.locked)):
            self.show(item_name)

    def stop(self):
        '''Stops current animation from playing. Wont do anything to single sprite'''
        if self.currently_shown and isinstance(self.currently_shown, Animation):
            self.currently_shown.stop()
            log.debug(f"{self.name} has stopped playback of {self.currently_shown.name}")

#idk if I should begin its name it with _, since it shouldnt be called manually,
#but only from AnimatedObject's sprite initialization
class Animation:
    '''Animation node. Meant to be initalized from SpritesheetObject. Holds one
    animation from spritesheet with provided playback settings'''
    def __init__(self, name:str, sprites: list, animation_offsets:tuple,
                 parent, loop: bool, speed:float = DEFAULT_ANIMATIONS_SPEED,
                 length = 0, reset_on_complete:bool = False):
        #name of the animation itself
        self.name = name

        #parent node, to which animation applies.
        #Must be AnimatedObject with spritesheet texture attached to it
        self.parent = parent.node

        if reset_on_complete:
            self.default_action = parent.default_action
            self.parent_switch = parent.switch
        else:
            self.default_action = None

        #playback speed of animation
        self.speed = speed

        self.timer = self.speed

        #what to do at the end of animation. Either keep it playing or stop at last frame
        self.loop = loop

        #current status of animation's playback
        self.playing = False

        self.sprites = sprites
        self.offsets = animation_offsets
        self.current_frame = self.offsets[0]

        #if object has specified playback length set - locking animation from
        #changing until length timer is exhausted
        if length and length > 0:
            self.length = length
            self.current_length = length
        else:
            self.length = 0
            self.current_length = 0

        self.locked = False

    #idk if current name is okay, but keeping is as "play" would be weird for
    #static sprite
    def show(self):
        '''Plays the animation'''
        #maybe add ability to override speed and loop policies for once?

        #there was some rare bug that cause animation to glitch out in case two
        #"show" functions has been casted at once. It shouldnt happen anymore,
        #but this wasnt fixed properly - just avoided #TODO #NEEDFIX
        def update_animation(event):
            if not self.parent:
                return

            if not self.playing:
                if self.default_action:
                    self.parent_switch(self.default_action)
                return

            #ensuring that whatever below only runs if enough time has passed
            dt = globalClock.get_dt()
            self.timer -= dt
            if self.timer > 0:
                return event.cont

            #log.debug("Updating anims")
            #resetting anims timer, so countdown above will start again
            self.timer = self.speed

            if self.current_frame < self.offsets[1]:
                self.current_frame += 1
            else:
                #if looping is disabled - keep the last frame and destroy task
                if not self.loop:
                    self.playing = False
                    return

                self.current_frame = self.offsets[0]

            self.parent.set_tex_offset(TextureStage.getDefault(),
                                       *self.sprites[self.current_frame])

            return event.cont

        #this way we wont need to set starting frame manually
        self.current_frame = self.offsets[0]
        self.playing = True
        base.task_mgr.add(update_animation,
                        f"updates animation {self.name} of {self.parent}")

        if not self.length:
            return

        self.locked = True
        def length_timer(event):
            if not self.parent:
                return

            dt = globalClock.get_dt()
            self.current_length -= dt
            if self.current_length > 0:
                return event.cont

            self.current_length = self.length
            self.locked = False

            if self.default_action:
                self.parent_switch(self.default_action)

        base.task_mgr.add(length_timer,
                    f"locks {self.name} of {self.parent} from being changed")

    def stop(self):
        '''Stops animation playback'''
        #unless I've messed up, this should stop the task from above
        self.playing = False

class Sprite:
    '''Single-sprite node. Used if you need to get part of spritesheet to be displayed'''
    def __init__(self, name:str, sprites: list, offset:int, parent, length = 0,
                 reset_on_complete:bool = False):
        # Sprites are still list and not str, to make it keep the same format as
        # animation. Just use list with single str inside if you need just one
        # sprite from the whole sheet, idk
        self.name = name
        self.parent = parent.node

        self.sprites = sprites
        self.offset = offset

        #TODO: maybe make some parent class for this stuff, to avoid copypaste
        if length and length > 0:
            self.length = length
            self.current_length = length
        else:
            self.length = 0
            self.current_length = 0

        self.locked = False

        #its only applied to sprites with length, for obvious reasons
        if self.length and reset_on_complete:
            self.default_action = parent.default_action
            self.parent_switch = parent.switch
        else:
            self.default_action = None

    def show(self):
        '''Shows the current sprite'''
        self.parent.set_tex_offset(TextureStage.getDefault(),
                                   *self.sprites[self.offset])

        if not self.length:
            return

        self.locked = True
        def length_timer(event):
            if not self.parent:
                return

            dt = globalClock.get_dt()
            self.current_length -= dt
            if self.current_length > 0:
                return event.cont

            self.current_length = self.length
            self.locked = False

            if self.default_action:
                self.parent_switch(self.default_action)

        base.task_mgr.add(length_timer,
                    f"locks {self.name} of {self.parent} from being changed")
