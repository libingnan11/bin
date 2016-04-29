#!/usr/bin/env python
desc="""Combine values for geneids and report summed values for genes. 
"""
epilog="""Author: l.p.pryszcz@gmail.com
Warsaw, 30/09/2015
"""

import os, sys
import numpy as np
from datetime import datetime

def get_transcript2gene(handle):
    """Load transcript-gene relationships from ensembl GTF."""
    tid2gid = {}
    for l in handle:
        l = l.strip()
        if l.startswith('#') or not l: 
            continue
      
        contig,source,feature,start,end,score,strand,frame,comments = l.split('\t')
        if feature != "transcript":
            continue
    
        description={}
        for atr_value in comments.split(';'):
            atr_value = atr_value.strip()
            if not atr_value:
                continue
            atr   = atr_value.split()[0]
            value = " ".join( atr_value.split()[1:] ).strip('"')
            #value = value.strip('"')
            description[atr]=value

        #
        if "transcript_id" in description and "gene_name" in description:
            genename = description["gene_name"]
            tid = description["transcript_id"]
            gid = description["gene_id"]
            tid2gid[tid] = (gid, genename)
    return tid2gid
   
def transcript2gene(handle, out, gtf, header=0, verbose=0):
    """Report summed gene expression from transcripts"""
    if verbose:
        sys.stderr.write("Parsing GTF...\n")
    tid2gid = get_transcript2gene(gtf)
    if verbose:
        sys.stderr.write(" %s transcripts parsed.\n"%len(tid2gid))

    if verbose:
        sys.stderr.write("Parsing input...\n")
    gid2data = {}
    for i, l in enumerate(handle):
        # write header
        lData = l[:-1].split('\t')
        # no. of header lines
        if i<header:
            lData = ["geneid", "gene name"]+lData[1:]
            out.write("\t".join(lData)+"\n")
            continue
        # unload data
        tid = lData[0] #map(float, lData[1:])
        # check if tid in dict
        if tid not in tid2gid:
            sys.stderr.write("[WARNING] Transcript '%s' not found in tid2gid!\n"%tid)
            gid = "-"
        else:
            gid = tid2gid[tid]
        # add gid
        out.write('%s\t%s\t%s\n'%(tid, gid, "\t".join(lData[1:])))
        
def main():
    import argparse
    usage   = "%(prog)s -v" #usage=usage, 
    parser  = argparse.ArgumentParser(description=desc, epilog=epilog, \
                                      formatter_class=argparse.RawTextHelpFormatter)
  
    parser.add_argument('--version', action='version', version='1.0a')   
    parser.add_argument("-v", "--verbose", default=False, action="store_true",
                        help="verbose")    
    parser.add_argument("-i", "--input", default=sys.stdin, type=file,  
                        help="input stream    [stdin]")
    parser.add_argument("-o", "--output",    default=sys.stdout, type=argparse.FileType('w'), 
                        help="output stream   [stdout]")
    parser.add_argument("-g", "--gtf",   required=True, type=file, 
                        help="annotation gtf")
    parser.add_argument("--header", default="0", 
                        help="header lines or header text [%(default)s]")
    
    o = parser.parse_args()
    if o.verbose:
        sys.stderr.write("Options: %s\n"%str(o))
    # add header
    if o.header.isdigit():
        o.header = int(o.header)
    else:
        o.output.write(o.header.strip()+"\n")
        o.header = 0
    transcript2gene(o.input, o.output, o.gtf, o.header, o.verbose)

if __name__=='__main__': 
    t0 = datetime.now()
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("\nCtrl-C pressed!      \n")
    except IOError as e:
        sys.stderr.write("I/O error({0}): {1}\n".format(e.errno, e.strerror))
    dt = datetime.now()-t0
    sys.stderr.write("#Time elapsed: %s\n"%dt)
