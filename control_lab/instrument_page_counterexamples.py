"""Exact integer algebra supplies truth; native probes supply measurements."""
import ast
import itertools
import math
from .core import score_content
from .instrument_math import page, pure_request, yes_no, weights, margin

PAGE = page('counterexamples', 'Counterexample foundry', 'Teach the instrument to find its own blind spots.',
    'Change the spelling of a calculation without changing its answer. Does the model still see the same thing?',
    'A restricted polynomial grammar, exact canonical algebra and native semantic probes share one graph. Search for equivalent expressions that move the observer, or distinct expressions that it fails to separate. Equivalent means all integers, not just the slider examples.',
    ['exact equivalence', 'semantic sensitivity', 'training pairs'],
    'Broaden the verified expression language, search beyond this finite bank, and evaluate discovered pairs on held-out models. Add a property before calling a feature collision a model error.')

EXPRESSIONS = ['x', '((x+1)-1)', '(x+0)', '(1*x)', '((x-x)+x)', '((2*x)-x)',
               '(x+1)', '(x-1)', '(x*x)', '(((x+1)*(x-1))+1)', '((x*x)+0)', '((x*x)+1)']
PROBES = ['Is this expression equal to x for every integer x?',
          'Is this expression nonnegative for every integer x?']


def canonical(source):
    """No eval, calls, attributes, division or powers. Degree <= 2 at each node."""
    if not isinstance(source, str) or len(source) > 512:
        raise ValueError('Use a small integer expression')
    try:
        tree = ast.parse(source, mode='eval')
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ValueError('Invalid expression') from exc
    if sum(1 for _ in ast.walk(tree)) > 64:
        raise ValueError('Expression is too large')

    def checked(values):
        if any(values[3:]) or any(abs(x) > 10**9 for x in values):
            raise ValueError('Degree or coefficient bound exceeded')
        return tuple((values + [0, 0, 0])[:3])

    def visit(node):
        if isinstance(node, ast.Name) and node.id == 'x':
            return (0, 1, 0)
        if isinstance(node, ast.Constant) and type(node.value) is int and abs(node.value) <= 1000:
            return (node.value, 0, 0)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return tuple(-v for v in visit(node.operand))
        if isinstance(node, ast.BinOp):
            a, b = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return checked([u+v for u, v in zip(a, b)])
            if isinstance(node.op, ast.Sub):
                return checked([u-v for u, v in zip(a, b)])
            if isinstance(node.op, ast.Mult):
                c = [0]*5
                for i in range(3):
                    for j in range(3):
                        c[i+j] += a[i]*b[j]
                return checked(c)
        raise ValueError('Only x, small integers, unary minus, +, - and * are supported')
    return visit(tree.body)


def evaluate(coefficients, x):
    c, b, a = coefficients
    return c + b*x + a*x*x


def nonnegative(coefficients):
    c, b, a = coefficients
    if a < 0:
        return False
    if a == 0:
        return b == 0 and c >= 0
    lower = (-b)//(2*a)
    return min(evaluate(coefficients, lower), evaluate(coefficients, lower+1)) >= 0


def truth(coefficients):
    return [tuple(coefficients) == (0, 1, 0), nonnegative(coefficients)]


def witness(a, b):
    if tuple(a) == tuple(b):
        return None
    # A nonzero degree-two polynomial has at most two distinct roots.
    for x in [0, -1, 1, -2, 2, -3, 3]:
        av, bv = evaluate(a, x), evaluate(b, x)
        if av != bv:
            return dict(x=x, left=av, right=bv)
    raise AssertionError('Distinct degree-two polynomials need a witness')


def binary_js(a, b):
    m = (a+b)/2
    def k(p, q):
        return sum(u*math.log(u/v) for u, v in [(p, q), (1-p, 1-q)] if u)
    return (k(a, m)+k(b, m))/2


def compare(a, b):
    same = a['coefficients'] == b['coefficients']
    return dict(left=a['id'], right=b['id'], equivalent=same,
                same_probe_truth=a['truth'] == b['truth'],
                margin_distance=math.sqrt(sum((x-y)**2 for x,y in zip(a['z'], b['z']))),
                mean_binary_js_nats=sum(binary_js(x,y) for x,y in zip(a['p_yes'],b['p_yes']))/2,
                delta=[y-x for x,y in zip(a['z'],b['z'])],
                witness=witness(a['coefficients'], b['coefficients']))


async def run(ctx, opt):
    nodes = []
    for i, expression in enumerate(EXPRESSIONS):
        coefficients = canonical(expression)
        rows = [await yes_no(ctx, 'Expression: '+expression+'\nUse exact integer arithmetic, with x any integer.',
                             question, 'Probe E'+str(i)+': '+('identity' if j == 0 else 'nonnegative'))
                for j, question in enumerate(PROBES)]
        nodes.append(dict(id=i, expression=expression, coefficients=coefficients, truth=truth(coefficients),
                          measurements=rows, p_yes=[weights(r)[0] for r in rows], z=[margin(r) for r in rows]))
    pairs = [compare(a,b) for a,b in itertools.combinations(nodes,2)]
    equivalent = sorted([p for p in pairs if p['equivalent']], key=lambda p:-p['margin_distance'])
    distinct = sorted([p for p in pairs if not p['equivalent'] and not p['same_probe_truth']],
                      key=lambda p:p['margin_distance'])
    collision = sorted([p for p in pairs if not p['equivalent'] and p['same_probe_truth']],
                       key=lambda p:p['margin_distance'])
    body = pure_request('Choose an expression whose meaning is worth checking. Return only the expression.', EXPRESSIONS, 64)
    generated = score_content(await ctx.call('Native GBNF chooses a verified-language expression',body))
    if generated['text'] not in EXPRESSIONS or generated['finish_reason'] != 'stop':
        raise ValueError('Native expression must finish inside the finite grammar bank')
    edges = [dict(left=a, right=b, **{'operation': op}, equivalent=nodes[a]['coefficients']==nodes[b]['coefficients'])
             for a,b,op in [(0,1,'add and subtract one'),(0,2,'add zero'),(0,3,'multiply by one'),
                            (0,4,'insert cancelling x'),(0,5,'double then subtract x'),(0,6,'add one'),
                            (0,7,'subtract one'),(8,9,'factor then restore one'),(8,10,'add zero'),
                            (8,11,'add one'),(0,8,'square')]]
    return dict(nodes=nodes, pairs=pairs, edges=edges, probes=PROBES,
                rankings=dict(equivalent=equivalent, distinct=distinct, collision=collision),
                generated=dict(expression=generated['text'], coefficients=canonical(generated['text']),
                               grammar=body['grammar'], native=generated),
                training_pairs=[dict(left=p['left'], right=p['right'], relation='exactly equivalent',
                                     measurement_delta=p['delta']) for p in equivalent],
                semantics='Canonical coefficients prove equivalence for all integers. Mean binary JS averages two separate marginal comparisons; it is not a joint divergence. A feature collision can be expected information loss: two correct yes/no properties need not identify the whole expression. No probability is assumed calibrated.')
