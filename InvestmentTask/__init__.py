# from http.client import PAYMENT_REQUIRED
# from sysconfig import parse_config_h

#from tkinter import Pack
from otree.api import *
import random

import os
import datetime
import base64
import glob
import pathlib
import cv2
import numpy as np


doc = """
投資タスク
"""
photopath = "_static/photo"
os.makedirs(photopath, exist_ok=True)

class C(BaseConstants):
    NAME_IN_URL = 'InvestmentTask'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 100
    ENDOWMENT = cu(2200)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    price = models.IntegerField(min=0, max=50, label="最大希望価格")
    computer_price = models.IntegerField()
    reward = models.IntegerField()
    profit = models.IntegerField()
    total_profit = models.IntegerField()
    keep = models.IntegerField()
    tail = models.IntegerField()
    tail_total = models.IntegerField()
    overdraft = models.BooleanField()
    keep_end = models.IntegerField() 
    blackphoto = models.IntegerField(initial=0)
   
  


def computer_price(player: Player):
    player.computer_price = random.randint(1,50)
    
#发生损失的概率，从里面抽选
def reward(player: Player):
    player.reward = random.choice([10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,
                                   20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,
                                   30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
                                   40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,
                                   50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,
                                   -1000,-1000,-1000,-1000,-1000])   
        
#前5轮不会发生重大损失 practice rounds
def reward_5(player: Player):
    player.reward = random.choice([10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,
                                   20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,
                                   30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
                                   40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,
                                   50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50])     

def profit(player: Player):
    if player.price >= player.computer_price :
       player.profit = player.reward - player.computer_price
       
        
    else:
        player.profit = 0   
        


    

def tail_event(player: Player):
    Occurrence = 0
    if player.reward == -1000:
        Occurrence += 1
    if player.reward != -1000:
        Occurrence += 0
    player.tail = Occurrence    
        
        



def creating_session(subsession: Subsession):
    session = subsession.session
    round_number = subsession.round_number

# class MyModel(ExtraModel):
#     player = models.Link(Player)
#     photostr = models.LongStringField()
#     timestamp = models.StringField()

# PAGES

