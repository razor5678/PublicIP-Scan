**Description: **

Python script looks at the default Insight "Compute Instance With Public IP Attached (backoffice:536)" and fetches all the public IP's from InsightCloudSec. It then runs a scan for a particular port (tested for TCP 22 and 3389) and validates if these IP's are actually accessible over the internet. An InsightCloudSec data collection is created with the current timestamp is created with a list of Public IP's which are NOT accessible over the internet. This data collection can then be used to ignore Public IP's which are not accessible when using an appropriate Insight

**Prerequisites - **

1. Python3 
2. Org admin user in InsightCloudSec with API Keys. 


**Getting Started**

1. Download the script
2. Change the base_url variable
3. Add an InsightCloudSec apikey variable
4. (Optional) Change the scan_port variable and datacollection_name variable (Note: Currently tested only for TCP Port 22 and 3389)
5. Run the script on your workstation - workstation will need public internet access.
6. Upon completion - a data collection will be created with all the public IP's which are NOT accessible over the internet for the specified port in Step 4. The name of the data collection can be found in the output of the script.
7. Create a custom insight using the following query filters
     Instance With Public IP Attached - Select the data collection created in step 6 (This will ignore the IP's which are not accessible over the internet)
     Instance Exposing Public RDP



   



   
