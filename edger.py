""""Tkinter-based GUI"""

import funcs
import tkinter as tk
from tkinter import Tk, filedialog, END, MULTIPLE
import pandas as pd


class App:
    def __init__(self, master):
        self.master = master
        master.title('Edger')

        master.columnconfigure([0, 1], weight=1)
        master.rowconfigure([0, 1, 2, 4, 5, 6], minsize=40, weight=1)

        self.graphtypes = ['normal', 'citation', 'bipartite']
        self.om_graphtype_var = tk.StringVar(master)
        self.om_graphtype_var.trace('w', self.update_labels_on_graphtype)
        self.om_graphtype_var.set(self.graphtypes[0])

        self.cols = ['']
        self.om_nodecol_var = tk.StringVar(master)
        self.om_nodecol_var.set(self.cols[0])
        self.om_nodecol_var.trace('w', self.check_node_edge_equality)
        self.om_edgecol_var = tk.StringVar(master)
        self.om_edgecol_var.set(self.cols[0])
        self.om_edgecol_var.trace('w', self.check_node_edge_equality)

        self.seperators = ['', ',', ';', '|']
        self.om_node_sep = tk.StringVar(master)
        self.om_node_sep.set(self.seperators[0])
        self.om_edge_sep = tk.StringVar(master)
        self.om_edge_sep.set(self.seperators[0])

        self.lbl_file = tk.Label(text='Please choose a file')
        self.btn_file = tk.Button(text='Open', command=self.get_file)
        self.lbl_graphtype = tk.Label(text='Which graph type?')
        self.om_graphtype = tk.OptionMenu(
            master, self.om_graphtype_var, *self.graphtypes)
        self.lbl_nodecol = tk.Label(text='Which column contains your nodes?')
        self.om_nodecol = tk.OptionMenu(
            master, self.om_nodecol_var, *self.cols)
        self.lbl_nodesep = tk.Label(
            text='If you have multiple items per cell, specify seperator')
        self.om_nodesep = tk.OptionMenu(
            master, self.om_node_sep, *self.seperators)
        self.lbl_edgecol = tk.Label(text='Which column contains your edges?')
        self.om_edgecol = tk.OptionMenu(
            master, self.om_edgecol_var, *self.cols)
        self.lbl_edgesep = tk.Label(
            text='If you have multiple items per cell, specify seperator')
        self.om_edgesep = tk.OptionMenu(
            master, self.om_edge_sep, *self.seperators)
        self.lbl_nodeattrs = tk.Label(
            text='Node attribute column:')
        self.lbx_nodeattrs = tk.Listbox(master, selectmode=MULTIPLE)
        self.lbl_edgeattrs = tk.Label(
            text='Edge attribute collumn:')
        self.lbx_edgeattrs = tk.Listbox(master, selectmode=MULTIPLE)
        self.btn_close = tk.Button(
            master, text='Close', command=master.destroy)
        self.btn_run = tk.Button(text='Run', command=self.run_edger)
        self.lbl_info = tk.Label(text='')

        # Config
        self.om_graphtype.configure(state='disabled')
        self.om_nodecol.configure(state='disabled')
        self.om_edgecol.configure(state='disabled')
        self.om_nodesep.configure(state='disabled')
        self.om_edgesep.configure(state='disabled')
        self.btn_run.configure(
            bg='green', activebackground='pale green', state='disabled')

        self.lbl_file.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.btn_file.grid(row=0, column=1, sticky='e', padx=5, pady=5)

        self.lbl_graphtype.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.om_graphtype.grid(row=1, column=1, sticky='e', padx=5, pady=5)

        self.lbl_nodecol.grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.om_nodecol.grid(row=2, column=1, sticky='e', padx=5, pady=5)

        self.lbl_nodesep.grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.om_nodesep.grid(row=3, column=1, sticky='e', padx=5, pady=5)

        self.lbl_edgecol.grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.om_edgecol.grid(row=4, column=1, sticky='e', padx=5, pady=5)

        self.lbl_edgesep.grid(row=5, column=0, sticky='w', padx=5, pady=5)
        self.om_edgesep.grid(row=5, column=1, sticky='e', padx=5, pady=5)

        self.lbl_nodeattrs.grid(row=6, column=0, sticky='w', padx=5, pady=5)
        self.lbx_nodeattrs.grid(row=7, column=0, sticky='w', padx=5, pady=5)

        self.lbl_edgeattrs.grid(row=6, column=1, sticky='w', padx=5, pady=5)
        self.lbx_edgeattrs.grid(row=7, column=1, sticky='w', padx=5, pady=5)

        self.btn_close.grid(row=8, column=0, sticky='w', padx=5, pady=5)
        self.btn_run.grid(row=8, column=1, sticky='e', padx=5, pady=5)

        self.lbl_info.grid(row=9, column=0, columnspan=2,
                           sticky='w', padx=5, pady=5)

    def get_file(self):
        try:
            self.file_path = filedialog.askopenfilename(
                filetypes=[('CSV files', '.csv')])
            self.df = pd.read_csv(self.file_path)

            node_menu = self.om_nodecol['menu']
            node_menu.delete(0, 'end')
            for string in self.df.columns:
                node_menu.add_command(
                    label=string, command=lambda value=string:
                    self.om_nodecol_var.set(value))

            edge_menu = self.om_edgecol['menu']
            edge_menu.delete(0, 'end')
            for string in self.df.columns:
                edge_menu.add_command(
                    label=string, command=lambda value=string:
                    self.om_edgecol_var.set(value))

            for col in self.df.columns:
                self.lbx_nodeattrs.insert(END, col)
                self.lbx_edgeattrs.insert(END, col)

            self.om_graphtype.configure(state='normal')
            self.om_nodecol.configure(state='normal')
            self.om_edgecol.configure(state='normal')
            self.om_nodesep.configure(state='normal')
            self.om_edgesep.configure(state='normal')
            self.btn_run.configure(state='normal')
            self.btn_file.configure(bg='grey')

        except (ValueError, FileNotFoundError):
            pass

    def update_labels_on_graphtype(self, *args):
        # We need try-except because the variable isn't set on load
        try:
            if self.om_graphtype_var.get() in ('normal', 'citation'):
                self.lbl_nodecol['text'] = 'Which column contains your nodes?'
                self.lbl_edgecol['text'] = 'Which column contains your edges?'
            elif self.om_graphtype_var.get() == 'bipartite':
                self.lbl_nodecol['text'] = 'Which is your first node column?'
                self.lbl_edgecol['text'] = 'Which is your second node column?'
        except AttributeError:
            pass

    def check_node_edge_equality(self, *args):
        if self.om_nodecol_var.get() == self.om_edgecol_var.get():
            self.lbl_info['text'] = 'Node and edge columns should not be the same.'
            self.lbl_info['fg'] = 'red'
        else:
            self.lbl_info['text'] = ''
            self.lbl_info['fg'] = 'black'

    def run_edger(self):
        nodeattrs = [self.lbx_nodeattrs.get(
            i) for i in self.lbx_nodeattrs.curselection()]

        filename = funcs.edger(
            df=self.df,
            node=self.om_nodecol_var.get(),
            link=self.om_edgecol_var.get(),
            graphtype=self.om_graphtype_var.get(),
            attr_cols=nodeattrs,
            node_sep=self.om_node_sep.get(),
            link_sep=self.om_edge_sep.get(),
            file_path=self.file_path,
        )
        if filename:
            self.lbl_info['text'] = f'Success! Saved to {filename}'
            self.btn_file.configure(state='disabled')


if __name__ == '__main__':
    root = Tk()
    App(root)
    root.mainloop()
