class FactorEvaluationReport:
  def __init__(self, evaluators):
    self.evaluators = evaluators

  def run(self, factor_values, forward_returns):
    report = {}
    for evaluator in self.evaluators:
      report[evaluator.__class__.__name__] = evaluator.evaluate(
        factor_values,
        forward_returns,
      )
    return report
