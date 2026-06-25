"""
Propositional Logic Engine
Python translation of the C++23 logical sentence evaluator.
"""

# ============================================================================
# Abstract Base Class: Sentence
# ============================================================================

class Sentence:
    def evaluate(self, model: dict[str, bool]) -> bool:
        """Evaluates the logical sentence against a model."""
        raise NotImplementedError

    def formula(self) -> str:
        """Returns a string representing the logical formula."""
        raise NotImplementedError

    def symbols(self) -> set[str]:
        """Returns a set of all symbols in the logical sentence."""
        raise NotImplementedError

    @classmethod
    def validate(cls, sentence: 'Sentence'):
        """Validates that the provided object is a Sentence subclass."""
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def balanced(cls, s: str) -> bool:
        """Checks if a string has balanced parentheses."""
        count = 0
        for char in s:
            if char == "(":
                count += 1
            elif char == ")":
                if count <= 0:
                    return False
                count -= 1
        return count == 0

    @classmethod
    def parenthesize(cls, s: str) -> str:
        """Adds parentheses around a string if necessary."""
        if not s or s.isalpha():
            return s

        if s.startswith("(") and s.endswith(")"):
            inner = s[1:-1]
            if cls.balanced(inner):
                return s

        return f"({s})"


# ============================================================================
# Logical Sentence Subclasses
# ============================================================================

class Symbol(Sentence):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, model: dict[str, bool]) -> bool:
        if self.name in model:
            return model[self.name]
        raise RuntimeError(f"variable {self.name} not in model")

    def formula(self) -> str:
        return self.name

    def symbols(self) -> set[str]:
        return {self.name}

    def __repr__(self) -> str:
        return self.name


class Not(Sentence):
    def __init__(self, operand: Sentence):
        Sentence.validate(operand)
        self.operand = operand

    def evaluate(self, model: dict[str, bool]) -> bool:
        return not self.operand.evaluate(model)

    def formula(self) -> str:
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def symbols(self) -> set[str]:
        return self.operand.symbols()

    def __repr__(self) -> str:
        return f"Not({repr(self.operand)})"


class And(Sentence):
    def __init__(self, *conjuncts: Sentence):
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def add(self, conjunct: Sentence):
        Sentence.validate(conjunct)
        self.conjuncts.append(conjunct)

    def evaluate(self, model: dict[str, bool]) -> bool:
        return all(c.evaluate(model) for c in self.conjuncts)

    def formula(self) -> str:
        if not self.conjuncts:
            return ""
        if len(self.conjuncts) == 1:
            return self.conjuncts[0].formula()
        
        return " ∧ ".join(Sentence.parenthesize(c.formula()) for c in self.conjuncts)

    def symbols(self) -> set[str]:
        return set.union(*(c.symbols() for c in self.conjuncts)) if self.conjuncts else set()

    def __repr__(self) -> str:
        conjs = ", ".join(repr(c) for c in self.conjuncts)
        return f"And({conjs})"


class Or(Sentence):
    def __init__(self, *disjuncts: Sentence):
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = list(disjuncts)

    def evaluate(self, model: dict[str, bool]) -> bool:
        return any(d.evaluate(model) for d in self.disjuncts)

    def formula(self) -> str:
        if not self.disjuncts:
            return ""
        if len(self.disjuncts) == 1:
            return self.disjuncts[0].formula()
            
        return " ∨  ".join(Sentence.parenthesize(d.formula()) for d in self.disjuncts)

    def symbols(self) -> set[str]:
        return set.union(*(d.symbols() for d in self.disjuncts)) if self.disjuncts else set()

    def __repr__(self) -> str:
        disjs = ", ".join(repr(d) for d in self.disjuncts)
        return f"Or({disjs})"


class Implication(Sentence):
    def __init__(self, antecedent: Sentence, consequent: Sentence):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def evaluate(self, model: dict[str, bool]) -> bool:
        return not self.antecedent.evaluate(model) or self.consequent.evaluate(model)

    def formula(self) -> str:
        ant = Sentence.parenthesize(self.antecedent.formula())
        cons = Sentence.parenthesize(self.consequent.formula())
        return f"{ant} => {cons}"

    def symbols(self) -> set[str]:
        return self.antecedent.symbols().union(self.consequent.symbols())

    def __repr__(self) -> str:
        return f"Implication({repr(self.antecedent)}, {repr(self.consequent)})"


class Biconditional(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def evaluate(self, model: dict[str, bool]) -> bool:
        l_val = self.left.evaluate(model)
        r_val = self.right.evaluate(model)
        return l_val == r_val

    def formula(self) -> str:
        # Matches the C++ implementation's choice to use repr() here
        l_str = Sentence.parenthesize(repr(self.left))
        r_str = Sentence.parenthesize(repr(self.right))
        return f"{l_str} <=> {r_str}"

    def symbols(self) -> set[str]:
        return self.left.symbols().union(self.right.symbols())

    def __repr__(self) -> str:
        return f"Biconditional({repr(self.left)}, {repr(self.right)})"


# ============================================================================
# Model Checking Core Algorithm
# ============================================================================

def check_all(knowledge: Sentence, query: Sentence, symbols: set[str], model: dict[str, bool]) -> bool:
    """Recursively checks if knowledge entails the query in all possible models."""
    # If model has an assignment for each symbol
    if not symbols:
        # If knowledge base is true in model, then query must also be true
        if knowledge.evaluate(model):
            return query.evaluate(model)
        return True
    
    # Choose one of the remaining unused symbols
    remaining_symbols = symbols.copy()
    p = remaining_symbols.pop()

    # Create a model where the symbol is true
    model_true = model.copy()
    model_true[p] = True

    # Create a model where the symbol is false
    model_false = model.copy()
    model_false[p] = False

    # Ensure entailment holds in both models
    return (check_all(knowledge, query, remaining_symbols, model_true) and
            check_all(knowledge, query, remaining_symbols, model_false))


def model_check(knowledge: Sentence, query: Sentence) -> bool:
    """Returns True if knowledge entails query, otherwise False."""
    # Get all symbols in both knowledge and query
    symbols = knowledge.symbols().union(query.symbols())
    
    # Check that knowledge entails query
    return check_all(knowledge, query, symbols, dict())


# ============================================================================
# Main Execution / Sanity Verification
# ============================================================================

def main():
    # Example Setup: 
    # Knowledge Base: (A => B) ∧ A
    # Query: B
    symA = Symbol("A")
    symB = Symbol("B")

    # Replaces std::initializer_list with Python's *args
    KB = And(
        Implication(symA, symB),
        symA
    )

    print(f"Knowledge Base Formula: {KB.formula()}")
    print(f"Query Formula: {symB.formula()}")

    if model_check(KB, symB):
        print("Success: The Knowledge Base entails the query!")
    else:
        print("Failure: The Knowledge Base does NOT entail the query.")

if __name__ == "__main__":
    main()
