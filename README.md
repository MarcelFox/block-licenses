# About
CLI tool that helps us easily define which licenses are not good based on the _requirements.txt_ file. It uses _pkg_resources_ to get details from the packages, given us the licenses listed byt the package owner and returns exit 1 if found a package that contains a blocked license. Here goes the output of with all the possible options of the CLI package:
```
Usage: block-licenses [OPTIONS]

  CLI tool that helps us easily define which licenses are not good based on
  the requirements.txt file. It uses pkg_resources to get details from the
  packages, given us the licenses listed byt the package owner and returns
  exit 1 if found a package that contains a blocked license.

Options:
  -b, --blocked                   Print blocked licenses list.
  -p, --permitted                 Print permitted licenses list.
  -i, --interactive               Block packages interactively by analysing
                                  their licenses.
  -q, --quiet                     Do not print any output.
  -v, --verbose                   Print a detailed output for blocked
                                  packages.
  -P, --paranoid                  Paranoid mode for the interactive option,
                                  loop through each package even if contains
                                  a license that was already checked.
  -r TEXT                         Indicate the requirements file to be used.
  -a, --all                       Print all available licenses based on the
                                  requirements file.
  --mode [permitted|blocked]      Mode which will be used to check packages,
                                  either from the permitted list or blocked
                                  list perspective.
  --format [text|json|column|content]
                                  Format output.
  --get-allowed                   Retrieve allowed packages instead.
  -h, --help                      Show this message and exit.
  ```
