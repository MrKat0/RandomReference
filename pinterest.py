from concurrent.futures import ThreadPoolExecutor
from py3pin.Pinterest import Pinterest
from dotenv import dotenv_values
from typing import Any, Union
from random import choice, sample
import os


VALUES = dotenv_values()
EMAIL = VALUES['EMAIL']
PASSWORD = VALUES['PASSWORD']
USERNAME = VALUES['USERNAME']

style = '''
<style>
    body, html {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        min-height: 100vh;
        overflow-x: hidden;
    }
    
    /* Fondo con degradado */
    body {
        background: linear-gradient(to bottom, #000000, #4b0082);
        background-attachment: fixed;
    }

    /* Contenedor de estrellas */
    #stars-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }

    /* Estilo para el título fijo */
    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 15px 0;
        border-radius: 0 0 25px 25px;
        z-index: 1000;
        color: white; /* Texto blanco */
        font-size: 1.5em; /* Ajuste del tamaño del texto */
        mix-blend-mode: normal; /* Mezcla el texto con el fondo */
        backdrop-filter: blur(3px); /* Desenfoque para el fondo */
    }

    .fixed-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(94, 74, 209, 100%) 5% , transparent 100%);
        z-index: -1; /* Asegura que esté detrás del texto */
    }

    /* Asegurando el espaciado debajo del título fijo */
    .main-container {
        width: 70%;
        margin: 100px auto 0;
        padding-top: 60px;
        box-sizing: border-box;
    }

   /* Estilo para las imágenes en cuadrícula */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr); /* 3 columnas */
        gap: 10px; /* Espacio entre las imágenes */
    }

    .image-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr); /* 3 columnas */
        gap: 10px; /* Espacio entre las imágenes */
    }

    .image-grid div {
        display: block;
        /* gap: 5px; */
    }

    .image-grid img {
        width: 100%;
        height: 400px; /* Ajustar altura fija */
        object-fit: cover; /* Recortar la imagen para ajustarse al contenedor */
        border: 5px solid #7a618b; /* Borde de 15px */
        border-radius: 10px; /* Bordes redondeados */
        display: block; /* Asegura que las imágenes se comporten como bloques */
    }

    .button-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        width: 100%;
    }

    .button {
        background-color: #2a3b61;
        color: rgb(134, 231, 231);
        padding: 10px 20px;
        border-radius: 25px;
        text-decoration: none;
        text-align: center;
        width: 100%;
        border: none;
        cursor: pointer;
        display: inline-block;
        box-sizing: border-box;
    }

    .button:hover {
        background-color: #334a7a;
    }

    /* Estilo para el título */
    .rounded-title {
        display: inline-block; /* Para que el tamaño del borde se ajuste al contenido */
        width: 100%; /* Hace que el fondo ocupe toda la pantalla */
        padding: 10px 20px; /* Espaciado interno */
        background-color: #5e4ad1; /* Fondo detrás del título */
        color: white; /* Color del texto */
        border-radius: 25px; /* Bordes redondeados */
        text-align: center; /* Alinear el texto en el centro */
        border: 2px solid #555; /* Borde alrededor del fondo */
        cursor: pointer; /* Cambia el cursor al pasar por encima */
    }

    /* Centrando el contenedor del título */
    .title-container {
        text-align: center; /* Centrar el título */
        margin-top: 50px; /* Margen superior para espaciar el título */
        border-radius: 10px; /* Bordes redondeados del contenedor */
    }

    /* Estilos modificados para el div colapsable */
    .collapsible-toggle {
        display: none;
    }

    .collapsible-label {
        display: inline-block;
        width: 100%;
        padding: 10px 20px;
        background-color: #5e4ad1;
        color: white;
        border-radius: 25px;
        text-align: center;
        border: 2px solid #555;
        cursor: pointer;
        margin-bottom: 10px;
        /* box-sizing: border-box; */
    }

    .collapsible-content {
        background-color: #49475e;
        max-height: 0;
        overflow: hidden;
        border-radius: 10px; /* Bordes redondeados del contenedor */
        border: 2px solid #5f4979;
        transition: max-height 0.5s cubic-bezier(0, 1, 0, 1);
    }

    .collapsible-toggle:checked + .collapsible-label + .collapsible-content {
        max-height: 9999px;
        transition: max-height 1s ease-in-out;
    }

    .collapsible-label::after {
        content: '▼';
        float: right;
        transform: rotate(0deg);
        transition: transform 0.3s ease-out;
    }

    .collapsible-toggle:checked + .collapsible-label::after {
        transform: rotate(180deg);
    }
</style>
'''
script='''
<script>
    function createStar() {
        const star = document.createElement('div');
        star.style.position = 'absolute';
        star.style.width = '2px';
        star.style.height = '2px';
        star.style.backgroundColor = 'yellow';
        star.style.borderRadius = '50%';
        star.style.left = `${Math.random() * 100}vw`;
        star.style.top = `${Math.random() * 100}vh`;
        star.dataset.speed = Math.random() * 0.10 + 0.01; // Store speed as a dataset attribute
        return star;
    }

    function initStars() {
        const container = document.getElementById('stars-container');
        for (let i = 0; i < 100; i++) {
            container.appendChild(createStar());
        }
        moveStars(); // Initial position update
    }

    function moveStars() {
        const stars = document.querySelectorAll('#stars-container div');
        const scrollY = window.scrollY;
        
        stars.forEach(star => {
            const speed = parseFloat(star.dataset.speed);
            star.style.transform = `translateY(${scrollY * speed}px)`;
        });
        
        requestAnimationFrame(moveStars); // Request next frame for smooth animation
    }

    window.addEventListener('load', initStars);
    window.addEventListener('scroll', () => {
        requestAnimationFrame(moveStars); // Trigger the movement only on scroll
    });
</script>
'''

