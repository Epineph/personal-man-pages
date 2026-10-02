#!/usr/bin/env python3
"""A complete numerical example with separate mathematical documentation."""

from pathlib import Path
import argparse
import math
import sys

example_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(example_root / "integrations"))
from pman_help import show_requested_help


# ----- Numerical calculation ---------------------------------------------------

def standardize(values: list[float], ddof: int) -> list[float]:
  """Center and scale finite values; ddof selects the variance denominator."""
  if len(values) <= ddof:
    raise ValueError("The number of values must exceed ddof.")
  if not all(math.isfinite(value) for value in values):
    raise ValueError("All values must be finite numbers.")
  # Scale before summation to avoid overflow for large finite inputs.
  magnitude = max(abs(value) for value in values)
  if magnitude == 0:
    raise ValueError("Constant input has zero variance; z-scores are undefined.")
  scaled = [value / magnitude for value in values]
  mean = math.fsum(scaled) / len(scaled)
  deviations = [value - mean for value in scaled]
  variance = math.fsum(delta * delta for delta in deviations)
  variance /= len(values) - ddof
  if variance == 0:
    raise ValueError("Input has zero variance at floating-point precision.")
  scale = math.sqrt(variance)
  return [delta / scale for delta in deviations]


# ----- Help routing and ordinary execution ------------------------------------

def main(arguments: list[str] | None = None) -> int:
  argv = list(sys.argv[1:] if arguments is None else arguments)
  status = show_requested_help(
    "demo.zscore", argv, allow_all=True, viewer=example_root / "bin" / "pman"
  )
  if status is not None:
    return status
  parser = argparse.ArgumentParser(
    description=(
      "Center and scale numbers; this is not a hypothesis test."
    ),
    epilog=(
      "More help: --long-help, --detailed-help, --technical-help, "
      "--list-examples, --all. Put an extended-help flag first. "
      "Append --save FILE.md, FILE.html or FILE.pdf to export that help."
    ),
    allow_abbrev=False,
  )
  parser.add_argument("values", type=float, nargs="+")
  parser.add_argument("--ddof", type=int, choices=(0, 1), default=1)
  parser.add_argument("--digits", type=int, default=6)
  args = parser.parse_args(argv)
  if not 0 <= args.digits <= 15:
    parser.error("--digits must be between 0 and 15")
  try:
    scores = standardize(args.values, args.ddof)
  except ValueError as exc:
    parser.error(str(exc))
  for score in scores:
    print(f"{score:.{args.digits}f}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
