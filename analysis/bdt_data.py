from k3pi_config.modes import gcm
from analysis.mass_fitting import get_sweights
from analysis import add_variables, selection, extended_selection
import numpy as np
from hep_ml.commonutils import train_test_split


def prep_data_for_sklearn(sw=False):
    features = [f.functor(f.particle) for f in gcm().bdt_vars]
    spectators = [f.functor(f.particle) for f in gcm().spectator_vars]

    data = get_bdt_data(sklearn=True)

    train, test = train_test_split(data, random_state=43)
    return (train, test, train['labels'].astype(np.bool),
            test['labels'].astype(np.bool)), features, spectators


def get_bdt_data(sw=False, sklearn=True):
    """Returns the data for the bdt training, containing all the necessary
    variables and weights.

    :sw: Use sweights instead of sidebands and signal region
    :sklearn: return sklearn compatible dataframe
    :returns: if sklearn is True:  DataFrame
              if sklearn is False: sig_df, bkg_df, sig_wgt, bkg_wgt
    """
    bdt_vars = gcm().bdt_vars + gcm().spectator_vars + gcm().just_plot
    df = gcm().get_data([v.var for v in bdt_vars])
    add_variables.append_angle(df)
    sel = extended_selection.get_complete_selection()
    add_variables.append_phsp(df)
    add_variables.append_dtf_ip_diff(df)

    for f in gcm().bdt_vars:
        if f.convert is not None:
            df[f.var] = f.convert(df[f.var])

    if sw:
        sweights = get_sweights(gcm())

        np.random.seed(42)
        df['labels'] = (np.random.rand(df.index.size) < 0.5).astype(np.int)
        sweights['bkg'] = sweights.rnd + sweights.comb
        df['weights'] = (df['labels'] == 1)*sweights.sig
        df['weights'] += (df['labels'] == 0)*(sweights['rnd'] + sweights['comb'])  # NOQA

        # Weights are only present for those rows that are selected,
        # so we select
        df = df.loc[~np.isnan(df['weights'])]
    else:
        df['weights'] = np.ones(df.index.size)
        df.loc[selection.mass_signal_region() & sel, 'labels'] = 1
        df.loc[selection.mass_sideband_region() & sel, 'labels'] = 0

        df = df.loc[~np.isnan(df['labels'])]

    if sklearn:
        return df

    return (df.query('labels == 1'),
            df.query('labels == 0'),
            df.query('labels == 1').weights,
            df.query('labels == 0').weights)
