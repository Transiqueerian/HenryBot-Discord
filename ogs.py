#ogs json handler
import json
import requests
import random
from io import BytesIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from apng import APNG
import imgur
import subprocess

def getID(link):
    #returns the ID from an OGS link as a string.
    #Works for player, game, group, ladder IDs
    print("Running ogs.getID()")
    link_contents = link.split('/')
    link_contents = [i for i in link_contents if i]
    if len(link_contents) < 4:
        error = "ERROR: ID NOT FOUND - ogs.py getID()"
        print(error)
        return error
    gamenumber = link_contents[3]
    return gamenumber

class Player:
    def __init__(self, id):
        self.id = id
        self.data = requests.get(f"https://online-go.com/api/v1/players/{self.id}"
                                 ).json()
        self.link = f"https://online-go.com/player/{self.id}/"
        
    def get_icon(self, size = "32"):
        icon_link = self.data["icon"]
        if size != "32":
            if icon_link.startswith("https://secure.gravatar.com"):
                link_elements = icon_link.split("=")
                icon_link_new = f"{link_elements[0]}={size}&d=retro"
            elif icon_link.startswith(
                "https://b0c2ddc39d13e1c0ddad-93a52a5bc9e7cc06050c1a",
                "999beb3694.ssl.cf1.rackcdn.com"):
                link_elements = icon_link.split("-")
                icon_link_new = f"{link_elements[0]}-{link_elements[1]}-{size}.png"
            try:
                icon = requests.get(icon_link_new)
                pic = Image.open(BytesIO(icon.content))
                print(icon_link_new)
                with BytesIO() as output:
                    pic.save(output, format="PNG")
                    return output.getvalue()
            except:
                print("image does not exist at the link")
                print(icon_link_new)
        icon = requests.get(icon_link)
        pic = Image.open(BytesIO(icon.content))
        print(icon_link)
        print("assume 32")
        with BytesIO() as output:
            pic.save(output, format="PNG")
            return output.getvalue()
        
