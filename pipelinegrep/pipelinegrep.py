#!/usr/bin/env python3
# Look for a regexp in the config.xml for GoCD (works with v17),
# then report which pipeline it's in.
import sys
import re

usage = """\
pipelinegrep.py: Look for patterns provided as command-line args in the config.xml for GoCD (works with v17),
which user pipes to stdin, then report it and, optionally, which pipeline it's in.
Quote your patterns to protect them from the shell, and escape any periods with a backslash.

-i to ignore case,
-n to number lines, -p to show the pipeline for each match, -l to skip showing
   the matching line (forces -p).
-f means the next argument is a format string; this means -n, -p, and -l will be ignored;
   special format strings csv, tab, and json output in those formats.
   Format keys, which go in curly braces, are: pipeline, n, line, and sline;
   sline has no leading whitespace and is used in the special formats.

Example usage:
  python3 pipelinegrep.py -ni artifactcleanupprohibited -p < config.xml
  python3 pipelinegrep.py -pin '\bgithub.*\.com\b' < config.xml
  python3 pipelinegrep.py -i 'example\.com' fakedomain.com wassamatta.edu -f CSV < config.xml
  python3 pipelinegrep.py 'example\.com' -f '{pipeline}:{n}--{line}' < config.xml
"""

def get_pipeline_from_this_line(hits, lines):
    # line looks like:     <pipeline name="census_publish" isLocked="false">
    i = hits[0]
    if i == 0 or len(hits) == 1:  # first and last hit are no pipeline
        return "(none)"
    ln = lines[i]
    chopped = ln[ln.index('pipeline name="')+15:]
    return chopped[:chopped.index('"')]



def scan_for(s, lines):
    """Return a 0-based list of lines containing s"""
    hits = [0]
    for i in range(len(lines)):
        if s in lines[i]:
            hits.append(i)
    return hits

def escape_quotes(line):
    return line.replace('"', '\\"')

def double_quotes(line):
    return line.replace('"', '""')


output_format = None

output_formats = {
    'json': '{{ "pipeline":"{pipeline}", "n":{n}, "line":"{eline}" }}',
    'csv': '"{pipeline}",{n},"{cline}"',
    'tab': '{pipeline}\t{n}\t{sline}',
}

def construct_format():
    outfmt = ""
    if show_pipeline:
        outfmt += "pipeline: {pipeline}\n"
    if show_matching_line:
        if number_lines:
            outfmt += "{n}: "
        outfmt += "{line}"
    return outfmt

def line_matches(check_line, patterns):
    for pattern in patterns:
        if re.search(pattern, check_line):
            return True
    return False



def parse_args(args):
    global patterns, number_lines, ignore_case, show_pipeline, show_matching_line, output_format, program_name
    patterns = []
    number_lines = False
    ignore_case = False
    show_pipeline = False
    show_matching_line = True
    program_name = args.pop(0)

    while args:
        arg = args.pop(0)
        if arg[0] != '-':
            patterns.append(arg)
        else:
            for flag in arg[1:]:
                if flag == 'p':
                    show_pipeline = True
                elif flag == 'i':
                    ignore_case = True
                elif flag == 'n':
                    number_lines = True
                elif flag == 'l':
                    show_matching_line = False
                    show_pipeline = True
                elif flag == 'f':
                    output_format = args.pop(0)
                else:
                    die("unrecognized option flag: " + flag, 2)

def die(msg, exitcode):
    sys.stderr.write("%s: ERROR: %s\n\n" % (program_name, msg))
    sys.stderr.write(usage)
    sys.exit(exitcode)


def main(args):
    global patterns, output_format
    parse_args(args)
    if not patterns:
        die("no patterns provided on command line", 1)

    if ignore_case:
        patterns = [pattern.lower() for pattern in patterns]

    patterns = [re.compile(pattern) for pattern in patterns]

    if not output_format:
        output_format = construct_format()
    elif output_format.lower() in output_formats:
        output_format = output_formats[output_format.lower()]

    lines = sys.stdin.readlines()
    lines = [ln.rstrip() for ln in lines]
    pipeline_line_numbers = scan_for("<pipeline name=", lines)
    last_close = scan_for("</pipelines>", lines)[-1]
    pipeline_line_numbers.append(last_close)

    i = 0
    for line in lines:
        if len(pipeline_line_numbers) > 1 and i >= pipeline_line_numbers[1]:
            pipeline_line_numbers.pop(0)

        if ignore_case:
            check_line = line.lower()
        else:
            check_line = line

        if line_matches(check_line, patterns):
            pipeline_name = get_pipeline_from_this_line(pipeline_line_numbers, lines)
            sline=line.strip()
            eline=escape_quotes(sline)
            cline=double_quotes(sline)
            # internally, we're 0-based; externally, 1-based:
            print(output_format.format(pipeline=pipeline_name, n=i+1, line=line,
                                       sline=sline, eline=eline, cline=cline))
            
        i += 1


if __name__ == '__main__':
    main(sys.argv)
