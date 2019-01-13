# -*- coding: utf-8 -*-

import logging as lg
import os
import tkinter as tk
import tkinter.font as tkFont
from glob import glob
from json import load as jsload
from logging.handlers import RotatingFileHandler
from time import perf_counter

import numpy as np
from PIL import Image

import Entities.dynamic_entity as dyent
import Entities.static_entity as stent
from Images.imgs_manip import PNGS, LabObj, create_bg, save_img

t1 = perf_counter()



# CWD = r"C:\Users\Timelam\git\pyalb\pyalb\src\Labyrinth2"
# os.chdir(CWD)

NO_COLLISION = False


temps = set() # fichiers temporaires



logger = lg.getLogger()
logger.setLevel(lg.DEBUG)

formatter = lg.Formatter('%(asctime)s | %(levelname)s | %(message)s')

file_handler = RotatingFileHandler('labyrinth.log', 'a', 1000000, 1)

file_handler.setLevel(lg.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)





class Root(tk.Tk) :

    def __init__(self, *args, **kwarks) :

        super().__init__(*args, **kwarks)


        self.in_game = InGameInterface(self)
        self.main_menu = MainMenuInterface(self, borderwidth=0, highlightthickness=0)

        self.com = dict()

        self.bind_all("<KeyPress-Delete>", lambda *a : self.quit())


    def change_page(self, actual, new) :
        
        getattr(self, actual).pack_forget()
        getattr(self, new).pack(fill="both", expand=True)


    def reinitialise(self, attr, new_class, **kwargs) :

        getattr(self, attr).destroy()
        setattr(self, attr, new_class(self, **kwargs))
        






class MainMenuInterface(tk.Frame) :

    def __init__(self, root, **kwargs):
        
        tk.Frame.__init__(self, root, **kwargs)


        self.root = root
        

        self.menu_map_dis = dict()

        for a in glob("Cartes/*.json") :
            
            b = a[7:-5]
            self.menu_map_dis[b] = a
        

        self.canvas = tk.Canvas(self)

        self.img = tk.PhotoImage(file="Images/main_menu_bg_resized.png")
        self.canvas.create_image(0, 0, image=self.img, anchor="nw")

        self.canvas.pack(fill="both", expand=True)

        # self.img_txt = tk.PhotoImage(file="Images/txt_main_menu.png")
        # self.canvas.create_image(
        #     root.winfo_screenwidth() // 2,
        #     root.winfo_screenheight() // 2 + root.winfo_screenheight() // 4,
        #     image = self.img_txt
        # )

        self.start_txt = self.canvas.create_text(
            root.winfo_screenwidth() // 7,
            root.winfo_screenheight() // 7 *5,
            text="Start",
            fill="white",
            activefill="gray",
            font=["Lucida", 38],
            tag="text"
        )

        self.quit_txt = self.canvas.create_text(
            root.winfo_screenwidth() // 7,
            root.winfo_screenheight() // 7 *5 + 100,
            text="Quit ",
            fill="white",
            activefill="gray",
            font=["Lucida", 38],
            tag="text"
        )

        # self.txt_start_inactive = tk.PhotoImage(file="Images/TXT/txt_start.png")
        # self.txt_start_active = tk.PhotoImage(file="Images/TXT/txt_start2.png")

        # self.start_txt = self.canvas.create_image(
        #     root.winfo_screenwidth() // 8 *7,
        #     root.winfo_screenheight() // 7 *5,
        #     activeimage=self.txt_start_active,
        #     image=self.txt_start_inactive
        # )



        self.canvas.bind("<Button-1>", self.click)

        # self.img_but = tk.PhotoImage(file="Images/Buttons/button.png")



    def click(self, evt) :

        item = self.canvas.find_closest(evt.x, evt.y)
        
        if item[0] == self.canvas.find_withtag(self.start_txt)[0] :
            self.start()
        elif item[0] == self.canvas.find_withtag(self.quit_txt)[0] :
            self.root.quit()


    def start(self, *args) :

        self.canvas.delete("text")

        self.map_choice_frame = tk.Frame(self.canvas)

        self.button_list = list()
        

        for i, carte in enumerate(self.menu_map_dis.keys()) :

            self.button_list.append(tk.Button(
                self.map_choice_frame,
                text=carte,
                command=lambda path=carte : self.get_map(path),
                width=50
            ))

            self.button_list[i].pack()




        self.window = self.canvas.create_window(
            root.winfo_screenwidth() // 2,
            root.winfo_screenheight() // 4 *3,
            window=self.map_choice_frame
        )

        self.canvas.delete(self.start_txt)



    def get_map (self, carte) :

        json_path = self.menu_map_dis[carte]


        with open(json_path, "r", encoding="utf8") as data :
            data_dict = jsload(data) # jsload -> json.load

        self.root.com["data"] = data_dict
        self.root.change_page("main_menu", "in_game")

        logger.info('Game started with the map called "{}".'.format(json_path))

        self.root.in_game.play()





