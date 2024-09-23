# from os import listdir, remove, rename
# from os.path import exists
# from random import randrange
# from argparse import ArgumentParser
# from pinterest import *
# from dotenv import dotenv_values
# from random import randint
# from json import load, dump

# VALUES = dotenv_values()

# path = r"C:\Users\Gato\Documents\OneDrive\Obsidian Vault"
# get_links = lambda data: [p['images']['orig']['url']  for p in data if 'images' in p.keys()]
# r = ReferenceShuffle(email=VALUES['EMAIL'], username=VALUES['USERNAME'], password=VALUES['PASSWORD'])

# selections = {}

# def updating(boards):
#     all_data = {}
#     links = {}
#     memory = load(open(fr'{path}\scripts\python\data\data.json', 'r', encoding='UTF-8'))
#     for name in boards:
#         if name not in memory.keys():
#             memory[name] = []
#         if memory[name]:
#             prev_data = memory[name]
#             data = r.get_board_pins(boards[name]['id'], as_url=False, prev_data=prev_data)
#         else:
#             data = r.get_board_pins(boards[name]['id'], as_url=False)
#         all_data[name] = data
#         links[name] = get_links(data)
#         print(f'{name} refreshed!')
#     save_data(all_data)
    
#     return links
    
    
# def shuffle_data(name, pins):
#     selections[name] = []
#     i = 0
    
#     while len(selections[name]) < 12 and i <= 500 and len(pins) > 1:
#         temp = f'<img src="{pins[randint(0, len(pins) - 1)]}"  style="width: 100%;">'
#         if temp not in selections[name]:
#             selections[name].append(temp)
#         i+=1
    
# def save_markdown():          
#     with  open(fr'{path}\References.md', 'w+', encoding='UTF-8') as f:
#         header = '''```button
# name Reset References
# type command
# action Execute Code: Run all Code Blocks in Current File
# color blue
# ```
# '''
#         bottom = '''```python
# from os import system
# from os.path import expanduser

# usr = expanduser('~')
# path = fr'{usr}\Documents\OneDrive\Obsidian Vault\scripts\python'
# system(fr'python "{path}\DailyDrawScript.py" -s')
# print('# References chaged')
# ```
# '''

#         f.write(header)
#         for name in selections:
#             f.write('\n---\n')
#             f.write(f'## {name}')
#             f.write('\n<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">\n')
#             f.write('\n'.join(selections[name]))
#             f.write('\n</div>\n')
#         f.write('\n')
#         f.write(bottom)
#         f.close()
        
# def save_data(all_data):        
#     with open(fr'{path}\scripts\python\data\data.json', 'w+') as datafile:
#         dump(all_data, datafile, indent=4)
#         datafile.close()

# def main(refresh, shuffle):
#     r.get_boards_data(VALUES['USERNAME'])
#     boards = r.boards_data
    
#     if refresh:
#         links = updating(boards)
#     else:
#          data = load(open(fr'{path}\scripts\python\data\data.json', 'r', encoding='UTF-8'))
#          links = dict(get_links(data))
#     if shuffle:
#         for name, pins in links.items():
#             shuffle_data(name, pins)
#         save_markdown()
    
# if __name__== '__main__':
#     parser = ArgumentParser()
#     parser.add_argument('-r', '--refresh',action='store_true')
#     parser.add_argument('-s', '--shuffle',action='store_true')
#     args = parser.parse_args()
    
#     main(args.refresh, args.shuffle)

import os
import json
import argparse
from random import choice
from typing import Dict, List
from dotenv import dotenv_values
from pinterest import ReferenceShuffle
from concurrent.futures import ThreadPoolExecutor

VALUES = dotenv_values()
PATH = r"C:\Users\Gato\Documents\OneDrive\Obsidian Vault"
DATA_FILE = os.path.join(PATH, "scripts", "python", "data", "data.json")
REFERENCES_FILE = os.path.join(PATH, "References.md")

def get_links(data: List[Dict]) -> List[str]:
    return [p['images']['orig']['url'] for p in data if 'images' in p]

