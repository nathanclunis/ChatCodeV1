import openai
import requests
import subprocess
#from openai import OpenAI
import tkinter as tk
from tkinter import scrolledtext, Menu, filedialog, Text, messagebox, ttk
import re
from CCparse import parser
from semantics3 import ASTSimplifier, SemanticAnalyzer
from configparser import ConfigParser
from lark.exceptions import UnexpectedEOF




def query_chatgpt(ast):
    config = ConfigParser()
    config.read('config.ini')
    openai.api_key = config.get('openai', 'api_key')
    prompt = f"Process the following abstract syntax tree produced by CodeChat Compiler a newly created programming language " \
            f"You are a Syntax and semantic analyser Scan the ast for syntax and semantic errors then compile and provide the output of the program: {ast} " \
            f"Format your responses appropriately."

    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",  # Use an available and supported engine
            prompt=prompt,
            temperature=0.7,
            max_tokens=150,
            n=1,
            stop=None
        )
        return response.choices[0].text.strip(), None
    except Exception as e:
        return None, str(e)


def run_code():
    try:
         # Clear the output console at the start of each run
        output_console.config(state=tk.NORMAL)
        output_console.delete(1.0, "end")
        output_console.config(state=tk.DISABLED)

        source_code = code_entry.get("1.0", tk.END)
        ast = parser.parse(source_code)
        simplifier = ASTSimplifier()
        simplified_ast = simplifier.transform(ast)
        analyzer = SemanticAnalyzer()
        analyzer.transform(simplified_ast)

        if analyzer.get_errors():
            display_errors(analyzer.get_errors())
        else:
            response, error = query_chatgpt(simplified_ast.pretty())
            if error:
                display_errors([error])
            else:
                display_output(response)
    except Exception as e:
        display_errors([f"Unexpected error: {str(e)}"])


def display_errors(errors):
    # Clear the output console and enable it for editing
    output_console.config(state=tk.NORMAL)
    output_console.delete(1.0, "end")

    # Insert each error message into the output console
    for error in errors:
        output_console.insert(tk.INSERT, f"{error}\n", 'error')

    # Apply a custom tag for error styling (red text)
    output_console.tag_configure('error', foreground='red')

    # Make the output console read-only again to prevent user edits
    output_console.config(state=tk.DISABLED)



def display_output(output):
    output_console.config(state=tk.NORMAL)
    output_console.delete(1.0, "end")
    output_console.insert(tk.INSERT, str(output))
    output_console.config(state=tk.DISABLED)

# Remember to call `highlight_syntax` in appropriate places, such as after displaying errors or after editing the code, to maintain syntax highlighting.


def highlight_syntax(event=None):
    for tag in ["loop_struct", "contract", "identifier", "data_type", "string"]:
        code_entry.tag_remove(tag, '1.0', tk.END)

    loop_keywords = ['if', 'then', 'else', 'for', 'do', 'while', 'end']
    contract_keywords = ['contract', 'deploy', 'emit', 'event', 'function', 'print']
    modifiers = ['public', 'private', 'return', 'returns']
    data_type_keywords = ['int', 'string', 'bool', 'address', 'var']

    all_keywords = loop_keywords + contract_keywords + modifiers + data_type_keywords
    keyword_pattern = "|".join(r"\b{}\b".format(word) for word in all_keywords)

    for match in re.finditer(keyword_pattern, code_entry.get("1.0", tk.END)):
        start, end = match.span()
        word = match.group(0)

        if word in loop_keywords:
            tag = "loop_struct"
        elif word in contract_keywords:
            tag = "contract"
        elif word in modifiers:
            tag = "identifier"
        elif word in data_type_keywords:
            tag = "data_type"
        code_entry.tag_add(tag, f"1.0+{start}c", f"1.0+{end}c")

    string_pattern = r'\".*?\"'
    for match in re.finditer(string_pattern, code_entry.get("1.0", tk.END), re.S):
        start, end = match.span()
        code_entry.tag_add("string", f"1.0+{start}c", f"1.0+{end}c")

    identifier_pattern = r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'
    for match in re.finditer(identifier_pattern, code_entry.get("1.0", tk.END)):
        start, end = match.span()
        word = match.group(0)
        if word not in all_keywords:
            code_entry.tag_add("identifier", f"1.0+{start}c", f"1.0+{end}c")

    comment_pattern = r'//.*|\#[^\n]*'
    for match in re.finditer(comment_pattern, code_entry.get("1.0", tk.END)):
        start, end = match.span()
        code_entry.tag_add("comment", f"1.0+{start}c", f"1.0+{end}c")
    number_pattern = r'\d+'
    for match in re.finditer(number_pattern, code_entry.get("1.0", tk.END)):
        start, end = match.span()
        code_entry.tag_add("number", f"1.0+{start}c", f"1.0+{end}c")

def on_key_release(event=None):
    highlight_syntax()
    # Additional functionality can go here (e.g., auto-indentation)

    code_entry.bind("<KeyRelease>", on_key_release)

