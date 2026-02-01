import os
from datetime import datetime, timedelta
from supabase import create_client
from collections import Counter
import json

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def analyze_patterns():
    """Generate 3 emerging patterns from last 7 days."""
    week_start = (datetime.now() - timedelta(days=7)).date()
    
    items = supabase.table('items').select('id, tags, source').gte('pub_date', week_start.isoformat()).execute()
    
    keeps = supabase.table('votes').select('item_id').eq('vote_type', 'keep').gte('voted_at', week_start.isoformat()).execute()
    kept_ids = {v['item_id'] for v in keeps.data}
    
    tags_seen = Counter()
    tags_kept = Counter()
    sources_kept = Counter()
    
    for item in items.data:
        for tag in item['tags']:
            tags_seen[tag] += 1
            
            if item['id'] in kept_ids:
                tags_kept[tag] += 1
                sources_kept[item['source']] += 1
    
    patterns = []
    for tag in tags_kept:
        if tags_seen[tag] == 0:
            continue
        
        keep_rate = tags_kept[tag] / tags_seen[tag]
        if keep_rate > 0.3 and tags_kept[tag] >= 3:
            patterns.append({
                'tag': tag,
                'keep_count': tags_kept[tag],
                'seen_count': tags_seen[tag],
                'keep_rate': keep_rate
            })
    
    patterns.sort(key=lambda x: x['keep_rate'], reverse=True)
    
    results = []
    for i, p in enumerate(patterns[:3], 1):
        tag = p['tag']
        
        co_tags = Counter()
        for item in items.data:
            if item['id'] in kept_ids and tag in item['tags']:
                for t in item['tags']:
                    if t != tag:
                        co_tags[t] += 1
        
        top_co = co_tags.most_common(2)
        
        pattern_obj = {
            'pattern_title': f"High engagement with {tag.replace('_', ' ').title()}",
            'evidence': {
                'tag': tag,
                'kept': p['keep_count'],
                'seen': p['seen_count'],
                'rate': round(p['keep_rate'] * 100, 1),
                'co_tags': [t[0] for t in top_co],
                'sources': dict(sources_kept.most_common(3))
            },
            'direction': f"Strong preference for {tag.replace('_', ' ')} combined with {', '.join([t[0].replace('_', ' ') for t in top_co[:2]])}",
            'action': generate_action(tag, [t[0] for t in top_co])
        }
        
        results.append(pattern_obj)
        
        supabase.table('weekly_patterns').insert({
            'week_start': week_start.isoformat(),
            'pattern_title': pattern_obj['pattern_title'],
            'evidence': pattern_obj['evidence'],
            'direction': pattern_obj['direction'],
            'action': pattern_obj['action']
        }).execute()
    
    return results

def generate_action(primary_tag, co_tags):
    """Generate concrete design action."""
    actions = {
        'motorsport': 'Oversized racing graphics on washed black tees with checkered flags',
        'metal': 'Distressed band-style typography with skull motifs',
        'western': 'Outlaw dagger and barbed wire back prints',
        'tattoo_flash': 'Classic flash sheet layouts: eagle, snake, skull cluster',
        'washed_black': 'Acid-washed black bases with high-contrast prints',
        'oversized_graphic': 'Statement back hits, minimal front chest logo',
        'grunge': 'Raw edge graphics, cracked screen print effect',
        'gym': 'Performance-inspired typography with athletic motifs'
    }
    
    base_action = actions.get(primary_tag, f"Focus on {primary_tag.replace('_', ' ')} aesthetic")
    
    if co_tags:
        base_action += f" combined with {co_tags[0].replace('_', ' ')} elements"
    
    return base_action