class PinterestManager(ReferenceShuffle):
    def __init__(self):
        super().__init__(email=VALUES['EMAIL'], username=VALUES['USERNAME'], password=VALUES['PASSWORD'])
        self.boards_data = {}
        self.selections = {}

    def update_boards(self) -> Dict[str, List[str]]:
        all_data = {}
        links = {}
        try:
            with open(DATA_FILE, 'r', encoding='UTF-8') as f:
                memory = json.load(f)
        except:
            memory = {}
    
        # Usar ThreadPoolExecutor para paralelizar la obtención de pins
        with ThreadPoolExecutor() as executor:
            futures = {}
            
            # Enviar cada tarea de obtención de pins a un futuro
            for name, board in self.boards_data.items():
                prev_data = memory.get(name, [])
                futures[name] = executor.submit(self.get_board_pins, board['id'], -1, False)
            
            # Recoger los resultados de los futuros
            for name, future in futures.items():
                data = future.result()  # Espera a que el hilo termine y recoge el resultado
                all_data[name] = data
                # links[name] = get_links(data)  # Obtener los links de las imágenes
                print(f'{name} refreshed!')

        with open(DATA_FILE, 'w', encoding='UTF-8') as f:
            json.dump(all_data, f, indent=4)

        return data

    def shuffle_data(self, name: str, pins: List[dict], links:bool):
        self.selections[name] = []
        for _ in range(min(12*5, len(pins))):
            pin = {}
            while 'images' not in pin.keys():
                pin = choice(pins)
            url = f"https://pinterest.com/pin/{pin['id']}"
            img = pin['images']['orig']['url']
            # temp = f'\n<img src="{img}" max-height: 150px;  style="width: 100%;">'
            temp = f'\n\t\t\t\t<img src="{img}">'
            
            buttons = ['\n\t\t\t\t<div class="button-container">',
            f'\t\t\t\t\t<a href="{url}" target="_blank">',
            '\t\t\t\t\t\t<button class="button" rel="noopener noreferrer">Pinterest</button>',
            '\t\t\t\t\t</a >',
            f'\t\t\t\t\t<a href="{img}" target="_blank">',
            '\t\t\t\t\t\t<button class="button" rel="noopener noreferrer">Full</button>',
            '\t\t\t\t\t</a>',
            '\t\t\t\t</div>\n']
            button_block = "\n".join(buttons)
            temp = '\t\t\t<div class="image-grid">'+f'{temp}' + f'{button_block}'+ '\t\t\t</div>'
            if temp not in self.selections[name]:
                self.selections[name].append(temp)
            if len(self.selections[name]) >=12:
                break
            

    def save_markdown(self):
        header = ['\n```button\n',
                        'name Reset References\n',
                        'type command\n',
                        'action Execute Code: Run all Code Blocks in Current File\n',
                        'color blue\n',
                        '```\n'
                        ]
        bottom = ['```python\n',
          'import os\n',
          'import sys\n\n',
          'usr = os.path.expanduser("~")\n',
          'path = os.path.join(usr, "Documents", "OneDrive", "Obsidian Vault", "scripts", "python")\n',
          'script = os.path.join(path, "DailyDrawScript.py")\n',
          'os.system(f\'python "{script}" -r\')\n',
          "print('# References changed')\n",
          "```\n\n",
          '```python\n',
          'import os\n',
          'import sys\n\n',
          'usr = os.path.expanduser("~")\n',
          'path = os.path.join(usr, "Documents", "OneDrive", "Obsidian Vault", "scripts", "python")\n',
          'script = os.path.join(path, "DailyDrawScript.py")\n',
          'os.system(f\'python "{script}" -s -l\')\n',
          "print('# References changed')\n",
          "```"]
        content = header
        # for name, selection in self.selections.items():
        #     content.extend([
        #         '\n---\n',
        #         f'## {name}',
        #         '\n<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">\n',
        #         '\n'.join(selection),
        #         '\n</div>\n\n'
        #     ])

        content.extend([
            '\n---\n',
            '<body>\n'
        ])

        for i, (name, selection) in enumerate(self.selections.items()):
            content.extend([
            '\t<div class="title-container">\n',
            f'\t\t<input type="checkbox" id="{name}-toggle" class="collapsible-toggle" checked>\n',
            f'\t\t<label for="{name}-toggle" class="collapsible-label">{name}</label>\n',
            # '</div>\n',  # Encabezado para cada nombre
            # '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">\n',
            '\t\t<div class="collapsible-content">\n',
            '\t\t\t<div class="image-grid">\n',
            '\n'.join(selection),
            '\n\t\t\t</div>\n',  # Termina el grid de 3 columnas para el contenido
            '\t\t</div>\n',  # Termina el contenido colapsable
            # '</div>\n'  # Termina la división para esta sección
            '\t</div>\n'  # Termina la división para main container
            ])
        content.extend([
            '</body>\n',  # Cierra el div de las 2 columnas
            '\n---\n'
        ])
        
        content.extend(bottom)

        with open(REFERENCES_FILE, 'w', encoding='UTF-8') as f:
            f.write(''.join(content))

def main(refresh: bool, shuffle: bool, links:bool):
    manager = PinterestManager()
    manager.get_boards_data()

    if refresh:
        manager.update_boards()
    
    with open(DATA_FILE, 'r', encoding='UTF-8') as f:
        data = json.load(f)
        if not data and not refresh:        
            manager.update_boards()
            exit()
    # finally:
    #     links = {name: get_links(pins) for name, pins in data.items()}
            
    if shuffle:
        for name, pins in data.items():
            manager.shuffle_data(name, pins, links)
        manager.save_markdown()

if __name__ == '__main__':
    from time import time
    start_time = time()
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--refresh', action='store_true')
    parser.add_argument('-s', '--shuffle', action='store_true')
    parser.add_argument('-l', '--links', action='store_true')
    args = parser.parse_args()

    # main(args.refresh, args.shuffle, args.links)
    main(args.refresh, True, args.links)
    print('Execution time ', {time()-start_time})