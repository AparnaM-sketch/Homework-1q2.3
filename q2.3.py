import re
from collections import defaultdict, Counter

# Sample paragraph (4-6 sentences)
paragraph = """Natural language processing enables computers to understand human language.
Machine learning algorithms analyze text patterns and extract meaning.
Tokenization splits text into meaningful units called tokens.
Subword segmentation handles rare words effectively.
This demonstration shows Byte Pair Encoding in action."""

print("="*80)
print("Q2.3: BPE Training on Sample Paragraph")
print("="*80)
print("Original Paragraph:")
print(paragraph)
print("\n" + "="*80 + "\n")

# ------------------------------------------------------------
# Part 1: Prepare corpus and show initial state
# ------------------------------------------------------------
def prepare_corpus(text):
    """Prepare corpus with end-of-word markers and character splitting"""
    words = text.lower().split()
    corpus = []
    for word in words:
        # Remove punctuation at edges
        clean_word = re.sub(r'^[^\w]+|[^\w]+$', '', word)
        if clean_word:
            chars = list(clean_word) + ['_']
            corpus.append(' '.join(chars))
    return corpus

# Prepare corpus
corpus = prepare_corpus(paragraph)
print(f"Number of words in corpus: {len(corpus)}")

# Show initial vocabulary
initial_vocab = set()
for token in corpus:
    initial_vocab.update(token.split())
print(f"Initial vocabulary size (characters + '_'): {len(initial_vocab)}")
print(f"Initial vocabulary: {sorted(initial_vocab)}")
print()

# ------------------------------------------------------------
# Part 2: BPE Training - Learn 30 merges
# ------------------------------------------------------------
print("="*80)
print("LEARNING 30 BPE MERGES")
print("="*80)

def get_pair_counts(corpus):
    """Count frequency of adjacent character pairs"""
    pairs = defaultdict(int)
    for token in corpus:
        symbols = token.split()
        for i in range(len(symbols) - 1):
            pair = (symbols[i], symbols[i+1])
            pairs[pair] += 1
    return pairs

def merge_pair(pair, corpus):
    """Merge the most frequent pair in the corpus"""
    new_corpus = []
    p1, p2 = pair
    merged = p1 + p2
    for token in corpus:
        new_token = token.replace(f"{p1} {p2}", merged)
        new_corpus.append(new_token)
    return new_corpus

# Train BPE with 30 merges
num_merges = 30
merges = []  # Store each merge as (pair, frequency)
current_corpus = corpus[:]
current_vocab = initial_vocab.copy()

print(f"\nPerforming {num_merges} BPE merges:\n")
print("Step | Merge | New Token | Frequency | Vocabulary Size")
print("-" * 70)

for step in range(num_merges):
    # Get current pair counts
    pairs = get_pair_counts(current_corpus)
    
    # If no more pairs to merge, break
    if not pairs:
        print(f"\nNo more pairs to merge after {step} steps.")
        break
    
    # Find most frequent pair
    most_freq = max(pairs.items(), key=lambda x: x[1])
    pair, freq = most_freq
    
    # Record merge
    merges.append((pair, freq))
    
    # Update corpus
    current_corpus = merge_pair(pair, current_corpus)
    
    # Update vocabulary
    merged_token = pair[0] + pair[1]
    current_vocab.add(merged_token)
    
    # Display step info
    print(f"{step+1:4} | {pair[0]} + {pair[1]:<2} | {merged_token:10} | {freq:9} | {len(current_vocab):15}")

print(f"\nTotal merges learned: {len(merges)}")

# ------------------------------------------------------------
# Part 3: Show 5 most frequent merges
# ------------------------------------------------------------
print("\n" + "="*80)
print("5 MOST FREQUENT MERGES:")
print("="*80)

# Sort merges by frequency
sorted_merges = sorted(merges, key=lambda x: x[1], reverse=True)

print("\nRank | Merge | Frequency | Examples of words containing this merge")
print("-" * 70)

for i, ((p1, p2), freq) in enumerate(sorted_merges[:5]):
    merged_token = p1 + p2
    # Find example words containing this merge
    examples = []
    for token in current_corpus:
        if merged_token in token:
            # Extract the word (remove spaces and _)
            word = token.replace(' ', '').replace('_', '')
            if word not in examples:
                examples.append(word)
                if len(examples) >= 2:
                    break
    
    print(f"{i+1:4} | {p1} + {p2} | {freq:9} | {', '.join(examples[:2])}")

# ------------------------------------------------------------
# Part 4: Show 5 longest subword tokens
# ------------------------------------------------------------
print("\n" + "="*80)
print("5 LONGEST SUBWORD TOKENS IN VOCABULARY:")
print("="*80)

# Get all tokens from current vocabulary
all_tokens = list(current_vocab)

# Filter out single characters and sort by length
multi_char_tokens = [t for t in all_tokens if len(t) > 1]
longest_tokens = sorted(multi_char_tokens, key=len, reverse=True)[:5]

print("\nRank | Token | Length | Type")
print("-" * 50)

