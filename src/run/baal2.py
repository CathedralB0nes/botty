from pickle import FALSE
from re import search


from char.i_char import IChar
from typing import Dict, Tuple, Union, List, Callable
from config import Config
from logger import Logger
import keyboard
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from utils.custom_mouse import mouse
from dataclasses import dataclass
import cv2
import time
from screen import Screen
from char import IChar
import numpy as np
from utils.misc import load_template, list_files_in_folder, alpha_to_mask
import random


class Baal:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt,

    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._pather = pather
 
    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Baal")
        if not self._char.can_teleport():
            raise ValueError("Baal requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(5, 8): # Worldstone
            return Location.A5_BAAL_START
        return False

    def _scout(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber)-> bool:
        pos_m = self._screen.convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m)))
        t0 = self._screen.grab()
        self._char.move(pos_m, force_tp=True, force_move=True)
        t1 = self._screen.grab()
        diff = cv2.absdiff(t0, t1)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
        score = (float(np.sum(mask)) / mask.size) * (1/255.0)
        Logger.debug(str(score) + ": is our current score")
        if score < .10:
            stuck_count += 1
            if stuck_count >=2:
                Logger.debug(str(corner_picker) + ": Seems we are stuck, let's go reverse 2 x 3 teleports")
                pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                self._char.move(pos_m, force_tp=True)
                self._char.move(pos_m, force_tp=True)
                self._char.move(pos_m, force_tp=True)
                pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                self._char.move(pos_m, force_tp=True)
                self._char.move(pos_m, force_tp=True)
                self._char.move(pos_m, force_tp=True)
                super_stuck +=1
            if super_stuck >= 2:
                Logger.debug(str(corner_picker) + ": Seems we are still stuck, randomly chosing a different corner: SWAPPING AREA")
                keepernumber = random.randint(1, 4)
                if keepernumber == corner_exclude or keepernumber == corner_picker or keepernumber == exclude1 or keepernumber == exclude2:
                    keepernumber = random.randint(1, 4) 
                    super_stuck = 0
                else:
                    corner_exclude = corner_picker
                    corner_picker = keepernumber
                    super_stuck = 0
                    Logger.debug(str(corner_picker) + ": is now our selected corner.")
            
    def _to_throne(self)-> bool:      #do_pre_buff: bool
        # if do_pre_buff: self._char.pre_buff()   
        keyboard.send("tab")
        keyboard.send(self._char._skill_hotkeys["teleport"])
        #setting up variables
        found = False
        score = -1
        corner_picker = 2 #we start searching towards the top, as often the cold plains entrance is at the bottom of the map
        corner_exclude = 2
        exclude1 = corner_picker - 2
        exclude2 = corner_picker + 2 
        stuck_count = 0
        super_stuck = 0
        keepernumber = 0
        #lets start the search
        Logger.debug(str(corner_picker) + ": is our selected corner.")
        while not found:   
            found = self._template_finder.search_and_wait(["RED_GOOP_PURPLE", "BAAL_LVL2_4", "BAAL_LVL2_5", "BAAL_LVL2_EXIT"], best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False)
            if found.valid:
                self._exitclicker()
            if corner_picker == 1:
                self._scout(1, -250, -600, -200, -400, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) #top - left
            elif corner_picker == 2:
                self._scout(2, 250, 600, -200, -400, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # top - right
            elif corner_picker == 3:
                self._scout(3, 250, 600, 200, 400, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # bottom - right
            elif corner_picker == 4:
                self._scout(4, -250, -600, 200, 400, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # bottom - left

    def _exitclicker(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber)-> bool:
            roomfound = False
            badroom = False
            template_match = self._template_finder.search_and_wait(["RED_GOOP_PURPLE", "BAAL_LVL2_4", "BAAL_LVL2_5", "BAAL_LVL2_EXIT"], best_match=True, threshold=0.8,  time_out=0.1, use_grayscale=False)
            if template_match.valid:
                pos_m = self._screen.convert_screen_to_monitor(template_match.position)
                keyboard.send("tab")
            while not roomfound and not badroom:
                template_match = self._template_finder.search_and_wait(["RED_GOOP_PURPLE", "BAAL_LVL2_4", "BAAL_LVL2_5", "BAAL_LVL2_EXIT"], best_match=True, threshold=0.8,  time_out=0.1, use_grayscale=False)
                t0 = self._screen.grab()
                self._char.move(pos_m, force_tp=True, force_move=True)
                t1 = self._screen.grab()
                # check difference between the two frames to determine if tele was good or not
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0)
                super_stuck = 0
                self._char.move(pos_m, force_tp=True, force_move=True)
                if score < .15:
                    stuck_count += 1
                    if stuck_count >=3:
                        x, y = (0, 0)
                        x, y = pos_m
                        pos_m = x * 1.1, y * 1.1
                        Logger.debug("INCREASING DISTANCE")
                        self._char.move(pos_m, force_move=True)
                        self._char.move(pos_m, force_move=True)
                        self._char.move(pos_m, force_move=True)
                        self._char.move(pos_m, force_move=True)
                        super_stuck += 1
                        if not roomfound == True or badroom == True and super_stuck >=3:
                            keyboard.send("tab")                            
                            Logger.debug("GOING DEEP WITH THE COORDS BABYYYY!!!")
                            stuck_count = 0
                            pos_m = self._screen.convert_abs_to_monitor((-500, -275))
                            self._char.move(pos_m, force_tp=True)
                            pos_m = self._screen.convert_abs_to_monitor((500, -275))
                            self._char.move(pos_m, force_tp=True)
                            pos_m = self._screen.convert_abs_to_monitor((-500, 275))
                            self._char.move(pos_m, force_tp=True)
                            template_match = self._template_finder.search_and_wait(["PURPENT2", "PURPENT3"], threshold=0.8, time_out=0.1, use_grayscale=False)
                            super_stuck = 0
                            if template_match.valid:
                                pos_m = self._screen.convert_screen_to_monitor(template_match.position)
                                keyboard.send("tab")
                            elif template_match == False:
                                pos_m = pos_m = self._screen.convert_abs_to_monitor((20, -50))                                      
                                keyboard.send("tab")
                found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(2.0)
                if not self._char.select_by_template(["BAAL_LVL2_EXIT"], found_loading_screen_func, threshold=0.63, time_out=4):
                    # do a random tele jump and try again
                    pos_m = self._screen.convert_abs_to_monitor((150, -200))
                    self._char.move(pos_m, force_move=True)
                    if not self._char.select_by_template(["BAAL_LVL2_EXIT"], found_loading_screen_func, threshold=0.63, time_out=4):
                        pos_m = self._screen.convert_abs_to_monitor((-150, 200))
                        self._char.move(pos_m, force_move=True)
                        if not self._char.select_by_template(["BAAL_LVL2_EXIT"], found_loading_screen_func, threshold=0.63, time_out=4):
                            return False
                
    

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        # TODO: We might need a second template for each option as merc might run into the template and we dont find it then
        if do_pre_buff:
            self._char.pre_buff()
        stuck_count = 0
        keyboard.send("f4")
        self._to_throne()
        ##ending clicker get in
        dinky = 0
        roomfound = False
        template_match = self._template_finder.search_and_wait(["RED_GOOP_PURPLE", "BAAL_LVL2_4", "BAAL_LVL2_5", "BAAL_LVL2_EXIT"], best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False)
        if template_match.valid:
            keyboard.send("tab")
            pos_m = self._screen.convert_screen_to_monitor(template_match.position)
        while not roomfound:
            roomfound = self._template_finder.search_and_wait(["BAAL_LVL2_4", "BAAL_LVL2_5", "BAAL_LVL2_EXIT"], threshold=0.65, time_out=0.1, take_ss=False, use_grayscale=False).valid
            pos_m = self._screen.convert_screen_to_monitor(template_match.position)
            t0 = self._screen.grab()
            self._char.move(pos_m, force_tp=True, force_move=True)
            t1 = self._screen.grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            self._char.move(pos_m, force_tp=True, force_move=True)
            self._char.move(pos_m, force_tp=True, force_move=True)
            self._char.move(pos_m, force_tp=True, force_move=True)
            if score < .15:
                stuck_count += 1
                if stuck_count >=3:
                    pos_m2 = self._screen.convert_abs_to_monitor((-150, -200))
                    self._char.move(pos_m2, force_tp=True)
                    pos_m2 = self._screen.convert_abs_to_monitor((-350, -150))
                    self._char.move(pos_m2, force_tp=True)
                    stuck_count = 0
                    score = .5
                    Logger.debug("STUCK")
                    dinky += 1                  

        found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(2.0)
        if not self._char.select_by_template(["BAAL_LVL2_EXIT"], found_loading_screen_func, threshold=0.8, time_out=4):
            # do a random tele jump and try again
            if not self._char.select_by_template(["BAAL_LVL2_EXIT"], found_loading_screen_func, threshold=0.8, time_out=4):
                return False
        # Wait until templates in durance of hate lvl 3 entrance are found
        if self._template_finder.search_and_wait(["BAAL_THRONE_START_0", "BAAL_THRONE_START_1", "BAAL_THRONE_START_2", "BAAL_THRONE_START_3"], threshold=0.8, time_out=20).valid:
            #throne killd
            Logger.debug("GOTTA DO THRONE")
        else:
            self._to_throne()
     

