#!/usr/bin/env python
# -*- coding: utf-8 -*-
# add missing mapping_wordnet.json from here:
# https://github.com/ozendelait/wordnet-to-json/releases

import os, sys, argparse, json, csv, time
import requests

retry_time_sleep_s = 1.0
max_retries_wikidata = 3

#OPEN: OID "balloon" is mixture of party balloons and balloon vehicles
#TODO: check if COCO keyboard-> computer_keyboard or musical_keyboard

#fixed renaming of matching concepts with different writing
fix_unified_labels = {'flying_disc':'frisbee', 'doughnut':'donut', 'keyboard': 'computer_keyboard',
                 'cell_phone':'mobile_phone', 'microwave_oven':'microwave',
                 'playing_field':'ball_field', 'skis':'ski', 'loveseat':'couch',
                 'maracas':'maraca', 'houseplant':'potted_plant', 'remote_control':'remote',
                 'hair_drier':'hair_dryer', 'earrings':'earring', 'band-aid': 'adhesive_bandage', 'ring-binder':'ring_binder',
                 'chopsticks':'chopstick', 'headphones':'headphone', 'vehicle_registration_plate':'license_plate', 'cosmetics':'cosmetic',
                 'crash_helmet' : 'bicycle_helmet', 'shoes':'shoe', 'picture':'picture_frame', 'speaker':'loudspeaker',
                 'monitor' : 'computer_monitor', 'gun' : 'handgun', 'luggage':'luggage_and_bags', 'table_tennis':'table_tennis_racket',
                 'pepper' : 'chilli', 'barbell':'dumbbell', "noodle":"pasta", 'asparagus' : 'garden_asparagus', 'drill' : 'electric_drill',
                 'seal': 'harbor_seal', 'sign' : 'billboard', 'shower' : 'showerhead', 'folder': 'binder', 'tape' : 'adhesive_tape',
                 'tablet' : 'tablet_computer', 'football' : 'american_football', 'baseball': 'baseball_ball', 'formula_1_':'formula_one_car',
                 'carraige' : 'horse_carraige'
                }

#faulty qid (corresp./data must be fixed on wikidata itself): "balance_beam"
# these manual corrections are necessary to resolve conflicts with identical words of different meaning
# tuple of context and wordnet_pwn30 per joined label key; context is used to find correct entry on wikidata
oid_context_fixed = {"gondola": ("boat","n03447447"), "cucumber":("fruit","n07718472"), "dog":("animal","n02084071"),
                     "sink":("basin","n04553703"), "hat":("head", "n03497657"), "sombrero":("hat", "n04259630"),
                     "dumbbell":("weight", "n03255030"), "diaper":("garment ", "n03188531"), "ruler":("stick", "n04118776"),
                     "jellyfish":("aquatic","n01910747"), "broccoli":("vegetable","n07714990"), "hot_dog":("bun", "n07697537"),
                     "microwave":("appliance","n03761084"), "toaster":("appliance","n04442312"), "bow_and_arrow":("weapon","n02879718"),
                     "drum":("instrument","n03249569"), "door":("entrance","n03221720"), "harp":("instrument", "n03495258"),
                     "racket":("equipment","n04039381"), "bowl":("tableware","n13893694"), "missile":("propelled","n03773504"),
                     "party_balloon":("inflatable","n02782329"), "balloon":("aerostat", "n02782093"), "banana":("fruit","n07753592"),
                     "car":("auto","n02958343"), "orange":("fruit","n07747607"), "train":("rail","n04468005"),
                     "mirror":("surface","n03773035"), "sports_equipment": ("object","n04285146"), "envelope": ("letter","n03291819"),
                     "submarine": ("submersible","n04347754"), "sock": ("foot", "n04254777"), "hand": ("extremity", "n05564590"),
                     "ball" :("round","n02778669"), "printer": ("computer","n04004767"), "wardrobe":("furniture","n04550184"),
                     "perfume":("mixture","n03916031"), "remote": ("device","n04074963"), "alpaca" :("camelid","n02438272"),
                     "apple":("fruit","n07739125"), "arm":("human","n05563770"), "banner":("cloth","n02788021"),
                     "bat":("animal", "n02139199"), "bathroom_cabinet":("toiletries","n03742115"), "bear":("mammal","n02131653"),
                     "beard":("human", "n05261566"), "pitcher":("spout", "n03950228"), "belt":("waist","n02827606"),  #"window_blind":("covering","n02851099"),
                     "boot":("footwear","n02872752"), "beetle":("insect","n02164464"), "bird":("animal", "n01503061"),
                     "bull":("cattle","n02403325")
                     }

