using System.Numerics;
using Microsoft.ML.Probabilistic.Collections;
using Microsoft.ML.Probabilistic.Factors;
using Microsoft.ML.Probabilistic.Learners;
using Microsoft.VisualBasic.FileIO;



class Program
{

    public static string? SourceFolder { get; set; }
    public static string? OutputFolder { get; set; }
    public static int? Batch { get; set; }

    private static string[]? Features { get; set; }
    private static List<double[]> Data = new List<double[]>();
    
    private static List<string> Label = new List<string>();

    static void Main(string[] args)
    {
        //Parsing program arguments
        string usageMessage = "Usage: dotnet run -s source_folder -o output_folder [-b batch]";
        
        if (args.Length != 4 && args.Length != 6)
        {
            Console.WriteLine(usageMessage);
            Environment.Exit(1);
        }
        else
        {
            Batch = 0;
            for(int i = 0; i < args.Length; i++)
            {
                switch(args[i])
                {
                    case "-s":
                        SourceFolder = args[++i];
                        break; 
                    case "-o":
                        OutputFolder = args[++i];
                        break; 
                    case "-b":
                        Batch =  Int32.Parse(args[++i]);
                        break;

                    default:
                        Console.WriteLine(usageMessage);
                        Environment.Exit(1);
                        break;
                    
                }
            }
            if (SourceFolder == null || OutputFolder == null)
            {
                Console.WriteLine(usageMessage);
                Environment.Exit(1);
            }
        }
        //Ok, loading data
        if (Directory.Exists(SourceFolder))
        {
            string[] files = Directory.GetFiles(SourceFolder, "*.csv");

            string[] lines = File.ReadAllLines(files[0]);
            
            //Get features from the first file
            Features = lines[0].Split(",");
            
            //Get data from all files
            double[] row_dbl = new double[Features.Length - 1];

            foreach(string file in files)
            {
                lines = File.ReadAllLines(file);

                foreach(string line in lines.Skip(1))
                {
                    string[] row_str = line.Split(",");
                    row_str.SkipLast(1).ForEach( (int i, string data) => 
                            {
                                row_dbl[i] = Double.Parse(data) + 1;
                            });
                    // row_str.SkipLast(1).ForEach( (int i, string data) => Console.WriteLine(i + " " + data));
                    Data.Add(row_dbl);
                    // Get label at the end of the row
                    Label.Add(row_str.Last());
                }
            }

            //Training the classifier
            // Create the Bayes Point Machine classifier from the mapping  
            var mapping = new DataMapping();  
            var classifier = BayesPointMachineClassifier.CreateBinaryClassifier(mapping);
            classifier.Train(Data, Label);

        }
        else
        {
            Console.WriteLine($"Directory not found: {SourceFolder}");
        }

    }
}

