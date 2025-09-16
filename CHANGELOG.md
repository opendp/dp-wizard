# CHANGELOG

## 0.5.0

Highlights:

- Add synthetic data generation [#588](https://github.com/opendp/dp-wizard/pull/588)
- upgrade opendp [#585](https://github.com/opendp/dp-wizard/pull/585)

Also includes:

- get rid of extra padding at bottom [#590](https://github.com/opendp/dp-wizard/pull/590)
- Add python syntax highlights and add Context example [#582](https://github.com/opendp/dp-wizard/pull/582)
- Add favicon [#583](https://github.com/opendp/dp-wizard/pull/583)
- Fix: No bounds on count [#578](https://github.com/opendp/dp-wizard/pull/578)
- change dataset page to two columns [#580](https://github.com/opendp/dp-wizard/pull/580)
- add a global registry_url [#581](https://github.com/opendp/dp-wizard/pull/581)
- Round the epsilon values [#575](https://github.com/opendp/dp-wizard/pull/575)
- Calculated default value causes re-render [#576](https://github.com/opendp/dp-wizard/pull/576)

## 0.4.1

Highlights:

- Expand the tutorial notes, and allow them to be toggled on and off [#503](https://github.com/opendp/dp-wizard/pull/503), [#571](https://github.com/opendp/dp-wizard/pull/571)
- Factor out [dp-wizard-templates](https://github.com/opendp/dp-wizard-templates) [#569](https://github.com/opendp/dp-wizard/pull/569)
- Light mode / dark mode toggle [#482](https://github.com/opendp/dp-wizard/pull/482)
- Unit of privacy: Add another step to help the user think about the kind of entity being protected [#525](https://github.com/opendp/dp-wizard/pull/525)
- Bug fix: Changing epsilon will not reset columns [#508](https://github.com/opendp/dp-wizard/pull/508)

Also includes:

- Add isort as precommit [#565](https://github.com/opendp/dp-wizard/pull/565)
- Consolidate state [#566](https://github.com/opendp/dp-wizard/pull/566)
- Add row count bounds [#559](https://github.com/opendp/dp-wizard/pull/559)
- Cleanup margin code gen [#568](https://github.com/opendp/dp-wizard/pull/568)
- Upgrade starlette [#557](https://github.com/opendp/dp-wizard/pull/557)
- add backticks; Move utility function into class [#551](https://github.com/opendp/dp-wizard/pull/551)
- add a placholder, so both inputs are the same width [#558](https://github.com/opendp/dp-wizard/pull/558)
- Misc. small notebook text fixes [#554](https://github.com/opendp/dp-wizard/pull/554)
- upgrade pyright [#555](https://github.com/opendp/dp-wizard/pull/555)
- Stronger typing: `AnalysisName` and `ColumnName` [#541](https://github.com/opendp/dp-wizard/pull/541)
- Add note about "dp.median" in generated code [#522](https://github.com/opendp/dp-wizard/pull/522)
- better docs about quoting for Windows users [#505](https://github.com/opendp/dp-wizard/pull/505)
- Analysis inputs empty by default [#502](https://github.com/opendp/dp-wizard/pull/502)
- Add note about grouping in panel titles [#509](https://github.com/opendp/dp-wizard/pull/509)
- inline playwright helper functions [#512](https://github.com/opendp/dp-wizard/pull/512)
- Remove unneeded "else"s [#520](https://github.com/opendp/dp-wizard/pull/520)
- make has_bins a property [#527](https://github.com/opendp/dp-wizard/pull/527)
- upgrade dependencies to resolve dependabot warnings [#529](https://github.com/opendp/dp-wizard/pull/529)
- Check that IDs match on startup [#530](https://github.com/opendp/dp-wizard/pull/530)
- Pin doc links [#516](https://github.com/opendp/dp-wizard/pull/516)
- add a mini-toc [#504](https://github.com/opendp/dp-wizard/pull/504)
- explain weights [#524](https://github.com/opendp/dp-wizard/pull/524)
- make the analysis_panel logic match the results_panel logic [#514](https://github.com/opendp/dp-wizard/pull/514)
- pass contributions as reactive [#517](https://github.com/opendp/dp-wizard/pull/517)
- Suppport count queries [#454](https://github.com/opendp/dp-wizard/pull/454)
- Use function templates for short blocks [#414](https://github.com/opendp/dp-wizard/pull/414)
- validate number of bins; generate dummy CSV when running in cloud mode [#489](https://github.com/opendp/dp-wizard/pull/489)
- Update dependencies with security warnings [#478](https://github.com/opendp/dp-wizard/pull/478)
- one dependency per line in toml makes diffs easier to read [#449](https://github.com/opendp/dp-wizard/pull/449)
- Just add a comment about endpoint inclusion [#445](https://github.com/opendp/dp-wizard/pull/445)
- Explain use of jupyter lab template [#484](https://github.com/opendp/dp-wizard/pull/484)
- Release process: Pull out highlights [#477](https://github.com/opendp/dp-wizard/pull/477)
- Note about "None" for string valued columns [#441](https://github.com/opendp/dp-wizard/pull/441)

## 0.4.0

Highlights:

- Run DP wizard in the cloud [#404](https://github.com/opendp/dp-wizard/pull/404)
- And since we don't allow uploads in the cloud, let user just provide column names [#388](https://github.com/opendp/dp-wizard/pull/388)

Also includes:

- Better title at the top of the notebook [#418](https://github.com/opendp/dp-wizard/pull/418)
- pull out highlights in changelog [#466](https://github.com/opendp/dp-wizard/pull/466)
- deployment fixes [#462](https://github.com/opendp/dp-wizard/pull/462)
- Move analysis blurbs and inputs lists [#458](https://github.com/opendp/dp-wizard/pull/458)
- Fill in templates for medians [#451](https://github.com/opendp/dp-wizard/pull/451)
- Update READMEs with current information [#428](https://github.com/opendp/dp-wizard/pull/428)
- Merge feedback and about tabs [#456](https://github.com/opendp/dp-wizard/pull/456)
- Histograms do not need margins [#453](https://github.com/opendp/dp-wizard/pull/453)
- swap public and private [#447](https://github.com/opendp/dp-wizard/pull/447)
- generalize analysis plans [#440](https://github.com/opendp/dp-wizard/pull/440)
- swap columns and grouping in ui [#452](https://github.com/opendp/dp-wizard/pull/452)
- Python executable might not be named "python" [#429](https://github.com/opendp/dp-wizard/pull/429)
- Fix deploy script [#423](https://github.com/opendp/dp-wizard/pull/423)
- in histogram results, rename len to count [#432](https://github.com/opendp/dp-wizard/pull/432)
- remove reference to "Queryable" [#443](https://github.com/opendp/dp-wizard/pull/443)
- capital "L" in "Library" [#439](https://github.com/opendp/dp-wizard/pull/439)
- Upgrade h11 [#412](https://github.com/opendp/dp-wizard/pull/412)
- test error handling in notebook execution [#415](https://github.com/opendp/dp-wizard/pull/415)
- strip ansi from stack traces [#403](https://github.com/opendp/dp-wizard/pull/403)
- OpenDP -> "the OpenDP library" [#408](https://github.com/opendp/dp-wizard/pull/408)
- Disable downloads if analysis undefined [#422](https://github.com/opendp/dp-wizard/pull/422)
- Changelog bug was a hack I had left from the first release [#409](https://github.com/opendp/dp-wizard/pull/409)
- Show warnings if you jump around tabs [#417](https://github.com/opendp/dp-wizard/pull/417)
- "bin count" -> "number of bins" [#413](https://github.com/opendp/dp-wizard/pull/413)
- informative download file names [#416](https://github.com/opendp/dp-wizard/pull/416)
- upgrade opendp and recompile requirements [#397](https://github.com/opendp/dp-wizard/pull/397)
- Fix `type` in issue template [#402](https://github.com/opendp/dp-wizard/pull/402)
- fallback to 0 if unexpected key [#396](https://github.com/opendp/dp-wizard/pull/396)
- Pin all dependencies for application install [#386](https://github.com/opendp/dp-wizard/pull/386)

## 0.3.1

Highlight:

- upgrade to opendp 0.13 from nightly [#398](https://github.com/opendp/dp-wizard/pull/398)

Also includes:

- Add a warning on the first run [#355](https://github.com/opendp/dp-wizard/pull/355)
- minimum version on pyarrow [#358](https://github.com/opendp/dp-wizard/pull/358)
- add webpdf extra and it works for me [#360](https://github.com/opendp/dp-wizard/pull/360)

## 0.3.0

Highlights:

- Support means [#264](https://github.com/opendp/dp-wizard/pull/264) and fill codegen gaps for means [#293](https://github.com/opendp/dp-wizard/pull/293)
- Support medians [#299](https://github.com/opendp/dp-wizard/pull/299)

Also includes:

- provide command line alias [#337](https://github.com/opendp/dp-wizard/pull/337)
- Specify the minimum python version in readme [#338](https://github.com/opendp/dp-wizard/pull/338)
- reactive isolate fixes infinite loop [#311](https://github.com/opendp/dp-wizard/pull/311)
- No silent errors for code gen [#312](https://github.com/opendp/dp-wizard/pull/312)
- Issue templates and an invitation to contribute [#322](https://github.com/opendp/dp-wizard/pull/322)
- A little bit of input validation [#303](https://github.com/opendp/dp-wizard/pull/303)
- Use functions as templates [#301](https://github.com/opendp/dp-wizard/pull/301)
- Distinguish generic `code_template` from specific `code_generator` [#298](https://github.com/opendp/dp-wizard/pull/298)
- Fix tool tips that have been floating to the right [#302](https://github.com/opendp/dp-wizard/pull/302)
- Add "bounds" to variable and UI labels [#294](https://github.com/opendp/dp-wizard/pull/294)
- Hacky CSS for a better epsilon slider [#292](https://github.com/opendp/dp-wizard/pull/292)
- Only access CLIInfo from server [#284](https://github.com/opendp/dp-wizard/pull/284)
- Exercise all downloads [#280](https://github.com/opendp/dp-wizard/pull/280)
- Make Analysis templates OO [#290](https://github.com/opendp/dp-wizard/pull/290)
- upgrade jinja; not sure why other compiled deps changed [#279](https://github.com/opendp/dp-wizard/pull/279)
- typo [#288](https://github.com/opendp/dp-wizard/pull/288)
- pyyaml does not need to be installed in notebook [#283](https://github.com/opendp/dp-wizard/pull/283)
- Add "about" tab [#287](https://github.com/opendp/dp-wizard/pull/287)
- Use xdist for parallel tests [#266](https://github.com/opendp/dp-wizard/pull/266)
- lower the logging level if kernel needs install [#265](https://github.com/opendp/dp-wizard/pull/265)
- Bump dependency versions and drop 3.9 support [#260](https://github.com/opendp/dp-wizard/pull/260)

## 0.2.0

Highlights:

- Handle both public and private CSVs [#218](https://github.com/opendp/dp-wizard/pull/218), and in particular, show histogram previews of public CSVs.
- Support grouping [#237](https://github.com/opendp/dp-wizard/pull/237)

Also includes:

- Release v0.2.0 [#258](https://github.com/opendp/dp-wizard/pull/258)
- remove debug code [#252](https://github.com/opendp/dp-wizard/pull/252)
- fix typos [#250](https://github.com/opendp/dp-wizard/pull/250) [#251](https://github.com/opendp/dp-wizard/pull/251)
- Download unexecuted notebooks [#248](https://github.com/opendp/dp-wizard/pull/248)
- Simplify plotting: No major/minor; instead angle label [#247](https://github.com/opendp/dp-wizard/pull/247)
- Handle more columns in dataframe helper [#240](https://github.com/opendp/dp-wizard/pull/240)
- Cleanup pip output [#234](https://github.com/opendp/dp-wizard/pull/234)
- Add a helper for making the changelog, and update the README [#241](https://github.com/opendp/dp-wizard/pull/241)
- HTML and PDF notebook download [#229](https://github.com/opendp/dp-wizard/pull/229)
- Capture and show any error messages from notebook execution [#223](https://github.com/opendp/dp-wizard/pull/223)
- Pin opendp version [#239](https://github.com/opendp/dp-wizard/pull/239)
- Remove old issue template [#228](https://github.com/opendp/dp-wizard/pull/228)
- Validate contributions [#214](https://github.com/opendp/dp-wizard/pull/214)
- Change the plot's aspect ratio [#213](https://github.com/opendp/dp-wizard/pull/213)
- Add confidence interval text + histogram table [#211](https://github.com/opendp/dp-wizard/pull/211)
- Include unit of privacy in graphs and output [#205](https://github.com/opendp/dp-wizard/pull/205)
- Remove unused sort [#206](https://github.com/opendp/dp-wizard/pull/206)
- Document dependencies in generated code [#207](https://github.com/opendp/dp-wizard/pull/207)
- Strip coda from notebook [#209](https://github.com/opendp/dp-wizard/pull/209)

## 0.0.1

Initial release provides:

- Notebook and python script downloads
- DP Histograms