## Un codigo que regrese todos los pins en un tablero desde la url usando la libreria py3pin?
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

if __name__== '__main__':
    r = ReferenceShuffle(email=EMAIL, password=PASSWORD)
    r.get_boards_data(username=USERNAME)
    boards = r.boards_data
    shake = {}
        
    # def get_board_shake(pins):
    #     selection = []

    #     for i in range(len(pins)):
    #         pin = {}
            # while 'images' not in pin.keys():
            #     pin = choice(pins)
            # url = f"https://pinterest.com/pin/{pin['id']}"
            # img = pin['images']['orig']['url']
            # temp = f'<a href={url}>\n<img src="{img}" max-height: 150px;  style="width: 100%;">\n</a>'
    #         if temp not in selection:
    #             selection.append(temp)
    #         if len(selection)  >= 12:
    #             break
            
    #     return selection
    
    with ThreadPoolExecutor() as executor:
        futures = {name: executor.submit(r.get_board_pins, boards[name]['id'], 3, False) for name in boards}
        
        # Recoger los resultados cuando los hilos terminen
        for name, future in futures.items():
            pins = future.result()
            selection = []
            
            for i in range(len(pins)):
                pin = {}
                while 'images' not in pin.keys():
                    pin = choice(pins)
                url = f"https://pinterest.com/pin/{pin['id']}"
                img = pin['images']['orig']['url']
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
                if temp not in selection:
                    selection.append(temp)
                if len(selection) >= 1:
                    break

            shake[name] = selection
        
    # for name in boards:
    #     pins = r.get_board_pins(boards[name]['id'], as_url=False)
    #     shake[name] = get_board_shake()
    
    content = ['<html>']
    
    content.extend([style])
    
    content.extend([
            '<body>\n',
            '<div id="stars-container"></div>',
            '<header class="fixed-header">',
            f'<h1>{USERNAME}\'s random references</h1>',
            '</header>',
            f'<div class="main-container">\n\t',
        ])

    for i, (name, selection) in enumerate(shake.items()):                   
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

    
    content.extend(['</html>'])

    with open('./referenceShuffle.html', 'w+', encoding='UTF-8') as f:
        f.write(''.join(content))

    os.system('start ./referenceShuffle.html')