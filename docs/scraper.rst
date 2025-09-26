Why Playwright?
=====================

We initially used Selenium for our scraping tasks but encountered frequent timeout errors due to connection issues on the HPC cluster.
To address these issues, we transitioned to Playwright, based on a recommendation from a previous team member who is no longer actively 
involved in this project. If future requirements change, moving to a different platform remains an option with justifiable reasoning.

It's worth noting that Playwright was not originally designed as a dedicated web scraping framework—its primary purpose is end-to-end 
browser testing. However, its ability to control modern browsers programmatically makes it well-suited for scraping in cases where websites 
rely heavily on JavaScript or dynamic rendering.

