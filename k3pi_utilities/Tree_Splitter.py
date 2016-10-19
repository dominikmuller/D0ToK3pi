#!/usr/bin/env python
from __future__ import division
from __future__ import print_function

import argparse
import os
import warnings

import numpy
import ROOT
from collections import defaultdict


YPES_MAP = {
    # int-like
    "B": "int8",
    "b": "uint8",
    "S": "int16",
    "s": "uint16",
    "I": "int32",
    "i": "uint32",
    "L": "int64",
    "l": "uint64",
    "O": "bool",
    # float-like
    "F": "float32",
    "D": "float64"
}


def add_branch(tree, name):
    b_var = numpy.zeros(1, dtype=numpy.float64)
    b = tree.Branch(name, b_var, name+'/D')
    return b, b_var


def tree_splitter(tree_path_in, input_fns, out_fn, variables_to_copy,
                  selection_string, formula_vars=None):
    # Build the input TChain and get a list of branches
    in_tree = ROOT.TChain(tree_path_in)
    for fn in input_fns:
        in_tree.Add(fn)
    in_branches = [b.GetName() for b in list(in_tree.GetListOfBranches())]
    tree_name_out = tree_path_in

    # Set up the output TFile with the path of directories
    outputfile = ROOT.TFile(out_fn, 'RECREATE')
    components = tree_path_out.split('/')
    # Tree name is the last component of the 'path'
    tree_name_out = components.pop()
    for dirname in components:
        d = outputfile.mkdir(dirname)
        d.cd()

    # Decativate all branches
    in_tree.SetBranchStatus('*', 0)

    # Loop over all the variables
    for new_var in variables_to_copy:
        in_tree.SetBranchStatus(new_var, 1)

    if os.path.basename(tree_path_in) == os.path.basename(tree_path_out):
        # Copy the activated branches from the input tree with a selection
        out_tree = in_tree.CopyTree(selection_string)
    else:
        # Copy the activated branches from the input tree with a selection
        temp_tree = in_tree.CopyTree(selection_string)
        # Set up the outputted tree
        out_tree = ROOT.TTree(tree_name_out, tree_name_out)
        branch_addresses = []
        for var in variables_to_copy:
            # Get the old variable name
            temp_var = var
            if var[:len(new_mother)] == new_mother:
                temp_var = old_mother + var[len(old_mother):]
            # Check the variable is present and refers to the old mother
            if temp_var in in_branches:
                btype = temp_tree.GetBranch(temp_var).GetTitle().split('/')[-1]
                branch_addresses.append(
                    numpy.zeros(1, dtype=TYPES_MAP.get(btype, 'F'))
                )
                temp_tree.SetBranchAddress(temp_var, branch_addresses[-1])
                branch_title = '{0}/{1}'.format(var, btype)
                out_tree.Branch(var, branch_addresses[-1], branch_title)
        # Make the new TTree
        for i in range(temp_tree.GetEntries()):
            temp_tree.GetEntry(i)
            out_tree.Fill()

    # Place the TTrees in the directories
    if d:
        out_tree.SetDirectory(d)

    # Set up for the formula variables
    formulae = []
    for f_name, f_formula in formula_vars:
        f = ROOT.TTreeFormula(f_name, f_formula, out_tree)
        f.GetNdata()
        f_var = numpy.zeros(1, dtype=numpy.float64)
        f_branch = out_tree.Branch(f_name, f_var, f_name+'/D')
        formulae.append((f, f_var, f_branch))

    # If variables need to be added loop over the tree
    if formula_vars:
        for i in range(out_tree.GetEntries()):
            out_tree.GetEvent(i)
            # Add the formula variables
            for f, f_var, f_branch in formulae:
                f_var[0] = f.EvalInstance()
                f_branch.Fill()

    # Save and exit
    if d:
        d.WriteTObject(out_tree)
    else:
        outputfile.WriteTObject(out_tree)

    new_lumi_tree = ROOT.TTree('LumiTuple', 'new_lumi_ntuple')
    lumi_var = [
        numpy.zeros(1, dtype=numpy.float64),
        numpy.zeros(1, dtype=numpy.float64)
    ]
    lumi_err_var = [
        numpy.zeros(1, dtype=numpy.float64),
        numpy.zeros(1, dtype=numpy.float64)
    ]

    for fn in input_fns:
        # Get the existing lumituple, skipping if it isn't found
        f = ROOT.TFile.Open(fn)
        f_dirs = [x.GetName() for x in list(f.GetListOfKeys())]
        if 'GetIntegratedLuminosity' not in f_dirs:
            continue
        if tree_path_in.split('/')[0] in f_dirs:
            data_tree = f.Get(tree_path_in)
        elif 'Tuple' in f_dirs[0]:
            data_tree = f.Get(f_dirs[0] + '/' + tree_path_in.split('/')[1])
        else:
            raise RuntimeError('Lumi tuple present but no DecayTreeTuple found'
                               ' in: '.format(fn))
        lumi_tree = f.Get('GetIntegratedLuminosity/LumiTuple')

        # Find all the rum numbers corresponding to this input file
        run_number = numpy.zeros(1, dtype=numpy.int)
        data_tree.SetBranchAddress('runNumber', run_number)

        run_numbers = []
        for i in range(data_tree.GetEntries()):
            data_tree.GetEvent(i)
            if run_number[0] not in run_numbers:
                run_numbers.append(run_number[0])

        lumi_tree.SetBranchAddress('IntegratedLuminosity', lumi_var[0])
        lumi_tree.SetBranchAddress('IntegratedLuminosityErr', lumi_err_var[0])

        for i in range(lumi_tree.GetEntries()):
            lumi_tree.GetEvent(i)
            lval = lumi_var[0][0]
            lerr = lumi_err_var[0][0]
            lumi_var[1][0] = lval
            lumi_err_var[1][0] = lerr
            new_lumi_tree.Fill()

        f.Close()

    lumi_per_fill = dict(lumi_per_fill)
    if len(lumi_per_fill) > 0:
        utilities.dump(lumi_per_fill,
                    out_fn.replace('.root', '_lumi.p'))

    d = outputfile.mkdir('GetIntegratedLuminosity')
    d.WriteTObject(new_lumi_tree)

    outputfile.Close()