def unify_namings(name0):
    unif_name = name0.replace(' ','_').lower()
    return fix_unified_labels.get(unif_name,unif_name)

def get_wordnet_gloss(pwn30, retries = 0):
    res0 = None
    try:
        res0_r = requests.get(
        "http://wordnet-rdf.princeton.edu/json/pwn30/%s"%(pwn30[1:]+'-'+pwn30[0]), params={"format": "json"})
        if res0_r.status_code == 200:
            res0 = res0_r.json()
    except:
        print("Unexpected error:", sys.exc_info()[0], res0_r)
        res0 = None
    if res0 == None or len(res0) < 1 or 'n'+res0[0]['old_keys']['pwn30'][0][:-2] != pwn30:
        if retries <= 0:
            print("Warning: bad request:", pwn30, res0_r)
            return {}
        else:
            time.sleep(retry_time_sleep_s)#wait 1s to reduce number of 429 errors
            return get_wordnet_gloss(pwn30, retries - 1)
    return {'wordnet_pwn30': pwn30, 'wordnet_gloss': res0[0]['definition']}

def get_wordnet(str0, context = None, retries = 0):
    res0 = None
    if not context is None and len(context) == 1 and len(context[0]) == 0:
        context = None
    try:
        res0_r = requests.get(
        "http://wordnet-rdf.princeton.edu/json/lemma/%s"%str0.replace('_','%20'), params={"format": "json"})
        if res0_r.status_code == 200:
            res0 = res0_r.json()
    except:
        print("Unexpected error:", sys.exc_info()[0], res0_r)
        res0 = None
    if res0 == None:
        if retries <= 0:
            print("Warning: bad request:", res0_r)
            return {}
        else:
            time.sleep(retry_time_sleep_s)#wait 1s to reduce number of 429 errors
            return get_wordnet(str0, context, retries - 1)

    if res0 == [] and retries > 0 and str0[0].lower() == str0[0]: #search is case sensitve
        return get_wordnet(str0[0].upper()+str0[1:], context, 0)

    best_r = None
    for r in res0[:min(16, len(res0))]:
        if not 'old_keys' in r or not 'pwn30' in r['old_keys']:
            continue
        pwn30 = r['old_keys']['pwn30'][0]
        if pwn30[-2:] != '-n':
            continue
        curr_pwn = int(pwn30[:-2])
        if not context is None:
            if len(context) > 1 or r['subject'] != "noun."+context[0].replace('human','body'):
                # check if context words are in the gloss.
                pos_context = min([r['definition'].find(c) for c in context])
                if pos_context < 0:
                    continue
        if best_r is None:
            best_r = r
        if context is None:
            if r['subject'] == 'noun.artifact' and best_r['subject'] != 'noun.artifact':
                best_r = r #usually man-made objects are the best represenation for COCo/OID representations
            if best_r['subject'] == 'noun.artifact' and r['subject'] != 'noun.artifact':
                continue
        min_pwn = int(best_r['old_keys']['pwn30'][0][:-2])
        if curr_pwn < min_pwn:  # smaller q usually stands for a more general entry (vs. an instance)
            best_r = r
            continue

    if not best_r is None:
        ret_b = {'wordnet_pwn30': 'n'+best_r['old_keys']['pwn30'][0][:-2], 'wordnet_gloss': best_r['definition']}
        return ret_b
    return {}

