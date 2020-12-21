import random
import pysmt
from pysmt.shortcuts import Symbol, LE, GE, Int, GT, LT, And, Equals, Plus, Solver, is_sat, Or, Not, Minus, Ite, Implies, is_unsat, get_model, Times
from pysmt.typing import INT, STRING, BOOL, REAL
from sklearn import svm
import matplotlib.pyplot as plt
import numpy as np


###
# Settings
###
SETTINGS = {
    'POINTS': {
        'GENERATE': {
            'START': 80,
            'ZONE': 100
        },
        'X': {
            'START': -10,
            'END': 10
        },
        'Y': {
            'START': -10,
            'END': 10
        },
        'MARGIN_MULTIPLIER': 10
    }
}


###
# Helper functions
###
def mirror_point( a, b, c, x1, y1): 
    temp = -2 * (a * x1 + b * y1 + c) /(a * a + b * b) 
    x = temp * a + x1 
    y = temp * b + y1  
    return (x, y) 


def plot_sp(SP, clf=None):
    # draw a plot of the data; helps visualizing what is happening
    POSITIVE = np.array(SP['POSITIVE'])
    NEGATIVE = np.array(SP['NEGATIVE'])
    NP = np.array(SP['NP'])
    plt.scatter([17], [0], s=60, c=[9])
    plt.scatter(NP[:, 0], NP[:, 1], s=30)
    plt.scatter(NEGATIVE[:, 0], NEGATIVE[:, 1], s=30)
    plt.scatter(POSITIVE[:, 0], POSITIVE[:, 1], s=30)
    # plot the` decision function
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    # plot margin if clf exists
    if clf is not None:
        # create grid to evaluate model
        xx = np.linspace(xlim[0], xlim[1], 30)
        yy = np.linspace(ylim[0], ylim[1], 30)
        YY, XX = np.meshgrid(yy, xx)
        xy = np.vstack([XX.ravel(), YY.ravel()]).T
        Z = clf.decision_function(xy).reshape(XX.shape)
        # plot decision boundary and margins
        ax.contour(XX, YY, Z, colors='k', levels=[-1, 0, 1], alpha=0.5,
                    linestyles=['--', '-', '--'])
        # plot support vectors
        ax.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s=100,
                    linewidth=1, facecolors='none', edgecolors='k')
        # my special line
        # plt.plot([0, -clf.intercept_ / clf.coef_[0][0]], [-clf.intercept_ / clf.coef_[0][1], 0])
    plt.show()


def get_var(name, index=None):
    if index is None:
        return Symbol(name, INT)
    return Symbol(name + str(index), INT)


def get_variables_from_formula(formula, index='lowest'):
    assert index == 'lowest' or index == 'highest'
    variables = get_model(formula).__iter__()
    values = {}
    for variable in variables:
        name = variable[0].serialize()
        key = name[0]
        height = int(name[1:])
        value = int(variable[1].serialize())
        if index == 'lowest' and key in values.keys() and values[key]['height'] < height:
            continue
        if index == 'highest' and key in values.keys() and values[key]['height'] > height:
            continue
        values[key] = {
            'value': value,
            'height': height
        }
    variables = {}
    for key, value in values.items():
        variables[key] = value['value']
    return variables


def find_points_from_formula(formula, n_points=20):
    points = []
    while (len(points) < n_points):
        print(get_model(formula))
        raise Exception()
    return points


###
# Example programs from the paper
###
code_1 = {
    'pre': LT(get_var('x', 1), get_var('y', 1)),
    'cond': LT(get_var('x', 1), get_var('y', 1)),
    'body': And(
        Ite(
            LT(get_var('x', 1), Int(0)),
            Equals(
                get_var('x', 2),
                Plus(get_var('x', 1), Int(7))
            ),
            Equals(
                get_var('x', 2),
                Plus(get_var('x', 1), Int(10))
            )
        ),
        Ite(
            LT(get_var('y', 1), Int(0)),
            Equals(
                get_var('y', 2),
                Minus(get_var('y', 1), Int(10))
            ),
            Equals(
                get_var('y', 2),
                Plus(get_var('y', 1), Int(3))
            ),
        )
    ),
    # 'paths': [
    #     x < y + 5,
    #     y > 0,
    #     x == 0
    # ],
    'post': And(
        LE(get_var('y', 2), get_var('x', 2)),
        LE(get_var('x', 2), Plus(get_var('y', 2), Int(16)))
    ),
    'map': {
        'x': {
            'pre': 1,
            'body': 2
        },
        'y': {
            'pre': 1,
            'body': 2
        }
    }
}

