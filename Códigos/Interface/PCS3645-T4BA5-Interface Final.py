import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Importar o PIL para carregar imagens
import serial

# Configuração da porta serial
ser = serial.Serial(
    port='COM25',
    baudrate=115200,
    bytesize=serial.SEVENBITS,  # 7 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bit
    timeout=1
)

# Function to send binary data
def send_binary_string(binary_str):
    # Convert binary string to byte
    byte_data = int(binary_str, 2).to_bytes(1, byteorder='big')
    ser.write(byte_data)

# Input bomb times as strings
bomb_time_string_list = [
    "#02,12",
    "#01,02",
    "#20,08",
    "#12,07",
    "#09,12",
    "#12,12",
]

current_index = 0  # To track the current index of the bomb time string list
current_values = [0, 0]  # To store the current values for smooth transition

# Function to interpolate between two colors
def interpolate_color(start_color, end_color, factor):
    start_r = int(start_color[1:3], 16)
    start_g = int(start_color[3:5], 16)
    start_b = int(start_color[5:7], 16)
    
    end_r = int(end_color[1:3], 16)
    end_g = int(end_color[3:5], 16)
    end_b = int(end_color[5:7], 16)
    
    new_r = int(start_r + (end_r - start_r) * factor)
    new_g = int(start_g + (end_g - start_g) * factor)
    new_b = int(start_b + (end_b - start_b) * factor)
    
    return f'#{new_r:02x}{new_g:02x}{new_b:02x}'

# Function to map a value to a color gradient for the strawberry drink (red)
def get_strawberry_color(value, max_value=20):
    red_component = 200 + int((value / max_value) * 55)  # Vai de 200 a 255 para uma variação suave
    return f'#{red_component:02x}4040'

# Function to map a value to a color gradient for the orange drink (orange)
def get_orange_color(value, max_value=20):
    red_component = 255  # Laranja sempre tem um componente de vermelho alto
    green_component = 150 + int((value / max_value) * 105)  # Vai de 150 a 255 para clarear gradualmente
    return f'#{red_component:02x}{green_component:02x}00'

def update_display():
    global current_index, current_values
    
    # Read the bomb time string from the serial port
    if ser.in_waiting > 0:
        current_bomb_time = ser.readline().decode('utf-8').rstrip()
        
        if current_bomb_time.startswith('#') and ',' in current_bomb_time[1:]:
            values = [int(value.strip()) for value in current_bomb_time[1:].split(',')]
            
            # Update the displayed values
            dose1_value_label.config(text=str(values[0]))
            dose2_value_label.config(text=str(values[1]))
            
            # Start the smooth transition for both values
            smooth_transition(values[0], 0, get_strawberry_color)
            smooth_transition(values[1], 1, get_orange_color)
    
    current_index = (current_index + 1) % len(bomb_time_string_list)
    root.after(1000, update_display)

def smooth_transition(target_value, index, color_func, steps=20):
    current_value = current_values[index]
    step_size = (target_value - current_value) / steps
    
    def step():
        nonlocal current_value
        if abs(current_value - target_value) > abs(step_size):
            current_value += step_size
            current_values[index] = current_value
            draw_led_bar(dose1_canvas if index == 0 else dose2_canvas, int(current_value), color_func)
            root.after(50, step)  # Wait 50 ms before the next step
        else:
            current_values[index] = target_value
            draw_led_bar(dose1_canvas if index == 0 else dose2_canvas, target_value, color_func)
    
    step()

def draw_led_bar(canvas, value, color_func, max_value=20):
    canvas.delete("all")
    num_segments = 20
    segment_height = canvas.winfo_height() / num_segments
    
    # Draw LED segments
    for i in range(num_segments):
        y1 = canvas.winfo_height() - (i + 1) * segment_height
        y2 = canvas.winfo_height() - i * segment_height
        if i < value:
            color = color_func(i + 1)
        else:
            color = "#7f8c8d"  # Gray color for inactive segments
        
        canvas.create_rectangle(0, y1, canvas.winfo_width(), y2, fill=color, outline=color)

def number_to_binary_string(number):
    if 1 <= number <= 20:
        return format(number, '08b')  # Convert number to a 5-bit binary string
    else:
        return "Number out of range. Please enter a number between 1 and 20."

