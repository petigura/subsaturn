from argparse import ArgumentParser
import os
from jinja2 import Environment, PackageLoader, FileSystemLoader
import k2phot.phot
import pandas as pd
import subsaturn.rv

RADVEL_SETUP_DIR="/Users/petigura/Research/subsaturn/subsaturn/data/RV/radvel_setup/"
RADVEL_OUTPUT_DIR="/Users/petigura/Research/subsaturn/subsaturn/data/RV/radvel_output/"
TEXDIR="/Users/petigura/Research/subsaturn/Papers/subsat2/subsat2/"

STARS="3167 ck00367 ck00094 epic201505350 epic205071984 epic203771098 epic206245553 epic201546283 epic211945201 epic211736671".split()

HOME = os.environ['HOME']


def rv_table():
    rv = subsaturn.rv.read_subsat2()
    rv = rv.sort_values(by=['starname','tel'])
    tablefn = "{}/tab_rv.tex".format(TEXDIR)
    with open(tablefn, 'w') as f:
        f.write('% starname, tel, time, mnvel, errvel \n')
        for i, row in rv.iterrows():
            s = (
                r"{starname:s} & {tel:s} & {time:.6f} & ".format(**row)
                +r"{mnvel:.2f} & {errvel:.2f} \\".format(**row)
            )
            s += "\n"
            f.write(s)

def main():
    psr = ArgumentParser()
    subpsr = psr.add_subparsers(title="subcommands",dest="subparser_name")

    # Run sub parser command
    psr_radvel_fit = subpsr.add_parser("radvel_fit")
    psr_radvel_fit.add_argument('star',type=str)

    psr_radvel_table = subpsr.add_parser("radvel_table")
    psr_radvel_table.add_argument('star',type=str)
 
    psr_rv_table = subpsr.add_parser("rv_table")

    args = psr.parse_args()

    if args.subparser_name=="radvel_fit":
        radvel_fit(args.star)

    if args.subparser_name=="radvel_table":
        radvel_table(args.star)

    if args.subparser_name=="rv_table":
        rv_table()

if __name__=="__main__":
    main()
