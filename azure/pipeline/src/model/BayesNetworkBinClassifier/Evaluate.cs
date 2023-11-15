using System.Numerics;
using Microsoft.ML.Probabilistic.Collections;
using Microsoft.ML.Probabilistic.Factors;
using Microsoft.ML.Probabilistic.Learners;
using Microsoft.VisualBasic.FileIO;
using System.Text.Json;
using Microsoft.ML.Probabilistic.Distributions;
using Microsoft.ML.Probabilistic.Learners.Mappings;

class Evaluate
{

    static List<Instance> TestSet { get; set; }
    static List<string> Label { get; set; }
    static ClassifierEvaluator<List<Instance>, int, List<string>, bool> Evaluator { get; set; }
    static List<Dictionary<bool, double>> PredictionsDictionary { get; set; }
    static List<bool> Estimates { get; set; }
    static string SourceFolder { get ; set;}
    static string OutputFolder { get ; set;}

    public static void Run(string sourceFolder, string outputFolder)
    {
        
        SourceFolder = sourceFolder;
        OutputFolder = outputFolder;

        TestSet = new List<Instance>();
        Label = new List<string>();
        string[] train_files = Directory.GetFiles(SourceFolder, "test*.csv");
        string[] lines = File.ReadAllLines(train_files[0]);
        var all_original_features = lines[0].Split(",");
        var isSparseBitmask = Program.GenerateIsSparseBitMask(Program.Features).ToArray();

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
                            if (Array.Find(Program.Features, x => x == feature) != null)
                                row_dbl[Program.Features.FindIndex(x => x == feature)] = Double.Parse(data) + 1;
                        });
                
                // row_str.SkipLast(1).ForEach( (int i, string data) => Console.WriteLine(i + " " + data));

                
                Instance inst = new Instance(row_dbl, Program.BaseIndexes, isSparseBitmask, row_str.Last());
                TestSet.Add(inst);
                // Get label at the end of the row
                Label.Add(row_str.Last());
            }
        }

        Estimate();
        
    }

    static void Estimate()
    {
        var evaluatorMapping = new EvaluatorMapping();
        Evaluator = new ClassifierEvaluator  
            <List<Instance>,   
            int,   
            List<string>,   
            bool>(evaluatorMapping);

        Console.WriteLine("Start predict distribution");
        
        var savedclassifier = BayesPointMachineClassifier.LoadBinaryClassifier  
            <List<Instance>, int, List<string>, bool, Bernoulli>(Path.Join(SourceFolder, "bpm.bin"));

        var predictions = savedclassifier.PredictDistribution(TestSet);  
        Estimates = savedclassifier.Predict(TestSet).ToList<bool>();
        // Estimates = (List<bool>)estimates;

        PredictionsDictionary = new List<Dictionary<bool, double>>();
        predictions.ForEach( p => 
                    {   
                        var dict = new Dictionary<bool, double>();
                        dict.Add(true,  p.GetProbTrue());
                        dict.Add(false, p.GetProbFalse());
                        PredictionsDictionary.Add(dict);
                    }
        );

        ComputeMetrics();
    }

    static void ComputeMetrics()
    {
        var options = new JsonSerializerOptions
            {
                IncludeFields = true,
            };

        options.JsonSerializerOptions.Converters.Add(new NetTopologySuite.IO.Converters.GeoJsonConverterFactory());
        

        var confusionMatrix = Evaluator.ConfusionMatrix(TestSet, Estimates);  
        var jsonString = JsonSerializer.Serialize(confusionMatrix, options);
        File.WriteAllText(Path.Join(OutputFolder, "confusionMatrix.json"), jsonString);

        double errorCount = Evaluator.Evaluate(  
            TestSet, Label, Estimates, Metrics.ZeroOneError);  

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
            if (TestSet[i].label == "normal" && !Estimates[i]) //we predicted attack, but it is not
            {
                    falseNegative++; 
            }
            if (TestSet[i].label == "attack" && Estimates[i]) //we predicted normal, but it is an attack
            {
                    falsePositive++; 
            }
        }

        var metrics = new Dictionary<string, double>();

        metrics.Add("precisionTrue", precisionTrue);
        metrics.Add("precisionFalse", precisionFalse);
        metrics.Add("accuracyTrue", accuracyTrue);
        metrics.Add("accuracyFalse", accuracyFalse);
        metrics.Add("recallTrue", recallTrue);
        metrics.Add("recallFalse", recallFalse);
        metrics.Add("falsePositive", falsePositive);
        metrics.Add("falseNegative", falseNegative);
        metrics.Add("errorCount", errorCount);

        jsonString = JsonSerializer.Serialize(metrics, options);
        File.WriteAllText(Path.Join(OutputFolder, "metrics.json"), jsonString);   

        var rocCurve = Evaluator.ReceiverOperatingCharacteristicCurve(  
            true, TestSet, PredictionsDictionary);  

        var precisionRecallCurve = Evaluator.PrecisionRecallCurve(  
            true, TestSet, PredictionsDictionary);  

        var calibrationCurve = Evaluator.CalibrationCurve(  
            true, TestSet, PredictionsDictionary);

        var auc = Evaluator.AreaUnderRocCurve(  
            true, TestSet, PredictionsDictionary);

        Console.WriteLine("Total Estimates: " + Estimates.Count() + " error count: " +  errorCount + " area under curve: " + auc);

        jsonString = JsonSerializer.Serialize(rocCurve, options);
        File.WriteAllText(Path.Join(OutputFolder, "rocCurve.json"), jsonString);
        jsonString = JsonSerializer.Serialize(precisionRecallCurve, options);
        File.WriteAllText(Path.Join(OutputFolder, "precisionRecallCurve.json"), jsonString);
        jsonString = JsonSerializer.Serialize(calibrationCurve, options);
        File.WriteAllText(Path.Join(OutputFolder, "calibrationCurve.json"), jsonString);
    }
}

