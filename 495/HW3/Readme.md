README for Hw3 Hadoop MapReduce
===============================
I've applied preprocessing to csv file since there are missing data and ',' char is used in some values. Therefore, I've converted csv file to tsv file and fill the blank values with "null" string using pandas.

Firstly, this command should be executed to convert csv file to tsv file:
```bash
python3 csv2tsv.py movies.csv movies.tsv
```
Then, tsv file should be uploaded to hdfs:
```bash
hadoop fs -put movies.tsv /user/{username in hdfs file system}
```
After that, java files should be compiled as written in the homework pdf:
```bash
hadoop com.sun.tools.javac.Main *.java
```
After that, jar file should be created:
```bash
jar cf hw3.jar *.class
```
Finally, jar file should be executed with tsv file as input and output directory as output:
```bash
hadoop jar Hw3.jar Hw3 {operation} movies.tsv {output_folder}
```