class Game:
    def __init__(self, id):
        self.id = id
        self.data = requests.get(
            f"https://online-go.com/api/v1/games/{self.id}").json()
        self.link = f"https://online-go.com/game/{self.id}/"
        self.moves = self.data["gamedata"]["moves"]
        self.width = self.data["gamedata"]["width"]
        self.height = self.data["gamedata"]["height"]
        self.sgf = requests.get(
            f"https://online-go.com/api/v1/games/{self.id}/sgf/").text
        self.totalmoves = len(self.moves)
        self.frames = []
        self.gif = BytesIO()
        self.time = []
        self.kifu = BytesIO()
        
        self.player_info_height=90
        self.stone_size=20
        self.data_column_width=200
    
    def background(self, stone_size=20):
        pass
        
    
    def ogs_frames(self):
        print("Fetching APNG from OGS (at a rate of about 10 moves per second).\nMay take some time for longer games.")
        print(f"Requested game is {self.totalmoves} moves long.")
        response = requests.get(f"https://online-go.com/api/v1/games/{self.id}/apng/{self.id}-0-0-100.png?from=0&to=0&frame_delay=100")
        print("...\nOpening image with APNG, formatting using BytesIO.")
        im = APNG.open(BytesIO(response.content))
        print("...\nSplitting apng into frames, storing in framelist[].")
        for i, (png, control) in enumerate(im.frames):
            output=BytesIO()
            png.save(output)
            print(type(png))
            if i:
                background = self.frames[i-1].copy()
                newmove = Image.open(output)
                background.paste(newmove, (control.x_offset, control.y_offset))
            else:
                background = Image.open(output)
                print(type(background))
            
            self.frames.append(background)
        self.gif=BytesIO()
        self.frames[0].copy().save(self.gif, format="GIF", save_all=True, append_images=self.frames[1:].copy(), optimize=True, duration=1000, loop=0)
    
    def get_time(self):
        for item in self.moves:
            self.time.append(item[2])
        self.time.append(2000)
        print(self.time)
        print(len(self.time))
        print(len(self.frames))
            
    def get_gif(self, time=0):
        if time:
            if isinstance(time, str):
                if time == "realtime":
                    self.frames[0].copy().save(self.gif, format="GIF", save_all=True,
                                               append_images=self.frames[1:].copy(),
                                               optimize=True, duration=self.time, loop=0)
                else:
                    self.frames[0].copy().save(self.gif, format="GIF", save_all=True,
                                               append_images=self.frames[1:].copy(),
                                               optimize=True, duration=1000, loop=0) 
            else:
                self.frames[0].copy().save(self.gif, format="GIF", save_all=True,
                                           append_images=self.frames[1:].copy(),
                                           optimize=True, duration=time, loop=0) 
        return self.gif.getvalue()
    
    def get_player_icon(self, color="white", icon_size=64):
        icon_link = self.data["players"][f"{color}"]["icon"]
        if icon_size != 32:
            if icon_link.startswith("https://b0c2ddc"):
                icon_link_segments = icon_link.split("-")
                icon_link_segments[-1] = f"{icon_size}.png"
                icon_link = "-".join(map(str,icon_link_segments))
            elif icon_link.startswith("https://secure.gravatar.com"):
                link_elements = icon_link.split("=")
                icon_link = f"{link_elements[0]}={icon_size}&d=retro"
        try:
            response = requests.get(icon_link)
            icon = Image.open(BytesIO(response.content))
            with BytesIO() as output:
                icon.save(output, format="PNG")
                return output.getvalue()
        except:
            print('error in get_player_icon()')
    
    def draw_goban(self, coordinates=True, display_gamedata = True, stone_size = 20,
                   data_column_width=200, player_info_height = 90,
                   board_color = (220,179,92), player_font_size=16,
                   coordinate_font_size=16, player_icon_size=64):
        coordinate_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghjklmnopqrstuvwxyz"
        board_margin = int((stone_size/2) + stone_size)+1
        board_width = (self.width*stone_size)
        board_height = (self.height*stone_size)
        goban = Image.new("RGB", (board_width + (board_margin*2),
                                  board_height + (board_margin*2)), board_color)
        background = Image.new("RGBA", (board_width + (board_margin*2) +
                                        data_column_width,
                                        board_height + (board_margin*2)))#, (40,40,40))
        canvas_background = ImageDraw.Draw(background)
        canvas_background.rounded_rectangle((board_width + (board_margin*2), 1,
                                            board_width + (board_margin*2) +
                                            data_column_width - 1, player_info_height + 1),
                                            fill=(245,245,245), outline="black",
                                            width=1, radius=7)
        canvas_background.rounded_rectangle((board_width + (board_margin*2),
                                             player_info_height + 1,
                                             board_width + (board_margin*2) +
                                             data_column_width - 1,
                                             (player_info_height*2) + 1),
                                            fill=(15,15,15), outline="black",
                                            width=1, radius=7)
        player_white_icon = Image.open(BytesIO(
            self.get_player_icon(icon_size=player_icon_size))).convert("RGBA")
        player_black_icon = Image.open(BytesIO(
            self.get_player_icon(icon_size=player_icon_size, color="black"))).convert(
                "RGBA")
        background.paste(player_white_icon, (board_width + (board_margin*2) + 10,
                                             int((player_info_height/2) - (player_icon_size/2))),
                         player_white_icon)
        background.paste(player_black_icon, (board_width + (board_margin*2) + 10,
                                             int((player_info_height*2) -
                                                 (player_info_height/2) - (player_icon_size/2))),
                         player_black_icon)
        
        def name_color(player_info):
            ui_class = player_info["ui_class"]
            if "bot" in ui_class:
                return (136,136,136)
            elif "professional" in ui_class:
                return (0,128,0)
            elif "moderator" in ui_class:
                return (172,92,241)
            elif "aga" in ui_class:
                return (185,82,0)
            elif "supporter" in ui_class:
                return (223,186,0)
            else:
                return (157,198,255)
        
        player_font = ImageFont.truetype("./arial_ce/ArialCE.ttf",
                                         size=player_font_size)
        player_white_name = self.data["players"]["white"]["username"]
        player_black_name = self.data["players"]["black"]["username"]
        text_x_coordinate = int(board_width + (board_margin*2) + 20 + player_icon_size)
        canvas_background.text((text_x_coordinate, int((player_info_height/2) - (coordinate_font_size/2))),
                               player_white_name, font=player_font,
                               fill=name_color(self.data["players"]["white"]))
        canvas_background.text((text_x_coordinate, int((player_info_height/2) + player_info_height -
                                            (coordinate_font_size/2))), player_black_name,
                               font=player_font,
                               fill=name_color(self.data["players"]["black"]))
        
        canvas = ImageDraw.Draw(goban)
        coordinate_font = ImageFont.truetype("./arial_ce/ArialCE.ttf",
                                             size=coordinate_font_size)
        
        for line in range(self.width):
            x = (stone_size*line) + board_margin + int(stone_size/2) + 1
            top_y = board_margin + (stone_size/2) + 1
            bottom_y = board_height + board_margin - int(stone_size/2)
            shape = [(x, top_y), (x, bottom_y)]
            canvas.line(shape, fill="black", width=0)
            if coordinates:
                coordinate = coordinate_letters[line]
                canvas.text((x, top_y-int(stone_size/2)), coordinate, fill="black",
                            font=coordinate_font, anchor="md")
                canvas.text((x, bottom_y+int((stone_size/2) + (stone_size/4))),
                            coordinate, fill="black", font=coordinate_font,
                            anchor="ma")
        
        for line in range(self.height):
            y = (stone_size*line) + board_margin +int(stone_size/2) + 1
            left_x = board_margin + int(stone_size/2) + 1
            right_x = board_width + board_margin - int(stone_size/2) + 1
            shape = [(left_x, y), (right_x, y)]
            canvas.line(shape, fill="black", width=0)
            if coordinates:
                coordinate = str(self.height-line)
                canvas.text((left_x-int(stone_size/2),y), coordinate, fill="black",
                            font=coordinate_font, anchor="rm")
                canvas.text((right_x+int(stone_size/2),y), coordinate, fill="black",
                            font=coordinate_font, anchor="lm")
            
        star_points=[]
        if self.height%2 and self.width%2:
            tengen = [(int((self.width + 1)/2), int((self.height + 1)/2))]
            star_points = star_points + tengen
        if self.height > 11 and self.width > 11:
            corner_star_points = [(4,4), (4, self.height-3),
                                  (self.width-3,4), (self.width-3,self.height-3)]
            star_points = star_points + corner_star_points
            if self.height%2 and self.height>14 and self.width==self.height:
                side_star_points = [(4, int((self.height + 1)/2)),
                    (self.width-3, int((self.height+1)/2)),
                    (int((self.width+1)/2),4),
                    (int((self.width+1)/2),self.height-3)]
                star_points = star_points + side_star_points
        elif self.height > 8 and self.width > 8:
                corner_star_points = [(3,3), (3, self.height-2),
                                      (self.width-2,3), (self.width-2,self.height-2)]
                star_points = star_points + corner_star_points 
        
        for star_point in star_points:
            x0=((star_point[0]-1)*stone_size) + board_margin + (stone_size/2) - 1
            y0=((star_point[1]-1)*stone_size) + board_margin + (stone_size/2) - 1
            x1=((star_point[0]-1)*stone_size) + board_margin + (stone_size/2) + 3
            y1=((star_point[1]-1)*stone_size) + board_margin + (stone_size/2) + 3
            bounding_box = ((x0,y0),(x1,y1))
            canvas.ellipse(bounding_box, fill="black", outline=None, width=1)
        
        background.paste(goban)
        
        with BytesIO() as output:
            background.save(output, format="PNG")
            self.frames = self.frames + [output.getvalue()]
        
    def draw_kifu(self, stone_size=20):
        board_margin = int(stone_size/2) + 1
        move_history = []
        column_moves = []
        if not self.frames:
            self.draw_goban()
        background = Image.open(BytesIO(self.frames[0])).copy()
        canvas = ImageDraw.Draw(background)
        movenum_font = ImageFont.truetype("./arial_ce/ArialCE.ttf", size=int(stone_size/2))
        for index, move in enumerate(self.moves):
            if index%2:
                color = "white"
                font_color = "black"
            else:
                color = "black"
                font_color = "white"
            move=(move[0],move[1])
            if move[0] == -1:
                move = (index, color, font_color, "pass")
                column_moves = column_moves + [move]
            elif move not in move_history:
                x=(move[0]*stone_size) + board_margin + stone_size
                y=(move[1]*stone_size) + board_margin + stone_size
                x0 = x+1
                y0 = y+1
                x1 = x + stone_size+1
                y1 = y + stone_size+1
                bounding_box = ((x0,y0),(x1,y1))
                canvas.ellipse(bounding_box, fill=color, outline="black", width=1)
                canvas.text((x + int(stone_size/2)+1, y + int(stone_size/2)+1),
                                       f"{index +1}", font=movenum_font, fill=font_color,
                                       anchor="mm")
                move_history = move_history + [move]
            else:
                previous_move = move_history.index(move)
                move = (index,color,font_color, previous_move)
                column_moves = column_moves+[move]
        for index, move in enumerate(column_moves):
            print(move)
            board_margin=int(self.stone_size/2)+self.stone_size+1
            x=(self.width*self.stone_size) + (board_margin*2) + int(self.stone_size/2)
            y=(self.player_info_height*2) + int(
                self.stone_size/2) +(self.stone_size*index) + index
            x1 = x + stone_size
            y1 = y + stone_size
            bounding_box = ((x,y),(x1,y1))
            if move[1] == "white":
                outline_color = "black"
            else:
                outline_color = "gray"
            canvas.ellipse(bounding_box, fill=move[1], outline=outline_color, width=1)
            canvas.text((x + int(stone_size/2), y + int(stone_size/2)),
                        f"{move[0]+1}", font=movenum_font, fill=move[2],
                        anchor="mm")
            if "pass" not in move:
                text = "at"
            else:
                text = "pass"
            y_at = y + int(stone_size/2)
            x_at = x1 + int(stone_size/3)
            canvas.text((x_at+1,y_at), text, font=movenum_font, fill="black", anchor="lm")
            canvas.text((x_at-1,y_at), text, font=movenum_font, fill="black", anchor="lm")
            canvas.text((x_at,y_at+1), text, font=movenum_font, fill="black", anchor="lm")
            canvas.text((x_at,y_at-1), text, font=movenum_font, fill="black", anchor="lm")
            canvas.text((x_at,y_at), text, font=movenum_font, fill="white", anchor="lm")
                
            if "pass" not in move:
                x = x1 + stone_size
                x1 = x + stone_size
                bounding_box = ((x,y),(x1,y1))
                if move[3]%2:
                    color = "white"
                    font_color = "black"
                    outline_color = "black"
                else:
                    color = "black"
                    font_color = "white"
                    outline_color = "gray"
                canvas.ellipse(bounding_box, fill=color, outline=outline_color, width=1)
                canvas.text((x+int(stone_size/2)+1, y + int(stone_size/2) + 1),
                            f"{move[3]+1}", font=movenum_font, fill=font_color,
                            anchor="mm")
            
        with BytesIO() as output:
            background.save(output, format="GIF")
            self.kifu = output.getvalue()

