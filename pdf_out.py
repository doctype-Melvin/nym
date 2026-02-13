import pandas as pd
import knime.scripting.io as knio
from fpdf import FPDF
import os
import shutil

def write_pdf(content, id):
    content_str = str(content)
    clean_id = os.path.basename(id)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', size=12)

    encode_content = content_str.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, text=encode_content)
    save_path = os.path.join(output_dir, f"complyable_{clean_id}.pdf")
    pdf.output(save_path)
    return save_path

data = knio.input_tables[0].to_pandas()
output_dir = "../test_output"

if os.path.exists(output_dir):
    shutil.rmtree(output_dir) # cleanup for dev testing

os.makedirs(output_dir)

data['Output_Path'] = data.apply(lambda row: write_pdf(row['Output_final'], row['Filepath']), axis=1)

# Output the audit data to the KNIME table
knio.output_tables[0] = knio.Table.from_pandas(data)
