import lancedb
import transformers
from pathlib import Path
from typing import List, Dict, Literal, Tuple
from unstructured.partition.html import partition_html



def get_chunk_start_and_end_indices(seq_len: int, chunk_len: int, overlap: float) -> List[Tuple[str, int]]:
    """
    Get start/end indices for a text/token sequence given parameters
    Parameters
    ----------
    seq_len : Length of the sequence
    chunk_len : Length of the chunks
    overlap : Proportion of overlapping/repeated elements betweed *adjacent* chunks
        NOTE: for e.g. 0.2 (20%) overlap, a given chunk will overlap 20% with the previous chunk, 
        ......and another 20% with the subsequent chunk
    """
    start = 0
    end = chunk_len
    chunks = [(start, end)]
    while end < seq_len:
        start = int(end - (chunk_len * overlap))
        end = min(seq_len, (start + chunk_len))
        chunks.append((start, end))
    return chunks

assert get_chunk_start_and_end_indices(500, 100, 0.2) == [(0, 100), (80, 180), (160, 260), (240, 340), (320, 420), (400, 500)]
assert get_chunk_start_and_end_indices(499, 100, 0.2) == [(0, 100), (80, 180), (160, 260), (240, 340), (320, 420), (400, 499)]



def get_document_chunks(file_path: Path, 
                        tokenizer:transformers.models.bert.tokenization_bert_fast.BertTokenizerFast,
                        txt_parsing_eng: Literal['unstructuredio', 'pymupdf'] = 'pymupdf',
                        txt_chunking_alg: Literal['default'] = 'default',
                        chunk_len_tok:int=500,
                        chunk_frac_overlap:float=0.2)-> List[Dict[str, str]]:
    # input validation
    if chunk_len_tok > tokenizer.model_max_length:
        raise ValueError("chunk lenght in tokens must not exceed max of the embedding model associated with the tokenizer")

    # get full text from document
    if txt_parsing_eng == 'unstructuredio':
        fulltext = " ".join([e.text for e in partition_html(file_path)])
    else:
        raise NotImplementedError("Only 'unstructuredio' text parsing engine is implemented so far")

    # Tokenize the entire text
    tokens = tokenizer.encode(fulltext, add_special_tokens=False)
    print(f"fulltext has {len(tokens):,} tokens, number of words is: {len(fulltext.split(' ')):,}")
    
    # Split text into (text) chunks, of specified (token) lengths
    if txt_chunking_alg == 'default':
        tok_chnk_indx = get_chunk_start_and_end_indices(len(tokens), chunk_len_tok, chunk_frac_overlap)
        tok_chunks = [tokens[start:end] for start, end in tok_chnk_indx]
        txt_chunks = [tokenizer.decode(chunk) for chunk in tok_chunks]
        print(f"Chunked document into {len(txt_chunks):,} chunks of {chunk_len_tok:,} tokens each, with {chunk_frac_overlap*100}% overlap")
    else:
        raise NotImplementedError("Only 'default' chunking algorithm is implemented so far")

    return txt_chunks





"""
if len(seq) is 500 and I want 100-token chunks w/ 20% overlap, I want indices:
    * 0-100
    * 90-190
    * 180-280
    * 270-370
    * 360-460
    * 450-500


"""    



"""
Pros / Cons of this approach so far:
Pro: 
 * Like that each element has a category (title/narrative-text/list-item per https://docs.unstructured.io/open-source/core-functionality/partitioning)
 * Like that it automatically also keeps metadata like file-dir, filename, filetype
Cons:
 * Need a consolidation post-processing step: first 72+ elements are just a few words each
 * Category not accurate; 
    * first 70 elements are classified as 'title'
    * No apparent reason e70 is title but e71 is narrative-text; they're just consecutive names in the 'committee staff' name list
    * Inaccurate 'title' classification means I also unfortunately couldn't use this to e.g.
        keep all narrative text, w/ prev title text as metadata
 * importing partition_pdf throws error that I don't have pdfminer installed
    * I think hm, pdfminer I don't think is as good as pymupdf, but go to pypi to 
    ...install it to give unstructured/partition_pdf a shot...last pdfminer release was 2019(!)

TODO:
* For v0.0.1 final report:
    * use unstructured/html
    * just append all element.text together, chunk up with something canned
* For future versions w/ more doc inventory where we have to turn to pdfs:
    * use pymupdf + something like semchunk?



...maybe I just append e.text altogether then pass it through different chunking approaches?

Issues with this approach so far:



"""