def get_wikidata(str0, context = None, retries = 0):
    res0, res0_r = None, None
    try:
        res0_r = requests.get(
        "https://query.wikidata.org/sparql", params={"query": str0, "format": "json"})
        if res0_r.status_code == 200:
            res0 = res0_r.json()
    except:
        print("Unexpected error:", sys.exc_info()[0], res0_r)
        res0 = None
    if res0 == None:
        if retries <= 0:
            print("Warning: bad request:", res0_r)
            return {}
        else:
            time.sleep(retry_time_sleep_s)#wait 1s to reduce number of 429 errors
            return get_wikidata(str0, context, retries - 1)
    bindings = res0['results'].get('bindings',[])
    if len(bindings) < 1:
        return {}
    best_b = None
    for b in bindings[:min(16, len(bindings))]:
        qid = b['item']['value'].split('/')[-1]
        if not 'itemDescription' in b or len(qid) > 16:
            continue
        prev_has_wn3 = False
        if not context is None:
            #check if context words are in the first sentence
            pos_context = min([b['itemDescription']['value'].find(c) for c in context])
            if pos_context < 0:
                continue
            pos_fullstop = b['itemDescription']['value'].find('.')
            if pos_fullstop > 0 and pos_context > pos_fullstop:
                continue
        curr_q = int(b['item']['value'].split('/')[-1][1:])
        if best_b is None:
            best_b = b
        else:
            prev_has_wn3 = 'WN3' in best_b
        min_q = int(best_b['item']['value'].split('/')[-1][1:])
        if curr_q < min_q: #smaller q usually stands for a more general entry (vs. an instance)
            best_b = b
            break
        has_wn3 = 'WN3' in b
        has_frn = 'FREEN' in b
        if has_wn3 and has_frn:
            best_b = b
            break
        elif has_wn3 or not prev_has_wn3 and has_frn:
            best_b = b

    if not best_b is None:
        ret_b = {'wikidata_qid': best_b['item']['value'].split('/')[-1], 'wikidata_name': best_b['itemLabel']['value'], 'wikidata_desc': best_b['itemDescription']['value']}
        if 'WN3' in best_b and best_b['WN3']['value'].find('wordnet-rdf.princeton.edu/wn30/') >= 0:
            wn3_conv = best_b['WN3']['value'].split('/')[-1]
            ret_b['wordnet_pwn30'] = wn3_conv[-1]+wn3_conv[:-2]
        if 'FREEN' in best_b:
            ret_b['freebase_mid'] = best_b['FREEN']['value']
        return ret_b
    return {}