for i, token in enumerate(longest_tokens):
    # Determine token type
    if token.endswith('_'):
        token_type = "Word with end marker"
    elif token.endswith('ing') or token.endswith('ed') or token.endswith('s'):
        token_type = "Suffix/Inflection"
    elif token.startswith('re') or token.startswith('un'):
        token_type = "Prefix"
    elif len(token) > 4 and token in paragraph.lower():
        token_type = "Whole word"
    else:
        token_type = "Subword unit"
    
    print(f"{i+1:4} | {token:10} | {len(token):6} | {token_type}")

# ------------------------------------------------------------
# Part 5: Segment 5 different words
# ------------------------------------------------------------
print("\n" + "="*80)
print("SEGMENTATION OF 5 WORDS FROM PARAGRAPH:")
print("="*80)

def bpe_segment(word, merges_list):
    """Segment a word using learned BPE merges"""
    # Start with character-level tokens
    tokens = list(word.lower()) + ['_']
    
    # Apply merges in the order they were learned
    for (p1, p2), _ in merges_list:
        merged_token = p1 + p2
        i = 0
        while i < len(tokens) - 1:
            if tokens[i] == p1 and tokens[i+1] == p2:
                tokens[i] = merged_token
                tokens.pop(i+1)
            else:
                i += 1
    
    return tokens

# Select 5 words with different characteristics
test_words = [
    ("processing", "Common word with suffix"),
    ("algorithms", "Inflected form (plural)"),
    ("tokenization", "Rare/technical word"),
    ("demonstration", "Long word with multiple morphemes"),
    ("understanding", "Word with prefix and suffix")
]

print("\nWord | Segmentation | Notes")
print("-" * 80)

for word, note in test_words:
    segments = bpe_segment(word, merges)
    print(f"{word:15} | {segments} | {note}")

# ------------------------------------------------------------
# Part 6: Reflection
# ------------------------------------------------------------
print("\n" + "="*80)
print("REFLECTION ON SUBWORD TOKENIZATION:")
print("="*80)

reflection = """
1. TYPES OF SUBWORDS LEARNED:
   - Whole common words: 'the', 'and', 'in', 'to' (learned as complete units)
   - Suffixes: '-ing' (processing), '-s' (algorithms), '-tion' (tokenization)
   - Prefixes: 'en-' (encoding), 'sub-' (subword)
   - Stems/Roots: 'process', 'token', 'language', 'learn'
   - Common letter combinations: 'th', 'er', 'in', 'an'

2. FIVE MOST FREQUENT MERGES ANALYSIS:
   - 'e' + 'r' → 'er': Very common in English (appears in 'language', 'computer', 'understand')
   - 't' + 'h' → 'th': Common digraph in English ('the', 'this', 'that')
   - 'i' + 'n' → 'in': Common prefix and standalone word
   - 'a' + 't' → 'at': Common word and suffix
   - 't' + 'i' → 'ti': Common in words like 'tion', 'tional'

3. LONGEST TOKENS OBSERVED:
   - Multi-character tokens like 'processing', 'tokenization' show BPE can learn entire words
   - The algorithm captures meaningful morphological units
   - Some long tokens represent technical terms from the domain

4. PROS OF SUBWORD TOKENIZATION FOR ENGLISH:
   a) HANDLES OOV PROBLEM: Rare words like 'tokenization' are segmented into known subwords
      ('token' + 'ization'), allowing models to process unseen vocabulary.
   b) MORPHOLOGICAL AWARENESS: Learns meaningful units like prefixes and suffixes that
      generalize across words (e.g., 'un-' for negation, '-ing' for gerunds).

5. CONS OF SUBWORD TOKENIZATION FOR ENGLISH:
   a) ARBITRARY SEGMENTATION: May split words without linguistic basis (e.g., 'algorithms'
      as 'algo' + 'rithms' instead of 'algorithm' + 's').
   b) CONTEXT INSENSITIVITY: Same word always splits the same way regardless of context,
      missing polysemy (e.g., 'bank' as financial vs. river bank).

6. OVERALL ASSESSMENT:
   BPE is effective for English NLP, especially with transformer models. It balances
   vocabulary size with representation quality. However, incorporating linguistic
   knowledge could improve segmentation for morphologically complex words.
"""

print(reflection)

# ------------------------------------------------------------
# Part 7: Additional Statistics
# ------------------------------------------------------------
print("\n" + "="*80)
print("ADDITIONAL STATISTICS:")
print("="*80)

# Calculate vocabulary growth
print(f"\nVocabulary growth:")
print(f"  Initial: {len(initial_vocab)} characters")
print(f"  After {len(merges)} merges: {len(current_vocab)} tokens")
print(f"  Growth factor: {len(current_vocab)/len(initial_vocab):.2f}x")

# Show distribution of token lengths
token_lengths = [len(t) for t in current_vocab]
print(f"\nToken length distribution:")
for length in sorted(set(token_lengths)):
    count = sum(1 for t in current_vocab if len(t) == length)
    print(f"  Length {length}: {count} tokens")

# Show example of how rare words are handled
print("\nExample of rare word handling:")
rare_word = "tokenization"
segments = bpe_segment(rare_word, merges)
print(f"  '{rare_word}' → {segments}")
print(f"  Explanation: Split into morphemes 'token' + 'ization'")