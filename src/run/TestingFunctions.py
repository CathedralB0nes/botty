        while not self._template_finder.search_and_wait(["LAUGHING"], best_match=True, threshold=0.75, time_out=0.1, use_grayscale=False).valid:
            if self._template_finder.search_and_wait(["LAUGHING"], best_match=True, threshold=0.75, time_out=0.1, use_grayscale=False).valid:
                break
            if corner_count < 5:
                if corner_count == 0: #by entrance
                    Logger.debug("MINI ENTRANCE")
                    pos_m = self._screen.convert_abs_to_monitor((-350, 220))
                    self._char.move(pos_m, force_tp=True)        
                    self._char._mini_trash()
                    self._pather.traverse_nodes([9000], self._char, time_out=3)
                    corner_count += 1
                elif corner_count == 1: #top left
                    Logger.debug("MINI TOP LEFT")
                    self._pather.traverse_nodes_fixed("baal_minitrash_tops", self._char)        
                    self._char._mini_trash()
                    self._pather.traverse_nodes_fixed("baal_minitrash_tope", self._char)
                    self._pather.traverse_nodes([9000], self._char, time_out=3)
                    corner_count += 1
                elif corner_count == 2: #top right
                    Logger.debug("MINI TOP RIGHT")
                    self._pather.traverse_nodes_fixed("baal_minitrash_rights", self._char)    
                    self._char._mini_trash()
                    self._pather.traverse_nodes_fixed("baal_minitrash_righte", self._char)
                    self._pather.traverse_nodes([9000], self._char, time_out=3)
                    corner_count += 1
                elif corner_count == 3: # bottom right
                    Logger.debug("MINI BOT RIGHT")
                    self._pather.traverse_nodes_fixed("baal_minitrash_brights", self._char)       
                    self._char._mini_trash()
                    self._pather.traverse_nodes_fixed("baal_minitrash_brighte", self._char)
                    self._pather.traverse_nodes([9000], self._char, time_out=3)
                    corner_count += 1
                elif corner_count == 3: # bottom left
                    Logger.debug("MINI BOT LEFT")
                    self._pather.traverse_nodes_fixed("baal_minitrash_blefts", self._char)          
                    self._char._mini_trash()
                    self._pather.traverse_nodes_fixed("baal_minitrash_blefte", self._char)
                    self._pather.traverse_nodes([9000], self._char, time_out=3)
                    corner_count += 1
                elif corner_count == 4:
                    break



    def take_break(self, failed: bool = False):
        if self._config.general["info_screenshots"] and failed:
            cv2.imwrite("./info_screenshots/info_failed_game_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        self._curr_loc = False
        self._pre_buffed = False
        self._ui_manager.save_and_exit()
        game_count = self._game_stats._game_counter
        self._do_runs = copy(self._do_runs_reset)
        if self._config.general["randomize_runs"]:
            self.shuffle_runs()
        if game_count > 1:            
            Logger.info("BREAK TIME!")
            wait("""TIME YOU WANNA WAIT IN SECONDS!""")
        wait(0.2, 0.5)           
        self.trigger_or_stop("create_game"






               new_counter = self._game_stats._game_counter
        mini_counter = new_counter - 1
        holder = new_counter - new_counter
        Logger.debug("HOLDER FIRST:" + str(holder))
        game_count = self._game_stats._game_counter
        Logger.debug("GAMECOUNT FIRST AND NEW:" + str(game_count))       
        holder = game_count - holder
        Logger.debug("HOLDER = COUNT - HOLDER:" + str(holder))        
        Logger.debug("GAMECOUNT" + str(game_count))
        Logger.debug("GAMECOUNT" + str(holder))  