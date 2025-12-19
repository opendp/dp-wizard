The files in this directory can be used as Python modules typically are,
but they are also injected into generated notebooks. In the latter case,
they can't import any other DP Wizard modules, because the generated notebooks
need to be able to run without `dp-wizard` installed.