code_2 = {
    'pre': Or(
        GT(get_var('x', 1), Int(0)), 
        GT(get_var('y', 1), Int(0))
    ),
    'cond': LE(
        Plus(get_var('x', 1), get_var('y', 1)), 
        Int(-2)
    ),
    'body': Ite(
        GT(get_var('x', 1), Int(0)),
        And(
            Equals(get_var('x', 2), Plus(get_var('x', 1), Int(1))),
            Equals(get_var('y', 2), get_var('y', 1))
        ),
        And(
            Equals(get_var('y', 2), Plus(get_var('y', 1), Int(1))),
            Equals(get_var('x', 2), get_var('x', 1))
        )
    ),
    'post': Or(
        GT(get_var('x', 2), Int(0)), 
        GT(get_var('y', 2), Int(0))
    ),
    'map': {
        'x': {
            'pre': 1,
            'body': 2
        },
        'y': {
            'pre': 1,
            'body': 2
        }
    }
}

code_3 = {
    'pre': And(
        Equals(get_var('x', 1), Int(1)), 
        Equals(get_var('y', 1), Int(0))
    ),
    'cond': LT(get_var('x', 1), Int(3)),  # while(*)
    'body': And(
        Equals(get_var('x', 2), Plus(get_var('x', 1), get_var('y', 1))),
        Equals(get_var('y', 2), Plus(get_var('y', 1), Int(1)))
    ),
    'post': GE(get_var('x', 2), get_var('y', 2)),
    'map': {
        'x': {
            'pre': 1,
            'body': 2,
        },
        'y': {
            'pre': 1,
            'body': 2,
        }
    }
}

code_4 = {
    'pre': LT(get_var('x', 1), Int(0)),
    'cond': LT(get_var('x', 1), Int(0)),
    'body': And(
        Equals(
            get_var('x', 2),
            Plus(get_var('x', 1), get_var('y', 1))
        ),
        Equals(
            get_var('y', 2),
            Plus(get_var('y', 1), Int(1))
        )
    ),
    'post': GT(get_var('y', 2), Int(0)),
    'map': {
        'x': {
            'pre': 1,
            'body': 2
        },
        'y': {
            'pre': 1,
            'body': 2
        }
    }
}

###
# Invariant check
###
def get_substitution(code, place='body', replace_index=False):
    substitution = {}
    for key in code['map'].keys():
        index = code['map'][key]['pre'] if replace_index else None
        if place == 'body':
            substitution[get_var(key, index)] = get_var(
                key, code['map'][key]['body'])
        elif place == 'pre':
            substitution[get_var(key, index)] = get_var(
                key, code['map'][key]['pre'])
        else:
            raise Exception("Place needs to be 'body' or 'pre'.")
    return substitution


def is_invariant_correct(code, invariant):
    # test (4)
    # pre ∧ ¬invariant
    formula = And(
        code['pre'],
        Not(invariant.substitute(get_substitution(code, 'pre')))
    )
    if is_sat(formula):
        return (False, get_variables_from_formula(formula))

    # test (5)
    # sp(invariant ∧ cond, body) ∧ ¬invariant
    sp = And(
        code['cond'],
        code['body'],
        invariant.substitute(get_substitution(code, 'pre'))
    )
    formula = And(
        sp,
        Not(invariant.substitute(get_substitution(code, 'body')))
    )
    if is_sat(formula):
        return (False, get_variables_from_formula(formula))

    # test (6)
    # invariant ∧ ¬cond ∧ ¬post
    formula = And(
        invariant.substitute(get_substitution(code, 'body')),
        Not(code['cond'].substitute(get_substitution(code, 'body', True))),
        Not(code['post'])
    )
    if is_sat(formula):
        return (False, get_variables_from_formula(formula))

    return (True, )


