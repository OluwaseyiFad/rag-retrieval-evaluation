from pathlib import Path
from process_pdf import extract_pdf


pdf_folder = Path("sources")

all_documents = []

for pdf_path in pdf_folder.glob("*.pdf"):
    documents = extract_pdf(pdf_path)
    all_documents.extend(documents)


# Fixed-size fallback

def fixed_size_chunk_text(text, chunk_size=500, overlap=100):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks

# Recursive splitting


def recursive_split(text, chunk_size, separators, sep_idx=0):
    # Already small enough
    if len(text) <= chunk_size:
        return [text]

    # No more separators available
    if sep_idx >= len(separators):
        return fixed_size_chunk_text(
            text,
            chunk_size,
            overlap=0
        )

    separator = separators[sep_idx]
    parts = text.split(separator)
    pieces = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= chunk_size:
            pieces.append(part)
        else:
            # recursively try the next separator
            smaller_parts = recursive_split(
                part,
                chunk_size,
                separators,
                sep_idx + 1
            )
            pieces.extend(smaller_parts)

    return pieces


# Merge pieces into chunks with overlap

def merge_with_overlap(pieces, chunk_size=500, overlap=100):
    chunks = []
    current_pieces = []
    current_length = 0

    for piece in pieces:
        extra_length = len(piece)
        if current_pieces:
            extra_length += 1

        # Can this piece fit in the current chunk?
        if current_length + extra_length <= chunk_size:
            current_pieces.append(piece)
            current_length += extra_length
        else:
            # Save the completed chunk
            if current_pieces:
                chunks.append(" ".join(current_pieces))
    
            # Build overlap using WHOLE previous pieces

            overlap_pieces = []
            overlap_length = 0

            for old_piece in reversed(current_pieces):

                extra = len(old_piece)
                if overlap_pieces:
                    extra += 1
                if overlap_length + extra > overlap:
                    break
                overlap_pieces.insert(0, old_piece)
                overlap_length += extra

            # Start the new chunk with overlap
            current_pieces = overlap_pieces.copy()
            current_length = len(" ".join(current_pieces))

            # Add the new piece
            if current_pieces:
                candidate_length = (current_length + 1 + len(piece))
            else:
                candidate_length = len(piece)

            # Normally this should fit because recursive_split
            # already guarantees pieces <= chunk_size
            if candidate_length <= chunk_size:
                current_pieces.append(piece)
                current_length = candidate_length
            else:
                # If overlap + piece is too large,
                # drop overlap and start fresh
                current_pieces = [piece]
                current_length = len(piece)

    # Add final chunk
    if current_pieces:
        chunks.append(" ".join(current_pieces))

    return chunks



# Main recursive chunking function

def recursive_chunk_text(text, chunk_size=500, overlap=100):
    separators = ["\n\n", "\n", ". ", " "]
    pieces = recursive_split(text, chunk_size, separators)
    chunks = merge_with_overlap(pieces, chunk_size, overlap)

    return chunks