# Função para enviar o número em binário pela porta serial
def enviar_numero():
    try:
        valor = int(spinbox_numero.get())
        if 1 <= valor <= 20:
            binary_to_send = number_to_binary_string(valor)  # Binary string to send
            send_binary_string(binary_to_send)
        else:
            print('Por favor, insira um número entre 1 e 20.')
    except ValueError:
        print('Entrada inválida. Por favor, insira um número inteiro.')

# Create the main window
root = tk.Tk()
root.title("Bomb Time Display")
root.attributes('-fullscreen', True)

# Adicionar o logo no topo da janela
logo_image = Image.open("logo.png")  # Certifique-se de que o arquivo logo.png está no mesmo diretório
logo_image = logo_image.resize((200, 100), Image.LANCZOS)  # Usar LANCZOS em vez de ANTIALIAS
logo_photo = ImageTk.PhotoImage(logo_image)

# Criar um frame para o logo e o texto
logo_frame = tk.Frame(root, bg="#5DE2E7")  # Frame para manter o logo e o texto juntos
logo_frame.pack(pady=10)  # Adiciona um espaço ao redor do frame

logo_label = tk.Label(logo_frame, image=logo_photo, bg="#5DE2E7")  # Adicione um fundo se desejar
logo_label.pack(side="left")  # O logo ficará à esquerda no frame

# Adicionar o nome FRISC-V ao lado do logo
name_label = tk.Label(logo_frame, text="FRISC-V", font=("Helvetica", 48, "bold"), fg="#ecf0f1", bg="#5DE2E7")
name_label.pack(side="left", padx=20)  # O nome ficará à direita do logo com espaçamento

background_frame = tk.Frame(root, bg="#5DE2E7")
background_frame.pack(fill="both", expand=True)

dose1_frame = tk.Frame(background_frame, bg="#5DE2E7")
dose1_frame.pack(side="left", padx=100, pady=100)

dose2_frame = tk.Frame(background_frame, bg="#5DE2E7")
dose2_frame.pack(side="right", padx=100, pady=100)

dose1_title_label = tk.Label(dose1_frame, text="Morango", font=("Helvetica", 36, "bold"), fg="#ecf0f1", bg="#5DE2E7")
dose1_title_label.pack()

dose1_value_label = tk.Label(dose1_frame, text="", font=("Helvetica", 48), fg="#ecf0f1", bg="#5DE2E7")
dose1_value_label.pack()  # Display current value for strawberry

dose1_canvas = tk.Canvas(dose1_frame, width=100, height=450, bg="#5DE2E7", highlightthickness=0)  # Increased height
dose1_canvas.pack(pady=10)  # Added padding to position the canvas

dose2_title_label = tk.Label(dose2_frame, text="Laranja", font=("Helvetica", 36, "bold"), fg="#ecf0f1", bg="#5DE2E7")
dose2_title_label.pack()

dose2_value_label = tk.Label(dose2_frame, text="", font=("Helvetica", 48), fg="#ecf0f1", bg="#5DE2E7")
dose2_value_label.pack()  # Display current value for orange

dose2_canvas = tk.Canvas(dose2_frame, width=100, height=450, bg="#5DE2E7", highlightthickness=0)  # Increased height
dose2_canvas.pack(pady=10)  # Added padding to position the canvas

# Adicionar o campo de entrada como um Spinbox e o botão de enviar
frame_input = tk.Frame(background_frame, bg="#5DE2E7")
frame_input.pack(side="top", pady=20)

label_instrucoes = tk.Label(frame_input, text="Limite:", font=("Helvetica", 24), fg="#ecf0f1", bg="#5DE2E7")
label_instrucoes.pack(side="left", padx=10)

spinbox_numero = tk.Spinbox(frame_input, from_=1, to=20, font=("Helvetica", 24), width=5)
spinbox_numero.pack(side="left", padx=10)

botao_enviar = tk.Button(frame_input, text="Enviar", command=enviar_numero, font=("Helvetica", 20), bg="#27ae60", fg="white", relief="flat", padx=20, pady=10)
botao_enviar.pack(side="left", padx=10)

exit_button = tk.Button(background_frame, text="Exit", command=root.destroy, font=("Helvetica", 20), bg="#e74c3c", fg="white", relief="flat", padx=20, pady=10)
exit_button.pack(side="bottom", pady=50)

update_display()
root.mainloop()

# Fechar a porta serial ao sair
# ser.close() # descomentar
