import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2
import numpy as np
import os
import pandas as pd

# Função para calcular a porosidade usando o método Otsu
def calculate_porosity(image):
    ycbcr = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    cb_channel = ycbcr[:, :, 2]
    _, BW_otsu = cv2.threshold(cb_channel, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    inverted_BW = cv2.bitwise_not(BW_otsu)
    total_area = BW_otsu.size
    white_area = np.sum(inverted_BW == 255)
    porosity = (white_area / total_area) * 100
    return porosity, inverted_BW

# Função para cortar as imagens e calcular a porosidade
def crop_and_calculate_porosity(input_folder_path, output_folder_path, top_border, bottom_border, left_border, right_border):
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    results = []
    for file_name in os.listdir(input_folder_path):
        if file_name.endswith(('.jpg', '.jpeg', '.png', '.tiff')):
            image_path = os.path.join(input_folder_path, file_name)
            img = cv2.imread(image_path)
            
            if img is None:
                print(f"Não foi possível carregar a imagem {file_name}")
                continue

            height, width, _ = img.shape
            start_y = top_border
            end_y = height - bottom_border
            start_x = left_border
            end_x = width - right_border

            if start_y >= end_y or start_x >= end_x:
                print(f"As dimensões de corte excedem o tamanho da imagem {file_name}")
                continue

            # Cortar a imagem
            cropped_image = img[start_y:end_y, start_x:end_x]
            new_file_name = f"{os.path.splitext(file_name)[0]}_cropped{os.path.splitext(file_name)[1]}"
            new_image_path = os.path.join(output_folder_path, new_file_name)
            cv2.imwrite(new_image_path, cropped_image)

            # Calcular a porosidade da imagem cortada
            porosity, inverted_BW = calculate_porosity(cropped_image)
            output_file_name = os.path.splitext(new_file_name)[0] + '_otsu.png'
            output_image_path = os.path.join(output_folder_path, output_file_name)
            cv2.imwrite(output_image_path, inverted_BW)

            # Adicionar os resultados
            results.append({'Imagem': new_file_name, 'Porosidade (%)': porosity})

    df = pd.DataFrame(results)
    return df

# Função para abrir o diálogo de seleção de pasta
def select_folder(entry_widget):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_path)

# Função para exibir o DataFrame na interface gráfica
def show_dataframe(df):
    # Limpar qualquer tabela anterior
    for i in tree.get_children():
        tree.delete(i)
    
    # Inserir os dados no Treeview
    for index, row in df.iterrows():
        tree.insert("", "end", values=(row['Imagem'], f"{row['Porosidade (%)']:.2f}"))

# Função para processar as imagens ao clicar no botão
def process_images():
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()
    if not input_folder or not output_folder:
        messagebox.showerror("Erro", "Por favor, selecione as pastas de entrada e saída.")
        return

    top_border = int(top_border_entry.get())
    bottom_border = int(bottom_border_entry.get())
    left_border = int(left_border_entry.get())
    right_border = int(right_border_entry.get())

    # Cortar as imagens e calcular a porosidade
    df_porosity = crop_and_calculate_porosity(input_folder, output_folder, top_border, bottom_border, left_border, right_border)

    # Exibir o DataFrame na interface gráfica
    show_dataframe(df_porosity)

    # Exibir uma mensagem de conclusão
    messagebox.showinfo("Concluído", "Imagens processadas com sucesso!")

# Criar a janela principal
window = tk.Tk()
window.title("Processamento de Imagens")
window.geometry("600x600")

# Labels e caixas de entrada para pastas
tk.Label(window, text="Pasta de Entrada").pack()
input_folder_entry = tk.Entry(window, width=50)
input_folder_entry.pack()
tk.Button(window, text="Selecionar Pasta", command=lambda: select_folder(input_folder_entry)).pack()

tk.Label(window, text="Pasta de Saída").pack()
output_folder_entry = tk.Entry(window, width=50)
output_folder_entry.pack()
tk.Button(window, text="Selecionar Pasta", command=lambda: select_folder(output_folder_entry)).pack()

# Labels e caixas de entrada para bordas de corte
tk.Label(window, text="Bordas de Corte (px)").pack()

tk.Label(window, text="Topo").pack()
top_border_entry = tk.Entry(window)
top_border_entry.pack()

tk.Label(window, text="Fundo").pack()
bottom_border_entry = tk.Entry(window)
bottom_border_entry.pack()

tk.Label(window, text="Esquerda").pack()
left_border_entry = tk.Entry(window)
left_border_entry.pack()

tk.Label(window, text="Direita").pack()
right_border_entry = tk.Entry(window)
right_border_entry.pack()

# Tabela para mostrar o DataFrame de porosidades
tree = ttk.Treeview(window, columns=("Imagem", "Porosidade (%)"), show="headings", height=10)
tree.heading("Imagem", text="Imagem")
tree.heading("Porosidade (%)", text="Porosidade (%)")
tree.pack(fill="x", pady=10)

# Botão para processar as imagens
tk.Button(window, text="Processar Imagens", command=process_images).pack()

# Iniciar a interface gráfica
window.mainloop()