def player_data(player_id): #replace instances of this with class Player.data 
    response = requests.get("https://online-go.com/api/v1/players/" + str(player_id))
    return response.json()

def game_data(game_id): #replace instances of this with class Game.data
    response = requests.get("https://online-go.com/api/v1/games/" + str(game_id))
    return response.json()

def rank_conversion(rank):
    ranking = 30-int(rank)
    if ranking > 0:
        return f"{ranking}k"
    else:
        return f"{(1 - ranking)}d"

def rank(player_id):
    data = player_data(player_id)
    rank = data["ranking"]
    return rank_conversion(rank)
    
def verses(game_id):
    game_info = game_data(game_id)
    black = game_info["players"]["black"]
    white = game_info["players"]["white"]
    brank = rank_conversion(black["ranking"])
    wrank = rank_conversion(white["ranking"])
    challengers = f"{black['username']} {brank} (B) vs {white['username']} {wrank} (W)"
    return challengers
    
def cat():
    response = requests.get("https://thiscatdoesnotexist.com")
    cat = Image.open(BytesIO(response.content))
    with BytesIO() as output:
        cat.save(output, format="PNG")
        return output.getvalue()

def human():
    response = requests.get("https://thispersondoesnotexist.com/image")
    human = Image.open(BytesIO(response.content))
    with BytesIO() as output:
        human.save(output, format="PNG")
        return output.getvalue()
    