class Investment1(Page):
    timeout_seconds = 300
    timer_text = '最大購入希望価格を決めるまでの残り時間は:'
    form_model = 'player'
    form_fields = ['price']
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number <= 5

    # @staticmethod
    # def live_method(player: Player, data):
    #     if data == 'clicked-button':
    #         player.button_clicks += 1    


        



    @staticmethod
    def js_vars(player: Player):
        return dict(endowment=C.ENDOWMENT)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.price = random.randint(0,50)
            
        
        computer_price(player)
        reward_5(player)
        profit(player)
        tail_event(player)
        player_in_all_rounds = player.in_all_rounds()
        player.tail_total = sum([p.tail for p in player_in_all_rounds])
        player.total_profit=sum([p.profit for p in player_in_all_rounds])
        participant = player.participant
        player.keep = participant.initial + player.total_profit
        if player.keep <= 0:
            player.overdraft = True
        else:
            player.overdraft = False 
        if player.keep >=1000:
            player.keep_end = player.keep - 1000
        if player.keep <1000:
            player.keep_end = 0
        
        participant.keep_end = player.keep_end    

    #写真 
    def live_method(player: Player, data):
        photostr = data["photostr"]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        ## 受け取ったBASE64形式の写真データからプレフィックスを取り除いてから，バイナリに変換する
        prefixstr = "data:image/jpeg;base64,"
        img = base64.b64decode(photostr.replace(prefixstr, "").encode())

        ## バイナリをjpgファイルに書き出す
        with open("{}/{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number), mode='bw') as f:
            f.write(img)  
        photosize = os.path.getsize("{}/{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number))
        if photosize < 204800:
            player.blackphoto = 1
        else :
            player.blackphoto = 0     

        
        # ExtraModelにBASE64形式の写真データを記録する（しなくても良い）
        # MyModel.create(
        #     player = player,
        #     photostr = photostr,
        #     timestamp = timestamp
        # )
    @staticmethod
    def error_message(player: Player, values):
        if player.blackphoto == 1:
            return "通信エラーが発生しました。もう一度価格を決定して、「決定」ボタンを押してください。"


class Investment2(Page):
    timeout_seconds = 15
    timer_text = '最大購入希望価格を決めるまでの残り時間は:'
    form_model = 'player'
    form_fields = ['price']
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number > 5

   

    @staticmethod
    def js_vars(player: Player):
        return dict(endowment=C.ENDOWMENT)
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.price = random.randint(0,50)
            
        
        computer_price(player)
        reward(player)
        profit(player)
        tail_event(player)
        player_in_all_rounds = player.in_all_rounds()
        player.tail_total = sum([p.tail for p in player_in_all_rounds])
        player.total_profit=sum([p.profit for p in player_in_all_rounds])
        participant = player.participant
        player.keep = participant.initial + player.total_profit
        if player.keep <= 0:
            player.overdraft = True
        else:
            player.overdraft = False                     
        if player.keep >=1000:
            player.keep_end = player.keep - 1000
        if player.keep <1000:
            player.keep_end = 0
       
        participant.keep_end = player.keep_end      
        
    ##写真 
    def live_method(player: Player, data):
        photostr = data["photostr"]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        ## 受け取ったBASE64形式の写真データからプレフィックスを取り除いてから，バイナリに変換する
        prefixstr = "data:image/jpeg;base64,"
        img = base64.b64decode(photostr.replace(prefixstr, "").encode())

        ## バイナリをjpgファイルに書き出す
        with open("{}/{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number), mode='bw') as f:
            f.write(img) 
        photosize = os.path.getsize("{}/{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number))
        if photosize < 204800:
            player.blackphoto = 1
        else :
            player.blackphoto = 0      
    
        # MyModel.create(
        #     player = player,
        #     photostr = photostr,
        #     timestamp = timestamp
        # )
    @staticmethod
    def error_message(player: Player, values):
        if player.blackphoto == 1:
            return "通信エラーが発生しました。もう一度価格を決定して、「決定」ボタンを押してください。"




class can_buy(Page):
    timeout_seconds = 10
    @staticmethod
    def is_displayed(player):
      return player.price >= player.computer_price



class cannot_buy(Page):
    timeout_seconds = 10
    @staticmethod
    def is_displayed(player):
      return player.price < player.computer_price





class Feedback_buy(Page):
    timeout_seconds = 15
    @staticmethod
    def is_displayed(player):
      return player.price >= player.computer_price and player.reward != -1000    



    ##写真 
    def live_method(player: Player, data):
        photostr = data["photostr"]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        ## 受け取ったBASE64形式の写真データからプレフィックスを取り除いてから，バイナリに変換する
        prefixstr = "data:image/jpeg;base64,"
        img = base64.b64decode(photostr.replace(prefixstr, "").encode())

        ## バイナリをjpgファイルに書き出す
        with open("{}/{}_{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number,player.tail), mode='bw') as f:
            f.write(img)   
        photosize = os.path.getsize("{}/{}_{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number,player.tail))
        if photosize < 204800:
            player.blackphoto = 1
        else :
            player.blackphoto = 0
    @staticmethod
    def error_message(player: Player, values):
        if player.blackphoto == 1:
            return "通信エラーが発生しました。もう一度「終わる」ボタンを押してください。"    

class Feedback_buy_bigloss(Page):

    @staticmethod
    def is_displayed(player):
      return player.price >= player.computer_price and player.reward == -1000 



    def live_method(player: Player, data):
        photostr = data["photostr"]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        ## 受け取ったBASE64形式の写真データからプレフィックスを取り除いてから，バイナリに変換する
        prefixstr = "data:image/jpeg;base64,"
        img = base64.b64decode(photostr.replace(prefixstr, "").encode())

        ## バイナリをjpgファイルに書き出す
        with open("{}/{}_{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number,player.tail), mode='bw') as f:
            f.write(img)  
        photosize = os.path.getsize("{}/{}_{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number,player.tail))
        if photosize < 204800:
            player.blackphoto = 1
        else :
            player.blackphoto = 0 
    @staticmethod
    def error_message(player: Player, values):
        if player.blackphoto == 1:
            return "通信エラーが発生しました。もう一度「終わる」ボタンを押してください。"    




class Feedback_notbuy(Page):
    timeout_seconds = 15
    @staticmethod
    def is_displayed(player):
      return player.price < player.computer_price and player.reward != -1000 
  
    ##写真 
    def live_method(player: Player, data):
        photostr = data["photostr"]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        ## 受け取ったBASE64形式の写真データからプレフィックスを取り除いてから，バイナリに変換する
        prefixstr = "data:image/jpeg;base64,"
        img = base64.b64decode(photostr.replace(prefixstr, "").encode())

        ## バイナリをjpgファイルに書き出す
        with open("{}/{}_{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number,player.tail), mode='bw') as f:
            f.write(img) 
        photosize = os.path.getsize("{}/{}_{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number,player.tail))
        if photosize < 204800:
            player.blackphoto = 1
        else :
            player.blackphoto = 0  
    @staticmethod
    def error_message(player: Player, values):
        if player.blackphoto == 1:
            return "通信エラーが発生しました。もう一度「終わる」ボタンを押してください。"


class Feedback_notbuy_bigloss(Page):

    @staticmethod
    def is_displayed(player):
      return player.price < player.computer_price and player.reward == -1000 
 



    def live_method(player: Player, data):
        photostr = data["photostr"]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        ## 受け取ったBASE64形式の写真データからプレフィックスを取り除いてから，バイナリに変換する
        prefixstr = "data:image/jpeg;base64,"
        img = base64.b64decode(photostr.replace(prefixstr, "").encode())

        ## バイナリをjpgファイルに書き出す
        with open("{}/{}_{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number,player.tail), mode='bw') as f:
            f.write(img)   
        photosize = os.path.getsize("{}/{}_{}_{}_{}.jpg".format(photopath, player.participant.code, timestamp, player.round_number,player.tail))
        if photosize < 204800:
            player.blackphoto = 1
        else :
            player.blackphoto = 0
    @staticmethod
    def error_message(player: Player, values):
        if player.blackphoto == 1:
            return "通信エラーが発生しました。もう一度「終わる」ボタンを押してください。"    


class Delay(Page):
    timer_text = '休憩の残り時間は:'

    timeout_seconds = 600
    @staticmethod
    def is_displayed(player):
      return player.reward == -1000 and player.tail_total == 1   


class Adjustment(Page):
    @staticmethod
    def is_displayed(player):
      return player.reward == -1000 and player.tail_total == 1          

class OverdraftHappened(Page):
    @staticmethod
    def is_displayed(player: Player):
        
        return player.overdraft 

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return upcoming_apps[0]

class Result(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 100

class test1(Page):

    @staticmethod
    def vars_for_template(player: Player):
        player.participant.vars["videoframe"] = []
    
    @staticmethod
    def js_vars(player: Player):
        player.participant.vars["pagecount"] = 1
        print(player.participant.vars["pagecount"])
        return dict(
            cnt = player.participant.vars["pagecount"]
        )
    
    @staticmethod
    def live_method(player: Player, data):
        # print("get video data")
        # print(data)
        # print(len(data))
        # video = data['videodata']

        # print(video)
        # print(len(video))
        # for attr in dir(video):
        #     # Getting rid of dunder methods
        #     if not attr.startswith("__"):
        #         print(attr, getattr(video, attr))

        # with open("demo.mp4", 'wb+') as f:
        #     f.write(video)
        photostr = data["frame"]
        # timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        ## 受け取ったBASE64形式の写真データからプレフィックスを取り除いてから，バイナリに変換する
        prefixstr = "data:image/jpeg;base64,"
        img = base64.b64decode(photostr.replace(prefixstr, "").encode())
        print(img.__sizeof__())
        player.participant.vars["videoframe"].append(img)

    # @staticmethod
    # def before_next_page(player: Player, timeout_happened):
    #     # Define the codec and create VideoWriter object
    #     fourcc = cv2.VideoWriter_fourcc('M','J','P','G')  #fourccを定義
    #     video = cv2.VideoWriter('output.mp4',fourcc, 30.0, (1920,1080))  #動画書込準備
    #     # video = cv2.VideoWriter("video.mp4", 0, 30, (1920,1080))
    #     for i, image in enumerate(player.participant.vars["videoframe"]):
    #         #use numpy to construct an array from the bytes
    #         x = np.fromstring(image, dtype='uint8')

    #         #decode the array into an image
    #         img = cv2.imdecode(x, cv2.IMREAD_UNCHANGED)
    #         cv2.imwrite(f"test_{i}.jpg", img)
    #         video.write(img)

    #     cv2.destroyAllWindows()
    #     video.release()


class temptest1(Page):
    @staticmethod
    def js_vars(player: Player):
        player.participant.vars["pagecount"] += 1
        print(player.participant.vars["pagecount"])
        return dict(
            cnt = player.participant.vars["pagecount"]
        )

class temptest2(Page):
    @staticmethod
    def js_vars(player: Player):
        player.participant.vars["pagecount"] += 1
        print(player.participant.vars["pagecount"])
        return dict(
            cnt = player.participant.vars["pagecount"]
        )

class temptest3(Page):
    @staticmethod
    def js_vars(player: Player):
        player.participant.vars["pagecount"] += 1
        print(player.participant.vars["pagecount"])
        return dict(
            cnt = player.participant.vars["pagecount"]
        )

class temptest4(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            download_name = "timedelay_player_" + str(player.id_in_subsession),
        )

    @staticmethod
    def js_vars(player: Player):
        player.participant.vars["pagecount"] += 1
        print(player.participant.vars["pagecount"])
        print([x + 1 for x in range(player.participant.vars["pagecount"])])
        return dict(
            cnt = player.participant.vars["pagecount"],
            list = [x + 1 for x in range(player.participant.vars["pagecount"])],
        )

class test2(Page):
    pass

page_sequence = [test1, temptest1, temptest2, temptest3, temptest4, Investment1, Investment2, can_buy, cannot_buy, Feedback_buy, Feedback_buy_bigloss,Feedback_notbuy, Feedback_notbuy_bigloss, OverdraftHappened, Result, test2]

# def vars_for_admin_report(subsession: Subsession):
#     files = {}
#     for p in subsession.get_players():
#         code = p.participant.code
#         pnumber = p.participant.id_in_session
#         tmplist = ["{}/{}".format(pathlib.Path(x).parents[0].name, pathlib.Path(x).name) for x in glob.glob("{}/{}_*.jpg".format(photopath, code))]
#         files[pnumber] = tmplist

#     return dict(
#         files = files
#     )
# def custom_export(players):
#     yield ["session.code", "player.id_in_subsession", "timestamp", "photostr"]

#     for p in players:
#         records_list: list[MyModel] = MyModel.filter(player = p)
#         for record in records_list:
#             yield [p.session.code, p.id_in_subsession, record.timestamp, record.photostr]
