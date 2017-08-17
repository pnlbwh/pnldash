*pnldash* is a tool for tracking your data processing projects. Once you define
a meta data file in your project directory you can print a report summarizing
your pipelines' disk usage, as well as list any large extraneous image files.
Individual project information can be pushed to a central database, and an html
dashboard can be generated for all your projects.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->
**Table of Contents**

- [Setup](#setup)
- [Quick Overview](#quick-overview)
    - [Project Directory Interface](#project-directory-interface)
    - [Central Database Interface](#central-database-interface)
- [Details](#details)
    - [`pnldash.yml`](#pnldashyml)
    - [Cached files](#cached-files)
    - [Extra files](#extra-files)
    - [Typical Workflow](#typical-workflow)
    - [The Central Database](#the-central-database)

<!-- markdown-toc end -->


# Setup

    cd /software/dir
    git clone https://github.com/reckbo/pnldash
    export PNLDASH_DB=/software/dir/pnldash/db
    export PATH=$PATH:/software/dir/pnldash/scripts
    installdb.py  # makes $PNLDASH_DB directory and copies pnldashboard.Rmd to it


# Quick Overview

## Project Directory Interface

    cd /project/dir
    pnldash init # makes a template pnldash.yml
    # edit pnldash.yml
    pnldash status # prints disk usage and each pipeline's progress
    pnldash extra # prints large extraneous image files
    pnldash push # pushes project information to the central database

## Central Database Interface

    pnldash db list  # list all projects
    pnldash db info <project>  # shows information for <project>
    pnldash db report # makes pnldashboard.html
    pnldash db open # makes and opens pnldashboard.html

# Details

## `pnldash.yml`

`pnldash.yml` is a [yaml](http://www.yaml.org/start.html) file that you write to
describe your project's output paths and parameters, and is what `pnldash` uses
to compute information for your project. It must have the fields `name`,
`grantId`, `description`, and `pipelines`. `pipelines` is a list of dictionaries
that describe each of your data processing pipelines. Each pipeline has a
description, a list of parameters, and a list of template output paths that the
pipeline has generated/will generate. For example:

    name: test-project

    grantId: ''

    description: |
        This is my project that investigates the effects of x on y.

    pipelines:
        - description: |
            This is my raw data.

          parameters:
            scanner: Siemens

          paths:
            dwi: rawdata/001/001-dwi.nrrd
            caseid_placeholder: 001
            caselist: ./caselist.txt  # this can also be a list like [001, 002]


        - description: |
            Output from the standard PNL pipeline.

            Meaning of path keys:
            fs:      freesurfer subject directory
            dwied:   eddy corrected DWI
            dwimask: FSL bet generated DWI mask
            etc.

          parameters:
                version_FreeSurfer: 5.3.0
                hash_UKFTractography: 421a7ad
                hash_tract_querier: e045eab
                hash_BRAINSTools: 41353e8
                hash_trainingDataT1AHCC: d6e5990

          paths:
            fs: _data/003_GNX_007/freesurfer/*/* # use a glob pattern to select multiple files
            dwied: _data/003_GNX_007/std_dwied0.nrrd
            dwimask: _data/003_GNX_007/std_dwimask0.nrrd
            t1mask: _data/003_GNX_007/std_t1mask0.nrrd
            t1: _data/003_GNX_007/std_t10.nrrd
            wmql: _data/003_GNX_007/wmql/*.vtk # use a glob pattern to select multiple files
            tractmeasures: _data/003_GNX_007/std_tractmeasures0.csv
            dwixc: _data/003_GNX_007/std_dwixc0.nrrd
            ukf: _data/003_GNX_007/std_ukf0.vtk
            t1xc: _data/003_GNX_007/std_t1xc0.nrrd
            fsindwi: _data/003_GNX_007/std_fsindwi0.nii.gz
            dwi: _data/003_GNX_007/std_dwi0.nhdr
            caseid_placeholder: 003_GNX_007
            caselist: ./caselist.txt

## Cached files

When you run `pnldash status`, these cached files are made:

    .pnldash/paths.csv
    .pnldash/params.csv
    .pnldash/all_image_files.txt

`.pnldash/all_image_files.txt` is a list of all the image files it finds.
The defaults extensions are

    DEFAULT_EXTS = ['.nrrd', '.nii.gz', '.nii', '.vtk', '.nhdr', '.mgz', '.dcm',
                '.dcm.gz', '.IMA', '.IMA.gz', '.bval', '.bvec']

which you can override in `pnldash/config.py`. Once this cached file exists
`pnldash status` will use this file instead of crawling your project directory
again, since this may take a long time. If you know that more files have been
added to your project directory, or some files have been removed, you can update
this file by running

    pnldash find

Similarly, `.pnldash/paths.csv` and `.pnldash/params.csv` are reused by `pnldash
status` once they have been generated. These cached csvs record all the pipeline
paths and parameters specified in your `pnldash.yml` file, and may take a while
to generate if your project directory is large. When you know that more
pipeline files have been made, update them by running

    pnldash makepaths

## Extra files

One of the main goals of `pnldash` is to find large extraneous files that are not
essential to your project.  This is accomplished by subtracting all your pipeline
paths from all the large image files that are found.  To see these extra files,
run

    pnldash extra

If you see some paths that should be part of your project, edit `pnldash.yml`
and add them to your pipelines. `pnldash extra` should no longer show them.

## Typical Workflow

Typically, you'll write `pnldash.yml` and then run `pnldash status` and
`pnldash extra` to see what extraneous files are detected, and to get an overview
of your pipeline outputs.  Usually you'll notice some files that should
be part of your project, so you'll edit `pnldash.yml` and add those paths to one
or more of your pipelines, and rerun `pnldash extra`.  Once you're satisfied
that all of your project files are accounted for, you can begin to delete some of
the extraneous files.  For example, to delete all the extraneous vtk files:

    pnldash extra | grep -E '\.vtk$' | xargs rm

To update the result of `pnldash extra` and `pnldashs status` you need to update
the cached `.pnldash/all_image_files.txt` by running `pnldash find`. Then
`pnldash status` and `pnldash extra` will no longer include the extraneous
files.

So, a typical workflow looks like this:

    pnldash init
    # edit pnldash.yml
    pnldash status
    pnldash extra
    # delete some files, add some paths to pnldash.yml
    pnldash find  # because you deleted some files
    pnldash extra
    # delete some files
    pnldash find
    pnldash extra
    pnldash status

Once you're satisfied, you can submit your project to the central database:

    pnldash push


## The Central Database

The central database stores the information from every project that has used
`pnldash push`.  You can see a list of projects by running

    pnldash db list

The main point of the database is to get a dashboard summarizing every project's
pipelines, parameters, and disk usage efficiency. To generate the dashboard, run


    pnldash db report

This makes `pnldashboard.html` which you can open in a browser. To generate
and open the dashboard in one command, run:


    pnldash db open # or,
    pnldash db open -r  # overwrites current pnldashboard.html if it exists


## Listing Pipeline Files

You can list your pipeline paths using the `ls` command, e.g.

    pnldash ls dwi

This lists the existing file paths for the `dwi` template path in all your
pipelines.  To list results for a particular pipeline, use the `-p` flag:

    pnldash ls dwi -p 2  # lists dwi paths for second pipeline in pnldash.yml

  If you'd like to get a list of missing output, use the `-x` flag:

    pnldash ls -x dwi

For all output, existing and missing, use `-a`:

    pnldash ls -a dwi

Sometimes you just want the list of case ids for which a particular
output exists (or is missing), or perhaps you want the case ids alongside
their output paths.  You can do that as follows:

    pnldash ls -s dwi # prints <caseid> for existing paths
    pnldash ls -c dwi  # prints <caseid>,<path> for existing paths

You can combine flags together. To get the csv of all missing `dwi` paths, you would run

    pnldash ls -cx dwi

The `ls` command helps you inspect your generated data or use it for other types of
processing by piping its results to other commands. Say you want to get the
space directions of all your raw DWI's, you could do the following:

    pnldash ls dwi | unu head | grep 'space directions'

NOTE: the `ls` interface is exactly the same as it
for [pnlpipe](https://github.com/reckbo/pnlpipe).

## Shell Environment

You can export your template paths to the shell using `pnldash env`:

    pnldash env

prints a Bash setup that exports the pipeline paths. Add it to your
environment as follows:


    eval `pnldash env`  # or
    eval $(pnldash env)
