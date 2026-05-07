# Cherry Tree

<img src="https://i.imgur.com/QGyxImm.jpg" title="Cherry Tree" width="250" />

Cherry Tree is a set of tools that were originally designed to help
build releases for
[Apache Superset](https://github.com/apache/incubator-superset),
but can be used for any other project
that wants to implement a similar workflow.

> **Personal note:** I forked this to experiment with cherry-picking workflows
> for my own projects. The `bake` command is particularly useful.

Ideas behind `cherrytree` include:
* Github label driven development / releases
* Make release from specifying base reference and Github labels
* Apply cherries in correct order
* Follow a base reference + cherries approach

## An example build file

`cherrytree` offers tooling to both:
1. validate that all cherries apply cleanly before baking release
2. craft a branch in a target repo from a "bake file"

Here's an example :

`$ cherrytree bake -r apache/superset -l v1.3 1.3`
```
🍒🌳🍒 CherryTree
Running in dryrun mode, all changes will be rolled back
Base ref is 69c5cd792296167d503403455b7e434fb3fedcd6
2090 commits skipped due to missing PRs
Fetching labeled PRs: "v1.3" (113 labels found)
113 PRs found
Fetching all branches
Checking out base branch: 1.3
Recreating and checking out temporary branch: __tmp_branch
skip-applied #16233: fix(dashboard): cross filter chart highlight when filters badge ic...
apply-ok #16193: refactor: external metadata fetch API                                     [DRY-RUN]
skip-applied #16251: chore: bump superset-ui packages to 0.17.84
skip-applied #16253: fix: Homepage dashboard examples tab does not show user created ob...
skip-applied #16259: fix: pivot columns with ints for name
skip-applied #16260: fix: check roles before fetching reports
apply-ok #16293: fix(sqlite): week grain refer to day of week                              [DRY-RUN]
apply-ok #16167: feat: Adding Rockset db engine spec                                       [DRY-RUN]
apply-ok #16369: fix: call external metadata endpoint with correct rison object            [DRY-RUN]
apply-ok #16299: fix: copy to Clipboard order                                              [DRY-RUN]
apply-ok #16416: feat: add Shillelagh DB engine spec                                       [DRY-RUN]
apply-ok #16460: fix(native-filters): handle null values in value filter                   [DRY-RUN]
apply-ok #16464: fix: prevent page crash when chart can't render                           [DRY-RUN]
apply-ok #16468: fix(native-filters): handle undefined control value gracefully            [DRY-RUN]
apply-ok #16515: fix: Pin snowflake-sqlalchemy to 1.2.4                                    [DRY-RUN]
apply-ok #16372: fix: ensure setting operator to `None` (#16371)                           [DRY-RUN]
apply-ok #16526: fix: Set correct comparison operator for snowflake-sqlalchemy pinning     [DRY-RUN]
apply-ok #16482: fix: can't drop column when name overlap                                  [DRY-RUN]
apply-ok #16412: fix: Support Jinja template functions in global async queries             [DRY-RUN]
apply-ok #16573: fix: impersonate user label/tooltip                
```
