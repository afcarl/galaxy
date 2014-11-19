import json
from itertools import permutations

from core.vectorize import train
from core import concepts
from eval import evaluate, test

import click as c
import numpy as np
from sklearn.grid_search import ParameterGrid

# Suppress floating point errors.
np.seterr(all='ignore')

approaches = {
    'hac': ParameterGrid({
        'metric': ['cosine'],
        'linkage_method': ['average'],
        'threshold': np.arange(0.1, 0.25, 0.05),
        'weights': list( permutations(np.arange(1., 82., 20.), 3) )
    }),
    #'ihac': ParameterGrid({
        #'metric': ['cosine'],
        #'threshold': np.arange(40., 100., 10.),
        #'weights': list( permutations(np.arange(21., 102., 20.), 3) ),
        #'lower_limit_scale': np.arange(0.1, 1.1, 0.1),
        #'upper_limit_scale': np.arange(1.1, 2.0, 0.05)
    #}),
    #'ihac': ParameterGrid({
        #'metric': ['euclidean'],
        #'threshold': np.arange(40., 100., 10.),
        #'weights': [(21., 81., 41.)],
        #'lower_limit_scale': [0.8],
        #'upper_limit_scale': [1.15]
    #}),
    'ihac': ParameterGrid({
        'metric': ['euclidean'],
        'threshold': np.arange(40., 100., 10.),
        'weights': list( permutations(np.arange(1., 82., 10.), 3) ),
        'lower_limit_scale': np.arange(0.6, 0.9, 0.2),
        'upper_limit_scale': np.arange(1.1, 1.6, 0.1)
    }),
    'digbc': ParameterGrid({
        'threshold': np.arange(0.00295, 0.0100, 0.00005)
    })
}

params = {
    'ihac': {
        'metric': 'euclidean',
        'threshold': 60.,
        'weights': (21., 81., 41.),
        'lower_limit_scale': 0.8,
        'upper_limit_scale': 1.15
    }
}

datapath_type = c.Path(exists=True, dir_okay=False)
approach_type = c.Choice(['hac', 'ihac', 'digbc'])

@c.group()
def run():
    pass


@run.command()
@c.argument('datapath', type=datapath_type)
def train(datapath):
    """
    Train the feature pipelines.
    """
    training_file = open(datapath, 'r')
    training_data = json.load(training_file)

    docs = ['{0} {1}'.format(d['title'], d['text']) for d in training_data]
    train(docs)
    concepts.train(docs)


@run.command()
@c.argument('approach', type=approach_type)
@c.argument('datapath', type=datapath_type)
@c.option('--incremental', is_flag=True, help='Randomly order the input data.')
def eval(approach, datapath, incremental):
    """
    Eval a clustering approach on labeled data.
    """
    param_grid = approaches[approach] if not incremental else params[approach]
    report_path = evaluate(datapath,
                           approach=approach,
                           param_grid=param_grid,
                           incremental=incremental)
    c.echo('Report compiled at {0}.'.format(report_path))


@run.command()
@c.argument('approach', type=approach_type)
@c.argument('datapath', type=datapath_type)
def cluster(approach, datapath):
    """
    Run a clustering approach on unlabeled data.
    """
    report_path = test(datapath, approach, params[approach])
    c.echo('Report compiled at {0}.'.format(report_path))


if __name__ == '__main__':
    run()
