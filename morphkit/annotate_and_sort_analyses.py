# morphkit/init_compare_tags.py
# SPDX-License-Identifier: CC-BY-4.0
# Copyright (c) 2025 Tony Jurg
__version__ = "0.0.1"

import copy
import morphkit
from typing import Dict, Any, List, Tuple
import textwrap

def annotate_and_sort_analyses(
    full_analysis    : Dict[str, Any],
    reference_morph  : str,
    reference_lemma  : str,
    base_key         : str = 'lem_base_bc',
    full_key         : str = 'lem_full_bc',
    morph_key        : str = 'morph',
    sim_key          : str = 'morph_similarity',
    lower_case       : bool = True,
    debug            : bool = False
) -> Dict[str, Any]:
    """Annotate and sort analyses in a morphkit-compatible structure, grouping by base lemma
    and appending homonym suffixes extracted from lem_full_bc minus lem_base_bc.


    Args:
    -----

        :full_analysis (Dict[str, Any]): A dict with an 'analyses' list of blocks (dicts).

        :reference_morph (str): The reference morph tag to compare against each block.

        :reference_lemma (str): The Betacode lemma (base form, without suffix) to prioritize.

        :base_key (str): Optional argument. Defaults to `'lem_base_bc'`. Key under which the base lemma is stored in each block.

        :full_key (str): Optional argument. Defaults to `'lem_full_bc'`. Key under which the full lemma is stored in each block.

        :morph_key (str): Optional argument. Defaults to `'morph'`. Key under which the raw morph string is stored.

        :sim_key (str): Optional argument. Defaults to `'morph_similarity'`. Key under which to store the similarity string.

        :lower_case (bool): Optional argument. Defaults to `True`. If set to `True`, convert lemmas to lowercase before comparison.  

        :debug (bool):  Optional argument. Defaults to `False`. If set to `True`, the function print some debug information.

    Returns:
    --------

        :Dict[str, Any]: A new full_analysis dictionairy with annotated and sorted analyses, and with lem_base_bc modified to include homonym suffix when applicable.

    Steps:
    ------

      1. Deep-copy the input to avoid mutating the original data.

      2. For each analysis block:

         a. Compute the homonym suffix as the portion of lem_full_bc after lem_base_bc.
         b. If non-empty, append "_(SUFFIX)" to lem_base_bc.
         c. Compute similarity percentages for each tag against reference_morph.
         d. Store sim_key as a slash-separated string of percentages.
         e. Store '_max_' + sim_key as the integer max similarity for this block.

      3. Group blocks by their finalized lem_base_bc (with suffix).

      4. Identify which group key should be first:

         - If reference_lemma matches any finalized base lemma exactly, that group is first.
         - Else if normalize(reference_lemma) matches normalize(base lemma), that group is first.

      5. Compute for each group:

         - group_max: the highest block-level max similarity within that group.

      6. Sort groups so that:

         - The chosen reference group (if any) comes first.
         - Remaining groups follow in descending order of group_max.

      7. Within each group, sort its blocks by descending block-level max similarity.

      8. Flatten groups back into a single list.

      9. Remove temporary helper keys and return the new full_analysis dict.


    """

    def normalize_lemma(bc: str, lower_case:bool) -> str:
        """
        Return a version of the Betacode lemma with all hyphens removed.
        E.g. 'kata/-a)lala/w' -> 'kataa)lala/w'. Ignores any "_(SUFFIX)" suffix.
        If 'lower_case'==True, also make the full lemma lowercase.
        If bc is None or empty, return ''.
        """
        if not bc:
            return ''
        if lower_case:
           bc.replace('*', '')
        # Remove suffix if present
        base = bc.split('_(')[0]
        return base.replace('-', '')

    # 1) Deep copy to avoid mutating caller data
    fa = copy.deepcopy(full_analysis)
    analyses = fa.get('analyses', [])

    # 2) For each block, determine homonym suffix and append to lem_base_bc
    for blk in analyses:
        base_bc = blk.get(base_key, '') or ''
        full_bc = blk.get(full_key, '') or ''
        # Extract leftover after base_bc
        if full_bc.startswith(base_bc):
            leftover = full_bc[len(base_bc):]
        else:
            leftover = ''
        leftover = leftover.strip()
        if leftover:
            # Append “_(leftover)” unless already present
            suffix = f"_({leftover})"
            if not base_bc.endswith(suffix):
                blk[base_key] = f"{base_bc}{suffix}"

    # 3) Annotate each block with similarity string and block-level max
    for blk in analyses:
        raw_morph_str = blk.get(morph_key, '') or ''
        tags = [t for t in raw_morph_str.split('/') if t]
        percents: List[int] = []

        for tag in tags:
            if tag == reference_morph:
                percent = 100
            else:
                sim = morphkit.compare_tags(tag, reference_morph)
                overall = sim.get('overall_similarity', 0.0)
                percent = int(round(overall * 100))
            percents.append(percent)

        blk[sim_key] = '/'.join(str(p) for p in percents) if percents else '0'
        blk['_max_' + sim_key] = max(percents) if percents else 0

    # 4) Group blocks by their (possibly suffixed) lem_base_bc
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for blk in analyses:
        lemma_base = blk.get(base_key, '') or ''
        groups.setdefault(lemma_base, []).append(blk)

    # 5) Identify which group key to place first
    norm_ref_base = normalize_lemma(reference_lemma, lower_case)
    ref_group_key: str = None

    # 5a) First try exact match on possibly suffixed base lemma
    if reference_lemma in groups:
        ref_group_key = reference_lemma
    else:
        # 5b) If not found, look for normalized match among group keys
        for group_key in groups:
            if normalize_lemma(group_key, lower_case) == norm_ref_base:
                ref_group_key = group_key
                break

    # 6) Compute group_max for each group
    group_max_list: List[Tuple[str, int]] = []
    for gkey, blks in groups.items():
        max_in_group = max(blk.get('_max_' + sim_key, 0) for blk in blks)
        group_max_list.append((gkey, max_in_group))

    # 7) Sort groups so that:
    #    - ref_group_key first (if it exists)
    #    - then remaining groups by descending group_max
    sorted_group_keys: List[str] = []
    if ref_group_key is not None:
        sorted_group_keys.append(ref_group_key)

    other_groups = [(g, gm) for (g, gm) in group_max_list if g != ref_group_key]
    other_groups.sort(key=lambda x: x[1], reverse=True)
    sorted_group_keys.extend([g for (g, gm) in other_groups])

    # 8) Within each group, sort blocks by descending block-level max similarity
    final_sorted_blocks: List[Dict[str, Any]] = []
    for gkey in sorted_group_keys:
        blks = groups[gkey]
        blks.sort(key=lambda blk: blk.get('_max_' + sim_key, 0), reverse=True)
        final_sorted_blocks.extend(blks)

    # 9) Replace fa['analyses'] with the flattened, sorted list
    fa['analyses'] = final_sorted_blocks

    # 10) Remove temporary helper keys before returning
    for blk in fa['analyses']:
        blk.pop('_max_' + sim_key, None)

    return fa
