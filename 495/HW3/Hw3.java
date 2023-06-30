import java.io.Console;
import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.fs.FileSystem;


public class Hw3 {


    /*** input file path, input file is a tsv file , columns:
     * 0 : name
     * 1 : rating
     * 2 : genre
     * 3 : year
     * 4 : released
     * 5 : score
     * 6 : votes
     * 7 : director
     * 8 : writer
     * 9 : star
     * 10 : country
     * 11 : budget
     * 12 : gross
     * 13 : company
     * 14 : runtime
     */
    private static String input;

    // output file path
    private static String output;

    /***
     * total: The amount of time (in minutes) it would take to watch every movie in the dataset, back to back (total)
     * average: The average runtime of the movies (in minutes) (average)
     * employment: How many times each actor has been top-billed (starred) in a movie (employment)
     * ratescore: Average number of IMDb votes on G, PG, PG-13 and R rated movies (ratescore)
     • genrescore: The average IMDb score of genres that have more than 9 movies (genrescore)
     ***/
    private static String operation;


    public static void parse(String[] args) throws InterruptedException, IOException {
        if (args.length != 3) {
            System.out.println("Usage: java Hw3 <input> <output> <operation>");
            System.exit(1);
        }
        operation = args[0];
        input = args[1];
        output = args[2];
    }

    public static class TotalMapper extends Mapper<Object, Text, Text, DoubleWritable> {
        private final Text total = new Text("total");

        public void map(Object key, Text value, Context context) throws IOException, InterruptedException {

            // split the line into columns
            String[] columns = value.toString().split("\t");
            // do not include the first line
            if (columns[0].equals("name")) {
                return;
            }

            // check if the runtime is empty
            if (columns[14].equals("null")) {
                return;
            }

            // get the runtime
            double runtime = Double.parseDouble(columns[14]);

            // write the runtime to the context
            context.write(total, new DoubleWritable(runtime));

        }
    }

    public static class TotalReducer extends Reducer<Text, DoubleWritable, Text, DoubleWritable> {
        private final Text total = new Text("total");

        public void reduce(Text key, Iterable<DoubleWritable> values, Context context) throws IOException, InterruptedException {
            double sum = 0.0;
            for (DoubleWritable val : values) {
                sum += val.get();
            }
            context.write(total, new DoubleWritable(sum));
        }
    }

    public static class AverageReducer extends Reducer<Text, DoubleWritable, Text, DoubleWritable> {
        private final Text average = new Text("average");

        public void reduce(Text key, Iterable<DoubleWritable> values, Context context) throws IOException, InterruptedException {
            double sum = 0.0;
            int count = 0;
            for (DoubleWritable val : values) {
                sum += val.get();
                count++;
            }
            sum = sum / count;
            context.write(average, new DoubleWritable(sum));
        }
    }

    public static class EmploymentMapper extends Mapper<Object, Text, Text, IntWritable> {

        private final IntWritable one = new IntWritable(1);

        public void map(Object key, Text value, Context context) throws IOException, InterruptedException {

            // split the line into columns
            String[] columns = value.toString().split("\t");
            // do not include the first line
            if (columns[0].equals("name")) {
                return;
            }
            // check if the star is empty
            if (columns[9].equals("null")) {
                return;
            }
            String star = columns[9];
            context.write(new Text(star), one);

        }
    }

    public static class EmploymentReducer extends Reducer<Text, IntWritable, Text, IntWritable> {

