-- Items cache
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    source TEXT,
    image_url TEXT,
    tags TEXT[], -- Array of matched cluster tags
    pub_date TIMESTAMP,
    summary TEXT,
    cluster_score FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_items_url ON items(url);
CREATE INDEX idx_items_tags ON items USING GIN(tags);
CREATE INDEX idx_items_pub_date ON items(pub_date DESC);

-- User votes
CREATE TABLE votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    vote_type TEXT CHECK (vote_type IN ('keep', 'skip')),
    voted_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_votes_item ON votes(item_id);
CREATE INDEX idx_votes_type ON votes(vote_type);
CREATE INDEX idx_votes_date ON votes(voted_at DESC);

-- Tag preference profile
CREATE TABLE profile (
    tag TEXT PRIMARY KEY,
    weight FLOAT DEFAULT 1.0,
    keep_count INT DEFAULT 0,
    skip_count INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tag pair tracking
CREATE TABLE tag_pairs (
    tag_a TEXT,
    tag_b TEXT,
    weight FLOAT DEFAULT 1.0,
    co_keep_count INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (tag_a, tag_b)
);

-- Weekly patterns
CREATE TABLE weekly_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    week_start DATE NOT NULL,
    pattern_title TEXT,
    evidence JSONB, -- {tags, sources, frequency}
    direction TEXT,
    action TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_patterns_week ON weekly_patterns(week_start DESC);

-- Tee concepts
CREATE TABLE tee_concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    week_start DATE NOT NULL,
    concept_name TEXT,
    front_placement TEXT,
    back_placement TEXT,
    sleeve_detail TEXT,
    motifs TEXT,
    slogans TEXT[], -- Array of 2-4 options
    print_style TEXT,
    colorways TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_concepts_week ON tee_concepts(week_start DESC);

-- Enable Row Level Security (optional, but recommended)
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE tag_pairs ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE tee_concepts ENABLE ROW LEVEL SECURITY;

-- Public read/write policies for anon key usage
CREATE POLICY "Public read items" ON items FOR SELECT USING (true);
CREATE POLICY "Public insert items" ON items FOR INSERT WITH CHECK (true);
CREATE POLICY "Public read votes" ON votes FOR SELECT USING (true);
CREATE POLICY "Public insert votes" ON votes FOR INSERT WITH CHECK (true);
CREATE POLICY "Public read profile" ON profile FOR SELECT USING (true);
CREATE POLICY "Public update profile" ON profile FOR ALL USING (true);
CREATE POLICY "Public read pairs" ON tag_pairs FOR SELECT USING (true);
CREATE POLICY "Public update pairs" ON tag_pairs FOR ALL USING (true);
CREATE POLICY "Public read patterns" ON weekly_patterns FOR SELECT USING (true);
CREATE POLICY "Public insert patterns" ON weekly_patterns FOR INSERT WITH CHECK (true);
CREATE POLICY "Public read concepts" ON tee_concepts FOR SELECT USING (true);
CREATE POLICY "Public insert concepts" ON tee_concepts FOR INSERT WITH CHECK (true);

-- Helper functions for weight updates
CREATE OR REPLACE FUNCTION increment_tag_weight(tag_name TEXT, delta FLOAT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO profile (tag, weight, keep_count)
    VALUES (tag_name, 1.0 + delta, CASE WHEN delta > 0 THEN 1 ELSE 0 END)
    ON CONFLICT (tag) 
    DO UPDATE SET 
        weight = profile.weight + delta,
        keep_count = CASE WHEN delta > 0 THEN profile.keep_count + 1 ELSE profile.keep_count END,
        skip_count = CASE WHEN delta < 0 THEN profile.skip_count + 1 ELSE profile.skip_count END,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION increment_pair_weight(tag_a TEXT, tag_b TEXT, delta FLOAT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO tag_pairs (tag_a, tag_b, weight, co_keep_count)
    VALUES (tag_a, tag_b, 1.0 + delta, 1)
    ON CONFLICT (tag_a, tag_b)
    DO UPDATE SET
        weight = tag_pairs.weight + delta,
        co_keep_count = tag_pairs.co_keep_count + 1,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;
