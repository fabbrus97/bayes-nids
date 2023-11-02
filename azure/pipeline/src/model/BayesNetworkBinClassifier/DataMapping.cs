using System.Collections.Immutable;
using System.ComponentModel;
using System.Numerics;
using System.Reflection.Emit;
using Microsoft.ML.Probabilistic.Collections;
using Microsoft.ML.Probabilistic.Learners.Mappings;

/*
    reference: https://dotnet.github.io/infer/apiguide/api/Microsoft.ML.Probabilistic.Learners.Mappings.IBayesPointMachineClassifierMapping-4.html
*/

/*
Name 	            Description
TInstanceSource 	The type of the instance source.
TInstance 	        The type of an instance.
TLabelSource 	    The type of the label source.
TLabel 	            The type of a label.

To provide features in a dense representation, all arrays over feature indexes 
must be null and all instances must have the same number of feature values. 
To provide features in a sparse representation, each single instance must have 
the same number of feature indexes and values (arrays over feature indexes must 
not be null).
*/


public class DataMapping: 
    IBayesPointMachineClassifierMapping<List<Instance>, int, List<string>, bool>

{

    // public DataMapping(List<double[]> TInstanceSource, double[] TInstance, List<string> TLabelSource, bool TLabel)
    // {

    // }

    private int Batch { get; set; }

    public int GetClassCount(List<Instance> instanceSource, List<string> labelSource)
    {
        return 2; 
    }

    public int GetFeatureCount(List<Instance> instanceSource)
    {
        return instanceSource[0].featureCount;
    }

    public int[][]? GetFeatureIndexes(List<Instance> instanceSource, int batchNumber = 0)
    {  
        int elementsPerBatch = 0;
        int firstElement = 0;
        int n_features = n_features = instanceSource[0].featureCount;
        var batch = instanceSource.ToArray();
            
        if (batchNumber > 0){
            elementsPerBatch = (int)(instanceSource.Count()/Batch);
            firstElement = elementsPerBatch*(batchNumber - 1);
            n_features = instanceSource[0].featureCount;
            batch = instanceSource.Skip(firstElement).Take(elementsPerBatch).ToArray();                
        }

        var featureIndexes = new int[batch.Count()][];

        for(int i = 0; i < batch.Count(); i++)
        {
            featureIndexes[i] = new int[n_features];
            for(int j = 0; j < n_features; j++)
            {
                if (!batch[i].isSparse[j])
                    featureIndexes[i][j] = 0;
                else
                {
                    featureIndexes[i][j] = (int)batch[i].values[j];
                }
            }
        }
        return featureIndexes;
    }

    public int[]? GetFeatureIndexes(int instance, List<Instance> instanceSource)
    {
        var n_features = instanceSource[instance].featureCount;
        var indexes = new int[n_features];
        for(int i = 0; i < n_features; i++)
        {
            if (!instanceSource[instance].isSparse[i])
                indexes[i] = 0;
            else
                indexes[i] = (int)instanceSource[instance].values[i];
        }
        return indexes;
        // return vector.IndexOfAll(x => x != 0.0).ToArray(); // TODO non so se va qua
    }

    public double[][] GetFeatureValues(List<Instance> instanceSource, int batchNumber = 0)
    {
        var featureValues = new double[instanceSource.Count()][];
        int elementsPerBatch = 0;
        int firstElement = 0;
        var batch = instanceSource.ToArray();
        
        if (batchNumber > 0){
            elementsPerBatch = (int)(instanceSource.Count()/Batch);
            firstElement = elementsPerBatch*(batchNumber - 1);
            batch = instanceSource.Skip(firstElement).Take(elementsPerBatch).ToArray();                
        }

        int n_features = batch[0].featureCount;
        
        for (int i = 0; i < batch.Count(); i++)
        {
            featureValues[i] = new double[n_features];
            for (int j = 0; j < n_features; j++)
            {
                if (batch[i].isSparse[j])
                    featureValues[i][j] = 1;
                else
                    featureValues[i][j] = batch[i].values[j];
            }
        } 

        return featureValues;
    
    }

    public double[] GetFeatureValues(int instance, List<Instance> instanceSource)
    {
        var n_features = instanceSource[instance].featureCount;
        var values = new double[n_features];
        for(int i = 0; i < n_features; i++)
        {
            if (instanceSource[instance].isSparse[i])
                values[i] = 1;
            else
                values[i] = instanceSource[instance].values[i];
        }
        return values;
        // return instanceSource[instance];
        // return vector.FindAll(x => x != 0.0).Select(vi => vi.Value).ToArray();
    }


    public bool[] GetLabels(List<Instance> instanceSource, List<string> labelSource, int batchNumber = 0)
    {
        // return new bool[] {"normal", "intrusion"};
        bool[] labls = new bool[instanceSource.Count()];
        for (int i = 0; i < instanceSource.Count(); i++)
        {
            labls[i] = instanceSource[i].label == "normal";
        }
        return labls;
        
    }

    public bool IsSparse(List<Instance> instanceSource)
    {
        return true;
    }
}


            
            