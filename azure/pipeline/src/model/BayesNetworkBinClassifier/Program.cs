using System.Numerics;
using Microsoft.ML.Probabilistic.Collections;
using Microsoft.ML.Probabilistic.Factors;
using Microsoft.ML.Probabilistic.Learners;
using Microsoft.VisualBasic.FileIO;
using System.Text.Json;
using Microsoft.ML.Probabilistic.Distributions;
using Microsoft.ML.Probabilistic.Learners.Mappings;


class Program
{

    public static string? SourceFolder { get; set; }
    public static string? OutputFolder { get; set; }
    public static int? Batch { get; set; }
    public static string[] AllOriginalFeatures { get; set; }
    public static string[]? Features { get; set; }
    public static List<Instance> Data = new List<Instance>();
    public static int[] BaseIndexes; 
    public static string Mode = "inference";
    
    public static List<string> Label = new List<string>();

    public static List<bool> GenerateIsSparseBitMask(string[] features)
    {
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

    /*
    static void Evaluate(DataMapping mapping, IBayesPointMachineClassifier<
                    List<Instance>,
                    int, 
                    List<string>, 
                    bool, 
                    Bernoulli, 
                    BayesPointMachineClassifierTrainingSettings, 
                    BinaryBayesPointMachineClassifierPredictionSettings<bool>> 
                classifier)

    {
        List<Instance> TestSet = new List<Instance>();
        Label = new List<string>();
        string[] train_files = Directory.GetFiles(SourceFolder, "test*.csv");
        string[] lines = File.ReadAllLines(train_files[0]);
        var all_original_features = lines[0].Split(",");
        var isSparseBitmask = GenerateIsSparseBitMask(Features).ToArray();

        //Get data from all files
        double[] row_dbl = new double[isSparseBitmask.Length];
        // double[] row_dbl = new double[Features.Length - 1];
        
        Console.WriteLine("Opening test set files...");
        foreach(string file in train_files)
        {
            Console.WriteLine("Opening test file " + file);
            lines = File.ReadAllLines(file);

            foreach(string line in lines.Skip(1))
            {
                List<string> row_str = new List<string>(line.Split(","));
                // features_to_skip
                row_str.SkipLast(1).ForEach( (int i, string data) => 
                        {
                            var feature = all_original_features[i];
                            if (Array.Find(Features, x => x == feature) != null)
                                row_dbl[Features.FindIndex(x => x == feature)] = Double.Parse(data) + 1;
                        });
                
                // row_str.SkipLast(1).ForEach( (int i, string data) => Console.WriteLine(i + " " + data));

                
                Instance inst = new Instance(row_dbl, BaseIndexes, isSparseBitmask, row_str.Last());
                TestSet.Add(inst);
                // Get label at the end of the row
                Label.Add(row_str.Last());
            }
        }

        // var evaluatorMapping = mapping.ForEvaluation();  
        var evaluatorMapping = new EvaluatorMapping();
        var evaluator = new ClassifierEvaluator  
            <List<Instance>,   
            int,   
            List<string>,   
            bool>(evaluatorMapping);

        Console.WriteLine("Start predict distribution");
        
        var savedclassifier = BayesPointMachineClassifier.LoadBinaryClassifier  
            <List<Instance>, int, List<string>, bool, Bernoulli>("bpm.bin");

        var predictions = savedclassifier.PredictDistribution(TestSet);  
        var estimates = savedclassifier.Predict(TestSet);  
        
        //All errors
        double errorCount = evaluator.Evaluate(  
            TestSet, Label, estimates, Metrics.ZeroOneError);  


        var predictionsDictionary = new List<Dictionary<bool, double>>();
        predictions.ForEach( p => 
                {   
                    var dict = new Dictionary<bool, double>();
                    dict.Add(true,  p.GetProbTrue());
                    dict.Add(false, p.GetProbFalse());
                    predictionsDictionary.Add(dict);
                }
        );

        var options = new JsonSerializerOptions
            {
                IncludeFields = true,
            };
        

        var confusionMatrix = evaluator.ConfusionMatrix(TestSet, estimates);  
        var jsonString = JsonSerializer.Serialize(confusionMatrix, options);
        File.WriteAllText(Path.Join(OutputFolder, "confusionMatrix.json"), jsonString);

        var precisionTrue = confusionMatrix.Precision(true);
        var precisionFalse = confusionMatrix.Precision(false);
        var accuracyTrue = confusionMatrix.Accuracy(true);
        var accuracyFalse = confusionMatrix.Accuracy(false);
        var recallTrue = confusionMatrix.Recall(true);
        var recallFalse = confusionMatrix.Recall(false);

        int falsePositive = 0;
        int falseNegative = 0;
        for (int i = 0; i < TestSet.Count(); i++)
        {
            if (TestSet[i].label == "normal" && !estimates[i]) //we predicted attack, but it is not
            {
                    falseNegative++; 
            }
            if (TestSet[i].label == "attack" && estimates[i]) //we predicted normal, but it is an attack
            {
                    falsePositive++; 
            }
        }

        var rocCurve = evaluator.ReceiverOperatingCharacteristicCurve(  
            true, TestSet, predictionsDictionary);  

        var precisionRecallCurve = evaluator.PrecisionRecallCurve(  
            true, TestSet, predictionsDictionary);  

        var calibrationCurve = evaluator.CalibrationCurve(  
            true, TestSet, predictionsDictionary);

        var auc = evaluator.AreaUnderRocCurve(  
            true, TestSet, predictionsDictionary);

        Console.WriteLine("Total estimates: " + estimates.Count() + " error count: " +  errorCount + " area under curve: " + auc);

        jsonString = JsonSerializer.Serialize(rocCurve, options);
        File.WriteAllText(Path.Join(OutputFolder, "rocCurve.json"), jsonString);
        jsonString = JsonSerializer.Serialize(precisionRecallCurve, options);
        File.WriteAllText(Path.Join(OutputFolder, "precisionRecallCurve.json"), jsonString);
        jsonString = JsonSerializer.Serialize(calibrationCurve, options);
        File.WriteAllText(Path.Join(OutputFolder, "calibrationCurve.json"), jsonString);

        

    }
    */
    static void Run()
    {
        
        string[] train_files = Directory.GetFiles(SourceFolder, "train*.csv");

        var isSparseBitmask = GenerateIsSparseBitMask(Features).ToArray();

        //Get data from all files
        double[] row_dbl = new double[Features.Length];
        
        
        Console.WriteLine("Opening files...");
        foreach(string file in train_files)
        {
            Console.WriteLine("Opening train file " + file);

            var lines = File.ReadAllLines(file);

            foreach(string line in lines.Skip(1))
            {
                List<string> row_str = new List<string>(line.Split(","));
                // features_to_skip
                row_str.SkipLast(1).ForEach( (int i, string data) => 
                        {
                            var feature = AllOriginalFeatures[i];
                            if (Array.Find(Features, x => x == feature) != null)
                                row_dbl[Features.FindIndex(x => x == feature)] = Double.Parse(data) + 1;
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
        var mapping = new DataMapping(BaseIndexes[BaseIndexes.Length-1]+2);  
        // var mapping = new DataMapping(BaseIndexes[BaseIndexes.Length-1]+1);  
        var classifier = BayesPointMachineClassifier.CreateBinaryClassifier(mapping);
        Console.WriteLine("Training classifier");
        classifier.Train(Data, Label);
        classifier.Save(Path.Join(SourceFolder, "bpm.bin"));
        Console.WriteLine("Done");

    }

    static void Main(string[] args)
    {
        //Parsing program arguments
        string usageMessage = "Usage: dotnet run -s source_folder -o output_folder [-b batch] [-m inference|evaluate|both]";
        
        if (args.Length != 4 && args.Length != 6 && args.Length != 8)
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
                    case "-m":
                        i += 1;
                        if (args[i] != "inference" && args[i] != "evaluate" && args[i] != "both")
                        {
                            Console.WriteLine($"Argument {args[i]} error!");
                            Console.WriteLine(usageMessage);
                            Environment.Exit(1);
                            break;
                        }
                        Mode = args[i];
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
        
        if (Directory.Exists(SourceFolder))
        {
            // SparseFeatureIndex? sparseFeatureIndex = null;
            //First of all, sparse feature max index
            string jsonFile = Directory.GetFiles(SourceFolder, "sparse_features_max_index.json")[0];
            string[] jsonLines = File.ReadAllLines(jsonFile);
            string jsonString = string.Join(string.Empty, jsonLines);
            var sparseFeatureIndex = JsonSerializer.Deserialize<Dictionary<string, Dictionary<string, int>>>(jsonString);
            
            //Second, the features we actually need (from filter_features.py)
            Features = new string[0];
            if (File.Exists(Path.Join(SourceFolder, "feature_list.txt"))) 
            {
                var feat_filt_file = Directory.GetFiles(SourceFolder, "feature_list.txt")[0];
                Features = File.ReadAllLines(feat_filt_file)[0].Split(",");
                Console.WriteLine($"Using only the following {Features.Length} features:");
                foreach(string feature in Features)
                {
                    Console.Write(feature + " ");
                }
                Console.WriteLine("");
                
            }
            else
            {
                Console.WriteLine("WARNING: filter_output folder not found, consider using filter_features.py");
            }
            
            //Get random file for feature ist
            string random_file = Directory.GetFiles(SourceFolder, "train.0.csv")[0];

            string[] lines = File.ReadAllLines(random_file);

            AllOriginalFeatures = lines[0].Split(",");
            
            //Get features from the first file
            if (Features.Length == 0){
                Features = lines[0].Split(",");
            }
            
            var isSparseBitmask = GenerateIsSparseBitMask(Features).ToArray();

            //BaseIndexes are the index value of the features computed in the following way: e.g. suppose SrcAddr are 1..10, SrcPort are 1..100
            //and the features are, in order, SrcAddr, SrcBytes, SrcPort.
            //then BaseIndexes will contain: [0, 10, 11]
            //and the actual feature_i index will be computed as 0 + BaseIndex[feature_i] is the feature was not one hot encoded,
            //otherwise value[feature_i] + BaseIndex[feature_i] since values of one hot encoded features are always 1, and what is 
            //actually saved in the csv it's their index (e.g. SrcAddr1 -> 1, SrcAddr2 -> 2, ..., SrcAddr10 -> 10)
            BaseIndexes = new int[isSparseBitmask.Length];
            var cumulative = 0;
            BaseIndexes[0] = 0;

            Console.WriteLine("BaseIndexes.Length: " + BaseIndexes.Length + " Features.Count(): " + Features.Count());

            for(int i = 0; i < Features.Length; i++)
            {
                BaseIndexes[i] = cumulative;
                // if (Features[i] == "label")
                //     continue;
                if (!isSparseBitmask[i])
                {
                    cumulative++;
                }
                else
                {
                    cumulative += sparseFeatureIndex[Features[i]]["max"] + 1;
                }
            }
            
            BaseIndexes[BaseIndexes.Length-1] = cumulative;


        }
        else
        {
            Console.WriteLine($"Directory not found: {SourceFolder}");
        }

        switch(Mode)
        {
            case "inference":
                Run();
                break;
            case "evaluate":
                Evaluate.Run(SourceFolder, OutputFolder);
                break;
            case "both":
                Run();
                Evaluate.Run(SourceFolder, OutputFolder);
                break;
            
            default:
                break;
        }
        
    }
}

