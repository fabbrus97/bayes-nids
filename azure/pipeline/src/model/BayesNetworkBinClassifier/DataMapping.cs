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
    IBayesPointMachineClassifierMapping<List<double[]>, int, List<string>, bool>

{

    // public DataMapping(List<double[]> TInstanceSource, double[] TInstance, List<string> TLabelSource, bool TLabel)
    // {

    // }

    private int Batch { get; set; }

    public int GetClassCount(List<double[]> instanceSource, List<string> labelSource)
    {
        return 2; 
    }

    public int GetFeatureCount(List<double[]> instanceSource)
    {
        return instanceSource[0].Count();
    }

    public int[][]? GetFeatureIndexes(List<double[]> instanceSource, int batchNumber = 0)
    {  
        return null;
    }

    public int[]? GetFeatureIndexes(int instance, List<double[]> instanceSource)
    {
        // return null;
        return vector.IndexOfAll(x => x != 0.0).ToArray(); // TODO non so se va qua
    }

    public double[][] GetFeatureValues(List<double[]> instanceSource, int batchNumber = 0)
    {
        if (batchNumber > 0){
            int elementsPerBatch = (int)(instanceSource.Count()/Batch);
            int firstElement = elementsPerBatch*(batchNumber - 1);
            return instanceSource.Skip(firstElement).Take(elementsPerBatch).ToArray();
        }
        return instanceSource.ToArray(); 
    
    }

    public double[] GetFeatureValues(int instance, List<double[]> instanceSource)
    {
        // return instanceSource[instance];
        return vector.FindAll(x => x != 0.0).Select(vi => vi.Value).ToArray();
    }


    public bool[] GetLabels(List<double[]> instanceSource, List<string> labelSource, int batchNumber = 0)
    {
        // return new bool[] {"normal", "intrusion"};
        bool[] labls = new bool[instanceSource.Count()];
        for (int i = 0; i < instanceSource.Count(); i++)
        {
            labls[i] = true;
        }
        return labls;
        
    }

    public bool IsSparse(List<double[]> instanceSource)
    {
        return true;
    }
}


            
            