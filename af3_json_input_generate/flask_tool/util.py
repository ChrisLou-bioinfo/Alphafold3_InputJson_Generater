import json

# ================= 1. Configuration =================

# 3-letter -> 1-letter AA map (includes common PTMs)
AA_MAP = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
    'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
    'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
    'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
    # Common PTMs
    'SEP': 'S', 'TPO': 'T', 'PTR': 'Y', 'ALY': 'K', 'MLY': 'K',
    'MLZ': 'K', 'M3L': 'K', 'HYP': 'P', 'AGM': 'R', '2MR': 'R',
    'MSE': 'M', 'CSX': 'C', 'CAS': 'C', 'CME': 'C'
}

# ================= 2. Core Functions =================

def get_all_chain_ids(cif_content):
    """
    Scans the CIF content to find all unique auth_asym_id values.
    Returns a set of chain IDs.
    """
    lines = cif_content.splitlines()
    chain_ids = set()
    
    in_atom_site = False
    auth_asym_id_idx = -1
    headers = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("_atom_site."):
            in_atom_site = True
            headers.append(stripped)
            continue
            
        if in_atom_site:
            if not stripped.startswith("_atom_site.") and (stripped.startswith("ATOM") or stripped.startswith("HETATM")):
                if auth_asym_id_idx == -1:
                    try:
                        if "_atom_site.auth_asym_id" in headers:
                            auth_asym_id_idx = headers.index("_atom_site.auth_asym_id")
                        elif "_atom_site.label_asym_id" in headers:
                            auth_asym_id_idx = headers.index("_atom_site.label_asym_id")
                    except:
                        pass
                
                parts = line.split()
                if auth_asym_id_idx != -1 and len(parts) > auth_asym_id_idx:
                    chain_ids.add(parts[auth_asym_id_idx])
            elif not stripped.startswith("_") and not stripped.startswith("loop_") and stripped:
                # End of loop likely
                in_atom_site = False
                
    return chain_ids

def parse_cif_chain(cif_content, target_chain_id):
    """
    Extracts specific chain from CIF content.
    Returns:
    1. Filtered CIF text (only atoms for that chain)
    2. Sequence string (for alignment)
    """
    lines = cif_content.splitlines()
    new_lines = []
    sequence_list = []
    
    in_atom_site = False
    auth_asym_id_idx = -1
    label_comp_id_idx = -1
    auth_seq_id_idx = -1
    headers = []
    
    seen_residues = set() 
    
    for line in lines:
        stripped = line.strip()
        
        # 1. Handle Header
        if stripped.startswith("loop_") or stripped.startswith("data_") or stripped.startswith("_entry"):
            new_lines.append(line)
            continue
            
        if stripped.startswith("_atom_site."):
            in_atom_site = True
            headers.append(stripped)
            new_lines.append(line)
            continue
            
        if stripped.startswith("_entity_poly.pdbx_strand_id"):
            # Sanitize this header to claim only the single chain
            # The original formatting might be roughly fixed width, but simple space separation is standard CIF
            new_lines.append(f"_entity_poly.pdbx_strand_id {target_chain_id}")
            continue

        # 2. Handle ATOM Data
        if in_atom_site:
            if not stripped.startswith("_atom_site."):
                # Parse indices
                if auth_asym_id_idx == -1:
                    try:
                        if "_atom_site.auth_asym_id" in headers:
                            auth_asym_id_idx = headers.index("_atom_site.auth_asym_id")
                            label_comp_id_idx = headers.index("_atom_site.label_comp_id")
                            auth_seq_id_idx = headers.index("_atom_site.auth_seq_id")
                        elif "_atom_site.label_asym_id" in headers:
                            auth_asym_id_idx = headers.index("_atom_site.label_asym_id")
                            label_comp_id_idx = headers.index("_atom_site.label_comp_id")
                            auth_seq_id_idx = headers.index("_atom_site.label_seq_id")
                    except ValueError:
                        pass 

                if line.startswith("ATOM") or line.startswith("HETATM"):
                    parts = line.split()
                    if auth_asym_id_idx != -1 and len(parts) > auth_asym_id_idx:
                        current_chain = parts[auth_asym_id_idx]
                        
                        if current_chain == target_chain_id:
                            new_lines.append(line)
                            
                            if label_comp_id_idx != -1 and auth_seq_id_idx != -1:
                                res_name = parts[label_comp_id_idx]
                                seq_id = parts[auth_seq_id_idx]
                                
                                if seq_id not in seen_residues:
                                    seen_residues.add(seq_id)
                                    one_letter = AA_MAP.get(res_name, 'X')
                                    sequence_list.append(one_letter)
                else:
                    new_lines.append(line)
        else:
            new_lines.append(line)
            
    extracted_cif = "\n".join(new_lines)
    extracted_seq = "".join(sequence_list)
    
    return extracted_cif, extracted_seq

