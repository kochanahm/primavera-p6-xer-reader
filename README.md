# Primavera P6 XER Reader
A Flask web app to read Primavera P6 XER files and gives insight about the data

# Upload a File
Home page has a file uploader that accepts only a file which has a XER extension. If file is uploaded successfully, clickable button will be activated to navigate to the Project Selection page.

# Project Selection
Since XER file might have more than one project, this page will show a combobox to select a project

# Dashboard
Main window for displaying the statistics and diagnostics for the project. It has a side menu that has 3 tabs, "Statistics, Diagnostics and About"

# Metrics Details
Within the "Diagnostics" tab, metrics for Tasks and Milestones are summarized in tables. In order to see the details, click to "Show Details" button on the toolbar. It will navigate to a new browser tab to show the results. Users can download the results to Excel or save as PNG image.