def evaluate(code, variables):
    # s := variables
    numbers = And()
    for key, item in variables.items():
        numbers = And(numbers, Equals(get_var(key), Int(item)))

    # s ∈ pre
    formula = And(
        code['pre'],
        numbers.substitute(get_substitution(code, 'pre'))
    )
    pre = is_sat(formula)

    # s ⇒ s'
    # return all s and s'
    def body(variables):
        variables_list = [variables]

        numbers = And()
        for key, item in variables.items():
            numbers = And(numbers, Equals(get_var(key), Int(item)))

        cond = And(
            code['cond'],
            numbers.substitute(get_substitution(code, 'pre'))
        )
        if is_sat(cond):
            formula = And(
                code['body'],
                numbers.substitute(get_substitution(code, 'pre'))
            )
            variables = get_variables_from_formula(formula, 'highest')
            variables_list += body(variables)

        return variables_list

    # s' := last point in variables list
    variables_list = body(variables)
    numbers = And()
    for key, item in variables_list[-1].items():
        numbers = And(numbers, Equals(get_var(key), Int(item)))

    # s' ∈ cond
    formula = And(
        code['cond'],
        numbers.substitute(get_substitution(code, 'pre'))
    )
    cond = is_sat(formula)

    # s' ∈ post
    formula = And(
        code['post'],
        numbers.substitute(get_substitution(code, 'body'))
    )
    post = is_sat(formula)

    # evaluate
    if pre and not cond and not post:
        # CE = { s ∈ SP | s ∈ Pre ∧ s ⇒ s' ∧ s' !∈ Cond ∧ s' !∈ Post }
        evaluation = 'CE' 
    elif pre and not cond and post:
        # POSITIVE = { s ∈ SP | s ∈ Pre ∧ s ⇒ s' ∧ s' !∈ Cond ∧ s' ∈ Post }
        evaluation = 'POSITIVE'
    elif not pre and not cond and not post:
        # NEGATIVE = { s ∈ SP | s !∈ Pre ∧ s ⇒ s' ∧ s' !∈ Cond ∧ s' !∈ Post }
        evaluation = 'NEGATIVE'
    else:
        # NP = SP - CE - POSITIVE - NEGATIVE
        evaluation = 'NP'
    return (evaluation, variables_list)


###
# Verify function
# Finds correct invariants
###
def verify(code):
    SP = {}
    SP['CE'], SP['NEGATIVE'], SP['NP'], SP['POSITIVE'], SP['UNKNOWN'] = (
        [], [], [], [], [(1, 0)]
    )

    # generate points
    for _ in range(0, SETTINGS['POINTS']['GENERATE']['START']):
        x = random.randint(SETTINGS['POINTS']['X']['START'],
                           SETTINGS['POINTS']['X']['END'])
        y = random.randint(SETTINGS['POINTS']['Y']['START'],
                           SETTINGS['POINTS']['Y']['END'])
        point = (x, y)
        SP['UNKNOWN'].append(point)

    # find an invariant
    while True:
        # evaluate points
        for point in SP['UNKNOWN']:
            evaluation = evaluate(code, {'x': point[0], 'y': point[1]})
            SP[evaluation[0]] += list(map(lambda point: (point['x'], point['y']), evaluation[1]))
        SP['UNKNOWN'] = []

        # get a possible invariant
        invariant = find_conjunctive_invariant(SP)
        if not invariant[0]:
            return 'DISPROVED'

        # check if the invariant is actually correct
        correct = is_invariant_correct(code, invariant[1])
        
        if correct[0]:
            return invariant[1]
        else:
            print('####################')
            print('point', correct[1])
            print('####################')
        
        # add points to sp
        # point with which the invariant failed, this line actually does not have a big impact
        SP['UNKNOWN'].append((correct[1]['x'], correct[1]['y']))
        # points which are in the margin zone of the support vector machine
        SP['UNKNOWN'] += invariant[2]