def update_line_numbers(event=None):
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete('1.0', tk.END)
    number_of_lines = code_entry.index(tk.END).split('.')[0]
    line_number_string = "\n".join(str(no) for no in range(1, int(number_of_lines)))
    line_numbers.insert('1.0', line_number_string)
    line_numbers.config(state=tk.DISABLED)

    line_numbers = tk.Text(root, width=4, padx=3, takefocus=0, border=0, background='gray95', state='disabled', wrap='none')
    line_numbers.pack(side=tk.LEFT, fill=tk.Y)

    code_entry.bind("<KeyPress>", update_line_numbers)
    code_entry.bind("<MouseWheel>", update_line_numbers)

def update_status_bar(event=None):
    row, col = code_entry.index(tk.INSERT).split('.')
    status_var.set(f"Line: {row}, Column: {col}")

    status_var = tk.StringVar()
    status_bar = tk.Label(root, textvariable=status_var, anchor='w')
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    code_entry.bind("<KeyPress>", update_status_bar)
    code_entry.bind("<MouseWheel>", update_status_bar)




def open_file():
    try:
        file_path = filedialog.askopenfilename(filetypes=[("CodeChat Compiler File", "*.cc")])
        if file_path:
            with open(file_path, 'r') as file:
                code = file.read()
                code_entry.delete(1.0, "end")
                code_entry.insert("end", code)
    except Exception as e:
        display_errors([f"Failed to open file: {str(e)}"])

def save_file():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".cc", filetypes=[("CodeChat Compiler File", "*.cc")])
        if file_path:
            code = code_entry.get(1.0, "end")
            with open(file_path, 'w') as file:
                file.write(code)
    except Exception as e:
        display_errors([f"Failed to save file: {str(e)}"])


def show_about():
    messagebox.showinfo("About", "CodeChat Compiler\n Version 0.01\n Created By: University of Technology Jamaica")


def show_documentation():
    documentation_path = ''
    try:
        subprocess.run(["open", documentation_path], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def show_example_photo(photo_path):
    try:
        subprocess.run(["open", photo_path], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def find_text():
    find_window = tk.Toplevel(root)
    find_window.title('Find')
    find_window.geometry('300x70')

    def find_action():
        code_entry.tag_remove('match', '1.0', tk.END)
        search = find_entry.get()
        if search:
            idx = '1.0'
            while True:
                idx = code_entry.search(search, idx, nocase=1, stopindex=tk.END)
                if not idx: break
                lastidx = f"{idx}+{len(search)}c"
                code_entry.tag_add('match', idx, lastidx)
                idx = lastidx
            code_entry.tag_config('match', foreground='red', background='yellow')

    find_label = tk.Label(find_window, text="Find:")
    find_label.pack(side=tk.LEFT, padx=10)
    find_entry = tk.Entry(find_window)
    find_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    find_button = tk.Button(find_window, text='Find', command=find_action)
    find_button.pack(side=tk.LEFT, padx=10)

    find_window.transient(root)
    find_window.grab_set()
    root.wait_window(find_window)

def auto_indent(event=None):
    indentation = "    "  # 4 spaces, could be replaced with a tab "\t" based on preference
    line = code_entry.get("insert linestart", "insert lineend")
    indent_level = len(line) - len(line.lstrip())

    if event.keysym == 'Return':
        code_entry.insert(tk.INSERT, "\n" + " " * indent_level)
        return "break"  # to prevent the default newline behavior

    code_entry.bind("<Return>", auto_indent)



root = tk.Tk()
root.title("CodeChat Compiler IDE")
root.geometry("900x600") 

# Improved styling
style = ttk.Style(root)
style.theme_use("clam")  # You can experiment with different themes like 'alt', 'default', 'classic', 'clam', etc.

# Configure custom style
style.configure("TButton", foreground="white", background="#0078D7", padding=5)
style.configure("TScrolledText", foreground="#2B2B2B", background="white", padding=5)
style.configure("TMenu", foreground="#2B2B2B", background="white", padding=5)

# Code Entry (Styled Text Box)
code_entry = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, font=("Consolas", 10))
code_entry.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
# Syntax Highlighting remains the same

# Run Button
run_button = ttk.Button(root, text="Run Code", command=run_code)
run_button.pack(pady=5)

# Output Console (Styled Text Box)
output_console = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5, state=tk.DISABLED, font=("Times New Roman", 12))
output_console.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# Menu Bar
menuBar = Menu(root)
root.config(menu=menuBar)

fileMenu = Menu(menuBar, tearoff=False)
menuBar.add_cascade(label='File', menu=fileMenu)
fileMenu.add_command(label='Open...', command=open_file)
fileMenu.add_command(label='Save As...', command=save_file)

helpMenu = Menu(menuBar, tearoff=False)
menuBar.add_cascade(label='Help', menu=helpMenu)
helpMenu.add_command(label='About', command=show_about)
helpMenu.add_command(label='Documentation', command=show_documentation)

fileMenu.add_command(label='New', command=fileMenu)
fileMenu.add_separator()
editMenu = Menu(menuBar, tearoff=False)

menuBar.add_cascade(label="Edit", menu=editMenu)
editMenu.add_command(label='Cut', command=lambda: code_entry.event_generate("<<Cut>>"))
editMenu.add_command(label='Copy', command=lambda: code_entry.event_generate("<<Copy>>"))
editMenu.add_command(label='Paste', command=lambda: code_entry.event_generate("<<Paste>>"))
editMenu.add_separator()
editMenu.add_command(label='Find', command=find_text)


root.mainloop()