class InGameInterface(tk.Frame) :

    def __init__(self, root, **kwargs) :


        self.root = root

        tk.Frame.__init__(self, root, width=0, height=0, **kwargs)
        

        self.play_canvas = tk.Canvas(self, height=self["height"], background="#bbb", highlightthickness=0)
        
        self.coords = np.zeros(2, dtype=np.int)
        self.rlcoords = np.zeros(2, dtype=np.int)

        self.pos_bg = np.zeros(2, dtype=np.int)


        self.r = {"pers" : True, "cam" : True} # permet d'eviter l'appuyage prolongé de windows sur une touche
        self.rls = {"pers" : True, "cam" : True} # passe en True quand KeyRelease
        self.touche_save = {"pers" : None, "cam" : None} # permet de faire des virages fluides, sans pause
        self.touche = {"pers" : None, "cam" : None}

        
        self.play_canvas.focus_set()
        self.play_canvas.bind("<KeyPress>", self.clavier_press)
        self.play_canvas.bind("<KeyRelease>", self.clavier_release)
        self.play_canvas.pack(expand=True, fill="both")

        self.true = {"ontouch": lambda *a : True}

        self.animations = dict()
        for animations in glob("Images\\Animations\\*\\*a.png") : # chargement des animations

            a = animations.split("\\")
            if not a[2] in self.animations :
                self.animations[a[2]] = list()

            self.animations[a[2]].append(tk.PhotoImage(file=animations))
        # self.animations -> nom_de_lanimation : liste des tk.Photoimage de l'animation dans l'ordre

        self.static_entities = dict()
        self.stentcoords = dict() # <entity coords> : entity

        self.dynamic_entities = dict()
        self.dyentcoords = dict()


    def play(self) :

        

        carte = self.root.com["data"]["map_path"]

        self.rlcoords[0] = self.root.com["data"]["pers_x"]
        self.rlcoords[1] = self.root.com["data"]["pers_y"]

        self.coords[0] = self.psimg(self.root.com["data"]["pers_x"])
        self.coords[1] = self.psimg(self.root.com["data"]["pers_y"])


        global create_bg
        width_tab, height_tab, list_globale = create_bg(carte, "Images/bg.png", temps)

        self.global_tab = np.array(list_globale)

        self.pos_bg[0] = width_tab//2
        self.pos_bg[1] = height_tab//2
        self.defaultposbg = np.copy(self.pos_bg)


        self.screen = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        oos = np.array((width_tab, height_tab)) - np.array(self.screen) # oos = out of screen
        self.maxposbg = self.defaultposbg - oos

        self.test_persorcam_move = { # permet de tester si une coordonnee dans une certaine direction depasse le tier de l'ecran
            (0, -1) : lambda new_coords: (new_coords[1] > self.screen[1] * 11 // 30) or self.defaultposbg[1] == self.pos_bg[1],
            (0, 1) : lambda new_coords: ((new_coords[1] < self.screen[1] * 19 // 30) or
                self.maxposbg[1] == self.pos_bg[1]),

            (1, 0) : lambda new_coords: ((new_coords[0] < self.screen[0] * 19 // 30) or
                self.maxposbg[0] == self.pos_bg[0]),
            (-1, 0) : lambda new_coords: (new_coords[0] > self.screen[0] * 11 // 30) or self.defaultposbg[0] == self.pos_bg[0]
        } # si vrai, le personnage doit se deplacer, si faux, la camera doit se deplacer dans l'autre sens



        self.bg_img = tk.PhotoImage(file="Images/bg.png")
        self.bg = self.play_canvas.create_image(self.pos_bg[0], self.pos_bg[1], image=self.bg_img)

        self.entities = list()


        st = self.root.com["data"].get("static_entities", {})

        for entity_type, ele in st.items() :

            for entity_name in ele :
                
                ent_options = st[entity_type][entity_name]
                entity = getattr(stent, entity_type)(self, **ent_options)

                self.static_entities[entity_type + "/" + entity_name] = entity
                self.entities.append(entity)

                self.stentcoords[tuple(ent_options["rlcoords"])] = entity




        


        dy = self.root.com["data"].get("dynamic_entities", {}) # pour raccourcir

        for entity_type, ele in dy.items() :

            for entity_name in ele :
                
                ent_options = dy[entity_type][entity_name]
                entity = getattr(dyent, entity_type)(self, **ent_options)



                self.dynamic_entities[entity_type + "/" + entity_name] = entity
                self.entities.append(entity)

                self.dyentcoords[tuple(ent_options["rlcoords"])] = entity










        self.pers_img = tk.PhotoImage(file="Images/pers.png")
        self.pers = self.play_canvas.create_image(self.coords[0], self.coords[1], image=self.pers_img)







    def psimg (self, pos) :
        return (4+8*pos)*2



    def clavier_press (self, event) :
        touche = event.keysym.lower()
        if touche == "escape" : self.reinitialise()

        if touche in "zqsd" :

            if self.r["pers"] :
                self._pers_evt(touche)
            else :
                self.touche_save["pers"] = event


        if touche in "oklm" :

            if self.r["cam"] :
                self._bg_evt(touche)      
            else :
                self.touche_save["cam"] = event


    def _bg_evt (self, touche) :
        self.r["cam"] = False
        self.touche_save["cam"] = None
        self.touche["cam"] = touche.lower()
        self.rls["cam"] = False


        if self.touche["cam"] == "l" :
            self.move_bg(0, -1)
            
        elif self.touche["cam"] == "o" :
            self.move_bg(0, 1)

        elif self.touche["cam"] == "k" :
            self.move_bg(1, 0)

        elif self.touche["cam"] == "m" :
            self.move_bg(-1, 0)

        else :
            self.r["cam"] = True            
            

    def _pers_evt (self, touche) :
        self.r["pers"] = False
        self.touche_save["pers"] = None
        self.touche["pers"] = touche.lower()

            
        self.rls["pers"] = False
           
            
        if self.touche["pers"] == "z" :
            new_rlcoords = self.rlcoords + (0, -1)
            new_coords = self.coords + (0, -16)
            ispers = self.test_persorcam_move[(0, -1)](new_coords)
            self.move_pers(0, -1, new_rlcoords, new_coords, ispers)

        elif self.touche["pers"] == "s" :
            new_rlcoords = self.rlcoords + (0, 1)
            new_coords = self.coords + (0, 16)
            ispers = self.test_persorcam_move[(0, 1)](new_coords)
            self.move_pers(0, 1, new_rlcoords, new_coords, ispers)

        elif self.touche["pers"] == "d" :
            new_rlcoords = self.rlcoords + (1, 0)
            new_coords = self.coords + (16, 0)
            ispers = self.test_persorcam_move[(1, 0)](new_coords)
            self.move_pers(1, 0, new_rlcoords, new_coords, ispers)
                        
        elif self.touche["pers"] == "q" :
            new_rlcoords = self.rlcoords + (-1, 0)
            new_coords = self.coords + (-16, 0)
            ispers = self.test_persorcam_move[(-1, 0)](new_coords)
            self.move_pers(-1, 0, new_rlcoords, new_coords, ispers)

        else :
            self.r["pers"] = True


    def entity_test(self, x, y) :

        
        a = self.stentcoords.get((x, y), None)
        if a is not None :
            return a.contact()
        return True


    def move_pers(self, x, y, new_rlcoords, new_coords, ispers) :
        
        mur = False

        ispers = self.test_persorcam_move[(x, y)](new_coords)

        way = np.array((x, y), dtype=np.int)

        
        xb, yb = new_rlcoords
        if not (self.global_tab[yb, xb].tag != "mur" and 
            self.entity_test(xb, yb)
        ) :

            # n_2move = [2, 0] # x puis y
            # xory = 0 # 0 pour x, 1 pour y
            mur = True


        if NO_COLLISION :
            mur = False


        if not mur :
           

            n_2move = way*2

            if not ispers:
                self._movecam(n_2move, way, 8)
            else :
                self._movepers(n_2move, way, 8)

        else :
            if not self.rls["pers"] :
                self.after(128, self._mur_keytest)
            else :
                self.r["pers"] = True
                if self.touche_save["pers"] is not None :
                    if self.touche_save["pers"].keysym.lower() != self.touche :
                        self.clavier_press(self.touche_save["pers"])
            


    def _mur_keytest(self) : 
        "Permet d'\u00E9viter un arr\u00EAt apr\u00E8s rencontre avec un mur."

        if self.rls["pers"] :
            self.r["pers"] = True
            if self.touche_save["pers"] is not None :
                if self.touche_save["pers"].keysym.lower() != self.touche :
                    self.clavier_press(self.touche_save["pers"])

        else :
            self.after(128, self._mur_keytest)
        



    
    def _todo_after_moving(self, way, ispers=True) :
        
        if ispers :
            self.coords += way * 16
        else :
            self.pos_bg -= way * 16
            for entity in self.entities :
                entity.coords -= way * 16

        self.rlcoords += way


        if not self.rls["pers"] :
            new_rlcoords = self.rlcoords + way
            new_coords = self.coords + way * 16
            ispers = self.test_persorcam_move[tuple(way)](new_coords)
            self.after(6, self.move_pers, *way, new_rlcoords, new_coords, ispers)
        else :
            self.r["pers"] = True
            if self.touche_save["pers"] is not None :
                if self.touche_save["pers"].keysym.lower() != self.touche :
                    self.clavier_press(self.touche_save["pers"])


    def _movepers(self, n_2move, way, nb) :

        self.play_canvas.move(self.pers, n_2move[0], n_2move[1])

        nb -= 1
        if nb != 0 :
            self.after(16, self._movepers, n_2move, way, nb)
        else :
            self.after(10, self._todo_after_moving, way)

    

    def _movecam(self, n_2move, way, nb) :

        self.play_canvas.move(self.bg, -n_2move[0], -n_2move[1])
        self.play_canvas.move("Entity", -n_2move[0], -n_2move[1])

        nb -= 1
        if nb != 0 :
            self.after(16, self._movecam, n_2move, way, nb)
        else :
            self.after(10, self._todo_after_moving, way, False)



        
    def move_bg(self, x, y) :
        
        way = np.array((x, y))
        



        self._movebg(way)


    def _movebg(self, way) :
            
        self.coords += way * 8
        self.play_canvas.move(self.pers, *(way*8))

        self.pos_bg += way * 8
        self.play_canvas.move(self.bg, *(way*8))

        self.play_canvas.move("Entity", *(way*8))

        for entity in self.entities :
            entity.coords -= way * 8



        if not self.rls["cam"] :
            self.after(16, self._movebg, way)
        else :
            self.r["cam"] = True
            if self.touche_save["cam"] is not None :
                if self.touche_save["cam"].keysym.lower() != self.touche :
                    self.clavier_press(self.touche_save["cam"])






    def clavier_release(self, event):
        
        touche = event.keysym.lower()

        if touche in "zqsd" :
            self.rls["pers"] = True

            if self.touche_save["pers"] is not None :
                if event.keysym.lower() == self.touche_save["pers"].keysym.lower() :
                    self.touche_save["pers"] = None
        
        elif touche in "olmk" :
            self.rls["cam"] = True

            if self.touche_save["cam"] is not None :
                if event.keysym.lower() == self.touche_save["cam"].keysym.lower() :
                    self.touche_save["cam"] = None



    def reinitialise(self, *args) :
        
        self.root.reinitialise("in_game", InGameInterface)
        self.root.reinitialise("main_menu", MainMenuInterface)

        self.root.change_page("in_game", "main_menu")
        







root = Root()
root.title("Labyrinth")
root.attributes('-fullscreen', True)

root.main_menu.pack(fill="both", expand=True)


logger.info("This programme has taken {} to setup.".format(perf_counter()-t1))

root.mainloop()

for temp in temps :
    os.remove(temp)