def wikidata_from_freebaseid(freebaseid):
    sparql_query = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 WHERE{  
      ?item ?P646 "%s"
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    return get_wikidata(sparql_query%freebaseid,retries=max_retries_wikidata)

def wikidata_from_wordnet3p0(wordnetid):
    conv_wn = wordnetid[1:]+'-'+ wordnetid[0]
    sparql_query = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 WHERE{  
      ?item ?P646  <http://wordnet-rdf.princeton.edu/wn30/%s>
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    return get_wikidata(sparql_query%conv_wn,retries=max_retries_wikidata)

def wikidata_from_name(name, context = None):
    sparql_query0 = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 WHERE{  
      ?item ?label "%s"@en.  
      ?article schema:about ?item .
      ?article schema:inLanguage "en" .
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      OPTIONAL { ?item  wdt:P646  ?FREEN }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    sparql_query1 = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 WHERE{  
      ?item ?label "%s"
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      OPTIONAL { ?item  wdt:P646  ?FREEN }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    label_check = name.replace('_', ' ')
    d0 = get_wikidata(sparql_query0 % label_check, context=context, retries=max_retries_wikidata)
    if len(d0) == 0:
        d0 = get_wikidata(sparql_query1 % label_check, context=context, retries=max_retries_wikidata)
    return d0

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--freebase_src', type=str, default="./label_definitions/oid-class-descriptions-boxable.csv",
                    help='Path to json file containing source freebase labels')
    parser.add_argument('--append_json', type=str, default="./label_definitions/objects365_wordnet_mapping.json",
                        help='Path to json file containing additional mappings') #./label_definitions/panoptic_coco_categories.json
    parser.add_argument('--input', type=str, default="joint_mapping.json",
                        help="Input json file path, set to empty string to generate anew")
    parser.add_argument('--output', type=str, default="joint_mapping_tmp.json",
                        help="Output json file path")
    args = parser.parse_args(argv)

    inv_fix_unified_labels = {v: k for k, v in fix_unified_labels.items()}

    assign_pwns = {}
    if os.path.exists(args.input):
        with open(args.input, 'r') as ifile:
            joined_label_space = json.load(ifile)
        assign_pwns = {vals['wordnet_pwn30']:key for key, vals in joined_label_space.items() if 'wordnet_pwn30' in vals}

    if os.path.exists(args.append_json):
        with open(args.append_json, 'r') as ifile:
            appendj = json.load(ifile)
        if isinstance(appendj, dict) and "Person" in appendj:
            #obj365 file
            for key, vals in appendj.items():
                fitting_key = unify_namings(key)
                if vals["wordnet_pwn30"] in assign_pwns:
                    fitting_key = assign_pwns[vals["wordnet_pwn30"]]
                elif not fitting_key in joined_label_space and unify_namings(vals["wordnet_name"]) in joined_label_space:
                    fitting_key = unify_namings(vals["wordnet_name"])
                if not fitting_key in joined_label_space:
                    print("Adding: "+fitting_key+ " for "+ key + "("+vals["wordnet_gloss"]+")")
                else:
                    trg_entry = joined_label_space[fitting_key]
                    if 'obj365_cat' in trg_entry:
                        print("Dublicate obj365 cat: "+trg_entry['obj365_cat']+ " vs "+ key )
                    elif "wordnet_pwn30" in trg_entry and trg_entry["wordnet_pwn30"] != vals["wordnet_pwn30"]:
                        print("Conflicting wordnet entries for "+fitting_key+": " + trg_entry['wordnet_pwn30'] + ' ' + trg_entry['wordnet_gloss']+ " vs " + vals["wordnet_pwn30"] + ' ' + vals['wordnet_gloss'])
        elif isinstance(appendj, list) and isinstance(appendj[0], dict) and "supercategory" in appendj[0]:
            with open(args.limit_labels, 'r') as ifile:
                limit_labels_raw = json.load(ifile)
            coco_pano = {
                unify_namings(entry['name']): {'coco_pano_id': entry['id'], 'coco_pano_name': entry['name']} for entry
                in limit_labels_raw}
            joined_label_space.update(coco_pano)
            #coco panoptic file
    sys.exit(0)
    with open(args.freebase_src, newline='') as ifile:
        freebase_labels_raw = list(csv.reader(ifile))

    all_qids = {}
    for (fid, name) in freebase_labels_raw:
        key = unify_namings(name)
        if not key in joined_label_space:
            key = key.replace('-stuff','').replace('-merged','').replace('-other','')
        add_entry = {'oid_name': name, 'freebase_mid': fid}
        context = key.split('(')
        if len(context) > 1 and context[1][-1] == ')':
            key = context[0].replace('_', '')
            add_entry['context'] = context[1][:-1]
        elif key.find('human_') == 0:
            key = key.split('_')[-1]
            add_entry['context'] = 'human'
        if key in joined_label_space and 'wikidata_qid' in joined_label_space[key]:
            continue
        if key in oid_context_fixed:
            add_entry['context'] = oid_context_fixed[key][0]
            add_entry.update(get_wordnet_gloss(oid_context_fixed[key][1], retries=0))

        f_wd = wikidata_from_freebaseid(fid)
        if 'wordnet_pwn30' in add_entry and 'wordnet_pwn30' in f_wd and f_wd['wordnet_pwn30'] != add_entry['wordnet_pwn30']:
            print('Wordnet clash for '+ key +': ' + f_wd['wordnet_pwn30'] + ' vs ' + add_entry['wordnet_pwn30'])
            continue
        add_entry.update(f_wd)
        if 'wikidata_qid' in add_entry:
            qid = add_entry['wikidata_qid']
            if qid in all_qids:
                print("Warning: dublicate qid: ", all_qids[qid], key)
            all_qids[qid] = key
        if key in joined_label_space:
            joined_label_space[key].update(add_entry)
        else:
            joined_label_space[key] = add_entry
    
    for key, vals in joined_label_space.items():
        if 'wikidata_qid' in vals:
            continue
        n_qid = wikidata_from_name(key, context=vals.get('context','').split('_'))
        if len(n_qid) == 0:
            continue
        qid = n_qid['wikidata_qid']
        if qid in all_qids:
            vals.update(joined_label_space[all_qids[qid]])
            joined_label_space[all_qids[qid]].update(vals)
            print("Warning: dublicate qid: ", all_qids[qid], key)
        else:
            vals.update(n_qid)

    #no wordnet: stop_sign sports_ball potted_plant floor-wood playingfield wall-brick wall-stone wall-tile wall-wood window-blind
    for key, vals in joined_label_space.items():
        if 'wordnet_pwn30' in vals:
            if not 'wordnet_gloss' in vals:
                vals.update(get_wordnet_gloss(vals['wordnet_pwn30'], retries=0))
            r_wn = vals
        else:
            key0 = key.replace('-stuff','').replace('-merged','').replace('-other','')
            key0 = fix_unified_labels.get(key0, key0)
            if key0 in joined_label_space and 'wordnet_pwn30' in joined_label_space[key0]:
                continue
            r_wn = get_wordnet(key0, context=vals.get('context','').split('_'), retries=max_retries_wikidata)
            if len(r_wn) == 0:
                if key0 in inv_fix_unified_labels:
                    key0 = inv_fix_unified_labels[key0]
                else:
                    key0 = key0.replace('_','')
                key0 = fix_unified_labels.get(key0, key0)
                if key0 in joined_label_space and 'wordnet_pwn30' in joined_label_space[key0]:
                    continue
                r_wn = get_wordnet(key0, context=vals.get('context', '').split('_'), retries=max_retries_wikidata)

        if not 'wordnet_pwn30' in r_wn:
            print('Not found in wordnet: '+key)
            continue
        if 'wordnet_pwn30' in vals and vals['wordnet_pwn30'] != r_wn['wordnet_pwn30']:
            print('Wordnet clash for '+ key +': ' + vals['wordnet_pwn30'] + ' vs ' + r_wn['wordnet_pwn30'])
            continue
        vals.update(r_wn)

        if not 'freebase_mid' in vals or not 'wikidata_qid' in vals:
            w1 = wikidata_from_wordnet3p0(vals['wordnet_pwn30'])
            if 'wikidata_qid' in w1:
                qid = w1['wikidata_qid']
                if qid in all_qids:
                    print("Warning: dublicate qid: ", all_qids[qid], key)
                all_qids[qid] = key
            if 'freebase_mid' in w1 and 'freebase_mid' in vals and vals['freebase_mid'] != w1['freebase_mid']:
                print('Freebase clash for ' + key + ': ' + w1['freebase_mid']  + ' vs ' + vals['freebase_mid'])
                continue
            vals.update(w1)

    cnt_both = 0
    cnt_qid = 0
    for key, vals in joined_label_space.items():
        if 'freebase_mid' in vals and 'wordnet_pwn30' in vals:
            cnt_both += 1
        if 'wikidata_qid' in vals:
            cnt_qid += 1
    
    print("Found mappings for %i entries and %i have qids of %i" % (cnt_both , cnt_qid,len(joined_label_space)))
    
    with open(args.output, 'w') as ofile:
        json.dump(joined_label_space, ofile, sort_keys=True, indent=4)
        
    return 0
    
if __name__ == "__main__":
    print("Automatically generate mapping between freebase, imagenet (=wordnet 3.0) ids and optionally wikidata qids")
    sys.exit(main())