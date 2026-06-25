"""
Propositional Logic Engine - Knights and Knaves
Python translation of the C++23 logical sentence evaluator.
"""

# ============================================================================
# Logic Framework Definition
# ============================================================================

class Sentence:
    def evaluate(self, model: dict[str, bool]) -> bool:
        """Evaluates the logical sentence against a truth model."""
        raise NotImplementedError

    def formula(self) -> str:
        """Returns a string representing the logical formula."""
        raise NotImplementedError

    def symbols(self) -> set[str]:
        """Returns a set of all symbols in the logical sentence."""
        raise NotImplementedError

    @classmethod
    def validate(cls, sentence: 'Sentence'):
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def balanced(cls, s: str) -> bool:
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
        if not s or s.isalpha():
            return s
        if s.startswith("(") and s.endswith(")"):
            inner = s[1:-1]
            if cls.balanced(inner):
                return s
        return f"({s})"


class Symbol(Sentence):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, model: dict[str, bool]) -> bool:
        if self.name in model:
            return model[self.name]
        raise RuntimeError(f"variable '{self.name}' not in model")

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


# ============================================================================
# Model Checking Logic Engine
# ============================================================================

def check_all(knowledge: Sentence, query: Sentence, symbols: set[str], model: dict[str, bool]) -> bool:
    """Recursively evaluates the truth of a query given a knowledge base."""
    if not symbols:
        if knowledge.evaluate(model):
            return query.evaluate(model)
        return True
    
    remaining_symbols = symbols.copy()
    p = remaining_symbols.pop()

    # Pass dict copies to maintain branch state isolation, mimicking C++ pass-by-value
    model_true = model.copy()
    model_true[p] = True

    model_false = model.copy()
    model_false[p] = False

    return (check_all(knowledge, query, remaining_symbols, model_true) and
            check_all(knowledge, query, remaining_symbols, model_false))


def model_check(knowledge: Sentence, query: Sentence) -> bool:
    """Returns True if knowledge entails query, otherwise False."""
    symbols = knowledge.symbols().union(query.symbols())
    return check_all(knowledge, query, symbols, dict())


# ============================================================================
# Main Application / Puzzle Verification
# ============================================================================

def main():
    # Defining Global Puzzle Symbols
    AKnight = Symbol("A is a Knight")
    AKnave  = Symbol("A is a Knave")
    BKnight = Symbol("B is a Knight")
    BKnave  = Symbol("B is a Knave")
    CKnight = Symbol("C is a Knight")
    CKnave  = Symbol("C is a Knave")

    # Puzzle 0: A says "I am both a knight and a knave."
    knowledge0 = And(
        Or(AKnight, AKnave),
        Not(And(AKnight, AKnave)),
        Implication(AKnight, And(AKnight, AKnave)),
        Implication(AKnave, Or(Not(AKnight), Not(AKnave)))
    )

    # Puzzle 1: A says "We are both knaves."
    knowledge1 = And(
        Or(AKnight, AKnave),
        Not(And(AKnight, AKnave)),
        Or(BKnight, BKnave),
        Not(And(BKnight, BKnave)),
        Implication(AKnight, And(AKnave, BKnave)),
        Implication(AKnave, Or(
            And(AKnight, BKnave),
            And(AKnave, BKnight)
        ))
    )

    # Puzzle 2: A says "We are the same kind." B says "We are of different kinds."
    knowledge2 = And(
        Or(AKnight, AKnave),
        Not(And(AKnight, AKnave)),
        Or(BKnight, BKnave),
        Not(And(BKnight, BKnave)),
        Implication(AKnight, Or(
            And(AKnight, BKnight),
            And(AKnave, BKnave)
        )),
        Implication(AKnave, Or(
            And(AKnight, BKnave),
            And(AKnave, BKnight)
        )),
        Implication(BKnight, Or(
            And(AKnight, BKnave),
            And(AKnave, BKnight)
        )),
        Implication(BKnave, Or(
            And(AKnight, BKnight),
            And(AKnave, BKnave)
        ))
    )

    # Puzzle 3: Hidden complexities of A, B, and C's cross-referencing logic statements
    knowledge3 = And(
        Or(AKnight, AKnave),
        Not(And(AKnight, AKnave)),
        Or(BKnight, BKnave),
        Not(And(BKnight, BKnave)),
        Or(CKnight, CKnave),
        Not(And(CKnight, CKnave)),
        Implication(AKnight, Or(AKnight, AKnave)),
        Implication(AKnave, And(AKnight, AKnave)),
        Implication(BKnight, Implication(AKnight, BKnave)),
        Implication(BKnight, CKnave),
        Implication(BKnave, CKnight),
        Implication(CKnight, AKnight),
        Implication(CKnave, AKnave)
    )

    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]

    for name, knowledge in puzzles:
        print(name)
        if not knowledge.conjuncts:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {repr(symbol)}")

if __name__ == "__main__":
    main()
