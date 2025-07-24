# Gustavo Silva dos Santos responsável pela interface grafica
# Pedro Henrique Dias Simão responsável pela logica do programa
# Lucas Pereira Rapozo responsável pela revisão e teste do programa
# Felipe Sant'ana responsável por revisão do código e ajuda na interface
import tkinter as tk
from tkinter import scrolledtext, messagebox

def Calculo_Endereço(end_base_segmento, offset):
    return (end_base_segmento << 4) + offset

def simular_gpf_gui(end_base_cs, end_base_ss, end_base_ds, end_base_es, acessos_str, output_text_widget):
    output_text_widget.delete(1.0, tk.END)

    try:
        segmentos = {
            "CS": int(end_base_cs, 16),
            "SS": int(end_base_ss, 16),
            "DS": int(end_base_ds, 16),
            "ES": int(end_base_es, 16),
        }
    except ValueError as e:
        messagebox.showerror("Erro de Entrada", f"Erro de valor: {e}")
        return
    segmentos_literais ={"CS":"CÓDIGO","SS":"PILHA","DS":"DADOS","ES":"EXTRA DE DADOS"}
    intervalo_segmentos = {}
    for nome, base in segmentos.items(): #calculo de intervalo dos segmentos
        inicio = Calculo_Endereço(base, 0)
        fim = Calculo_Endereço(base, 0xFFFF)
        intervalo_segmentos[nome] = (inicio, fim)

    output_text_widget.insert(tk.END, "Simulação de GPF (modo real x86):\n\n")
    acessos = [a.strip() for a in acessos_str.split(',') if a.strip()]

    if not acessos:
        output_text_widget.insert(tk.END, " >>>Nenhum acesso para simular\n\n")
        return

    for acesso in acessos:
        try:
            segmento_usado, offset_str = acesso.split(":")
            segmento_usado = segmento_usado.upper()
            offset = int(offset_str, 16)

            if segmento_usado not in segmentos:
                output_text_widget.insert(tk.END, f" >>>Segmento Invalido: {segmento_usado}\n\n")
                continue

            base = segmentos[segmento_usado]
            endereco_fisico = Calculo_Endereço(base, offset)
            
            resultado_str = f" >>>{segmento_usado}:{offset_str}\n"


            

            segmento_invadido = None 
            for outro_segmento, (inicio, fim) in intervalo_segmentos.items(): #Ess trecho verifica quais segmentos foram acessados indevidamente
                if outro_segmento == segmento_usado:
                    continue

                if inicio <= endereco_fisico <= fim:
                    segmento_invadido = outro_segmento
                    break 

            if segmento_invadido:
                (inicio_invadido, fim_invadido) = intervalo_segmentos[segmento_invadido]
                resultado_str += (f" >>>End. Físico = 0x{endereco_fisico:X}\n"
                                f" >>>GPF de {segmentos_literais[segmento_usado]} em {segmentos_literais[segmento_invadido]} ({segmento_usado}:{segmento_invadido})\n")
            
            
            elif offset > 0xFFFF:#Caso meramente ilustrativo, caso seja preenchido errado os segmentos
                resultado_str += (f" >>>End. Físico = 0x{endereco_fisico:X}\n"
                                    f" >>>GPF! E.F. ultrapassa o limite de 64Kb\n")
            
                    
            else: # Se nenhuma das condições de GPF for atendida
                resultado_str += (f" >>>End. Físico = 0x{endereco_fisico:X}\n"
                                    " >>>Não ocorre GPF\n")
            
            output_text_widget.insert(tk.END, resultado_str + "\n")

        except ValueError:
            output_text_widget.insert(tk.END, f"Erro ao processar '{acesso}': formato inválido.\n\n")
        except Exception as e:
            output_text_widget.insert(tk.END, f"Erro inesperado em '{acesso}': {e}\n\n")

def criar_gui():#interface
    janela = tk.Tk()
    janela.title("Simulador de GPF (Modo Real x86)")
    janela.geometry("600x600") 

    frame_registradores = tk.LabelFrame(janela, text="Valores dos Registradores (Hex)", padx=10, pady=10)
    frame_registradores.pack(pady=10, padx=10, fill="x")

    labels_regs = ["CS", "SS", "DS", "ES"]
    entradas_regs = {}
    for i, reg in enumerate(labels_regs):
        tk.Label(frame_registradores, text=f"{reg}:").grid(row=i, column=0, sticky="w", pady=2)
        entrada = tk.Entry(frame_registradores, width=10)
        entrada.insert(0, "0x0000")
        entrada.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
        entradas_regs[reg] = entrada
    
    entradas_regs["CS"].delete(0, tk.END)
    entradas_regs["CS"].insert(0, "0x1000")
    entradas_regs["SS"].delete(0, tk.END) #Chumbancia
    entradas_regs["SS"].insert(0, "0x2000")
    entradas_regs["DS"].delete(0, tk.END)
    entradas_regs["DS"].insert(0, "0x3000")
    entradas_regs["ES"].delete(0, tk.END)
    entradas_regs["ES"].insert(0, "0x4000")

    frame_acessos = tk.LabelFrame(janela, text="Acessos à Memória (SEGMENTO:OFFSET, separados por vírgula)", padx=10, pady=10)
    frame_acessos.pack(pady=10, padx=10, fill="x")

    label_acessos = tk.Label(frame_acessos, text="Ex: CS:0x10, SS:0xFFFE, DS:0x0")
    label_acessos.pack(pady=2, anchor="w")

    entrada_acessos = scrolledtext.ScrolledText(frame_acessos, width=60, height=5, wrap=tk.WORD)

    entrada_acessos.pack(pady=5, padx=5, fill="both", expand=True)

    def on_simular_click(): #Botão de "simular gpf"
        cs_val = entradas_regs["CS"].get()
        ss_val = entradas_regs["SS"].get()
        ds_val = entradas_regs["DS"].get()
        es_val = entradas_regs["ES"].get()
        acessos_str = entrada_acessos.get(1.0, tk.END).strip()
        simular_gpf_gui(cs_val, ss_val, ds_val, es_val, acessos_str, resultado_output)

    botao_simular = tk.Button(janela, text="Simular GPF", command=on_simular_click, background="green", foreground="white")
    botao_simular.pack(pady=10)

    frame_resultado = tk.LabelFrame(janela, text="Resultados da Simulação", padx=10, pady=10)
    frame_resultado.pack(pady=10, padx=10, fill="both", expand=True)

    resultado_output = scrolledtext.ScrolledText(frame_resultado, width=70, height=15, wrap=tk.WORD)
    resultado_output.pack(pady=5, padx=5, fill="both", expand=True)

    janela.mainloop()

criar_gui()