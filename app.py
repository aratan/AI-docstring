import gradio as gr
import requests
from pathlib import Path
from openai import OpenAI

# Autor Victor Arbiol
# Función para detectar el lenguaje de programación según la extensión del archivo
def detect_language(file_path):
    extension = Path(file_path).suffix
    language_map = {
        ".py": "python",
        ".js": "javascript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".rb": "ruby",
        ".go": "go",
        ".rs": "rust",
        ".php": "php",
        ".ts": "typescript",
    }
    return language_map.get(extension.lower(), "unknown")

# Función para enviar el código al modelo LLM y recibir comentarios/docstrings
def generate_comments_and_docstrings(code, language):
    if language == "unknown":
        return "No se pudo detectar el lenguaje del archivo."
    
    # Instrucción para el modelo
    prompt = f"Por favor, agrega comentarios y docstrings al siguiente código en {language}:\n\n{code}\n\nModificado:"
    
    try:
        # Configurar el cliente de OpenAI con Ollama
        openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
        
        # Crear solicitud al modelo
        res = openai.chat.completions.create(
            model='tulu3',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt},  # Aquí se pasa el prompt correctamente
            ]
        )
        
        # Devolver la respuesta generada por el modelo
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al procesar el código: {e}"

# Función principal que maneja todo el flujo
def process_file(file):
    if file is None:
        return "", "Por favor, carga un archivo válido."
    
    # Leer el contenido del archivo
    with open(file.name, "r", encoding="utf-8") as f:
        original_code = f.read()
    
    # Detectar el lenguaje del archivo
    language = detect_language(file.name)
    if language == "unknown":
        return original_code, "No se pudo detectar el lenguaje del archivo."
    
    # Generar comentarios y docstrings usando el modelo LLM
    modified_code = generate_comments_and_docstrings(original_code, language)
    
    return original_code, modified_code

# Función para guardar el archivo modificado
def save_modified_code(filename, code):
    if not filename.strip():
        return "Debes proporcionar un nombre de archivo válido."
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        return f"Código guardado exitosamente en {filename}."
    except Exception as e:
        return f"Error al guardar el archivo: {e}"

# Interfaz Gradio
with gr.Blocks() as demo:
    gr.Markdown("# Procesador de Código con Comentarios y Docstrings")
    
    with gr.Row():
        file_input = gr.File(label="Carga tu archivo de código aquí")
        submit_button = gr.Button("Procesar", variant="primary")  # Botón verde
    
    with gr.Row():
        original_code_box = gr.Textbox(label="Código Original", interactive=False, lines=15)
        modified_code_box = gr.Textbox(label="Código Modificado", interactive=False, lines=15)
    
    with gr.Row():
        filename_input = gr.Textbox(label="Nombre del archivo de salida")
        save_button = gr.Button("Guardar Cambios", variant="primary")  # Botón verde
        save_message = gr.Textbox(label="Estado de Guardado", interactive=False)
    
    # Eventos
    submit_button.click(process_file, inputs=file_input, outputs=[original_code_box, modified_code_box])
    save_button.click(save_modified_code, inputs=[filename_input, modified_code_box], outputs=save_message)

# Ejecutar la interfaz
demo.launch()
