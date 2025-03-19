import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def adicionar_texto(img, texto, posicao, tamanho_fonte=30, cor=(0, 255, 255)):
    img_pil = Image.fromarray(img)
    desenhar = ImageDraw.Draw(img_pil)
    fonte = ImageFont.truetype("arial.ttf", tamanho_fonte)
    desenhar.text(posicao, texto, font=fonte, fill=cor)
    return np.array(img_pil)

def obter_area(contorno):
    return cv2.contourArea(contorno)

def localizar_contornos(img):
    escala_cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bordas = cv2.Canny(escala_cinza, 50, 150)
    contornos, _ = cv2.findContours(bordas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contornos

def processar_video(caminho_video):
    captura = cv2.VideoCapture(caminho_video)
    ultrapassagem = False
    impacto = False
    contato_anterior = False

    while captura.isOpened():
        sucesso, quadro = captura.read()
        if not sucesso:
            break

        quadro = cv2.resize(quadro, (quadro.shape[1] // 2, quadro.shape[0] // 2))
        resultado = quadro.copy()
        contornos = localizar_contornos(quadro)

        formas = [(c, obter_area(c)) for c in contornos]

        if len(formas) >= 2:
            maior = max(formas, key=lambda x: x[1])[0]
            menor = min(formas, key=lambda x: x[1])[0]
            cv2.drawContours(resultado, [maior], -1, (0, 0, 255), 2)

            colidiu = (cv2.boundingRect(menor)[0] + cv2.boundingRect(menor)[2] > cv2.boundingRect(maior)[0] and
                       cv2.boundingRect(menor)[0] < cv2.boundingRect(maior)[0] + cv2.boundingRect(maior)[2] and
                       cv2.boundingRect(menor)[1] + cv2.boundingRect(menor)[3] > cv2.boundingRect(maior)[1] and
                       cv2.boundingRect(menor)[1] < cv2.boundingRect(maior)[1] + cv2.boundingRect(maior)[3])

            if colidiu:
                impacto = True
                contato_anterior = True
                resultado = adicionar_texto(resultado, "COLISION DETECTED", (500, 50), tamanho_fonte=40, cor=(0, 255, 255))

            elif impacto and not colidiu:
                if cv2.boundingRect(maior)[0] < cv2.boundingRect(menor)[0]:
                    ultrapassagem = True
                    impacto = False
                    contato_anterior = False

            if ultrapassagem and not contato_anterior:
                resultado = adicionar_texto(resultado, "PASSED THE BARRIER", (500, 50), tamanho_fonte=40, cor=(0, 0, 255))

        cv2.imshow('Saída', resultado)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    captura.release()
    cv2.destroyAllWindows()

caminho_arquivo = 'q1/q1B.mp4'
processar_video(caminho_arquivo)
