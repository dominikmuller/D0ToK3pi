import tempfile
from k3pi_utilities import helpers


WS_DMASS_NAME = 'dmass_var'
WS_MASS_NAME = 'mass_var'


def get_delta_mass_var(workspace):
    """Return the RooRealVar of the fitted delta mass variable."""
    return workspace.var(workspace.obj(WS_DMASS_NAME).GetName())


def get_mass_var(workspace):
    """Return the RooRealVar of the fitted delta mass variable."""
    return workspace.var(workspace.obj(WS_MASS_NAME).GetName())


def workspace_import(workspace, obj, name='', cmdargs=None):
    import ROOT
    """Import object obj in to the RooWorkspace.
    Import as normal if name is given, else use hack to fix ROOT 6 bug.
    https://sft.its.cern.ch/jira/browse/ROOT-6785
    Keyword arguments:
    workspace -- RooWorkspace to import obj into
    obj -- Object to import in to the workspace
    name -- Optional name to give the object (default: None)
    cmdargs -- Optional list of RooCmdArg objects to forward (default: [])
    """
    if not cmdargs:
        cmdargs = []
    if name:
        getattr(workspace, 'import')(obj, name, *cmdargs)
    else:
        getattr(workspace, 'import')(obj, ROOT.RooCmdArg(), *cmdargs)


def pandas_to_roodataset(df, st, dataname='roofit_ds'):
    import ROOT
    import ROOT.RooFit as RF
    import root_pandas  # NOQA, actually need this for to_root function.
    tmpfile = tempfile.mktemp()+'.root'
    treename = 'default'
    df.index = df.index.astype('int32')
    df.to_root(tmpfile)
    f = ROOT.TFile.Open(tmpfile)
    tree = f.Get(treename)
    ds = ROOT.RooDataSet(dataname, dataname, st, RF.Import(tree))
    return ds


def dump_workspace(mode, wsp):
    outfile = mode.get_output_path('sweight_fit') + 'mass_fit.p'
    helpers.dump(wsp, outfile)


def load_workspace(mode):
    import ROOT
    outfile = mode.get_output_path('sweight_fit') + 'mass_fit.p'
    return helpers.load(outfile)
