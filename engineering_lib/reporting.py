import pandas as pd
from fpdf import FPDF
import os


def export_excel(filename, topic, subtopic, inputs, result, units):
    """Saves the calculation data to an Excel file."""
    # Create a dictionary for the data
    data = {
        "Parameter": list(inputs.keys()) + ["RESULT"],
        "Value": list(inputs.values()) + [result],
        "Unit": units + [""],
    }

    df = pd.DataFrame(data)

    # Use 'xlsxwriter' or 'openpyxl' engine
    try:
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Calculation Report", index=False)
        return True
    except Exception as e:
        print(f"Excel Export Error: {e}")
        return False


def export_pdf(filename, topic, subtopic, inputs, result, result_unit, plot_fig=None):
    """Saves a professional PDF report, including the plot if available."""
    pdf = FPDF()
    pdf.add_page()

    # 1. Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Process Engineering Report", ln=True, align="C")
    pdf.ln(10)

    # 2. Project Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Topic: {topic}", ln=True)
    pdf.cell(0, 10, f"Calculation: {subtopic}", ln=True)
    pdf.ln(5)

    # 3. Inputs Table
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 10, "Parameter", border=1)
    pdf.cell(50, 10, "Value", border=1)
    pdf.cell(40, 10, "Unit", border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    # We assume 'inputs' is a dict of Label -> Value
    # We need to map units correctly. For simplicity in this demo,
    # we assume the inputs dict and units list are aligned,
    # but in production, you might pass a list of dicts.

    # Quick fix for aligning units:
    unit_list = list(
        inputs.keys()
    )  # Just using keys as placeholders if units aren't passed strictly

    i = 0
    # You might want to pass units explicitly to this function in a real app
    # For now, we print inputs:
    for label, value in inputs.items():
        pdf.cell(90, 10, str(label), border=1)
        pdf.cell(50, 10, str(value), border=1)
        pdf.cell(40, 10, "-", border=1)  # Placeholder for unit
        pdf.ln()

    # 4. Result
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 0, 255)  # Blue
    pdf.cell(0, 10, f"Final Result: {result} {result_unit}", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset to black

    # 5. Graph (if exists)
    if plot_fig:
        # Save plot to a temp image
        temp_img = "temp_plot.png"
        plot_fig.savefig(temp_img, dpi=100)
        pdf.ln(10)
        pdf.image(temp_img, x=10, w=170)
        os.remove(temp_img)  # Clean up

    try:
        pdf.output(filename)
        return True
    except Exception as e:
        print(f"PDF Export Error: {e}")
        return False
