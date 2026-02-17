import knime.scripting.io as knio
import pandas as pd
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
import re

pipeline_options = {
    InputFormat.PDF: PdfFormatOption(backend=PyPdfiumDocumentBackend)
    }

converter = DocumentConverter(format_options=pipeline_options)

def to_titlecase(text):

    def replace_match(match):
        word = match.group(0)
        return word.title() if len(word) >= 4 else word
    return re.sub(r'\b[A-ZÜÖÄß]{3,}\b', replace_match, text)

def play_docling(path):
    try:
        result = converter.convert(path)
        markdown = result.document.export_to_markdown()

        clean_markdown = to_titlecase(markdown)

        del result
        return clean_markdown
    except Exception as e:
        return f"ERROR: {str(e)}"

input_table = knio.input_tables[0].to_pandas()
input_table['Markdown'] = input_table['Filepath'].apply(play_docling)



knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame({
    "Filepath": input_table["Filepath"],
    "Content": input_table["Content"],
    "Markdown": input_table["Markdown"]
}))

import gc
del converter
gc.collect()