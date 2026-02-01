import os
import feedparser
import requests
from datetime import datetime, timedelta
from supabase import create_client
from bs4 import BeautifulSoup
import yaml
import json

# Cluster tags
CLUSTER_TAGS = {
    'motorsport': ['racing', 'motorsport', 'moto', 'speedway', 'drag', 'nascar', 'f1', 'rally', 'checkered'],
    'metal': ['metal', 'hardcore', 'metalcore', 'punk', 'grunge', 'rock'],
    'western': ['western', 'outlaw', 'cowboy', 'rodeo', 'frontier', 'americana'],
    'tattoo_flash': ['skull', 'dagger', 'snake', 'barbed wire', 'tattoo', 'flash', 'rose', 'eagle'],
    'washed_black': ['washed', 'vintage wash', 'distressed', 'faded', 'acid wash', 'stone wash'],
    'oversized_graphic': ['oversized', 'back print', 'back hit', 'large graphic', 'statement graphic'],
    'grunge': ['grunge', 'street', 'urban', 'raw', 'edgy'],
    'gym': ['gym', 'training', 'workout', 'athletic', 'performance', 'activewear', 'sportswear']
}

# Quality filter signals
QUALITY_SIGNALS = ['tee', 't-shirt', 'graphic', 'print', 'typography', 'back print', 'oversized graphic']

# Initialize Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def extract_tags(text):
    """Match cluster tags from text."""
    text_lower = text.lower()
    matched = []
    
    for cluster, keywords in CLUSTER_TAGS.items():
        for keyword in keywords:
            if keyword in text_lower:
                matched.append(cluster)
                break
    
    return list(set(matched))

def passes_quality_filter(text, tags):
    """Looser filter for RSS: 1+ cluster tag is enough."""
    return len(tags) >= 1
    
    if len(tags) == 1:
        text_lower = text.lower()
        return any(signal in text_lower for signal in QUALITY_SIGNALS)
    
    return False

def extract_image(entry, feed_link):
    """Extract image from RSS entry."""
    # Try media:content
    if 'media_content' in entry and entry.media_content:
        return entry.media_content[0].get('url')
    
    # Try media:thumbnail
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        return entry.media_thumbnail[0].get('url')
    
    # Try enclosure
    if 'enclosures' in entry and entry.enclosures:
        for enc in entry.enclosures:
            if 'image' in enc.get('type', ''):
                return enc.get('href')
    
    # Fallback: parse link for og:image
    try:
        resp = requests.get(entry.link, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        og_image = soup.find('meta', property='og:image')
        if og_image:
            return og_image.get('content')
        
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image:
            return twitter_image.get('content')
    except:
        pass
    
    return None

def process_feed(feed_url, source_name):
    """Parse RSS feed and extract items."""
    print(f"Processing {source_name}...")
    
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        print(f"Error parsing feed {source_name}: {e}")
        return []
    
    items = []
    
    for entry in feed.entries[:50]:
        try:
            # Extract text for tagging
            text = f"{entry.get('title', '')} {entry.get('summary', '')}"
            tags = extract_tags(text)
            
            # Apply quality filter
            if not passes_quality_filter(text, tags):
                continue
            
            # Parse date
            pub_date = entry.get('published_parsed') or entry.get('updated_parsed')
            if pub_date:
                pub_date = datetime(*pub_date[:6]).isoformat()
            else:
                pub_date = datetime.now().isoformat()
            
            # Extract image
            image_url = extract_image(entry, feed_url)
            if not image_url:
                continue
            
            items.append({
                'url': entry.link,
                'title': entry.get('title', 'Untitled'),
                'source': source_name,
                'image_url': image_url,
                'tags': tags,
                'pub_date': pub_date,
                'summary': entry.get('summary', '')[:500],
                'cluster_score': len(tags)
            })
        
        except Exception as e:
            print(f"Error processing entry: {e}")
            continue
    
    return items

def calculate_personalized_score(item):
    """Calculate score based on user profile."""
    try:
        profile_data = supabase.table('profile').select('tag, weight').execute()
        weights = {row['tag']: row['weight'] for row in profile_data.data}
        
        pair_data = supabase.table('tag_pairs').select('tag_a, tag_b, weight').execute()
        pair_weights = {(row['tag_a'], row['tag_b']): row['weight'] for row in pair_data.data}
    except:
        weights = {}
        pair_weights = {}
    
    score = item['cluster_score']
    
    for tag in item['tags']:
        score += weights.get(tag, 1.0)
    
    tags = item['tags']
    for i, tag_a in enumerate(tags):
        for tag_b in tags[i+1:]:
            pair_key = tuple(sorted([tag_a, tag_b]))
            score += pair_weights.get(pair_key, 0.5)
    
    return score

def generate_explanation(item):
    """Generate 'Why you're seeing this' explanation."""
    try:
        profile_data = supabase.table('profile').select('tag, weight').execute()
        weights = {row['tag']: row['weight'] for row in profile_data.data}
    except:
        weights = {}
    
    matched_tags = item['tags']
    explanations = []
    
    high_weight_tags = [t for t in matched_tags if weights.get(t, 1.0) > 1.2]
    if high_weight_tags:
        explanations.append(f"You've kept {', '.join(high_weight_tags)} items recently")
    
    if len(matched_tags) >= 2:
        explanations.append(f"Matches {len(matched_tags)} clusters: {', '.join(matched_tags)}")
    
    if not explanations:
        explanations.append(f"Matches: {', '.join(matched_tags)}")
    
    return ". ".join(explanations) + "."

def main():
    print("Starting trend bot...")
    
    with open('sources.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    all_items = []
    
    for feed in config['feeds']:
        items = process_feed(feed['url'], feed['name'])
        all_items.extend(items)
    
    print(f"Collected {len(all_items)} items after filtering")
    
    for item in all_items:
        try:
            existing = supabase.table('items').select('id').eq('url', item['url']).execute()
            
            if not existing.data:
                supabase.table('items').insert(item).execute()
        except Exception as e:
            print(f"Error inserting item: {e}")
    
    try:
        items_data = supabase.table('items').select('*').order('pub_date', desc=True).limit(200).execute()
        
        skipped = supabase.table('votes').select('item_id').eq('vote_type', 'skip').execute()
        skipped_urls = set()
        for vote in skipped.data:
            item = supabase.table('items').select('url').eq('id', vote['item_id']).execute()
            if item.data:
                skipped_urls.add(item.data[0]['url'])
        
        feed_items = []
        for item in items_data.data:
            if item['url'] in skipped_urls:
                continue
            
            score = calculate_personalized_score(item)
            explanation = generate_explanation(item)
            
            feed_items.append({
                **item,
                'personalized_score': score,
                'explanation': explanation
            })
        
        feed_items.sort(key=lambda x: x['personalized_score'], reverse=True)
        
        with open('data.json', 'w') as f:
            json.dump(feed_items[:100], f, default=str)
        
        print("Daily feed updated successfully")
    except Exception as e:
        print(f"Error generating feed: {e}")

if __name__ == '__main__':
    main()
