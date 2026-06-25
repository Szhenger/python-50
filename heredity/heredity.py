import csv
import itertools
import sys

# ============================================================================
# Core Constants
# ============================================================================

PROBS_MUTATION = 0.01

PROBS_GENE = {
    2: 0.01,
    1: 0.03,
    0: 0.96
}

PROBS_TRAIT = {
    2: {True: 0.65, False: 0.35},
    1: {True: 0.56, False: 0.44},
    0: {True: 0.01, False: 0.99}
}


# ============================================================================
# Helper Functions
# ============================================================================

def load_data(filename: str) -> dict:
    """
    Load gene and trait data from a CSV file into a dictionary.
    """
    data = {}
    try:
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["name"]
                
                # Convert string 1/0 to boolean True/False, or None if empty
                trait = None
                if row["trait"] == "1":
                    trait = True
                elif row["trait"] == "0":
                    trait = False
                
                data[name] = {
                    "name": name,
                    "mother": row["mother"] or None,
                    "father": row["father"] or None,
                    "trait": trait
                }
    except OSError as e:
        sys.exit(f"Could not open file: {e}")
        
    return data

def powerset(s: set) -> list[set]:
    """
    Generates all subsets of a given set.
    """
    s_list = list(s)
    # Uses itertools to generate combinations of all possible lengths
    return [
        set(subset) for subset in itertools.chain.from_iterable(
            itertools.combinations(s_list, r) for r in range(len(s_list) + 1)
        )
    ]


# ============================================================================
# Core Logic
# ============================================================================

def joint_probability(people: dict, one_gene: set, two_genes: set, have_trait: set) -> float:
    """
    Compute and return a joint probability.
    """
    probability = 1.0

    for person, info in people.items():
        mother = info["mother"]
        father = info["father"]

        # 1. Determine probability of passing down from Mother
        mother_prob = PROBS_MUTATION
        if mother is not None:
            if mother in one_gene:
                mother_prob = 0.5
            elif mother in two_genes:
                mother_prob = 1.0 - PROBS_MUTATION

        # 2. Determine probability of passing down from Father
        father_prob = PROBS_MUTATION
        if father is not None:
            if father in one_gene:
                father_prob = 0.5
            elif father in two_genes:
                father_prob = 1.0 - PROBS_MUTATION

        # 3. Calculate likelihood of this person's gene configuration
        if person in one_gene:
            if mother is None and father is None:
                gene_prob = PROBS_GENE[1]
            else:
                # Inherit from mother NOT father, OR inherit from father NOT mother
                gene_prob = (mother_prob * (1.0 - father_prob)) + (father_prob * (1.0 - mother_prob))
            
            trait_prob = PROBS_TRAIT[1][person in have_trait]

        elif person in two_genes:
            if mother is None and father is None:
                gene_prob = PROBS_GENE[2]
            else:
                # Must inherit from both parents
                gene_prob = mother_prob * father_prob
                
            trait_prob = PROBS_TRAIT[2][person in have_trait]

        else:
            # 0 genes
            if mother is None and father is None:
                gene_prob = PROBS_GENE[0]
            else:
                # Must NOT inherit from either parent
                gene_prob = (1.0 - mother_prob) * (1.0 - father_prob)
                
            trait_prob = PROBS_TRAIT[0][person in have_trait]

        # 4. Multiply into joint probability chain
        probability *= (gene_prob * trait_prob)

    return probability

def update(probabilities: dict, one_gene: set, two_genes: set, have_trait: set, p: float):
    """
    Add to `probabilities` a new joint probability `p`.
    """
    for person in probabilities:
        # Check gene count
        if person in two_genes:
            gene = 2
        elif person in one_gene:
            gene = 1
        else:
            gene = 0
            
        probabilities[person]["gene"][gene] += p
        
        # Check trait presence
        has_trait = person in have_trait
        probabilities[person]["trait"][has_trait] += p

def normalize(probabilities: dict):
    """
    Update `probabilities` such that each probability distribution
    is normalized (sums to 1).
    """
    for person, probs in probabilities.items():
        # Normalize genes
        gene_sum = sum(probs["gene"].values())
        for gene in probs["gene"]:
            probs["gene"][gene] /= gene_sum

        # Normalize traits
        trait_sum = sum(probs["trait"].values())
        for trait in probs["trait"]:
            probs["trait"][trait] /= trait_sum


# ============================================================================
# Main Execution
# ============================================================================

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")

    people = load_data(sys.argv[1])
    
    # Initialize probabilities tracking dictionary
    probabilities = {
        person: {
            "gene": {2: 0.0, 1: 0.0, 0: 0.0},
            "trait": {True: 0.0, False: 0.0}
        }
        for person in people
    }

    names = set(people.keys())

    # Loop over all sets of people who might have the trait
    for have_trait in powerset(names):
        
        # Check if current set of people violates known information
        fails_evidence = False
        for person in names:
            person_trait = people[person]["trait"]
            if person_trait is not None and person_trait != (person in have_trait):
                fails_evidence = True
                break
        
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            
            # Python sets support direct subtraction, replacing custom set_difference function
            remaining_names = names - one_gene
            
            for two_genes in powerset(remaining_names):
                
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    normalize(probabilities)

    # Print results mapping identically to the C++ print output
    for person in names:
        print(f"{person}:")
        print("  Gene:")
        # Loop backwards [2, 1, 0] to match C++ loop behavior
        for i in range(2, -1, -1):
            print(f"    {i}: {probabilities[person]['gene'][i]:.4f}")
            
        print("  Trait:")
        print(f"    True: {probabilities[person]['trait'][True]:.4f}")
        print(f"    False: {probabilities[person]['trait'][False]:.4f}")


if __name__ == "__main__":
    main()