def find_conjunctive_invariant(SP):
    # safety check
    if len(SP['CE']) != 0:
        return (False,)

    print('POSITIVE', '(green) ', len(SP['POSITIVE']))
    print('NEGATIVE', '(orange)', len(SP['NEGATIVE']))
    print('NP      ', '(blue)  ', len(SP['NP']))
    plot_sp(SP)

    complete_invariant = And()
    NEGATIVE = np.array(SP['NEGATIVE'])
    hesse_normal_forms = []

    while(len(NEGATIVE) != 0):

        # shape the data for the support vector machine
        x = SP['POSITIVE'] + [NEGATIVE[random.randint(0, len(NEGATIVE) - 1)]]
        y = len(SP['POSITIVE']) * [1] + [0]
        x = np.array(x)
        y = np.array(y)
        clf = svm.SVC(kernel='linear')
        clf.fit(x, y)

        # calculate the seperating line
        print(clf.coef_)
        print(clf.intercept_)

        hesse_normal_forms.append((clf.coef_[0], clf.intercept_[0]))
        ax = int(round(clf.coef_[0][0] * 10))
        ay = int(round(clf.coef_[0][1] * 10))
        b = int(round(clf.intercept_[0] * 10))
        invariant = GT(
            Plus(
                Times(Int(ax), get_var('x')),
                Times(Int(ay), get_var('y')), 
                Int(b)
            ), 
            Int(0)
        )

        # W = clf.coef_[0]
        # I = clf.intercept_
        # print(W[0], W[1])
        # try:
        #     a = int(round(-W[0] / W[1]))
        # except OverflowError:
        #     a = 999999999999999999
        #     print('OVERFLOW A')
        # try:
        #     b = int(round(I[0] / W[1]))
        # except OverflowError:
        #     b = 999999999999999999
        #     print('OVERFLOW B')
        # def line(x): return a * x - b
        # lines.append(line)

        # margin calculation
        # margin = int(round(1 / np.linalg.norm(clf.coef_)) *
        #             SETTINGS['POINTS']['MARGIN_MULTIPLIER'])

        # check wheter <= or >= is correct
        # left: a * x - b
        # left = Minus(Times(Int(a), Symbol('x', INT)), Int(b))
        # right: y
        # right = Symbol('y', INT)
        # if clf.predict([(1, line(1) - 1)]) == 0:
        #     invariant = LT(left, right)
        # else:
        #     invariant = GT(left, right)
        # invariant: a * x - b < y
        # print(invariant, '\n')

        # remove successfully classified from negative
        prediction = clf.predict(NEGATIVE)
        # print(NEGATIVE[0])
        # print(NEGATIVE)
        # print(prediction)
        plot_sp(SP, clf)
        NEGATIVE = NEGATIVE[prediction > 0]
        complete_invariant = And(complete_invariant, invariant)

    invariant = complete_invariant
    print(invariant.serialize(), '\n')
    # generate points in the seperation zone
    points = []
    # for _ in range(0, SETTINGS['POINTS']['GENERATE']['ZONE']):
    #     xp = random.randint(SETTINGS['POINTS']['X']['START'],
    #                         SETTINGS['POINTS']['Y']['END'])
    #     yp = lines[random.randint(0, len(lines) - 1)](xp) + random.randint(-margin, margin)
    #     points.append((xp, yp))
    # print(points)

    # plot
    # plot_svm(SP, clf)

    # return found invariant and points in the seperation zone
    return (True, invariant, points)


def find_disjunctive_invariant(SP):
    pass


###
# Test code
###

# correct_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(16)))
# incorrect_invariant = LE(Symbol('x', INT), Plus(Symbol('y', INT), Int(9)))
# print(is_invariant_correct(code_1, incorrect_invariant))

# print(verify(code_1))
# print(evaluate(code_2, {'x': 0, 'y': -1}))

# SP = {}
# SP['UNKNOWN'] = []
# for _ in range(0, SETTINGS['POINTS']['GENERATE']['START']):
#     x = random.randint(SETTINGS['POINTS']['X']['START'],
#                        SETTINGS['POINTS']['X']['END'])
#     y = random.randint(SETTINGS['POINTS']['Y']['START'],
#                        SETTINGS['POINTS']['Y']['END'])
#     point = (x, y)
#     SP['UNKNOWN'].append(point)

# print(evaluate(code_1, {'x': -18, 'y': 24}))
# left = Minus(Times(Int(1), Symbol('x', INT)), Int(18))
# right = Symbol('y', INT)
# formula = LE(left, right)
# find_points_from_formula(formula)
