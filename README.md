*pnldash* is a tool for tracking your data processing projects.  Once you
define a meta data file for your project directory it can print out a report
summarizing data analysis pipelines including disk usage statistics.
Individual project information are pushed to a central database, and an html
dashboard is generated for all your projects.

# Setup

cd /software/dir
git clone https://github.com/reckbo/pnldash
export PNLDASH_DB=/software/dir/pnldash/db
export PATH=$PATH:/software/dir/pnldash/scripts
installdb.py  # makes $PNLDASH_DB directory and copies pnldashboard.Rmd to it


# Quick Walkthrough