        public void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
            int sum = 0;
            for (IntWritable val : values) {
                sum += val.get();
            }
            context.write(key, new IntWritable(sum));
        }
    }

    public static class RatescoreMapper extends Mapper<Object, Text, Text, DoubleWritable> {

        private final Text G = new Text("G");
        private final Text PG = new Text("PG");
        private final Text PG13 = new Text("PG-13");
        private final Text R = new Text("R");

        public void map(Object key, Text value, Context context) throws IOException, InterruptedException {

            // split the line into columns
            String[] columns = value.toString().split("\t");
            // do not include the first line
            if (columns[0].equals("name")) {
                return;
            }
            // check if the rating or votes is empty
            if (columns[1].equals("null") || columns[6].equals("null")) {
                return;
            }

            String rating = columns[1];
            double votes = Double.parseDouble(columns[6]);

            switch (rating) {
                case "G":
                    context.write(G, new DoubleWritable(votes));
                    break;
                case "PG":
                    context.write(PG, new DoubleWritable(votes));
                    break;
                case "PG-13":
                    context.write(PG13, new DoubleWritable(votes));
                    break;
                case "R":
                    context.write(R, new DoubleWritable(votes));
                    break;
                default:
                    break;
            }

        }
    }

    public static class RatescoreReducer extends Reducer<Text, DoubleWritable, Text, DoubleWritable> {

        public void reduce(Text key, Iterable<DoubleWritable> values, Context context) throws IOException, InterruptedException {
            double sum = 0.0;
            int count = 0;
            for (DoubleWritable val : values) {
                sum += val.get();
                count++;
            }
            sum = sum / count;
            context.write(key, new DoubleWritable(sum));
        }
    }

    public static class GenreMapper extends Mapper<Object, Text, Text, DoubleWritable> {
        private DoubleWritable score = new DoubleWritable();


        public void map(Object key, Text value, Context context) throws IOException, InterruptedException {

            // split the line into columns
            String[] columns = value.toString().split("\t");
            // do not include the first line
            if (columns[0].equals("name")) {
                return;
            }
            // check if the genre or score is empty
            if (columns[2].equals("null") || columns[5].equals("null")) {
                return;
            }
            String genre = columns[2];
            double score = Double.parseDouble(columns[5]);

            context.write(new Text(genre), new DoubleWritable(score));
        }
    }

    public static class GenreReducer extends Reducer<Text, DoubleWritable, Text, DoubleWritable> {

        public void reduce(Text key, Iterable<DoubleWritable> values, Context context) throws IOException, InterruptedException {
            double sum = 0.0;
            int count = 0;
            for (DoubleWritable val : values) {
                sum += val.get();
                count++;
            }
            // if the genre has more than 9 movies, then write the average score
            if (count > 9){
                sum = sum / count;
                context.write(key, new DoubleWritable(sum));
            }

        }
    }


    public static void main(String[] args) throws IOException, InterruptedException, ClassNotFoundException {

        parse(args);

        Configuration conf = new Configuration();

        Job job = Job.getInstance(conf, "Hw3");

        switch (operation) {
            case "total":
                job.setJarByClass(Hw3.class);
                job.setMapperClass(TotalMapper.class);
                job.setReducerClass(TotalReducer.class);
                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(DoubleWritable.class);
                FileInputFormat.addInputPath(job, new Path(input));
                FileOutputFormat.setOutputPath(job, new Path(output));
                System.exit(job.waitForCompletion(true) ? 0 : 1);
                break;
            case "average":
                job.setJarByClass(Hw3.class);
                job.setMapperClass(TotalMapper.class);
                job.setReducerClass(AverageReducer.class);
                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(DoubleWritable.class);
                FileInputFormat.addInputPath(job, new Path(input));
                FileOutputFormat.setOutputPath(job, new Path(output));
                System.exit(job.waitForCompletion(true) ? 0 : 1);
                break;
            case "employment":
                job.setJarByClass(Hw3.class);
                job.setMapperClass(EmploymentMapper.class);
                job.setReducerClass(EmploymentReducer.class);
                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(IntWritable.class);
                FileInputFormat.addInputPath(job, new Path(input));
                FileOutputFormat.setOutputPath(job, new Path(output));
                System.exit(job.waitForCompletion(true) ? 0 : 1);
                break;
            case "ratescore":
                job.setJarByClass(Hw3.class);
                job.setMapperClass(RatescoreMapper.class);
                job.setReducerClass(RatescoreReducer.class);
                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(DoubleWritable.class);
                FileInputFormat.addInputPath(job, new Path(input));
                FileOutputFormat.setOutputPath(job, new Path(output));
                System.exit(job.waitForCompletion(true) ? 0 : 1);
                break;
            case "genrescore":
                job.setJarByClass(Hw3.class);
                job.setMapperClass(GenreMapper.class);
                job.setReducerClass(GenreReducer.class);
                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(DoubleWritable.class);
                FileInputFormat.addInputPath(job, new Path(input));
                FileOutputFormat.setOutputPath(job, new Path(output));
                System.exit(job.waitForCompletion(true) ? 0 : 1);
                break;
            default:
                System.out.println("Invalid operation");
                System.exit(1);
        }

    }
}