def anime():
    creativity = str(random.randint(3, 20)).zfill(2)
    creativity = creativity[:1] + "." + creativity[1:]
    seed = str(random.randint(0, 99999))
    seed = seed.zfill(5)
    response = requests.get(f"https://thisanimedoesnotexist.ai/results/psi-{creativity}/seed{seed}.png")
    anime = Image.open(BytesIO(response.content))
    print(response)
    with BytesIO() as output:
        anime.save(output, format="PNG")
        return output.getvalue(), seed, creativity
    
def add_coordinates(image_link):
    response = requests.get(image_link)
    old_img = Image.open(BytesIO(response.content))
    old_size = old_img.size
    print(old_size)
    new_size = ((old_size[0]+28), old_size[1]+28)
    new_img = Image.new("RGB", new_size, color=(220,179,92))
    new_img.paste(old_img, ((new_size[0]-old_size[0])//2, (new_size[1]-old_size[1])//2))
    #new_img.show()
    
    coords1 = ImageDraw.Draw(new_img)
    myFont = ImageFont.truetype('FreeMono.ttf',17)
    
    coords1.text((21, 1), "A B C D E F G H J K L M N O P Q R S T", font=myFont, fill=(0,0,0))
    coords1.text((21, 392), "A B C D E F G H J K L M N O P Q R S T", font=myFont, fill=(0,0,0))
    
    coordinate = 19
    x=1
    y=15
    x2 = 390
    while coordinate:
        coords1.text((x, y), f"{coordinate}", font=myFont, fill=(0,0,0))
        coords1.text((x2, y), f"{coordinate}", font=myFont, fill=(0,0,0))
        y = y + 20
        coordinate = coordinate-1

    with BytesIO() as output:
        new_img.save(output, format="PNG")
        return output.getvalue()


def test():
    gameID = getID("https://online-go.com/game/44699254")
    game = Game(gameID)
    game.draw_goban()

    game.draw_kifu()
    kifu = Image.open(BytesIO(game.kifu))
    kifu.show()
#test()