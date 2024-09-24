from concurrent.futures import ThreadPoolExecutor
from py3pin.Pinterest import Pinterest
from typing import Any, Union
from random import sample

class ReferenceShuffle(Pinterest):
    def __init__(self, password:str='', username:str='', email:str='', proxies: Union[Any, None] = None, cred_root: str = 'data', user_agent:Union[Any, None] = None):
        super().__init__(email=email, password=password,username=username, proxies=proxies, cred_root=cred_root, user_agent=user_agent)
        self.boards_data = {}
        self.pins_data = {}
        self.random_boards = lambda boards, amount: {key:boards[key] for key in sample(list(boards.keys()), amount)}
        
    def get_boards_data(self, username: Union[Any, None] = None):
        if not username:
            data = super().boards()
        else:
            data = self.boards(username) 
        self.boards_data = {b['name']:{'id':b['id'], 'url':b['url']} for b in data} 
        self.boards_data = dict(sorted(self.boards_data.items()))
        
        return self.boards_data

    def search(self, scope, query, page_size=250, reset_bookmark=False, amount:int=1000):
        pins =[]
        temp = []
        while len(pins) < 1000 and  len(pins) < amount*4:
            temp += super().search(scope, query, page_size, reset_bookmark)
            if not temp:
                break
            pins += temp
        self.pin
        return pins
                
    def get_keywords_pins(self, keywords, amount_pins):
        pins = self.search('pins', keywords, 250, False, amount_pins)
        pins = [pin for pin in pins if 'images' in pin.keys()]
        if len(pins) > amount_pins:
            selection = sample(pins, amount_pins)
        else:
            selection = pins
        return {keywords:selection}    
                
    def get_random_pins(self, boards:dict, amount_boards:int=-1, amount_pins:int=12):
        if amount_boards > 0:
            boards = self.random_boards(boards, amount_boards)
        
        shake = {}
        
        with ThreadPoolExecutor() as executor:
            futures = {name: executor.submit(self.get_board_pins, boards[name]['id'], amount_pins, False) for name in boards}
            
            # Recoger los resultados cuando los hilos terminen
            for name, future in futures.items():
                pins = future.result()
                pins = [pin for pin in pins if 'images' in pin.keys()]
                if len(pins) > amount_pins:
                    selection = sample(pins, amount_pins)
                else:
                    selection = pins
                shake[name] = selection
        
        return shake
    
    def get_board_random_feed(self, board_id, amount_pins:int = 12):
        pins =[]
        temp = []
        if amount_pins < 0:
            amount_pins = 1000
        while len(pins) < 1000 and  len(pins) < amount_pins*4:
            temp += self.board_feed(board_id)
            if not temp:
                break
            pins += temp
            
        pins = [pin for pin in pins if 'images' in pin.keys()]
        if len(pins) > amount_pins:
            selection = sample(pins, amount_pins)
        else:
            selection = pins
        return selection
        

    def get_all_pins(self):
        for  board in self.boards_data:
            pins = []
            board_id = board['id']
            while 1:
                temp = self.board_feed(board_id)
                if not temp:
                    break
                pins += temp
            self.pins_data[board['name']] = pins
    
    def get_board_pins(self, board, amount:int=-1, as_url:bool=False, prev_data:list = {}):
        from time import sleep
        sleep(0.5)
        board_id = board
        pins =[]
        if not prev_data:
            while 1:
                temp = self.board_feed(board_id)
                if not temp or all([len(pins) >= amount, amount > 0]):
                    break
                pins += temp
        else:
            flag = True
            while flag:
                temp = self.board_feed(board_id)
                if not temp:
                    break
                for element in temp:
                    if element not in prev_data:
                        prev_data.append(element)
                    else:
                        flag = False
            return prev_data
        
        if as_url:
            return self.pins_url(pins)
        return pins
    
    def pins_url(self, pins):
        links = [p['images']['orig']['url'] if 'images' in p.keys() else None for p in pins]
        while None in links:
            links.remove(None)
        self.links = links
        return links
