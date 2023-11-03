using System.Numerics;
using Microsoft.ML.Probabilistic.Collections;
using Microsoft.ML.Probabilistic.Factors;
using Microsoft.ML.Probabilistic.Learners;
using Microsoft.VisualBasic.FileIO;
using System.Text.Json;


class Program
{

    public static string? SourceFolder { get; set; }
    public static string? OutputFolder { get; set; }
    public static int? Batch { get; set; }

    private static string[]? Features { get; set; }
    private static List<Instance> Data = new List<Instance>();
    private static int[] BaseIndexes; 
    
    private static List<string> Label = new List<string>();

    static List<bool> GenerateIsSparseBitMask(string featureString)
    {
        var features = featureString.Split(",");
        List<bool> bitmask = new List<bool>();
        foreach (string ft in features)
        {
            switch(ft)
            {
                case "SrcAddr":
                case "DstAddr":
                case "Sport":
                case "Dport":
                case "Proto":
                case "State":
                case "proto_state_and":
                    bitmask.Add(true);
                    break;
                default:
                    bitmask.Add(false);
                    break;
            }
        }

        return bitmask;
        
    }

    static void Main(string[] args)
    {
        //Parsing program arguments
        string usageMessage = "Usage: dotnet run -s source_folder -o output_folder [-b batch]";
        
        if (args.Length != 4 && args.Length != 6)
        {
            Console.WriteLine("Wrong number of args! " + args.Length + " used");
            foreach(string arg in args)
            {
                Console.Write($"{arg} ");
            }
            Console.WriteLine("");
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
                        Console.WriteLine($"Argument {args[i]} error!");
                        Console.WriteLine(usageMessage);
                        Environment.Exit(1);
                        break;
                    
                }
            }
            if (SourceFolder == null || OutputFolder == null)
            {
                Console.WriteLine("Error in source or output folder!");
                Console.WriteLine(usageMessage);
                Environment.Exit(1);
            }
        }
        //Ok, loading data
        
        
        if (Directory.Exists(SourceFolder))
        {
            // SparseFeatureIndex? sparseFeatureIndex = null;
            //First of all, sparse feature max index
            string jsonFile = Directory.GetFiles(SourceFolder, "sparse_features_max_index.json")[0];
            string[] jsonLines = File.ReadAllLines(jsonFile);
            string jsonString = string.Join(string.Empty, jsonLines);
            var sparseFeatureIndex = JsonSerializer.Deserialize<Dictionary<string, int>>(jsonString);
            
            //Second, the features we actually need (from filter_features.py) TODO

            //Then the actual data
            string[] files = Directory.GetFiles(SourceFolder, "*.csv");

            string[] lines = File.ReadAllLines(files[0]);
            
            //Get features from the first file
            var isSparseBitmask = GenerateIsSparseBitMask(lines[0]).ToArray();
            Features = lines[0].Split(",");

            //BaseIndexes are the index value of the features computed in the following way: e.g. suppose SrcAddr are 1..10, SrcPort are 1..100
            //and the features are, in order, SrcAddr, SrcBytes, SrcPort.
            //then BaseIndexes will contain: [0, 10, 11]
            //and the actual feature_i index will be computed as 0 + BaseIndex[feature_i] is the feature was not one hot encoded,
            //otherwise value[feature_i] + BaseIndex[feature_i] since values of one hot encoded features are always 1, and what is 
            //actually saved in the csv it's their index (e.g. SrcAddr1 -> 1, SrcAddr2 -> 2, ..., SrcAddr10 -> 10)
            BaseIndexes = new int[isSparseBitmask.Length - 1];
            var cumulative = 0;
            for(int i = 0; i < Features.Length; i++)
            {
                if (Features[i] == "label")
                    continue;
                BaseIndexes[i] = cumulative;
                if (!isSparseBitmask[i])
                {
                    cumulative++;
                }
                else
                {
                    cumulative += sparseFeatureIndex[Features[i]];
                }
            }

            //Get data from all files
            double[] row_dbl = new double[isSparseBitmask.Length - 1];
            // double[] row_dbl = new double[Features.Length - 1];

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
                    
                    Instance inst = new Instance(row_dbl, BaseIndexes, isSparseBitmask, row_str.Last());
                    Data.Add(inst);
                    // Get label at the end of the row
                    Label.Add(row_str.Last());
                }
            }

            //Training the classifier
            // Create the Bayes Point Machine classifier from the mapping  
            var mapping = new DataMapping(cumulative+1);  
            var classifier = BayesPointMachineClassifier.CreateBinaryClassifier(mapping);
            classifier.Train(Data, Label);

        }
        else
        {
            Console.WriteLine($"Directory not found: {SourceFolder}");
        }

    }
}

