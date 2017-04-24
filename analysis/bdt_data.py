from k3pi_config.modes import gcm, opposite_mode
from analysis import add_variables, selection
import numpy as np
from hep_ml.commonutils import train_test_split
from k3pi_config import config
from k3pi_utilities import logger

log = logger.get_logger('bdt_data')


def prep_data_for_sklearn(**kwargs):
    if kwargs.get('comb_data', False):
        features = [f.functor(f.particle) for f in gcm().comb_bkg_bdt_vars]
    else:
        features = [f.functor(f.particle) for f in gcm().rand_spi_bdt_vars]
    spectators = [f.functor(f.particle) for f in gcm().spectator_vars]

    kwargs.update({'sklearn': True})
    data = get_bdt_data(**kwargs)

    train, test = train_test_split(data, random_state=43)
    return (train, test, train['labels'].astype(np.bool),
            test['labels'].astype(np.bool)), features, spectators


def just_the_labels(sw=False, comb_data=False):
    data = get_bdt_data(sw=sw, sklearn=True, comb_data=comb_data)

    train, test = train_test_split(data, random_state=43)
    return train[['labels', 'weights']], test[['labels', 'weights']]


def get_bdt_data(sw=False, sklearn=True, same_weight=False, comb_data=False,
                 plot=False):
    """Returns the data for the bdt training, containing all the necessary
    variables and weights.

    :sw: Use sweights instead of sidebands and signal region
    :sklearn: return sklearn compatible dataframe
    :same_weight: Changes the weights to have identical normalisation
    :comb_data: Return BDT for comb_data, rand slow pion otherwise
    :returns: if sklearn is True:  DataFrame
              if sklearn is False: sig_df, bkg_df, sig_wgt, bkg_wgt
    """
    if comb_data:
        log.info('Doing returning data for combinatorial background')
        bdt_vars = gcm().comb_bkg_bdt_vars[:]
        bkg_sel = selection.comb_bkg_sideband_region()
    else:
        log.info('Doing returning data for random slow pion background')
        bdt_vars = gcm().rand_spi_bdt_vars[:]
        bkg_sel = selection.rand_spi_sideband_region()
    bdt_vars += gcm().spectator_vars
    # Only add the variables for plotting if needed
    if plot:
        bdt_vars += gcm().just_plot

    df = gcm().get_data(
        [v.var for v in bdt_vars if v.functor.additional is False])
    add_variables.append_angle(df)
    sel = selection.full_selection()
    add_variables.append_phsp(df)
    add_variables.append_dtf_ip_diff(df)

    for f in bdt_vars:
        if f.convert is not None:
            df[f.var] = f.convert(df[f.var])

    if sw:
        from analysis.mass_fitting import get_sweights
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
        df.loc[bkg_sel & sel, 'labels'] = 0

    if config.add_wrongsign and gcm().mode not in config.wrong_sign_modes:
        with opposite_mode():
            df_op = get_bdt_data(sw, sklearn=True)
        df = df.append(df_op.query('labels == 0'), ignore_index=True)

    tot0 = np.sum(df.query('labels == 0').weights)
    # Reduce the statistics of the signal to no more than 10 times the
    # background
    tot1 = np.sum(df.query('labels == 1').weights)
    if 5.*tot0 < tot1:
        sig_sel = df['labels'] == 1
        bkg_sel = df['labels'] == 0
        tot1_max = 5*tot0
        log.info('Changing signal events {} ---> {}'.format(tot1, tot1_max))

        sel = df.index.isin(df.query('labels==1').sample(
            int(tot1_max), random_state=45).index)
        df.loc[sig_sel & sel, 'keep'] = 1
        df.loc[bkg_sel, 'keep'] = 1
        log.info('DataFrame content before: {}'.format(df.index.size))
        if same_weight:
            # Weight the label 1 sample to have same total than label 0
            df.loc[df['labels'] == 1, 'weights'] = float(tot0)/tot1_max
        df = df.loc[~np.isnan(df['labels']) & ~np.isnan(df['keep'])]
        log.info('DataFrame content after: {}'.format(df.index.size))
    else:
        tot1_max = tot1
        if same_weight:
            # Weight the label 1 sample to have same total than label 0
            df.loc[df['labels'] == 1, 'weights'] = float(tot0)/tot1_max
        df = df.loc[~np.isnan(df['labels'])]

    if sklearn:
        return df

    return (df.query('labels == 1'),
            df.query('labels == 0'),
            df.query('labels == 1').weights,
            df.query('labels == 0').weights)
