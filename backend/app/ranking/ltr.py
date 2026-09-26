"""Pointwise learning-to-rank for the positioning module.

The ranker scores each (query, document) pair with a logistic model over four
features — retriever relevance, recency, source authority and aggregated user
feedback:

    P(relevant | x) = sigmoid(w . x + b)

and orders results by that probability. The weights are learned from the 👍/👎
votes stored in the `feedback` table (vote = +1 -> label 1, vote = -1 -> label 0).

Two details keep this honest with the small amount of feedback a personal
deployment collects:

* **Prior, not zero.** Training minimises log-loss plus an L2 penalty that
  pulls the weights toward a hand-set prior (``prior_model``), i.e. a MAP
  estimate under a Gaussian prior centred on those weights. The penalty is
  worth ``PRIOR_STRENGTH`` pseudo-examples, so it dominates while votes are
  scarce and fades as they accumulate. With no votes the model *is* the
  prior, and the prior is a monotonic transform of the old fixed-weight sum,
  so cold-start ordering is unchanged.
* **No label leakage.** The feedback feature of a training example is the
  Laplace-smoothed vote ratio of that document computed over its *other*
  votes (leave-one-out); otherwise the model would learn "a document's own
  vote predicts its own vote".

Relevance, recency and authority are the values logged when the vote was
cast (the features the user actually saw), not recomputed at training time.
"""

import math
from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.db.models import Feedback

FEATURES = ("relevance", "recency", "authority", "feedback")

# Hand-set starting point: what the ranker used before it could learn.
PRIOR_WEIGHTS = {"relevance": 0.5, "recency": 0.2, "authority": 0.15, "feedback": 0.15}
# Scales the prior into logit space: sigmoid(k * (sum(w_i x_i) - 0.5)) keeps the
# old weighted-sum ordering while spreading scores over a useful range.
PRIOR_SCALE = 6.0

MIN_EXAMPLES = 20
PRIOR_STRENGTH = 10.0  # how many votes' worth of evidence the prior is
LEARNING_RATE = 0.5
EPOCHS = 500


@dataclass
class RankingModel:
    weights: dict[str, float]
    bias: float
    trained: bool = False
    n_examples: int = 0
    metrics: dict[str, float] = field(default_factory=dict)

    def score(self, features: dict[str, float]) -> float:
        z = self.bias + sum(self.weights[f] * features[f] for f in FEATURES)
        return _sigmoid(z)


@dataclass
class Example:
    features: dict[str, float]
    label: int  # 1 = upvoted (relevant), 0 = downvoted


def prior_model() -> RankingModel:
    return RankingModel(
        weights={f: PRIOR_SCALE * PRIOR_WEIGHTS[f] for f in FEATURES},
        bias=-PRIOR_SCALE / 2,
    )


def laplace_ratio(positive: int, negative: int) -> float:
    return (positive + 1) / (positive + negative + 2)


def build_training_set(db: Session) -> list[Example]:
    rows = db.query(Feedback).filter(Feedback.relevance.isnot(None)).all()

    votes_per_doc: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # [positive, negative]
    for row in db.query(Feedback.doc_id, Feedback.vote).all():
        votes_per_doc[row.doc_id][0 if row.vote == 1 else 1] += 1

    examples = []
    for row in rows:
        positive, negative = votes_per_doc[row.doc_id]
        if row.vote == 1:
            positive -= 1
        else:
            negative -= 1
        examples.append(
            Example(
                features={
                    "relevance": row.relevance,
                    "recency": row.recency if row.recency is not None else 0.5,
                    "authority": row.authority if row.authority is not None else 0.5,
                    "feedback": laplace_ratio(positive, negative),
                },
                label=1 if row.vote == 1 else 0,
            )
        )
    return examples


def log_loss(model: RankingModel, examples: list[Example]) -> float:
    eps = 1e-12
    total = 0.0
    for ex in examples:
        p = min(max(model.score(ex.features), eps), 1 - eps)
        total -= ex.label * math.log(p) + (1 - ex.label) * math.log(1 - p)
    return total / len(examples)


def train(
    examples: list[Example],
    *,
    prior: RankingModel | None = None,
    prior_strength: float = PRIOR_STRENGTH,
    learning_rate: float = LEARNING_RATE,
    epochs: int = EPOCHS,
    min_examples: int = MIN_EXAMPLES,
) -> RankingModel:
    """Batch gradient descent on L2-regularised log-loss, anchored at the prior.

    Falls back to the prior when there is too little data, or when every vote
    has the same label (a single class says nothing about which features
    separate relevant from irrelevant results).
    """
    prior = prior or prior_model()
    labels = {ex.label for ex in examples}
    if len(examples) < min_examples or len(labels) < 2:
        return RankingModel(weights=dict(prior.weights), bias=prior.bias, n_examples=len(examples))

    weights = dict(prior.weights)
    bias = prior.bias
    n = len(examples)
    l2 = prior_strength / n
    for _ in range(epochs):
        grad_w = dict.fromkeys(FEATURES, 0.0)
        grad_b = 0.0
        for ex in examples:
            z = bias + sum(weights[f] * ex.features[f] for f in FEATURES)
            error = _sigmoid(z) - ex.label
            for f in FEATURES:
                grad_w[f] += error * ex.features[f]
            grad_b += error
        for f in FEATURES:
            gradient = grad_w[f] / n + l2 * (weights[f] - prior.weights[f])
            weights[f] -= learning_rate * gradient
        bias -= learning_rate * grad_b / n

    model = RankingModel(weights=weights, bias=bias, trained=True, n_examples=n)
    model.metrics = {
        "train_log_loss": log_loss(model, examples),
        "prior_log_loss": log_loss(prior, examples),
    }
    return model


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    exp_z = math.exp(z)
    return exp_z / (1 + exp_z)
