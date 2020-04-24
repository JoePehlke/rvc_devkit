#!/usr/bin/env python
# -*- coding: utf-8 -*-
# remap boxable COCO annotations using a supplied mapping csv file

import os, sys, argparse, json, csv, tqdm

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, 
                        help="Input json file of annotations to remap")
    parser.add_argument('--mapping', type=str, default='./obj_det_mapping.csv',
                        help="Csv file defining mapping")
    parser.add_argument('--mapping_row', type=str, default=None,
                        help="Row header from row in csv file to use; default: second row")
    parser.add_argument('--image_root', type=str, default=None,
                        help="adds image root to each filepath")
    parser.add_argument('--image_root_rel', type=str, default=None,
                        help="adds relative path between output json dir and this directory each filepath")
    parser.add_argument('--void_id', type=int, default=0,
                        help="Void id for labels not found in mapping csv")
    parser.add_argument('--output', type=str, 
                        help="Output json file path for result.")
    parser.add_argument('--reduce_boxable', dest='reduce_size', action='store_true',
                        help="Only keep minimum of annotation data needed for boxable training.")

    parser.set_defaults(do_merging=False, reduce_size=False)
    args = parser.parse_args(argv)

    if not args.image_root_rel is None:
        pos_curly = args.image_root_rel.find('{')
        pos_slash = args.image_root_rel.rfind('/',pos_curly) if pos_curly > 0 else -1
        recover_curly = ""
        if pos_slash >= 0:
            recover_curly = args.image_root_rel[pos_slash:]
            args.image_root_rel = args.image_root_rel[:pos_slash]
        args.image_root = os.path.relpath(args.image_root_rel, os.path.dirname(args.output)).replace('\\','/') + recover_curly + '/' #use only unix-style slashes

    print("Loading source annotation file " + args.input + "...")
    with open(args.input, 'r') as ifile:
        annot = json.load(ifile)


    # load pre-defined mapping; first row is target label name, row from --mapping_row
    # defines source row for this input data; use semicolon from N->1 mappings
    # e.g.
    # animal,cat;dog
    # will map both cat and dog source labels to the target label animal
    with open(args.mapping, newline='') as ifile:
        mapping0 = list(csv.reader(ifile))
        if args.mapping_row is None:
            idx_use = 1
        else:
            idx_use = mapping0[0].index(args.mapping_row)
        trg_labels = {m[0]:m[idx_use] for m in mapping0[1:]}
        cats_sorted = list(sorted(trg_labels.keys()))
        trg_cats = {c:{'supercategory':'rvc_jls', 'id': id0+1, 'name':c} for id0, c in enumerate(cats_sorted)}
        src_cats = {c['name'].lower().strip():c  for c in annot['categories']}
        src_to_trg = {}
        for t, src_all in trg_labels.items():
            t_id = trg_cats[t]['id']
            for s in src_all.split(';'): #allows multi-to-one mappings
                if len(s)  == 0:
                    continue
                s = s.lower().strip()
                if not s in src_cats:
                    print("Warning: Unknown source cat "+s+" requested. Skipping.")
                    continue
                src_to_trg[src_cats[s]['id']]= t_id

    if 'categories' in annot:
        annot['categories'] = [trg_cats[c] for c in cats_sorted]

    if not args.image_root is None:
        if args.image_root[-1] != '/' and args.image_root[-1] != '\\':
            args.image_root += '/'
        for i in annot['images']:
            i['file_name'] = args.image_root.format(file_name=i['file_name']) + i['file_name']
    if args.reduce_size:
        reduce_size_entries = ["date_captured","coco_url","url","flickr_url"]
        for i in annot['images']:
            for e in reduce_size_entries:
                i.pop(e,None)

    if 'annotations' in annot:
        for a in tqdm.tqdm(annot['annotations'], desc='Remapping annotations '):
            a['category_id'] = src_to_trg.get(a['category_id'],args.void_id)
            if args.reduce_size:
                a.pop('segmentation',None)

    print("Saving target annotation file "+args.output+"...")
    with open(args.output, 'w', newline='\n') as ofile:
        json.dump(annot, ofile)
        
    return 0
    
if __name__ == "__main__":
    sys.exit(main())