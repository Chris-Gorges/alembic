import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np

# --- Plotting ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Your Library ---
from engineering_lib import heat_transfer, reporting

# --- Configuration ---
ctk.set_appearance_mode("Dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"


class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Process Engineering Suite Pro")
        self.geometry("900x700")

        # Data Logic (Same as before)
        self.calc_map = {
            "Heat Transfer": {
                "Calc. HX Area (A)": {
                    "func": heat_transfer.calculate_hx_area,
                    "inputs": [
                        "Heat Load (Q)",
                        "Heat Trans. Coeff. (U)",
                        "LMTD (dT_lm)",
                    ],
                    "units": ["Watts", "W/m²K", "Kelvin"],
                    "result_unit": "m²",
                    "presets": {1: heat_transfer.U_GUIDELINES},
                    "equation_str": "A = Q / (U * dT_lm)",
                },
                "Calc. Heat Load (Q)": {
                    "func": heat_transfer.calculate_heat_load,
                    "inputs": ["U Value", "Area (A)", "LMTD (dT_lm)"],
                    "units": ["W/m²K", "m²", "Kelvin"],
                    "result_unit": "Watts",
                    "presets": {0: heat_transfer.U_GUIDELINES},
                    "equation_str": "Q = U * A * dT_lm",
                },
            }
        }

        # --- Layout: 2 Columns (Sidebar + Main Content) ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="ProcessTool v2",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.pack(pady=20)

        # Topic Selector (Sidebar)
        self.topic_label = ctk.CTkLabel(self.sidebar, text="Topic:", anchor="w")
        self.topic_label.pack(padx=20, pady=(10, 0), anchor="w")

        self.topic_var = ctk.StringVar(value=list(self.calc_map.keys())[0])

        # FIX 1: Added variable=self.topic_var
        self.topic_combo = ctk.CTkComboBox(
            self.sidebar,
            values=list(self.calc_map.keys()),
            command=self.update_subtopics,
            variable=self.topic_var,
        )
        self.topic_combo.pack(padx=20, pady=5)

        # Subtopic Selector (Sidebar)
        self.subtopic_label = ctk.CTkLabel(
            self.sidebar, text="Calculation:", anchor="w"
        )
        self.subtopic_label.pack(padx=20, pady=(20, 0), anchor="w")

        self.subtopic_var = ctk.StringVar(
            value="Calc. HX Area (A)"
        )  # Give it a default value

        # FIX 2: Added variable=self.subtopic_var
        self.subtopic_combo = ctk.CTkComboBox(
            self.sidebar, command=self.generate_inputs, variable=self.subtopic_var
        )
        self.subtopic_combo.pack(padx=20, pady=5)

        # 2. Main Content Area (Scrollable)
        self.main_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Header in Main Frame
        self.header_label = ctk.CTkLabel(
            self.main_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header_label.pack(anchor="w", pady=(10, 20))

        # Equation Display
        self.equation_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.equation_frame.pack(fill="x", pady=10)
        self.eq_label = ctk.CTkLabel(
            self.equation_frame, text="", font=ctk.CTkFont(family="Courier", size=16)
        )
        self.eq_label.pack()

        # Input Container
        self.input_container = ctk.CTkFrame(self.main_frame)
        self.input_container.pack(fill="x", pady=10)
        self.entry_widgets = []

        # Calculate Button
        self.calc_btn = ctk.CTkButton(
            self.main_frame,
            text="Calculate Result",
            command=self.perform_calculation,
            height=40,
        )
        self.calc_btn.pack(pady=20, fill="x")

        # Result Display
        self.result_var = ctk.StringVar(value="Result: -")
        self.result_display = ctk.CTkLabel(
            self.main_frame,
            textvariable=self.result_var,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#3B8ED0",
        )
        self.result_display.pack(pady=10)

        # --- Graphing & Export Section ---
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="x", pady=20)
        self.tabview.add("Sensitivity Plot")
        self.tabview.add("Export Report")

        # Tab 1: Plotting
        self.setup_plot_tab()

        # Tab 2: Exporting
        self.setup_export_tab()

        # Initialize
        self.update_subtopics(self.topic_var.get())
        self.current_fig = None  # Store figure for export

    def setup_plot_tab(self):
        tab = self.tabview.tab("Sensitivity Plot")

        # Controls
        ctrl_frame = ctk.CTkFrame(tab, fg_color="transparent")
        ctrl_frame.pack(fill="x")

        self.vary_combo = ctk.CTkComboBox(ctrl_frame, width=150)
        self.vary_combo.pack(side="left", padx=5)

        self.range_start = ctk.CTkEntry(ctrl_frame, placeholder_text="Start", width=80)
        self.range_start.pack(side="left", padx=5)

        self.range_end = ctk.CTkEntry(ctrl_frame, placeholder_text="End", width=80)
        self.range_end.pack(side="left", padx=5)

        ctk.CTkButton(
            ctrl_frame, text="Plot", command=self.generate_plot, width=80
        ).pack(side="left", padx=10)

        # Canvas container
        self.plot_container = ctk.CTkFrame(tab)
        self.plot_container.pack(fill="both", expand=True, pady=10)
        self.canvas = None

    def setup_export_tab(self):
        tab = self.tabview.tab("Export Report")

        ctk.CTkLabel(tab, text="Export current calculation & plot to:").pack(pady=10)

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(
            btn_frame,
            text="Export to Excel",
            command=self.save_excel,
            fg_color="#107C41",
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame, text="Export to PDF", command=self.save_pdf, fg_color="#b30b00"
        ).pack(side="left", padx=10)

    # --- Logic ---

    def update_subtopics(self, choice):
        subtopics = list(self.calc_map[choice].keys())
        self.subtopic_combo.configure(values=subtopics)
        self.subtopic_combo.set(subtopics[0])
        self.generate_inputs(subtopics[0])

    def generate_inputs(self, choice):
        # Clear old
        for widget in self.input_container.winfo_children():
            widget.destroy()
        self.entry_widgets = []

        topic = self.topic_var.get()
        data = self.calc_map[topic][choice]

        self.header_label.configure(text=choice)
        self.eq_label.configure(text=data.get("equation_str", ""))
        self.vary_combo.configure(values=data["inputs"])  # Update plot dropdown
        self.vary_combo.set(data["inputs"][1])  # Default to second param

        preset_map = data.get("presets", {})

        for i, (label_text, unit) in enumerate(zip(data["inputs"], data["units"])):
            row = ctk.CTkFrame(self.input_container, fg_color="transparent")
            row.pack(fill="x", pady=5)

            ctk.CTkLabel(
                row, text=f"{label_text} [{unit}]", width=200, anchor="w"
            ).pack(side="left")

            ent = ctk.CTkEntry(row)
            ent.pack(side="left", fill="x", expand=True, padx=10)
            self.entry_widgets.append(ent)

            # Helper Dropdown
            if i in preset_map:
                guidelines = preset_map[i]

                def make_cmd(e_widget=ent, g_data=guidelines):
                    return lambda val: (
                        e_widget.delete(0, "end"),
                        e_widget.insert(0, str(g_data[val])),
                    )

                helper = ctk.CTkComboBox(
                    row, values=list(guidelines.keys()), width=150, command=make_cmd()
                )
                helper.set("Presets...")
                helper.pack(side="right")

    def get_inputs(self):
        try:
            return [float(e.get()) for e in self.entry_widgets]
        except ValueError:
            return None

    def perform_calculation(self):
        inputs = self.get_inputs()
        if inputs is None:
            return

        topic = self.topic_var.get()
        subtopic = self.subtopic_var.get()
        data = self.calc_map[topic][subtopic]

        res = data["func"](*inputs)
        self.result_var.set(f"Result: {res} {data['result_unit']}")
        return res

    def generate_plot(self):
        # (Logic identical to previous snippet, adapted for CTK)
        # For brevity, reusing the core logic:
        topic = self.topic_var.get()
        subtopic = self.subtopic_var.get()
        vary_name = self.vary_combo.get()
        data = self.calc_map[topic][subtopic]

        try:
            idx = data["inputs"].index(vary_name)
            base = self.get_inputs()  # Might fail if empty
            if not base:
                # Fill base with 0s if empty, just to get structure
                base = [0.0] * len(data["inputs"])
                # Read valid entries
                for i, e in enumerate(self.entry_widgets):
                    if e.get():
                        base[i] = float(e.get())

            start = float(self.range_start.get())
            end = float(self.range_end.get())
        except:
            return

        x_vals = np.linspace(start, end, 50)
        y_vals = []

        for x in x_vals:
            args = base.copy()
            args[idx] = x
            res = data["func"](*args)
            y_vals.append(res if not isinstance(res, str) else None)

        # Plotting
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Create figure with dark background to match theme
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        # fig.patch.set_facecolor('#2b2b2b') # Dark background
        # ax.set_facecolor('#2b2b2b')
        # ax.tick_params(colors='white')
        # ax.xaxis.label.set_color('white')
        # ax.yaxis.label.set_color('white')
        # ax.title.set_color('white')

        ax.plot(x_vals, y_vals, color="#3B8ED0", linewidth=2)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.set_title(f"Sensitivity: {vary_name}")

        self.current_fig = fig  # Save for export

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def save_excel(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")]
        )
        if not path:
            return

        # Gather data
        topic = self.topic_var.get()
        subtopic = self.subtopic_var.get()
        data_def = self.calc_map[topic][subtopic]

        inputs_vals = self.get_inputs()
        inputs_dict = dict(zip(data_def["inputs"], inputs_vals))
        result_str = (
            self.result_var.get().split(": ")[1].split(" ")[0]
        )  # extracting number

        reporting.export_excel(
            path, topic, subtopic, inputs_dict, result_str, data_def["units"]
        )
        messagebox.showinfo("Success", "Excel report saved!")

    def save_pdf(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")]
        )
        if not path:
            return

        topic = self.topic_var.get()
        subtopic = self.subtopic_var.get()
        data_def = self.calc_map[topic][subtopic]

        inputs_vals = self.get_inputs()
        inputs_dict = dict(zip(data_def["inputs"], inputs_vals))
        result_str = self.result_var.get().split(": ")[1].split(" ")[0]

        reporting.export_pdf(
            path,
            topic,
            subtopic,
            inputs_dict,
            result_str,
            data_def["result_unit"],
            self.current_fig,
        )
        messagebox.showinfo("Success", "PDF report saved!")


if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
