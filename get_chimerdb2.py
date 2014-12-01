#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
It downloads the lastest known fusion genes from the literature (which have the
PubMed, SangerCGP, OMIM, Milteman as source) from ChimerDB 2.0 database
<http://ercsb.ewha.ac.kr/FusionGene/index.jsp>. It takes only the fusion genes
from sheets named PubMed, SangerCGP, OMIM, Milteman from the file:
"http://ercsb.ewha.ac.kr:8080/FusionGene/document/PO_down.xls".



Author: Daniel Nicorici, Daniel.Nicorici@gmail.com

Copyright (c) 2009-2014 Daniel Nicorici

This file is part of FusionCatcher.

FusionCatcher is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FusionCatcher is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with FusionCatcher (see file 'COPYING.txt').  If not, see
<http://www.gnu.org/licenses/>.

By default, FusionCatcher is running BLAT aligner
<http://users.soe.ucsc.edu/~kent/src/> but it offers also the option to disable
all its scripts which make use of BLAT aligner if you choose explicitly to do so.
BLAT's license does not allow to be used for commercial activities. If BLAT
license does not allow to be used in your case then you may still use
FusionCatcher by forcing not use the BLAT aligner by specifying the option
'--skip-blat'. Fore more information regarding BLAT please see its license.

Please, note that FusionCatcher does not require BLAT in order to find
candidate fusion genes!

