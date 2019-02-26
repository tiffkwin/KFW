# KFWX Data Analysis Toolkit

> This is a toolkit for **MacOS X** that automatically analyzes data for assays.

1. Installing KFWX
2. Tools Available
3. Using the Data Analysis Tools (Tools 1-3)
4. Using the Merge Tools (Tools 4-6)
5. Understanding the Output

## Installing KFWX
1. Ensure that Python 2.7 is installed. Python 2.7 ***should*** already be installed with MacOS X.
    * Open your Terminal and run the command `python --version`.
    * If the response is `Python 2.7.XX` then you have the correct version of Python installed. Otherwise, you should follow the installation instructions at https://docs.python-guide.org/starting/install/osx/#install-osx.
2. Make sure that pip is installed.
    * Run the command `pip --version`. 
    * If the response is `pip XX.X from ... (python 2.7)` then you have the correct version of pip installed. Otherwise, you should follow the installation instructions at https://ehmatthes.github.io/pcc/chapter_12/installing_pip.html#pip-on-os-x.
3. Install kfwx from the Python Package Index with pip.
    * Type the command `pip install --upgrade kfwx`.
4. You must have also some other Python modules installed.
    * matplotlib
    * pandas
    * seaborn
    * xlrd
    * openpyxl
    Use the command `pip install matplolib pandas seaborn xlrd openpyxl`. This may take a few minutes to finish.

## Tools Available
1. Membrane Potential
2. NADH Redox
3. H2O2
4. Membrane Potential Merge
5. NADH Redox Merge
6. H2O2 Merge

## Using the Data Analysis Tools (Tools 1-3)
1. Place the raw data files (.txt) to be analyzed in a folder.
2. Open the command line
3. Navigate to the folder 
    * e.g. if folder path is users/data_analysis, then type the command `cd users/data_analysis`
4. Type command `python -m kfwx` to run the toolkit and then follow the instructions provided

## Using the Merge Tools (Tools 4-6)
1. Place the excel files (.xlsx) to be merged in a folder.
2. Open the command line
3. Navigate to the folder 
    * e.g. if folder path is users/data_analysis, then type the command `cd users/data_analysis`
4. Type command `python -m kfwx` to run the toolkit and then follow the instructions provided

## Understanding the Output
This section explains in detail the significance of the results of the data analysis.

### Membrane Potential
1. **Metadata Sheet** - This sheet hosts information about the experiment itself
    * ID - The experimental ID.
    * Standard Curve - A true or false value indicating whether or not the standard curve calculation was used.
    * Slope - The slope value entered by the researcher to be used in calculations.
    * Y-Intercept - The y-intercept value entered by the researcher to be used in calculations.
    * Substrates - A column containing the list of substrates used in the experiment.
    * Additions - A column containing the list of additions used in the experiment.
    * Date - The date the analysis was run in the form YYYY-MM-DD.
2. **Raw Data** - The raw data taken from the lab tools.
    * The data is in the form  X | Y | X |...
3. **Averaged Raw Data** - The average membrane potential for 3-minute (i.e., 180 seconds) increments in each data set. Each data set is annotated with the buffer conditions of the assay at that time.
4. **Corrected Raw Data** - The same data as the Average Raw Data sheet, but with an additional correction calculation which divides each average membrane potential by the the average membrane potential for Ala.
5. **Standard Curve Data** - The results of the standard curve calculation on the raw data.
    * The data is in the form  X | Y | X |...
6. **Averaged Standard Curve** - The results of the standard curve calculation on the averaged data.

### NADH Redox
1. **Metadata Sheet** - This sheet hosts information about the experiment itself.
    * ID - The experimental ID.
    * Substrates - A column containing the list of substrates used in the experiment.
    * Additions - A column containing the list of additions used in the experiment.
    * Date - The date the analysis was run in the form YYYY-MM-DD.
2. **Raw Data** - The raw data taken from the lab tools. 
    * The data is in the form  X | Y | X |...
3. **Stripped Data** - Contains only the columns that correspond to the NADH data points. 
    * The data is in the form  X | Y | X |...
4. **Reduced Data** - The same data as the Stripped Data sheet, but with an additional reduction calculation.
    * `y_new = (y_old-min)/(max-min)*100`
5. **Averaged Reduced Data** - The averages of the reduced data for 3-minute (i.e., 180 seconds) increments in each data set. Each data set is annotated with the buffer conditions of the assay at that time.

### H2O2
1. **Metadata Sheet** - This sheet hosts information about the experiment itself
    * ID - The experimental ID.
    * Standard Curve - A true or false value indicating whether or not the standard curve calculation was used.
    * Slope - The slope value entered by the researcher to be used in calculations.
    * Y-Intercept - The y-intercept value entered by the researcher to be used in calculations.
    * Substrates - A column containing the list of substrates used in the experiment.
    * Additions - A column containing the list of additions used in the experiment.
    * Mitochondria - The amount of mitochondria use (in milligrams).
    * Date - The date the analysis was run in the form YYYY-MM-DD.
2. **Raw Data** - The raw data taken from the lab tools.
    * The data is in the form  X | Y | X |...
3. **Slopes Data** - The slope for 3-minute (i.e., 180 seconds) increments in each data set. Each data set is annotated with the buffer conditions of the assay at that time.
4. **Corrected Slopes** - The same data as the Slopes sheet, but with an additional correction calculation which divides each slope value by the mg of mitochondria used.
5. **Standard Curve** - The results of the standard curve calculation on the Raw Data.
6. **Standard Curve Slopes** - The results of the standard curve calculation on the Slopes Data.
7. **Corrected Standard Curve Slopes** - The results of the correction calculation on the Standard Curve Slopes data.

### Membrane Potential Merge
Combines data from all of the Averaged Standard Curve sheets in the Membrane Potential data analysis Excel files. Each row corresponds to a substrate. The Mean and SEM is calculated for each row.

### NADH Redox Merge
Combines data from all of the Averaged Reduced Data sheets in the NADH Redox data analysis Excel files. Each row corresponds to a substrate. The Mean and SEM is calculated for each row.

### H2O2 Merge
Combines data from all of the Corrected Standard Curve Slopes sheets in the H2O2 data analysis Excel files. Each row corresponds to a substrate. The Mean and SEM is calculated for each row.

