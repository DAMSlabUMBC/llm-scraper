CHIP HCP Cluster
=====================

The CHIP cluster provides both CPU and GPU resources:  
    - Use **CPU nodes** for lightweight tasks (e.g., web scraping).  
    - Use **GPU nodes** for compute-intensive tasks (e.g., entity extraction, validation, triple generation).  

Official UMBC Documentation
---------------------------
    - https://umbc.atlassian.net/wiki/spaces/faq/pages/1082589207/UMBC+HPCF+-+chip

DAMS Documentation
------------------
    - https://www.notion.so/dams-umbc/CHIP-HPC-Tutorial-1e4a970653c3809f9526d20c03e4bcef

Access
------
.. code-block:: bash

   ssh <username>@chip.rs.umbc.edu

Job Submission
--------------
We provide preconfigured batch scripts in the ``batch_scripts/`` folder. Submit jobs as follows:

.. code-block:: bash

   sbatch batch_scripts/<file_name>.sh

Example Batch Script
--------------------
.. code-block:: bash

   #!/bin/bash

    #SBATCH --job-name=hello_world          # Job name
    #SBATCH --output=slurm.out              # Output file name
    #SBATCH --error=slurm.err               # Error file name
    #SBATCH --cluster=chip-cpu              # Requesting a job on chip CPU cluster
    #SBATCH --account=pi_userid             # Account
    #SBATCH --partition=general             # Partition
    #SBATCH --qos=short                     # Queue
    #SBATCH --time=00:05:00                 # Time limit 
    #SBATCH --mem=4G                        # Memory requested
    #SBATCH --nodes=1                       # Number of nodes
    #SBATCH --ntasks-per-node=1             # MPI processes per node

    ./hello_world

Helpful Commands
----------------
- ``sinfo`` - view queue/partition status  
- ``sbatch`` - submit a job  
- ``squeue`` - check queued/running jobs  
- ``scontrol show job <jobID>`` - view job details  
- ``scancel <jobID>`` - cancel a job  
- ``cat slurm-<jobID>.out`` - view job output  

Notes
-----
- Do not run heavy jobs directly on the login node.  
- Default job logs are saved in the directory where the script was submitted.  
- Check DAMS and UMBC documentation for prebuilt configs and environment setup.  