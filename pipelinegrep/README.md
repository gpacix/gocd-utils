# Basic Use

pipelinegrep makes it much easier to report about pipelines on your
GoCD server.  As long as you have access to the XML configuration of
your server, you can save it to a file and run pipelinegrep on it.

Let's say you want to know which pipelines pull a particular
repository named "myrepo": the regular expression for that is
```
<git url.*/myrepo(|\.git)"
```
You can just run `grep -n` with that, and it will tell you where all
the matches for that are in your config.xml.  But you'll have to
figure out what pipelines they go with on your own.

With pipelinegrep, you can simply do:
```
python3 pipelinegrep.py  -p '<git url.*/myrepo(|\.git)"' < config.xml
```
(the `-p` means "show the pipeline name") and get output like the following:
```
pipeline: mypipeline_reporting
        <git url="https://github.agency.gov/dataeng/myrepo" />
pipeline: mypipeline_reporting_snapshots
        <git url="https://github.agency.gov/dataeng/myrepo.git" />
```

(From here on, we're assuming your GoCD config is in `config.xml`.)

If you want to see the line number each match occurred on, use the
`-n` flag.

If you don't care about the match itself and just want to see the
matching pipeline's name, use the `-l` flag.

If you want your matching to be case-insensitive (e.g. abc matches
aBc), use the `-i` flag.

# Machine-Readable Formats

If you want the output in CSV, tab-delimited, or JSON format, you can
use the `-f` flag and the name of the format:

```
python3 pipelinegrep.py -f csv '<git url.*/myrepo(|\.git)"' < config.xml
```
gives the same information in the output, but formatted like the following:
```
"mypipeline_reporting",6910,"<git url=""https://github.agency.gov/dataeng/myrepo"" />"
"mypipeline_reporting_snapshots",7071,"<git url=""https://github.agency.gov/dataeng/myrepo.git"" />"
```

`-f tab` or `-f TAB` gives the same, but tab-delimited:
```
mypipeline_reporting	6910	<git url="https://github.agency.gov/dataeng/myrepo" />
mypipeline_reporting_snapshots	7071	<git url="https://github.agency.gov/dataeng/myrepo.git" />
```

And if you're piping the output to a tool that prefers JSON, you can
use `-f json` to produce:
```
{ "pipeline": "mypipeline_reporting", "n":6910, "line":"<git url=\"https://github.agency.gov/dataeng/myrepo\" />" }
{ "pipeline": "mypipeline_reporting_snapshots, "n":7071, "line":"<git url=\"https://github.agency.gov/dataeng/myrepo.git\" />" }
```

Note that quotes in the matching line are backslash-escaped in the
JSON output, doubled to escape them in the CSV output, but unchanged
in the tab-delimited output.

Any whitespace at the beginning of the matching line is also
stripped.  Whitespace at the end of the line is always stripped.

# Custom Formats

If the built-in formats aren't what you need, you can build your own
format string, using `{pipeline}`, `{n}`, `{line}`, `{sline}`, `{eline}`,
and `{cline}` for the pipeline name, line number, matching line,
stripped matching line, and stripped-and-quotes-escaped matching
line (for JSON), and stripped-and-quotes-doubled matching line (for CSV).
```
python3 pipelinegrep.py '<git url.*/myrepo(|\.git)"' -f 'At line {n}, inside pipeline {pipeline}, we found this line: {sline}' < config.xml
```
You can put tabs and newlines in from the shell, but the usual escapes
like \t and \n won't work.  Every output match ends with a newline.

If you want to do custom JSON, you need to double up your curly
braces, like this:
```
-f '{{ "pipeline_name":"{pipeline}", "line_number":{n} }}'
```

# Examples

All of the below commands should have `< config.xml` appended,
or `cat config.xml | ` prepended, where `config.xml` is the name of the
file you saved the GoCD server's configuration in.  You can also pipe
the output of curl into the script:
```
curl ... | python3 pipelinegrep.py ...
```

Find all the pipelines that keep artifacts from being purged/deleted:

`python3 pipelinegrep.py -pi 'artifactcleanupprohibited="true"'`


Find all the pipelines that depend on any other pipeline:

`python3 pipelinegrep.py -pi pipelinename`


Find all the pipelines that pull from an internal git repository:

`python3 pipelinegrep.py -pi "github\.myagency\.gov/"`


Find the ones that pull from Agency's public Github:

`python3 pipelinegrep.py -pi 'github\.com/myagency'`


Find the ones that pull from any public Github:

`python3 pipelinegrep.py -pi 'github.*\.com'`


Find the ones that haven't updated a default email:

`python3 pipelinegrep.py -pi ops@example.com`


Find everywhere an offboarding user is mentioned:

`python3 pipelinegrep.py -pi pacig 'george\.paci' paci@`

