// IMPORTANT: Replace these with your actual Supabase credentials
const SUPABASE_URL = 'https://uyhdaziqmmfhestfyyhn.supabase.co';
const SUPABASE_KEY = 'sb_publishable_PpLi4l7kaybHrOsm1WVsCw_blfGkrEk';

// Supabase client setup
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

async function loadFeed() {
    try {
        const response = await fetch('data.json');
        const items = await response.json();
        
        const grid = document.getElementById('feed-grid');
        grid.innerHTML = '';
        
        if (items.length === 0) {
            grid.innerHTML = '<p>No items in feed yet. Run the daily workflow to populate.</p>';
            return;
        }
        
        items.forEach(item => {
            const tile = createTile(item);
            grid.appendChild(tile);
        });
    } catch (error) {
        console.error('Error loading feed:', error);
        document.getElementById('feed-grid').innerHTML = '<p>Error loading feed. Make sure data.json exists.</p>';
    }
}

async function loadSaved() {
    try {
        const { data: votes } = await supabase
            .from('votes')
            .select('item_id')
            .eq('vote_type', 'keep');
        
        const itemIds = votes.map(v => v.item_id);
        
        if (itemIds.length === 0) {
            document.getElementById('saved-grid').innerHTML = '<p>No saved items yet. Start voting on items in the feed!</p>';
            return;
        }
        
        const { data: items } = await supabase
            .from('items')
            .select('*')
            .in('id', itemIds);
        
        const grid = document.getElementById('saved-grid');
        grid.innerHTML = '';
        
        items.forEach(item => {
            const tile = createTile(item, true);
            grid.appendChild(tile);
        });
    } catch (error) {
        console.error('Error loading saved items:', error);
        document.getElementById('saved-grid').innerHTML = '<p>Error loading saved items. Check Supabase connection.</p>';
    }
}

async function loadWeekly() {
    try {
        const response = await fetch('weekly.json');
        const data = await response.json();
        
        // Patterns
        const patternsContainer = document.getElementById('patterns-container');
        patternsContainer.innerHTML = '';
        
        if (!data.patterns || data.patterns.length === 0) {
            patternsContainer.innerHTML = '<p>No patterns yet. Keep voting to generate intelligence!</p>';
        } else {
            data.patterns.forEach(pattern => {
                const card = document.createElement('div');
                card.className = 'pattern-card';
                card.innerHTML = `
                    <h3>${pattern.pattern_title}</h3>
                    <p><strong>Direction:</strong> ${pattern.direction}</p>
                    <p><strong>Action:</strong> ${pattern.action}</p>
                    <div class="evidence">
                        <p><strong>Evidence:</strong></p>
                        <p>Kept ${pattern.evidence.kept} of ${pattern.evidence.seen} items (${pattern.evidence.rate}%)</p>
                        <p>Common with: ${pattern.evidence.co_tags.join(', ')}</p>
                    </div>
                `;
                patternsContainer.appendChild(card);
            });
        }
        
        // Concepts
        const conceptsContainer = document.getElementById('concepts-container');
        conceptsContainer.innerHTML = '';
        
        if (!data.concepts || data.concepts.length === 0) {
            conceptsContainer.innerHTML = '<p>No concepts yet. Keep voting to generate tee concepts!</p>';
        } else {
            data.concepts.forEach(concept => {
                const card = document.createElement('div');
                card.className = 'concept-card';
                
                const slogansHTML = concept.slogans.map(s => `<span class="slogan-tag">${s}</span>`).join('');
                
                card.innerHTML = `
                    <h3>${concept.concept_name}</h3>
                    <div class="concept-detail"><strong>Front:</strong> ${concept.front_placement}</div>
                    <div class="concept-detail"><strong>Back:</strong> ${concept.back_placement}</div>
                    <div class="concept-detail"><strong>Sleeve:</strong> ${concept.sleeve_detail}</div>
                    <div class="concept-detail"><strong>Motifs:</strong> ${concept.motifs}</div>
                    <div class="concept-detail"><strong>Print Style:</strong> ${concept.print_style}</div>
                    <div class="concept-detail"><strong>Colorways:</strong> ${concept.colorways}</div>
                    <div class="concept-detail">
                        <strong>Slogans:</strong>
                        <div class="slogans">${slogansHTML}</div>
                    </div>
                `;
                conceptsContainer.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading weekly intelligence:', error);
        document.getElementById('patterns-container').innerHTML = '<p>Error loading weekly data. Run the weekly workflow first.</p>';
    }
}

function createTile(item, savedView = false) {
    const tile = document.createElement('div');
    tile.className = 'tile';
    
    const tagsHTML = item.tags.map(tag => 
        `<span class="tag">${tag.replace('_', ' ')}</span>`
    ).join('');
    
    const actionsHTML = savedView ? '' : `
        <div class="tile-actions">
            <button class="btn btn-keep" onclick="voteKeep('${item.id}', this)">✓ Keep</button>
            <button class="btn btn-skip" onclick="voteSkip('${item.id}', this)">✕ Skip</button>
        </div>
        <button class="toggle-explanation" onclick="toggleExplanation(this)">Why you're seeing this</button>
        <div class="explanation">${item.explanation || 'Matches your cluster preferences'}</div>
    `;
    
    tile.innerHTML = `
        <img src="${item.image_url}" alt="${item.title}" class="tile-image" onerror="this.src='https://via.placeholder.com/300x250?text=No+Image'">
        <div class="tile-content">
            <div class="tile-title">${item.title}</div>
            <div class="tile-tags">${tagsHTML}</div>
            ${actionsHTML}
        </div>
    `;
    
    return tile;
}

async function voteKeep(itemId, btn) {
    try {
        await supabase.from('votes').insert({
            item_id: itemId,
            vote_type: 'keep'
        });
        
        const { data: item } = await supabase.from('items').select('tags').eq('id', itemId).single();
        
        for (const tag of item.tags) {
            await supabase.rpc('increment_tag_weight', { tag_name: tag, delta: 0.2 });
        }
        
        for (let i = 0; i < item.tags.length; i++) {
            for (let j = i + 1; j < item.tags.length; j++) {
                const [tag_a, tag_b] = [item.tags[i], item.tags[j]].sort();
                await supabase.rpc('increment_pair_weight', { tag_a, tag_b, delta: 0.3 });
            }
        }
        
        btn.closest('.tile').style.opacity = '0.5';
        btn.disabled = true;
        btn.textContent = '✓ Saved';
    } catch (error) {
        console.error('Error voting keep:', error);
        alert('Error saving item. Check console.');
    }
}

async function voteSkip(itemId, btn) {
    try {
        await supabase.from('votes').insert({
            item_id: itemId,
            vote_type: 'skip'
        });
        
        const { data: item } = await supabase.from('items').select('tags').eq('id', itemId).single();
        
        for (const tag of item.tags) {
            await supabase.rpc('increment_tag_weight', { tag_name: tag, delta: -0.1 });
        }
        
        btn.closest('.tile').remove();
    } catch (error) {
        console.error('Error voting skip:', error);
        alert('Error skipping item. Check console.');
    }
}

function toggleExplanation(btn) {
    const explanation = btn.nextElementSibling;
    explanation.classList.toggle('visible');
}
