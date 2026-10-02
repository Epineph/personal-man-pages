# Z-score demonstration

<!-- pman:section purpose views=brief,long,detailed -->
## Purpose

`examples/zscore.py` centers and scales a list of numbers. This demonstrates a
Python script whose practical help is separate from its mathematical theory.
Standardization alone does not test a hypothesis or make data normally distributed.

<!-- pman:section usage views=brief,long,detailed -->
## Usage

```bash
python3 examples/zscore.py [--ddof {0,1}] [--digits N] VALUES...
```

`--ddof 1` is the default. Use `--ddof 0` to scale with the denominator equal
to the number of observations. Extended views are `--long-help`,
`--detailed-help`, `--technical-help`, `--list-examples` and `--all`.
Place an extended-help flag first, before any other arguments.

<!-- pman:section practical views=long,detailed -->
## Practical use

Each input value produces one output line. The output is dimensionless because
the numerator and scale have the same units. Display precision defaults to six
decimal places. `--digits` affects printing, not the calculation.

The script accepts finite numbers only. Constant input cannot be standardized
because its scale is zero. At least two values are needed with `--ddof 1`.

For actual analyses, choose the centering and scaling population deliberately.
This demonstration has no grouping, missing-value handling, fitting step or
train/test split. Those decisions belong in the analysis pipeline.

<!-- pman:section examples views=long,detailed,examples -->
## Examples

Sample-denominator standardization:

```bash
python3 examples/zscore.py 2 4 6
# -1.000000
#  0.000000
#  1.000000
```

Population-denominator standardization:

```bash
python3 examples/zscore.py --ddof 0 --digits 3 2 4 6
# -1.225
#  0.000
#  1.225
```

Read only the mathematical explanation:

```bash
python3 examples/zscore.py --technical-help --paging never
```

Save a PDF for study, or serve the HTML version locally:

```bash
pman zscore --technical-help --save-only zscore.pdf --save-log zscore.log
pman zscore --technical-help --save zscore.html --serve --open-browser
```

<!-- pman:section precision views=detailed -->
## Numerical limitations and exit status

Status 0 means success. Invalid numerical inputs or arguments return status 2.
The implementation first divides values by their maximum absolute magnitude to
reduce overflow risk. It uses `math.fsum` for summation. Very small differences
relative to magnitude can still be lost at floating-point precision.

The variance of the output, using the selected denominator, is approximately
one before display rounding. The sum of the output is approximately zero.

<!-- pman:section theory views=technical -->
## Definition and denominator

For $n$ observations $x_1,\ldots,x_n$, define the mean and scale by

$$
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i,
\qquad
s_d=\sqrt{\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-d}},
\qquad
z_i=\frac{x_i-\bar{x}}{s_d}.
$$

Here $d$ is `--ddof`, with $d\in\{0,1\}$ and $n>d$. When $d=1$, the variance
uses the familiar sample denominator $n-1$. When $d=0$, it uses $n$.

For independent, identically distributed observations with finite variance,
the $n-1$ correction makes the sample **variance** unbiased for the population
variance. The sample standard deviation obtained by taking its square root is
not generally unbiased. Neither formula removes dependence between observations.

<!-- pman:section worked-example views=technical -->
## Worked example

Let $x=(2,4,6)$, so $n=3$:

$$
\bar{x}=\frac{2+4+6}{3}=\frac{12}{3}=4.
$$

The centered values are $(-2,0,2)$, giving

$$
\sum_{i=1}^{3}(x_i-\bar{x})^2=(-2)^2+0^2+2^2=4+0+4=8.
$$

With $d=1$:

$$
s_1^2=\frac{8}{3-1}=4,
\qquad s_1=2,
\qquad z=\left(\frac{-2}{2},\frac{0}{2},\frac{2}{2}\right)=(-1,0,1).
$$

With $d=0$:

$$
s_0^2=\frac{8}{3},
\qquad s_0=\sqrt{\frac{8}{3}}\approx1.632993,
\qquad z\approx(-1.224745,0,1.224745).
$$

Both transformations are linear rescalings of the same data. Neither changes
the distribution's shape into a Gaussian distribution.
