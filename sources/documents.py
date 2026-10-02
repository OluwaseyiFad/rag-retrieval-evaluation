from pathlib import Path

source_folder = Path("sources")


def compile_sources():
    all_documents = []
    for txt_path in source_folder.glob("*.txt"):
        text = txt_path.read_text(encoding="utf-8")
        all_documents.append({
                "text": text,
                "source": txt_path.name
        })
    return all_documents
      

all_documents = compile_sources()