def inject_templates(input_json_data, cif_content):
    """
    Injects templates into the JSON data object using the provided CIF content string.
    Modifies input_json_data in place and returns logs.
    """
    logs = []
    sequences = input_json_data.get("sequences", [])
    modified_count = 0
    
    # 1. Pre-load all available chains from CIF
    available_chain_ids = get_all_chain_ids(cif_content)
    logs.append(f"Found chains in MMCIF: {sorted(list(available_chain_ids))}")
    
    # Parse and cache them strictly? No, just parse on demand or cache small text.
    # Given limited scale, we can parse them into a dict to avoid re-parsing same chain multiple times.
    chain_cache = {}
    for cid in available_chain_ids:
        cif_text, cif_seq = parse_cif_chain(cif_content, cid)
        chain_cache[cid] = {'text': cif_text, 'seq': cif_seq}
    
    for seq_obj in sequences:
        if "protein" in seq_obj:
            p = seq_obj["protein"]
            # Handle potential list ID (homomers)
            chain_ids = p["id"] if isinstance(p["id"], list) else [p["id"]]
            primary_chain_id = chain_ids[0]
            
            full_sequence = p["sequence"]
            
            logs.append(f"Processing Chain {primary_chain_id} (Length: {len(full_sequence)})...")
            
            p["unpairedMsa"] = ""
            p["pairedMsa"] = ""
            
            # --- Allocation Logic ---
            # 1. Try Exact Match (Chain ID A -> CIF Chain A)
            target_cif_data = chain_cache.get(primary_chain_id)
            match_source = "Exact ID Match"
            
            # 2. If not found, try Sequence Similarity (Substring Match)
            if not target_cif_data or not target_cif_data['seq']:
                if not target_cif_data:
                    logs.append(f"  -> Exact ID match for '{primary_chain_id}' failed. Searching by sequence similarity...")
                else:
                    logs.append(f"  -> Exact ID match found but empty sequence (ligand?). skipping.")
                    
                best_chain_id = None
                
                # Iterate all cached chains
                for cid, cdata in chain_cache.items():
                    cseq = cdata['seq']
                    if len(cseq) < 10: continue # Skip tiny fragments
                    
                    # Heuristic: Check if cseq is a substring of full_sequence (or vice versa? usually template inside query)
                    # We check: Is Template Sequence contained in Query Sequence?
                    if cseq in full_sequence:
                        best_chain_id = cid
                        match_source = f"Sequence Match (Template inside Query) with Chain {cid}"
                        break
                    
                    # Also checking partial match (start of template in query)
                    # Simple heuristic: first 20 residues
                    if len(cseq) >= 20 and cseq[:20] in full_sequence:
                        best_chain_id = cid
                        match_source = f"Partial Sequence Match (Start) with Chain {cid}"
                        break
                        
                if best_chain_id:
                    target_cif_data = chain_cache[best_chain_id]
                else:
                    logs.append("  -> No suitable template chain found via auto-mapping.")
                    continue

            # We have a target
            cif_text = target_cif_data['text']
            cif_seq = target_cif_data['seq']

            logs.append(f"  -> Selected Template: {match_source}. Template Length: {len(cif_seq)}")

            # Alignment
            start_index = full_sequence.find(cif_seq)
            
            if start_index == -1:
                # Optimized Alignment Strategy: Sliding Window Seed Search
                # Try to find a matching "seed" of 20 residues within the first 50 residues of the template
                # This handles cases where the template has an N-terminal tag (e.g. His-tag, GSR prefix)
                found_seed = False
                seed_length = 20
                search_window = 500  # Increased to handle large fusion tags (GST, MBP, etc.)
                
                for offset in range(0, min(search_window, len(cif_seq) - seed_length), 1):
                    seed_seq = cif_seq[offset:offset+seed_length]
                    seed_idx = full_sequence.find(seed_seq)
                    
                    if seed_idx != -1:
                        # Found a seed match!
                        # Now calculate the effective start index relative to the template start
                        # Input Index: seed_idx corresponds to Template Index: offset
                        # So, Template[0] would correspond to Input[seed_idx - offset]
                        # But be careful if this effective start is negative (meaning input starts inside template)
                        
                        start_index = seed_idx - offset
                        
                        # Note: start_index can be negative here if the query starts "after" the template starts (truncated query)
                        # But for this use case (inserting template into query), we usually assume template covers a region of query.
                        # If start_index is negative, it means the template starts BEFORE the query.
                        # We just clamp the injection range.
                        
                        logs.append(f"  -> Sliding window match found. Seed offset: {offset}. Effective Start: {start_index}.")
                        found_seed = True
                        break
                
                if not found_seed:
                     logs.append("  -> Error: Alignment failed (Exact, Partial-Start, and Sliding Window). Skipping.")
                     continue
            else:
                logs.append(f"  -> Exact/Partial alignment found at index {start_index}.")

            # Handle negative start_index (Template starts before Query)
            template_start_offset = 0
            if start_index < 0:
                template_start_offset = -start_index
                start_index = 0
            
            match_length = len(cif_seq) - template_start_offset
            
            # Clamp if template extends beyond query
            if start_index + match_length > len(full_sequence):
                match_length = len(full_sequence) - start_index
            
            if match_length <= 0:
                logs.append("  -> Error: Effective match length <= 0. Skipping.")
                continue

            query_indices = list(range(start_index, start_index + match_length))
            template_indices = list(range(template_start_offset, template_start_offset + match_length))
            
            logs.append(f"  -> Injection Range: Input[{start_index}-{start_index+match_length}] maps to Template[{template_start_offset}-{template_start_offset+match_length}]")

            template_obj = {
                "mmcif": cif_text,
                "queryIndices": query_indices,
                "templateIndices": template_indices
            }
            
            if "templates" not in p:
                p["templates"] = []
            
            p["templates"].append(template_obj)
            modified_count += 1

    logs.append(f"Updated {modified_count} chains with templates.")
    return logs
