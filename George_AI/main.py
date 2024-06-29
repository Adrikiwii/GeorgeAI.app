import flet as ft
from multiprocessing import Process, Queue
import requests

def main(page: ft.Page):
    url = "https://diverse-game-ringtail.ngrok-free.app/v1/chat/completions"
    page.title = "George.AI"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def resize_min(e):
        if page.width <= 720:
            reponse.height=(page.height-550)
            page.update()

    def resize_max(e):
        reponse.height=(page.height-200)
        page.update()
        
    
    def requete(queue,e,Q_tab,Q_value):
        req_Q = {'role': "user", 'content' : Q_value}
        Q_tab.append(req_Q)
        print(Q_tab)
        body = {
            "model": "lzlv-70b",
            "stream": False,
            "messages": Q_tab,
            "temperature": 1
            }
        json_response = requests.post(url, json=body).json().get('choices', [])
       
        for choice in json_response:
            print(choice.get('message', {}))
            rep_Q = choice.get('message', {})
            Q_tab.append(rep_Q)
        queue.put(Q_tab)
    
    def clear_reponse(e, Q_tab):
        Q_tab = [{'role': "system", 'content' : "Tu es un assistant IA nommé George, tu es spécialisé pour parler en français"}]
        return Q_tab
        


    
    def start_multiprocessing(e):
        try : clear = e.control.text
        except: clear = e.control.hint_text
        if 'result' not in globals():
            global result
            result = [{'role': "system", 'content' : "Tu es un assistant IA nommé George, tu es spécialisé pour parler en français"}]
        queue = Queue()
        Q_val = Question.value
        if clear == "clear":
            result = clear_reponse(e, result)
            reponse.controls.clear()
            page.update()
        elif clear == "Envoyer" or clear == "Question ?":
            reponse.controls.append(
                ft.Row([
                    ft.CircleAvatar(foreground_image_src="icons8-utilisateur-96.png"),
                    ft.Text("\n"+Q_val,expand=True)
                    ],
                ),)
            reponse.controls.append(ft.Row(
                    [
                        ft.CircleAvatar(foreground_image_src="icons8-chatgpt-100.png"),
                        ft.Text("\nJe réfléchis"),
                        ft.ProgressRing(stroke_width=2,stroke_align=-5,color="green")
                    ],vertical_alignment= ft.CrossAxisAlignment.START
            ))
            reponse.controls.append(ft.Markdown("\n ___"))
    
            Question.value = ""
            page.update()
 
            p1 = Process(target=requete, args=(queue, e,result,Q_val))
            p1.start()
            p1.join()

            if not queue.empty():
                result = queue.get()
            print(result)
            reponse.controls.clear()
            for T in result :
                if (T["role"] == 'user'):
                    reponse.controls.append(
                        ft.Row(
                            [
                                ft.CircleAvatar(foreground_image_src="icons8-utilisateur-96.png"),
                                ft.Text("\n"+T["content"],expand=True),
                            ],
                            vertical_alignment= ft.CrossAxisAlignment.START
                        )
                    )
                elif (T["role"] == 'assistant'):
                    reponse.controls.append(
                        ft.Row(
                            [
                                ft.CircleAvatar(foreground_image_src="icons8-chatgpt-100.png"),
                                ft.Markdown("\n"+T["content"],selectable=True,expand=True,extension_set="gitHubWeb",code_theme="atom-one-dark"),
                            ],
                            vertical_alignment= ft.CrossAxisAlignment.START
                        )
                    )
                    reponse.controls.append(ft.Markdown("\n ___"))
            page.update()
        

    
    
    print(page.window_width)
    reponse = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        auto_scroll = True,
        height=(page.height-200),
        width=page.width,
        spacing=50
        )
    
    Question = ft.TextField(hint_text='Question ?', expand=True)
    Question.on_focus = resize_min
    Question.on_blur = resize_max
    Question.on_submit = start_multiprocessing
    clear_bttn = ft.ElevatedButton(text="clear",bgcolor="red",color="black")
    clear_bttn.on_click = start_multiprocessing

    Header = ft.Row(
        [
            clear_bttn,
            ft.Text('George.AI',size=60),
            ft.TextButton(disabled=True),
        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN,expand=True,
        )
    
    Envoyer =  ft.ElevatedButton('Envoyer')
    Envoyer.on_click = start_multiprocessing
    page.add(Header,reponse,ft.Row([Question,Envoyer]))

ft.app(main,assets_dir="assets")