def create_parser():
    """Parse input arguments and return them.

    This method is responsible for checking that the input arguments are valid.
    """
    parser = argparse.ArgumentParser(
        description='Merge TTrees applying a selection'
    )
    parser.add_argument('--files', nargs='+', required=True)
    parser.add_argument('--name', default='MVA')
    parser.add_argument('--variables', nargs='+', required=True)
    parser.add_argument('--addvariables', nargs='+', required=True)
    parser.add_argument('--outputfile', required=True)
    parser.add_argument('--treename', required=True)
    parser.add_argument('--newtreename', required=True)
    parser.add_argument('--selection', required=True)
    parser.add_argument('--mothers', default=None)
    parser.add_argument('--year', default=None)
    parser.add_argument('--polarity', default=None)
    parser.add_argument('-v', '--silent', action='store_true', default=False,
                        help='Enable INFO level logging')

    return parser.parse_args()


def main():
    # Make ROOTs meaningless warnings quieter
    warnings.filterwarnings(action='ignore', category=RuntimeWarning,
                            message='creating converter.*')
    args = create_parser()
    # Convert the formula variables to tuples of form (name, formula)
    addvariables = []
    for i in range(0, len(args.addvariables), 2):
        addvariables.append((args.addvariables[i], args.addvariables[i+1]))
    # Get the boost to perform if possible
    if args.year is not None:
        ebeam = config.energies[args.year]
        beam1_angles = config.b1_angles[args.year][args.polarity]
        beam2_angles = config.b2_angles[args.year][args.polarity]
        boost_vector, z_angle, pp_zaxis = utilities.get_boost_vector(
            ebeam, beam1_angles, beam2_angles
        )
    else:
        boost_vector = z_angle = pp_zaxis = None
    tree_splitter(
        tree_path_in=args.treename,
        input_fns=args.files,
        out_fn=args.outputfile,
        variables_to_copy=args.variables,
        selection_string=args.selection,
        tree_path_out=args.newtreename if args.newtreename else args.treename,
        year=args.year,
        formula_vars=addvariables,
        decay_mother=args.mothers,
        boost_vector=boost_vector,
        z_angle=z_angle,
        pp_zaxis=pp_zaxis
    )

if __name__ == '__main__':
    config.devnull = None
    main()
