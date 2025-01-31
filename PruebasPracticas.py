
# -*- coding: utf-8 -*-

import requests

URL = "https://apivet-f3bdad4c157d.herokuapp.com/animales"

respuesta = requests.get(URL)

if respuesta.status_code == 200: 
    print(f"Se ha obtenido respuesta")
    data = respuesta.json()
    print(f"Hay estos animales:", data)

else: 
    print(f"Ha habido un error al recibir respuesta")

    

datos = {
        
        "tipo": "Perro",
        "raza": "Pastor Aleman",
        "color": "Marron",
        "nombre": "Sinfo"

        }
 
envio = requests.post(URL, json = datos)



if envio.status_code == 201:
   print(f"Se ha enviado con exito")   
    
else: 
 print(f"Ha habido un error de envio")   