def generate_tee_concepts():
    """Generate 10 tee concepts from kept items."""
    keeps = supabase.table('votes').select('item_id').eq('vote_type', 'keep').order('voted_at', desc=True).limit(30).execute()
    kept_ids = [v['item_id'] for v in keeps.data]
    
    if not kept_ids:
        return []
    
    items = supabase.table('items').select('*').in_('id', kept_ids).execute()
    
    tag_combos = Counter()
    for item in items.data:
        if len(item['tags']) >= 2:
            combo = tuple(sorted(item['tags'][:2]))
            tag_combos[combo] += 1
    
    concepts = []
    week_start = (datetime.now() - timedelta(days=7)).date()
    
    for i, (combo, count) in enumerate(tag_combos.most_common(10), 1):
        tag_a, tag_b = combo
        
        concept = {
            'concept_name': f"{tag_a.replace('_', ' ').title()} x {tag_b.replace('_', ' ').title()} #{i}",
            'front_placement': generate_front_placement(tag_a, tag_b),
            'back_placement': generate_back_placement(tag_a, tag_b),
            'sleeve_detail': generate_sleeve(tag_a, tag_b),
            'motifs': generate_motifs(tag_a, tag_b),
            'slogans': generate_slogans(tag_a, tag_b),
            'print_style': generate_print_style(tag_a, tag_b),
            'colorways': 'Washed black primary, vintage charcoal, acid wash black, stone grey'
        }
        
        concepts.append(concept)
        
        supabase.table('tee_concepts').insert({
            'week_start': week_start.isoformat(),
            **concept
        }).execute()
    
    return concepts

def generate_front_placement(tag_a, tag_b):
    placements = [
        'Small left chest logo',
        'Center chest wordmark',
        'Minimal script placement',
        'Upper chest icon',
        'Left chest badge'
    ]
    return placements[hash(tag_a + tag_b) % len(placements)]

def generate_back_placement(tag_a, tag_b):
    backs = [
        f'Oversized {tag_a.replace("_", " ")} graphic with {tag_b.replace("_", " ")} elements',
        f'Large back hit: {tag_a.replace("_", " ")} motif over {tag_b.replace("_", " ")} typography',
        f'Full back print: {tag_a.replace("_", " ")} and {tag_b.replace("_", " ")} split composition',
        f'Statement back graphic: {tag_a.replace("_", " ")} icon, {tag_b.replace("_", " ")} frame',
        f'Vertical back spine: {tag_a.replace("_", " ")} imagery, {tag_b.replace("_", " ")} accents'
    ]
    return backs[hash(tag_a + tag_b) % len(backs)]

def generate_sleeve(tag_a, tag_b):
    sleeves = [
        'Barbed wire sleeve stripe',
        'Racing stripe detail',
        'Distressed flag patch',
        'Minimal skull icon',
        'None (oversized silhouette focus)'
    ]
    return sleeves[hash(tag_a) % len(sleeves)]

def generate_motifs(tag_a, tag_b):
    motifs_map = {
        'motorsport': 'checkered flags, racing numbers, speed lines, drag strip',
        'metal': 'skulls, chains, pentagrams, gothic lettering',
        'western': 'daggers, revolvers, barbed wire, outlaw stars',
        'tattoo_flash': 'rose and dagger, eagle and snake, skull and crossbones',
        'washed_black': 'distressed textures, vintage grain, cracked effects',
        'oversized_graphic': 'bold scale, statement imagery, dominant placement',
        'grunge': 'splatter, rough edges, hand-drawn style',
        'gym': 'athletic icons, performance numbers, training symbolism'
    }
    
    return f"{motifs_map.get(tag_a, 'bold graphics')}, {motifs_map.get(tag_b, 'strong symbolism')}"

def generate_slogans(tag_a, tag_b):
    bases = [
        ['SPEED KILLS', 'NO LIMITS', 'FULL THROTTLE', 'REDLINE'],
        ['OUTLAW CULTURE', 'RIDE OR DIE', 'FREEDOM OR DEATH', 'UNTAMED'],
        ['HEAVY DUTY', 'IRON WILL', 'RELENTLESS', 'NO SURRENDER'],
        ['LEGENDS NEVER DIE', 'BUILT TO LAST', 'FOREVER WILD', 'UNBROKEN']
    ]
    
    selected = bases[hash(tag_a + tag_b) % len(bases)]
    return selected[:4]

def generate_print_style(tag_a, tag_b):
    styles = [
        'Distressed screen print with cracked ink effect',
        'Halftone gradient with vintage grain overlay',
        'Puff print detail on washed base',
        'High-density discharge print on acid wash',
        'Cracked plastisol with intentional aging'
    ]
    return styles[hash(tag_a) % len(styles)]

def main():
    print("Generating weekly intelligence...")
    
    patterns = analyze_patterns()
    concepts = generate_tee_concepts()
    
    os.makedirs('site', exist_ok=True)
    with open('site/weekly.json', 'w') as f:
        json.dump({
            'patterns': patterns,
            'concepts': concepts,
            'generated_at': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"Generated {len(patterns)} patterns and {len(concepts)} concepts")

if __name__ == '__main__':
    main()