This file is not running/executing/using BLAT.
"""



import os
import sys
import socket
import optparse
import shutil
import urllib2
import symbols


if __name__ == '__main__':

    #command line parsing

    usage = "%prog [options]"
    description = """It downloads the lastest known fusion genes from the literature (which have the
PubMed as source) from ChimerDB 2.0 database."""
    version = "%prog 0.10 beta"

    parser = optparse.OptionParser(usage=usage,description=description,version=version)

    parser.add_option("--organism",
                      action = "store",
                      type = "string",
                      dest = "organism",
                      default = "homo_sapiens",
                      help="""The name of the organism for which the known fusion genes are downloaded, e.g. homo_sapiens, mus_musculus, etc. Default is '%default'.""")

    parser.add_option("--output",
                      action="store",
                      type="string",
                      dest="output_directory",
                      default = '.',
                      help="""The output directory where the known fusion genes are stored. Default is '%default'.""")

    parser.add_option("--server",
                      action="store",
                      type="string",
                      dest="server",
                      default = "http://ercsb.ewha.ac.kr",
                      help="""The ChimerDB 2.0 server from where the known fusion genes are downloaded. Default is '%default'.""")

    (options,args) = parser.parse_args()

    # validate options
    if not (options.output_directory
            ):
        parser.print_help()
        sys.exit(1)

    try:
        import xlrd
        print "The Python Excel XLRD parser was found!"
    except:
        print >> sys.stderr,"WARNING: Python XLRD library not found!"
        print >> sys.stderr,"Please, install XLRD python library in order to be able to parse the ChimerDB 2.0 database!"
        file(os.path.join(options.output_directory,'chimerdb2.txt'),'w').write('')
        sys.exit(0)


    # timeout in seconds
    timeout = 1800
    socket.setdefaulttimeout(timeout)
    tmp_file = 'temp_chimerdb.xls'

    #http://ercsb.ewha.ac.kr/FusionGene/document/PO_down.xls
    url = '/FusionGene/document/PO_down.xls'

    if options.organism.lower() == 'homo_sapiens':

        file(os.path.join(options.output_directory,'version.txt'),'a').writelines(['ChimerDB database version: 2.0\n'])

        print "Downloading the known fusion genes from ChimerDB 2.0 database!"

        sem = True
        try:
            d = urllib2.urlopen('%s%s' % (options.server,url))
            file(tmp_file,'w').write(d.read())
        except:
            sem = False
            print >>sys.stderr, "Warning: Cannot access '%s%s'! The output file will be empty!" % (options.server,url)

        if sem:
            print "Parsing..."
            # parse the ChimerDB file with the known fusion genes
            wb = xlrd.open_workbook(tmp_file)
            fusions = set()

            # parse the PubMed sheet
            sheet = wb.sheet_by_name('PubMed') # u'PubMed'
            for row in xrange(sheet.nrows):
                if row == 0: # skip first line
                    continue
                line = sheet.row_values(row)
                g1 = line[0].upper().encode('ascii','ignore')
                g2 = line[1].upper().encode('ascii','ignore')
                (g1,g2) = (g2,g1) if g2 < g1 else (g1,g2)
                fusions.add((g1,g2))
            # parse the SangerCGP sheet
            sheet = wb.sheet_by_name('SangerCGP') #
            for row in xrange(sheet.nrows):
                if row == 0: # skip first line
                    continue
                line = sheet.row_values(row)
                g1 = line[0].upper().encode('ascii','ignore')
                g2 = line[4].upper().encode('ascii','ignore')
                (g1,g2) = (g2,g1) if g2 < g1 else (g1,g2)
                fusions.add((g1,g2))
            # parse the Mitelman sheet
            sheet = wb.sheet_by_name('Mitelman') #
            for row in xrange(sheet.nrows):
                if row == 0: # skip first line
                    continue
                line = sheet.row_values(row)
                g1 = line[0].upper().encode('ascii','ignore')
                g2 = line[3].upper().encode('ascii','ignore')
                (g1,g2) = (g2,g1) if g2 < g1 else (g1,g2)
                fusions.add((g1,g2))
            # parse the OMIM sheet
            sheet = wb.sheet_by_name('OMIM') #
            for row in xrange(sheet.nrows):
                if row == 0: # skip first line
                    continue
                line = sheet.row_values(row)
                g1 = line[2].upper().encode('ascii','ignore')
                g2 = line[4].upper().encode('ascii','ignore')
                (g1,g2) = (g2,g1) if g2 < g1 else (g1,g2)
                fusions.add((g1,g2))

            fusions = list(fusions)
            print "%d known gene fusions found!" % (len(fusions),)

            # read the gene symbols
            file_symbols = os.path.join(options.output_directory,'synonyms.txt')
            genes = symbols.read_genes_symbols(file_symbols)

            banned = set()
            loci = symbols.generate_loci(file_symbols)
            #for v in symbols.locus.values():
            for v in loci.values():
                if v:
                    n = len(v)
                    if n > 1:
                        for i in xrange(n-1):
                            for j in xrange(i+1,n):
                                if v[i].upper() != v[j].upper():
                                    ens1 = symbols.ensembl(v[i].upper(),genes,loci)
                                    ens2 = symbols.ensembl(v[j].upper(),genes,loci)
                                    if ens1 and ens2:
                                        for e1 in ens1:
                                            for e2 in ens2:
                                                if e1 != e2:
                                                    (e1,e2) = (e2,e1) if e2 < e1 else (e1,e2)
                                                    banned.add((e1,e2))


            d = []
            for (g1,g2) in fusions:
                if ( g1.upper() == g2.upper() or ((g1.endswith('@') and g2.endswith('@')) and g1.upper()[:2] == g2.upper()[:2])):
                    print "%s-%s skipped!" % (g1,g2)
                    continue
                ens1 = symbols.ensembl(g1,genes,loci)
                ens2 = symbols.ensembl(g2,genes,loci)

                if ens1 and ens2:
                    for e1 in ens1:
                        for e2 in ens2:
                            if e1 != e2 and ((e1,e2) not in banned) and ((e2,e1) not in banned):
                                d.append([e1,e2])


            data = ['\t'.join(sorted(line)) + '\n' for line in d]
            data = sorted(set(data))

            print "%d known fusion genes converted succesfully to Ensembl Gene ids!" % (len(data),)
        else:
            data = []
        file(os.path.join(options.output_directory,'chimerdb2.txt'),'w').writelines(data)
        if os.path.isfile(tmp_file):
            os.remove(tmp_file)
    else:
        # write an empty file for other organisms than human
        file(os.path.join(options.output_directory,'chimerdb2.txt'),'w').write('')
#
