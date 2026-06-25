import sys
import re
import random
from pathlib import Path

# Type Aliases for readability, matching the C++ types
Corpus = dict[str, set[str]]
ProbDist = dict[str, float]

# Constants
DAMPING = 0.85
SAMPLES = 10000

def crawl(directory: str) -> Corpus:
    """Extracts all links from HTML files in a given directory."""
    pages: Corpus = {}
    
    # Iterate through all files in the directory
    folder = Path(directory)
    if not folder.is_dir():
        print(f"Error: {directory} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    for file_path in folder.iterdir():
        if file_path.suffix != ".html":
            continue
            
        filename = file_path.name
        try:
            with file_path.open('r', encoding='utf-8') as f:
                contents = f.read()
        except IOError:
            continue
            
        # Regex to extract links (matches the C++ raw string literal R"(...)")
        link_re = re.compile(r'<a\s+(?:[^>]*?)href="([^"]*)"')
        links = set(link_re.findall(contents))
        
        # Remove self-links
        if filename in links:
            links.remove(filename)
            
        pages[filename] = links

    # Only include links to other pages that actually exist in the corpus
    for filename in pages:
        pages[filename] = {link for link in pages[filename] if link in pages}
        
    return pages

def transition_model(corpus: Corpus, page: str, damping_factor: float) -> ProbDist:
    """Returns a probability distribution over which page to visit next."""
    prob_dist: ProbDist = {state: 0.0 for state in corpus}
    
    if page in corpus:
        num_pages = float(len(corpus))
        linked_pages = corpus[page]
        num_links = float(len(linked_pages))

        if num_links > 0:
            # Probability of choosing a link on the page randomly
            for state in linked_pages:
                prob_dist[state] += damping_factor / num_links
                
            # Probability of choosing any page at random (damping mechanism)
            for state in corpus:
                prob_dist[state] += (1.0 - damping_factor) / num_pages
        else:
            # If no outgoing links, choose randomly over all pages equally
            for state in corpus:
                prob_dist[state] += 1.0 / num_pages
                
    return prob_dist

def sample_pagerank(corpus: Corpus, damping_factor: float, n: int) -> ProbDist:
    """Calculates PageRank values for a corpus by sampling an N-step random surfer."""
    pages = list(corpus.keys())
    samples: dict[str, int] = {page: 0 for page in pages}

    # Randomly choose the first sample uniformally
    sample = random.choice(pages)
    samples[sample] += 1

    # Randomly choose remaining samples based on the transition model
    for _ in range(1, n):
        model = transition_model(corpus, sample, damping_factor)
        keys = list(model.keys())
        weights = list(model.values())
        
        # random.choices uses weights to simulate C++'s std::discrete_distribution
        sample = random.choices(keys, weights=weights, k=1)[0]
        samples[sample] += 1

    # Normalize samples into proportions
    page_ranks: ProbDist = {page: count / n for page, count in samples.items()}
    return page_ranks

def iterate_pagerank(corpus: Corpus, damping_factor: float) -> ProbDist:
    """Calculates PageRank values for a corpus iteratively until convergence."""
    page_ranks: ProbDist = {}
    num_pages = float(len(corpus))

    # Initialize all pages with a rank of 0.0
    for page in corpus:
        page_ranks[page] = 0.0

    if num_pages > 0:
        # Initial state: rank each page equally
        for page in corpus:
            page_ranks[page] = 1.0 / num_pages

        # Cache the number of links for each page
        num_links: dict[str, float] = {
            page: (num_pages if not links else float(len(links)))
            for page, links in corpus.items()
        }

        # Iteratively update ranks until accuracy varies by less than 0.001
        iterate = True
        while iterate:
            iterate = False
            first_condition = (1.0 - damping_factor) / num_pages

            for page in corpus:
                current_rank = page_ranks[page]
                second_condition = 0.0

                for linking_page, links in corpus.items():
                    if page in links or not links:
                        second_condition += page_ranks[linking_page] / num_links[linking_page]
                
                second_condition *= damping_factor
                new_rank = first_condition + second_condition
                page_ranks[page] = new_rank

                if abs(new_rank - current_rank) > 0.001:
                    iterate = True
                    
    return page_ranks

def main() -> None:
    # Ensure correct CLI usage
    if len(sys.argv) != 2:
        print("Usage: python pagerank.py corpus", file=sys.stderr)
        sys.exit(1)

    directory = sys.argv[1]
    corpus = crawl(directory)

    # Print Sampling Results
    sampled_ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page, rank in sampled_ranks.items():
        print(f"  {page}: {rank:.4f}")

    # Print Iterative Results
    iterated_ranks = iterate_pagerank(corpus, DAMPING)
    print("PageRank Results from Iteration")
    for page, rank in iterated_ranks.items():
        print(f"  {page}: {rank:.4f}")

if __name__ == "__main__":
    main()
